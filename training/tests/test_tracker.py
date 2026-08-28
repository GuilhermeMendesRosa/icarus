from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / ".agents" / "skills" / "icarus-coaching" / "scripts" / "icarus_tracker.py"
SPEC = importlib.util.spec_from_file_location("icarus_tracker", SCRIPT)
tracker = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(tracker)


def exercise(exercise_id: str, name: str) -> dict:
    return {
        "exercise_id": exercise_id,
        "name": name,
        "target_sets": 2,
        "rep_range": [6, 8],
        "target_rir": [1, 2],
        "rest_seconds": 120,
        "load_context": "total",
        "progression": {"type": "double_progression", "increment_kg": 2.5},
        "notes": "",
    }


class TrackerFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        templates = self.root / "training" / "templates"
        templates.mkdir(parents=True)
        shutil.copyfile(REPO / "training" / "templates" / "profile.default.json", templates / "profile.default.json")
        shutil.copyfile(
            REPO / "training" / "templates" / "active_program.default.json",
            templates / "active_program.default.json",
        )
        tracker.initialize(self.root)
        target = tracker.paths(self.root)
        profile = tracker.read_json(target["profile"])
        profile["onboarding_complete"] = True
        target["profile"].write_text(json.dumps(profile), encoding="utf-8")
        program = {
            "schema_version": 1,
            "program_id": "test-program",
            "name": "Teste",
            "status": "active",
            "started_on": "2026-08-28",
            "rotation": ["upper-a", "lower-a"],
            "sessions": {
                "upper-a": {"name": "Upper A", "focus": "superiores", "exercises": [exercise("supino", "Supino")]},
                "lower-a": {"name": "Lower A", "focus": "inferiores", "exercises": [exercise("agachamento", "Agachamento")]},
            },
            "review": {"after_completed_sessions": 6, "notes": None},
            "notes": "",
        }
        target["program"].write_text(json.dumps(program), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def args(self, **values):
        defaults = {"repo_root": str(self.root)}
        defaults.update(values)
        return SimpleNamespace(**defaults)

    def call(self, function, **values) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            code = function(self.args(**values))
        return code, output.getvalue()

    def test_full_session_advances_rotation_and_preserves_events(self) -> None:
        code, output = self.call(
            tracker.cmd_start,
            session_key=None,
            readiness=8,
            sleep_hours=7,
            bodyweight_kg=80,
            notes=None,
        )
        self.assertEqual(code, 0)
        self.assertIn("Upper A", output)

        code, output = self.call(
            tracker.cmd_log_set,
            exercise="supino",
            weight=80.0,
            reps=8,
            rir=2.0,
            set_number=None,
            set_type="working",
            unit="kg",
            load_context=None,
            pain=0,
            notes=None,
        )
        self.assertEqual(code, 0)
        self.assertIn("80 kg × 8", output)

        code, output = self.call(
            tracker.cmd_finish,
            session_rpe=8,
            duration_minutes=60,
            notes=None,
        )
        self.assertEqual(code, 0)
        self.assertIn("Lower A", output)

        events, errors = tracker.load_events(tracker.paths(self.root)["logs"])
        self.assertFalse(errors)
        self.assertEqual([event["type"] for event in events], ["session_started", "set_logged", "session_completed"])

        code, output = self.call(tracker.cmd_today)
        self.assertEqual(code, 0)
        self.assertIn("Lower A", output)

    def test_cancel_does_not_advance_rotation(self) -> None:
        self.call(
            tracker.cmd_start,
            session_key=None,
            readiness=None,
            sleep_hours=None,
            bodyweight_kg=None,
            notes=None,
        )
        code, _ = self.call(tracker.cmd_cancel, reason="academia fechou")
        self.assertEqual(code, 0)
        code, output = self.call(tracker.cmd_today)
        self.assertEqual(code, 0)
        self.assertIn("Upper A", output)

    def test_e1rm_uses_rir_and_rejects_assistance(self) -> None:
        working = {"weight": 80, "reps": 8, "rir": 2, "load_context": "total"}
        assisted = {"weight": 20, "reps": 8, "rir": 2, "load_context": "assisted"}
        self.assertAlmostEqual(tracker.estimated_1rm(working), 106.666666, places=5)
        self.assertIsNone(tracker.estimated_1rm(assisted))

    def test_progress_reports_strength_trend(self) -> None:
        for weight in (80.0, 82.5):
            self.call(
                tracker.cmd_start,
                session_key="upper-a",
                readiness=8,
                sleep_hours=7,
                bodyweight_kg=None,
                notes=None,
            )
            self.call(
                tracker.cmd_log_set,
                exercise="supino",
                weight=weight,
                reps=8,
                rir=2.0,
                set_number=None,
                set_type="working",
                unit="kg",
                load_context=None,
                pain=0,
                notes=None,
            )
            self.call(
                tracker.cmd_finish,
                session_rpe=8,
                duration_minutes=60,
                notes=None,
            )
        code, output = self.call(tracker.cmd_progress, exercise="supino", limit=5)
        self.assertEqual(code, 0)
        self.assertIn("Tendência e1RM", output)
        self.assertIn("+3.1%", output)

    def test_correction_replaces_effective_set_without_deleting_event(self) -> None:
        self.call(
            tracker.cmd_start,
            session_key=None,
            readiness=None,
            sleep_hours=None,
            bodyweight_kg=None,
            notes=None,
        )
        self.call(
            tracker.cmd_log_set,
            exercise="supino",
            weight=80.0,
            reps=8,
            rir=2.0,
            set_number=None,
            set_type="working",
            unit="kg",
            load_context=None,
            pain=0,
            notes=None,
        )
        code, output = self.call(
            tracker.cmd_correct_last_set,
            exercise=None,
            weight=82.5,
            reps=None,
            rir=None,
            pain=None,
            notes=None,
            reason="ditado incorreto",
        )
        self.assertEqual(code, 0)
        self.assertIn("82.5 kg × 8", output)
        events, errors = tracker.load_events(tracker.paths(self.root)["logs"])
        self.assertFalse(errors)
        session = tracker.active_session(tracker.grouped_sessions(events))
        self.assertIsNotNone(session)
        self.assertEqual(len(events), 3)
        self.assertEqual(len(tracker.sets_for(session)), 1)
        self.assertEqual(tracker.sets_for(session)[0]["weight"], 82.5)


if __name__ == "__main__":
    unittest.main()
