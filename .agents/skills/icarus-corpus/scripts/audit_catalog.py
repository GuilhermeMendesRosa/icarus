#!/usr/bin/env python3
"""Validate stable source IDs and paths in knowledge/SOURCES.md."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path


ENTRY = re.compile(r"^- \[(?P<id>[SA]\d{2})\] `(?P<path>[^`]+)`")
REFERENCE = re.compile(
    r"(?P<id>[SA]\d{2}), l\. (?P<start>\d+)(?:[–-](?P<end>\d+))?"
)


def normalized(path: str) -> str:
    """Compare macOS-decomposed and portable NFC paths as the same name."""
    return unicodedata.normalize("NFC", path)


def main() -> int:
    repo = Path(__file__).resolve().parents[4]
    catalog = repo / "knowledge" / "SOURCES.md"
    if not catalog.is_file():
        print(f"ERROR: catálogo ausente: {catalog}")
        return 1

    entries: dict[str, str] = {}
    errors: list[str] = []
    actual_paths = {
        normalized(str(path.relative_to(repo))): path
        for path in (repo / "icaro").iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    }
    for number, line in enumerate(catalog.read_text(encoding="utf-8").splitlines(), 1):
        match = ENTRY.match(line)
        if not match:
            continue
        source_id = match.group("id")
        relative = match.group("path")
        if source_id in entries:
            errors.append(f"ID duplicado {source_id} na linha {number}")
        entries[source_id] = relative
        if normalized(relative) not in actual_paths:
            errors.append(f"Arquivo ausente para {source_id}: {relative}")

    if not entries:
        errors.append("Nenhuma entrada Sxx/Axx encontrada no catálogo")

    registered = {normalized(relative) for relative in entries.values()}
    corpus_dir = repo / "icaro"
    corpus_files = {
        normalized(str(path.relative_to(repo)))
        for path in corpus_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    }
    for relative in sorted(corpus_files - registered):
        errors.append(f"Fonte não catalogada: {relative}")
    for relative in sorted(registered - corpus_files):
        errors.append(f"Entrada fora do corpus ou inexistente: {relative}")

    for markdown in sorted((repo / "knowledge").rglob("*.md")):
        text = markdown.read_text(encoding="utf-8")
        for match in REFERENCE.finditer(text):
            source_id = match.group("id")
            if source_id not in entries:
                errors.append(
                    f"Referência a ID ausente {source_id} em "
                    f"{markdown.relative_to(repo)}"
                )
                continue
            source_path = actual_paths.get(normalized(entries[source_id]))
            if source_path is None:
                continue
            line_count = len(source_path.read_text(encoding="utf-8").splitlines())
            start = int(match.group("start"))
            end = int(match.group("end") or start)
            if start < 1 or end < start or end > line_count:
                errors.append(
                    f"Faixa inválida {source_id}, l. {start}–{end} em "
                    f"{markdown.relative_to(repo)} (fonte tem {line_count} linhas)"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    source_count = sum(source_id.startswith("S") for source_id in entries)
    artifact_count = sum(source_id.startswith("A") for source_id in entries)
    print(
        f"OK: {source_count} transcrições, {artifact_count} artefato(s), "
        "todos os caminhos e IDs estão consistentes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
