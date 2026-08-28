#!/usr/bin/env python3
"""Local, dependency-free workout tracker for the Icarus coaching skill."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import unicodedata
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SCHEMA_VERSION = 1
LOAD_CONTEXTS = {"total", "per_hand", "machine_stack", "bodyweight", "assisted", "other"}


def repo_root(override: str | None = None) -> Path:
    return Path(override).resolve() if override else Path(__file__).resolve().parents[4]


def paths(root: Path) -> dict[str, Path]:
    training = root / "training"
    data = training / "data"
    return {
        "training": training,
        "data": data,
        "profile": data / "profile.json",
        "program": data / "active_program.json",
        "logs": data / "logs",
        "reports": data / "reports",
        "profile_template": training / "templates" / "profile.default.json",
        "program_template": training / "templates" / "active_program.default.json",
    }


def initialize(root: Path) -> list[str]:
    target = paths(root)
    target["data"].mkdir(parents=True, exist_ok=True)
    target["logs"].mkdir(parents=True, exist_ok=True)
    target["reports"].mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for key, template_key in (("profile", "profile_template"), ("program", "program_template")):
        if not target[key].exists():
            if not target[template_key].is_file():
                raise FileNotFoundError(f"Template ausente: {target[template_key]}")
            shutil.copyfile(target[template_key], target[key])
            created.append(str(target[key].relative_to(root)))
    return created


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} deve conter um objeto JSON")
    return value


def load_runtime(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    initialize(root)
    target = paths(root)
    return read_json(target["profile"]), read_json(target["program"]), target


def timezone_for(profile: dict[str, Any]) -> ZoneInfo:
    name = profile.get("athlete", {}).get("timezone") or "America/Sao_Paulo"
    try:
        return ZoneInfo(name)
    except Exception as exc:
        raise ValueError(f"Fuso inválido no perfil: {name}") from exc


def now_iso(profile: dict[str, Any]) -> str:
    return datetime.now(timezone_for(profile)).isoformat(timespec="microseconds")


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return "-".join("".join(char.lower() if char.isalnum() else " " for char in ascii_value).split())


def event_base(profile: dict[str, Any], event_type: str, session_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": str(uuid.uuid4()),
        "timestamp": now_iso(profile),
        "type": event_type,
        "session_id": session_id,
    }


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def load_events(logs: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    sequence = 0
    if not logs.exists():
        return events, errors
    for file_path in sorted(logs.rglob("*.jsonl")):
        with file_path.open(encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, 1):
                if not raw.strip():
                    continue
                try:
                    event = json.loads(raw)
                    if not isinstance(event, dict):
                        raise ValueError("evento não é objeto")
                    event["_file"] = str(file_path)
                    event["_sequence"] = sequence
                    sequence += 1
                    events.append(event)
                except (json.JSONDecodeError, ValueError) as exc:
                    errors.append(f"{file_path}:{line_number}: {exc}")
    events.sort(key=lambda event: (str(event.get("timestamp", "")), int(event.get("_sequence", 0))))
    return events, errors


def grouped_sessions(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    sessions: dict[str, dict[str, Any]] = {}
    for event in events:
        session_id = event.get("session_id")
        if not session_id:
            continue
        session = sessions.setdefault(session_id, {"session_id": session_id, "events": []})
        session["events"].append(event)
        event_type = event.get("type")
        if event_type == "session_started":
            session["started"] = event
            session["session_key"] = event.get("session_key")
            session["file"] = Path(event["_file"])
        elif event_type == "session_completed":
            session["completed"] = event
        elif event_type == "session_cancelled":
            session["cancelled"] = event
    return sessions


def complete_sessions(sessions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    completed = [session for session in sessions.values() if session.get("started") and session.get("completed")]
    return sorted(completed, key=lambda session: session["completed"].get("timestamp", ""))


def active_session(sessions: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    active = [
        session
        for session in sessions.values()
        if session.get("started") and not session.get("completed") and not session.get("cancelled")
    ]
    if not active:
        return None
    return max(active, key=lambda session: session["started"].get("timestamp", ""))


def validation_errors(profile: dict[str, Any], program: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if profile.get("schema_version") != SCHEMA_VERSION:
        errors.append("profile.json usa schema_version incompatível")
    if program.get("schema_version") != SCHEMA_VERSION:
        errors.append("active_program.json usa schema_version incompatível")
    rotation = program.get("rotation")
    sessions = program.get("sessions")
    if not isinstance(rotation, list):
        errors.append("program.rotation deve ser lista")
        rotation = []
    if not isinstance(sessions, dict):
        errors.append("program.sessions deve ser objeto")
        sessions = {}
    for session_key in rotation:
        if session_key not in sessions:
            errors.append(f"rotação aponta para sessão ausente: {session_key}")
    for session_key, session in sessions.items():
        exercises = session.get("exercises") if isinstance(session, dict) else None
        if not isinstance(exercises, list) or not exercises:
            errors.append(f"{session_key}: exercises deve ser lista não vazia")
            continue
        seen: set[str] = set()
        for index, exercise in enumerate(exercises, 1):
            prefix = f"{session_key}.exercises[{index}]"
            exercise_id = exercise.get("exercise_id") if isinstance(exercise, dict) else None
            if not exercise_id:
                errors.append(f"{prefix}: exercise_id ausente")
                continue
            if exercise_id in seen:
                errors.append(f"{session_key}: exercise_id duplicado: {exercise_id}")
            seen.add(exercise_id)
            if not exercise.get("name"):
                errors.append(f"{prefix}: name ausente")
            if not isinstance(exercise.get("target_sets"), int) or exercise["target_sets"] < 1:
                errors.append(f"{prefix}: target_sets inválido")
            rep_range = exercise.get("rep_range")
            if not (isinstance(rep_range, list) and len(rep_range) == 2 and 0 < rep_range[0] <= rep_range[1]):
                errors.append(f"{prefix}: rep_range inválido")
            target_rir = exercise.get("target_rir")
            if not (isinstance(target_rir, list) and len(target_rir) == 2 and 0 <= target_rir[0] <= target_rir[1]):
                errors.append(f"{prefix}: target_rir inválido")
            if exercise.get("load_context") not in LOAD_CONTEXTS:
                errors.append(f"{prefix}: load_context inválido")
    event_ids: set[str] = set()
    for event in events:
        event_id = event.get("event_id")
        if not event_id:
            errors.append("evento sem event_id")
        elif event_id in event_ids:
            errors.append(f"event_id duplicado: {event_id}")
        else:
            event_ids.add(event_id)
        if event.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"evento {event_id or '?'} usa schema_version incompatível")
    return errors


def ensure_operational(profile: dict[str, Any], program: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not profile.get("onboarding_complete"):
        problems.append("onboarding pendente em training/data/profile.json")
    if program.get("status") != "active":
        problems.append("programa ainda não está active")
    if not program.get("rotation"):
        problems.append("programa não tem rotação")
    return problems


def next_session_key(program: dict[str, Any], completed: list[dict[str, Any]]) -> str:
    rotation = program["rotation"]
    if not completed:
        return rotation[0]
    last_key = completed[-1].get("session_key")
    if last_key not in rotation:
        return rotation[0]
    return rotation[(rotation.index(last_key) + 1) % len(rotation)]


def sets_for(session: dict[str, Any], exercise_id: str | None = None) -> list[dict[str, Any]]:
    candidates = [
        event for event in session.get("events", []) if event.get("type") in {"set_logged", "set_corrected"}
    ]
    replaced = {event.get("replaces_event_id") for event in candidates if event.get("replaces_event_id")}
    result = [event for event in candidates if event.get("event_id") not in replaced]
    if exercise_id:
        result = [event for event in result if event.get("exercise_id") == exercise_id]
    return sorted(result, key=lambda event: (int(event.get("set_number", 0)), str(event.get("timestamp", ""))))


def comparable(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left.get("exercise_id") == right.get("exercise_id")
        and left.get("unit") == right.get("unit")
        and left.get("load_context") == right.get("load_context")
    )


def estimated_1rm(event: dict[str, Any]) -> float | None:
    context = event.get("load_context")
    weight = event.get("weight")
    reps = event.get("reps")
    rir = event.get("rir")
    if context in {"bodyweight", "assisted", "other"}:
        return None
    if not isinstance(weight, (int, float)) or weight <= 0 or not isinstance(reps, int) or reps < 1 or reps > 20:
        return None
    effective_reps = reps + (rir if isinstance(rir, (int, float)) and 0 <= rir <= 5 else 0)
    return float(weight) * (1 + float(effective_reps) / 30)


def format_number(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def format_set(event: dict[str, Any]) -> str:
    weight = format_number(event.get("weight", 0))
    unit = event.get("unit", "kg")
    reps = event.get("reps", "?")
    rir = event.get("rir")
    rir_text = f" @ {format_number(rir)} RIR" if rir is not None else ""
    return f"{weight} {unit} × {reps}{rir_text}"


def previous_exposure(
    completed: list[dict[str, Any]], exercise_id: str, before_session_id: str | None = None
) -> dict[str, Any] | None:
    candidates = []
    for session in completed:
        if before_session_id and session.get("session_id") == before_session_id:
            continue
        if sets_for(session, exercise_id):
            candidates.append(session)
    return candidates[-1] if candidates else None


def progression_hint(exercise: dict[str, Any], previous_sets: list[dict[str, Any]]) -> str:
    if not previous_sets:
        return "Sem histórico: calibre uma carga que respeite a faixa e o RIR-alvo."
    target_sets = exercise["target_sets"]
    upper_reps = exercise["rep_range"][1]
    min_rir = exercise["target_rir"][0]
    relevant = previous_sets[:target_sets]
    reached = len(relevant) >= target_sets and all(
        event.get("reps", 0) >= upper_reps
        and (event.get("rir") is None or event.get("rir") >= min_rir)
        for event in relevant
    )
    last = ", ".join(format_set(event) for event in relevant)
    if reached:
        increment = exercise.get("progression", {}).get("increment_kg")
        if increment:
            return f"Última: {last}. Critério atingido; considere +{format_number(increment)} kg mantendo técnica e RIR."
        return f"Última: {last}. Critério atingido; use o menor incremento disponível."
    return f"Última: {last}. Tente acrescentar repetição sem perder técnica ou sair do RIR-alvo."


def session_definition(program: dict[str, Any], session_key: str) -> dict[str, Any]:
    try:
        return program["sessions"][session_key]
    except KeyError as exc:
        raise ValueError(f"Sessão não encontrada no programa: {session_key}") from exc


def resolve_exercise(definition: dict[str, Any], query: str) -> dict[str, Any]:
    normalized_query = normalize(query)
    exact = [exercise for exercise in definition["exercises"] if normalize(exercise["exercise_id"]) == normalized_query]
    if len(exact) == 1:
        return exact[0]
    matches = [
        exercise
        for exercise in definition["exercises"]
        if normalized_query in normalize(exercise["exercise_id"]) or normalized_query in normalize(exercise["name"])
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(f"Exercício não encontrado nesta sessão: {query}")
    raise ValueError("Exercício ambíguo: " + ", ".join(exercise["exercise_id"] for exercise in matches))


def print_problems(problems: list[str]) -> int:
    for problem in problems:
        print(f"ERRO: {problem}")
    return 2


def cmd_init(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    created = initialize(root)
    if created:
        print("Criado: " + ", ".join(created))
    else:
        print("OK: estrutura de dados já inicializada.")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, program, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    errors = log_errors + validation_errors(profile, program, events)
    if errors:
        return print_problems(errors)
    operational = ensure_operational(profile, program)
    if operational:
        print("Estrutura válida, mas ainda não operacional:")
        for item in operational:
            print(f"- {item}")
        return 0
    print(f"OK: programa ativo e {len(events)} evento(s) válido(s).")
    return 0


def cmd_today(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, program, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    errors = log_errors + validation_errors(profile, program, events)
    if errors:
        return print_problems(errors)
    operational = ensure_operational(profile, program)
    if operational:
        print("Icarus ainda precisa concluir seu onboarding antes de indicar o treino do dia.")
        for item in operational:
            print(f"- {item}")
        return 2
    sessions = grouped_sessions(events)
    current = active_session(sessions)
    completed = complete_sessions(sessions)
    if current:
        session_key = current["session_key"]
        print(f"Sessão em andamento: {session_definition(program, session_key).get('name', session_key)}")
        print(f"session_id: {current['session_id']} | séries registradas: {len(sets_for(current))}")
    else:
        session_key = next_session_key(program, completed)
        definition = session_definition(program, session_key)
        print(f"Treino do dia: {definition.get('name', session_key)} [{session_key}]")
        if definition.get("focus"):
            print(f"Foco: {definition['focus']}")
    definition = session_definition(program, session_key)
    for index, exercise in enumerate(definition["exercises"], 1):
        previous = previous_exposure(completed, exercise["exercise_id"])
        previous_sets = sets_for(previous, exercise["exercise_id"]) if previous else []
        rep_range = exercise["rep_range"]
        rir = exercise["target_rir"]
        print(
            f"{index}. {exercise['name']} ({exercise['exercise_id']}): "
            f"{exercise['target_sets']}×{rep_range[0]}–{rep_range[1]}, "
            f"RIR {rir[0]}–{rir[1]}, descanso {exercise['rest_seconds']}s"
        )
        print(f"   {progression_hint(exercise, previous_sets)}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, program, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    errors = log_errors + validation_errors(profile, program, events)
    if errors:
        return print_problems(errors)
    operational = ensure_operational(profile, program)
    if operational:
        return print_problems(operational)
    sessions = grouped_sessions(events)
    current = active_session(sessions)
    if current:
        print(f"ERRO: já existe sessão em andamento: {current['session_id']}")
        return 2
    if args.readiness is not None and not 1 <= args.readiness <= 10:
        print("ERRO: prontidão deve ficar entre 1 e 10.")
        return 2
    if args.sleep_hours is not None and not 0 <= args.sleep_hours <= 24:
        print("ERRO: horas de sono devem ficar entre 0 e 24.")
        return 2
    if args.bodyweight_kg is not None and args.bodyweight_kg <= 0:
        print("ERRO: peso corporal deve ser positivo.")
        return 2
    completed = complete_sessions(sessions)
    session_key = args.session_key or next_session_key(program, completed)
    definition = session_definition(program, session_key)
    timestamp = now_iso(profile)
    date = timestamp[:10]
    session_id = f"{date}-{session_key}-{uuid.uuid4().hex[:6]}"
    log_path = target["logs"] / date[:4] / date[5:7] / f"{session_id}.jsonl"
    event = event_base(profile, "session_started", session_id)
    event.update(
        {
            "session_key": session_key,
            "program_id": program.get("program_id"),
            "readiness_1_to_10": args.readiness,
            "sleep_hours": args.sleep_hours,
            "bodyweight_kg": args.bodyweight_kg,
            "notes": args.notes,
        }
    )
    append_event(log_path, event)
    print(f"Treino iniciado: {definition.get('name', session_key)}")
    print(f"session_id: {session_id}")
    return 0


def cmd_log_set(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, program, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    if log_errors:
        return print_problems(log_errors)
    sessions = grouped_sessions(events)
    current = active_session(sessions)
    if not current:
        print("ERRO: não existe treino em andamento. Use start primeiro.")
        return 2
    definition = session_definition(program, current["session_key"])
    try:
        exercise = resolve_exercise(definition, args.exercise)
    except ValueError as exc:
        print(f"ERRO: {exc}")
        return 2
    if args.reps < 0 or args.weight < 0:
        print("ERRO: peso e repetições não podem ser negativos.")
        return 2
    if args.set_number is not None and args.set_number < 1:
        print("ERRO: número da série deve ser positivo.")
        return 2
    if args.rir is not None and not 0 <= args.rir <= 10:
        print("ERRO: RIR deve ficar entre 0 e 10.")
        return 2
    if args.pain is not None and not 0 <= args.pain <= 10:
        print("ERRO: dor deve ficar entre 0 e 10.")
        return 2
    if args.load_context is not None and args.load_context != exercise["load_context"]:
        print(
            "ERRO: contexto de carga diverge do programa. "
            "Use o contexto configurado ou crie um novo exercise_id para a variante."
        )
        return 2
    existing = sets_for(current, exercise["exercise_id"])
    set_number = args.set_number or len(existing) + 1
    event = event_base(profile, "set_logged", current["session_id"])
    event.update(
        {
            "session_key": current["session_key"],
            "exercise_id": exercise["exercise_id"],
            "exercise_name": exercise["name"],
            "set_number": set_number,
            "set_type": args.set_type,
            "weight": args.weight,
            "unit": args.unit or profile.get("athlete", {}).get("default_unit") or "kg",
            "load_context": args.load_context or exercise["load_context"],
            "reps": args.reps,
            "rir": args.rir,
            "pain_0_to_10": args.pain,
            "notes": args.notes,
        }
    )
    append_event(current["file"], event)
    print(f"Registrado: {exercise['name']} — série {set_number}: {format_set(event)}.")
    completed = complete_sessions(sessions)
    previous = previous_exposure(completed, exercise["exercise_id"])
    previous_sets = sets_for(previous, exercise["exercise_id"]) if previous else []
    prior_same = next((item for item in previous_sets if item.get("set_number") == set_number and comparable(event, item)), None)
    if prior_same:
        current_e1rm = estimated_1rm(event)
        prior_e1rm = estimated_1rm(prior_same)
        comparison = f"Anterior equivalente: {format_set(prior_same)}"
        if current_e1rm and prior_e1rm:
            delta = (current_e1rm / prior_e1rm - 1) * 100
            comparison += f" | e1RM estimado {delta:+.1f}%"
        print(comparison + ".")
    elif previous_sets:
        print("Há histórico deste exercício, mas nenhuma série diretamente comparável nesta posição.")
    else:
        print("Primeiro registro comparável deste exercício.")
    if args.pain is not None and args.pain >= 4:
        print("ATENÇÃO: dor relevante registrada; interrompa a progressão e faça triagem de segurança antes da próxima série.")
    return 0


def cmd_correct_last_set(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, _, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    if log_errors:
        return print_problems(log_errors)
    current = active_session(grouped_sessions(events))
    if not current:
        print("ERRO: não existe treino em andamento.")
        return 2
    effective_sets = sets_for(current)
    if args.exercise:
        query = normalize(args.exercise)
        effective_sets = [
            event
            for event in effective_sets
            if query in normalize(str(event.get("exercise_id", "")))
            or query in normalize(str(event.get("exercise_name", "")))
        ]
    if not effective_sets:
        print("ERRO: nenhuma série compatível para corrigir.")
        return 2
    original = effective_sets[-1]
    updates = {
        "weight": args.weight,
        "reps": args.reps,
        "rir": args.rir,
        "pain_0_to_10": args.pain,
        "notes": args.notes,
    }
    if args.weight is not None and args.weight < 0:
        print("ERRO: peso não pode ser negativo.")
        return 2
    if args.reps is not None and args.reps < 0:
        print("ERRO: repetições não podem ser negativas.")
        return 2
    if args.rir is not None and not 0 <= args.rir <= 10:
        print("ERRO: RIR deve ficar entre 0 e 10.")
        return 2
    if args.pain is not None and not 0 <= args.pain <= 10:
        print("ERRO: dor deve ficar entre 0 e 10.")
        return 2
    if all(value is None for value in updates.values()):
        print("ERRO: informe ao menos um campo corrigido.")
        return 2
    event = event_base(profile, "set_corrected", current["session_id"])
    for key in (
        "session_key",
        "exercise_id",
        "exercise_name",
        "set_number",
        "set_type",
        "weight",
        "unit",
        "load_context",
        "reps",
        "rir",
        "pain_0_to_10",
        "notes",
    ):
        event[key] = original.get(key)
    for key, value in updates.items():
        if value is not None:
            event[key] = value
    event["replaces_event_id"] = original["event_id"]
    event["correction_reason"] = args.reason
    append_event(current["file"], event)
    print(
        f"Correção registrada: {event['exercise_name']} — série {event['set_number']}: "
        f"{format_set(event)} (substitui {original['event_id']})."
    )
    return 0


def cmd_finish(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, program, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    if log_errors:
        return print_problems(log_errors)
    sessions = grouped_sessions(events)
    current = active_session(sessions)
    if not current:
        print("ERRO: não existe treino em andamento.")
        return 2
    if args.session_rpe is not None and not 1 <= args.session_rpe <= 10:
        print("ERRO: RPE da sessão deve ficar entre 1 e 10.")
        return 2
    if args.duration_minutes is not None and args.duration_minutes <= 0:
        print("ERRO: duração deve ser positiva.")
        return 2
    event = event_base(profile, "session_completed", current["session_id"])
    event.update(
        {
            "session_rpe_1_to_10": args.session_rpe,
            "duration_minutes": args.duration_minutes,
            "notes": args.notes,
        }
    )
    append_event(current["file"], event)
    current_sets = sets_for(current)
    volume = sum(
        float(item.get("weight", 0)) * int(item.get("reps", 0))
        for item in current_sets
        if item.get("load_context") not in {"bodyweight", "assisted", "other"}
    )
    print(f"Treino finalizado: {len(current_sets)} série(s) registrada(s).")
    if volume:
        print(f"Volume externo registrado: {format_number(volume)} carga×reps (métrica descritiva).")
    completed_before = complete_sessions(sessions)
    next_key = next_session_key(program, completed_before + [{"session_key": current["session_key"], "completed": event}])
    print(f"Próxima sessão da rotação: {session_definition(program, next_key).get('name', next_key)} [{next_key}].")
    return 0


def cmd_cancel(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    profile, _, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    if log_errors:
        return print_problems(log_errors)
    current = active_session(grouped_sessions(events))
    if not current:
        print("ERRO: não existe treino em andamento.")
        return 2
    event = event_base(profile, "session_cancelled", current["session_id"])
    event["reason"] = args.reason
    append_event(current["file"], event)
    print(f"Sessão cancelada sem avançar a rotação: {current['session_id']}.")
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    root = repo_root(args.repo_root)
    _, program, target = load_runtime(root)
    events, log_errors = load_events(target["logs"])
    if log_errors:
        return print_problems(log_errors)
    if args.limit < 1:
        print("ERRO: limit deve ser positivo.")
        return 2
    completed = complete_sessions(grouped_sessions(events))
    exercise_names: dict[str, str] = {}
    for definition in program.get("sessions", {}).values():
        for exercise in definition.get("exercises", []):
            exercise_names[exercise["exercise_id"]] = exercise["name"]
    exercise_ids = sorted({event.get("exercise_id") for event in events if event.get("type") == "set_logged" and event.get("exercise_id")})
    if args.exercise:
        query = normalize(args.exercise)
        matches = [item for item in exercise_ids if query in normalize(item) or query in normalize(exercise_names.get(item, ""))]
        if len(matches) != 1:
            print("ERRO: filtro de exercício não encontrou correspondência única.")
            if matches:
                print("Possibilidades: " + ", ".join(matches))
            return 2
        exercise_ids = matches
    if not exercise_ids:
        print("Ainda não há séries registradas em treinos finalizados.")
        return 0
    for exercise_id in exercise_ids:
        signatures = sorted(
            {
                (item.get("unit", "?"), item.get("load_context", "other"))
                for session in completed
                for item in sets_for(session, exercise_id)
            }
        )
        if not signatures:
            continue
        print(f"\n{exercise_names.get(exercise_id, exercise_id)} [{exercise_id}]")
        for unit, load_context in signatures:
            exposures: list[tuple[str, list[dict[str, Any]]]] = []
            for session in completed:
                session_sets = [
                    item
                    for item in sets_for(session, exercise_id)
                    if item.get("unit", "?") == unit and item.get("load_context", "other") == load_context
                ]
                if session_sets:
                    date = session["completed"].get("timestamp", "")[:10]
                    exposures.append((date, session_sets))
            print(f"  Contexto comparável: {unit} / {load_context}")
            recent = exposures[-args.limit :]
            for date, session_sets in recent:
                best = max(session_sets, key=lambda item: estimated_1rm(item) or float(item.get("weight", 0)))
                volume = sum(
                    float(item.get("weight", 0)) * int(item.get("reps", 0))
                    for item in session_sets
                    if item.get("load_context") not in {"bodyweight", "assisted", "other"}
                )
                print(f"  - {date}: melhor {format_set(best)} | volume externo {format_number(volume)}")
            first_values = [estimated_1rm(item) for item in exposures[0][1]]
            last_values = [estimated_1rm(item) for item in exposures[-1][1]]
            first_best = max((value for value in first_values if value is not None), default=None)
            last_best = max((value for value in last_values if value is not None), default=None)
            if first_best and last_best and len(exposures) > 1:
                delta = (last_best / first_best - 1) * 100
                print(
                    f"    Tendência e1RM da primeira à última exposição: "
                    f"{delta:+.1f}% em {len(exposures)} exposições."
                )
    return 0


def parser() -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser(description="Memória local de treinos do Icarus")
    root_parser.add_argument("--repo-root", help=argparse.SUPPRESS)
    sub = root_parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Inicializa os dados locais")
    init.set_defaults(func=cmd_init)

    validate = sub.add_parser("validate", help="Valida perfil, programa e eventos")
    validate.set_defaults(func=cmd_validate)

    today = sub.add_parser("today", help="Mostra sessão do dia e histórico relevante")
    today.set_defaults(func=cmd_today)

    start = sub.add_parser("start", help="Inicia a próxima sessão")
    start.add_argument("--session-key")
    start.add_argument("--readiness", type=float)
    start.add_argument("--sleep-hours", type=float)
    start.add_argument("--bodyweight-kg", type=float)
    start.add_argument("--notes")
    start.set_defaults(func=cmd_start)

    log_set = sub.add_parser("log-set", help="Registra uma série na sessão atual")
    log_set.add_argument("--exercise", required=True)
    log_set.add_argument("--weight", required=True, type=float)
    log_set.add_argument("--reps", required=True, type=int)
    log_set.add_argument("--rir", type=float)
    log_set.add_argument("--set-number", type=int)
    log_set.add_argument("--set-type", default="working")
    log_set.add_argument("--unit")
    log_set.add_argument("--load-context", choices=sorted(LOAD_CONTEXTS))
    log_set.add_argument("--pain", type=float)
    log_set.add_argument("--notes")
    log_set.set_defaults(func=cmd_log_set)

    correct = sub.add_parser("correct-last-set", help="Corrige a última série sem apagar o evento original")
    correct.add_argument("--exercise")
    correct.add_argument("--weight", type=float)
    correct.add_argument("--reps", type=int)
    correct.add_argument("--rir", type=float)
    correct.add_argument("--pain", type=float)
    correct.add_argument("--notes")
    correct.add_argument("--reason", default="correção informada pelo usuário")
    correct.set_defaults(func=cmd_correct_last_set)

    finish = sub.add_parser("finish", help="Finaliza a sessão atual")
    finish.add_argument("--session-rpe", type=float)
    finish.add_argument("--duration-minutes", type=float)
    finish.add_argument("--notes")
    finish.set_defaults(func=cmd_finish)

    cancel = sub.add_parser("cancel", help="Cancela sem avançar a rotação")
    cancel.add_argument("--reason", required=True)
    cancel.set_defaults(func=cmd_cancel)

    progress = sub.add_parser("progress", help="Resume a evolução por exercício")
    progress.add_argument("--exercise")
    progress.add_argument("--limit", type=int, default=5)
    progress.set_defaults(func=cmd_progress)
    return root_parser


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
