#!/usr/bin/env python3
"""Validate and sanitize the private Markdown CV for the public site.

The private CV is intentionally treated as a small, strict input language.  A
successful import writes only the allowlisted fields to ``.generated/cv.json``
and, in release mode, copies a checked PDF to the public extra directory.  The
YAML front matter is never parsed into the public object. Outputs are staged in
their destination directories before either is replaced. If an import fails,
the requested output files are removed to avoid leaving a stale pair. This
cleanup cannot protect against process termination or a machine failure.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
REQUIRED_SECTIONS = (
    "SUMMARY",
    "EDUCATION",
    "AREAS OF EXPERTISE",
    "EXPERIENCE",
    "ADDITIONAL EXPERIENCE",
    "RESEARCH EXPERIENCE",
    "SKILLS",
)
SECTION_HEADINGS = set(REQUIRED_SECTIONS)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TABLE_RE = re.compile(r"^\|.*\|\s*$")
PAGEBREAK = "<!-- pagebreak -->"


class CVParseError(ValueError):
    """Raised when a CV does not follow the approved input structure."""


def _error(message: str, line_number: int | None = None) -> CVParseError:
    if line_number is not None:
        return CVParseError(f"line {line_number}: {message}")
    return CVParseError(message)


def _clean_text(value: str, *, line_number: int | None = None) -> str:
    """Remove the small set of formatting markers allowed in CV fields."""

    value = html.unescape(value).strip()
    value = re.sub(r"</?u>", "", value)
    if re.search(r"<[^>]+>", value):
        raise _error("unsupported HTML in field", line_number)
    value = value.replace("**", "").replace("`", "")
    value = re.sub(r"(?<!\w)\*(?!\s)(.*?)(?<!\s)\*", r"\1", value)
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        raise _error("empty field", line_number)
    return value


def _strip_front_matter(lines: list[str]) -> list[str]:
    """Discard a leading YAML document without interpreting any values."""

    if not lines:
        raise CVParseError("CV is empty")
    start = next((index for index, line in enumerate(lines) if line.strip()), None)
    if start is None:
        raise CVParseError("CV is empty")
    if lines[start].strip() != "---":
        return lines
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].strip() == "---"),
        None,
    )
    if end is None:
        raise _error("YAML front matter has no closing delimiter", start + 1)
    return lines[end + 1 :]


def _sections(markdown: str) -> dict[str, list[tuple[int, str]]]:
    lines = _strip_front_matter(markdown.splitlines())
    sections: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    saw_content = False
    for index, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            level, title = len(match.group(1)), match.group(2).strip()
            if level != 2:
                raise _error("only level-two section headings are allowed", index)
            if title not in SECTION_HEADINGS:
                raise _error(f"unknown section heading: {title}", index)
            if title in sections:
                raise _error(f"duplicate section: {title}", index)
            current = title
            sections[current] = []
            saw_content = False
            continue
        if current is None:
            if line.strip():
                raise _error("content outside an allowed section", index)
            continue
        if line.strip():
            saw_content = True
        sections[current].append((index, line))
    missing = [name for name in REQUIRED_SECTIONS if name not in sections]
    if missing:
        raise CVParseError("missing required section(s): " + ", ".join(missing))
    empty = [name for name in REQUIRED_SECTIONS if not any(value.strip() for _, value in sections[name])]
    if empty:
        raise CVParseError("empty required section(s): " + ", ".join(empty))
    return sections


def _without_pagebreak(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return [(number, line) for number, line in lines if line.strip() != PAGEBREAK]


def _is_bullet(line: str) -> bool:
    return line.lstrip().startswith("- ")


def _bullet(line: str, number: int) -> str:
    if not _is_bullet(line):
        raise _error("expected a hyphen bullet", number)
    return _clean_text(line.lstrip()[2:], line_number=number)


def _split_table_row(line: str, number: int) -> list[str]:
    if not TABLE_RE.match(line.strip()):
        raise _error("expected a Markdown table row", number)
    row = line.strip()[1:-1]
    cells = re.split(r"(?<!\\)\|", row)
    if len(cells) != 2:
        raise _error("table rows must contain exactly two cells", number)
    return [cell.strip().replace(r"\|", "|") for cell in cells]


def _is_separator_row(cells: list[str]) -> bool:
    return len(cells) == 2 and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _marked_cell(cell: str, marker: str, number: int) -> str | None:
    if marker == "*" and (cell.startswith("**") or cell.endswith("**")):
        return None
    if not (cell.startswith(marker) and cell.endswith(marker) and len(cell) > 2 * len(marker)):
        return None
    return _clean_text(cell[len(marker) : -len(marker)], line_number=number)


def _parse_entries(lines: list[tuple[int, str]], section: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    rows = _without_pagebreak(lines)
    index = 0
    while index < len(rows):
        number, line = rows[index]
        if not line.strip():
            index += 1
            continue
        if not TABLE_RE.match(line.strip()):
            raise _error(f"unexpected content in {section}", number)
        first = _split_table_row(line, number)
        index += 1
        organization = _marked_cell(first[0], "**", number)
        location = _marked_cell(first[1], "**", number)
        compact_organization = _marked_cell(first[0], "*", number)
        compact_period = _marked_cell(first[1], "*", number)
        compact = organization is None and location is None and compact_organization is not None and compact_period is not None
        if index >= len(rows) or not _is_separator_row(_split_table_row(rows[index][1], rows[index][0])):
            raise _error("expected a table separator row", rows[index][0] if index < len(rows) else number)
        index += 1
        if compact:
            # Research publications may use a compact organization/period row.
            organization, location, role, period = compact_organization, "", "", compact_period
        else:
            if index >= len(rows):
                raise _error("table is missing its role and period row", number)
            role_number, role_line = rows[index]
            role_cells = _split_table_row(role_line, role_number)
            index += 1
            role = _marked_cell(role_cells[0], "*", role_number)
            period = _marked_cell(role_cells[1], "*", role_number)
            if organization is None or location is None or role is None or period is None:
                raise _error("unexpected table row structure", number)

        bullets: list[str] = []
        while index < len(rows):
            bullet_number, bullet_line = rows[index]
            if not bullet_line.strip():
                index += 1
                continue
            if TABLE_RE.match(bullet_line.strip()):
                break
            bullets.append(_bullet(bullet_line, bullet_number))
            index += 1
        if not bullets:
            raise _error(f"entry in {section} has no bullet points", number)
        entries.append(
            {
                "organization": organization,
                "location": location,
                "role": role,
                "period": period,
                "bullets": bullets,
            }
        )
    if not entries:
        raise CVParseError(f"{section} has no entries")
    return entries


def _parse_education(lines: list[tuple[int, str]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    rows = _without_pagebreak(lines)
    index = 0
    while index < len(rows):
        number, line = rows[index]
        if not line.strip():
            index += 1
            continue
        cells = _split_table_row(line, number)
        if index + 1 >= len(rows) or not _is_separator_row(_split_table_row(rows[index + 1][1], rows[index + 1][0])):
            raise _error("expected an education table separator row", number)
        index += 2
        if len(cells) != 2:
            raise _error("education rows must contain two cells", number)
        degree_match = re.fullmatch(r"\*\*(.+?)\*\*\s*\|\s*(.+)", cells[0])
        period = _marked_cell(cells[1], "*", number)
        if not degree_match or period is None:
            raise _error("unexpected education row structure", number)
        degree = _clean_text(degree_match.group(1), line_number=number)
        institution = _clean_text(degree_match.group(2), line_number=number)
        details: list[str] = []
        while index < len(rows):
            detail_number, detail_line = rows[index]
            if not detail_line.strip():
                index += 1
                continue
            if TABLE_RE.match(detail_line.strip()):
                break
            detail_match = re.fullmatch(r"<u>([^<]+)</u>\s*:\s*(.+)", detail_line.strip())
            if not detail_match:
                raise _error("unexpected education detail structure", detail_number)
            label = _clean_text(detail_match.group(1), line_number=detail_number)
            value = _clean_text(detail_match.group(2), line_number=detail_number)
            details.append(f"{label}: {value}")
            index += 1
        entries.append({"institution": institution, "degree": degree, "period": period, "details": details})
    if not entries:
        raise CVParseError("EDUCATION has no entries")
    return entries


def _parse_summary(lines: list[tuple[int, str]]) -> dict[str, Any]:
    values = _without_pagebreak(lines)
    paragraph: list[str] = []
    highlights: list[str] = []
    in_highlights = False
    for number, line in values:
        if not line.strip():
            continue
        if _is_bullet(line):
            in_highlights = True
            highlights.append(_bullet(line, number))
        elif in_highlights:
            raise _error("summary text cannot follow summary bullets", number)
        else:
            paragraph.append(_clean_text(line, line_number=number))
    if not paragraph:
        raise CVParseError("SUMMARY has no summary paragraph")
    result: dict[str, Any] = {"summary": " ".join(paragraph)}
    if highlights:
        result["summaryHighlights"] = highlights
    return result


def _parse_expertise(lines: list[tuple[int, str]]) -> list[str]:
    body = "\n".join(line for _, line in _without_pagebreak(lines) if line.strip())
    match = re.fullmatch(r'<ul class="expertise">\s*(.*?)\s*</ul>', body, flags=re.DOTALL)
    if not match:
        raise CVParseError("AREAS OF EXPERTISE must contain one expertise list")
    items: list[str] = []
    position = 0
    for item_match in re.finditer(r"<li>([^<>]+)</li>", match.group(1)):
        if match.group(1)[position : item_match.start()].strip():
            raise CVParseError("unexpected expertise list structure")
        items.append(item_match.group(1))
        position = item_match.end()
    if not items or match.group(1)[position:].strip():
        raise CVParseError("unexpected expertise list structure")
    return [_clean_text(item) for item in items]


def _parse_skills(lines: list[tuple[int, str]]) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for number, line in _without_pagebreak(lines):
        if not line.strip():
            continue
        for part in re.split(r"<br\s*/?>", line.strip()):
            if not part.strip():
                continue
            match = re.fullmatch(r"\*\*([^*:]+):\*\*\s*(.+)", part.strip())
            if not match:
                raise _error("skills must use '**Category:** values' rows", number)
            category = _clean_text(match.group(1), line_number=number)
            value_text = match.group(2).strip()
            delimiter = ";" if ";" in value_text else ","
            items = [_clean_text(item, line_number=number) for item in value_text.split(delimiter) if item.strip()]
            if not items:
                raise _error("skill category has no values", number)
            if any(item["category"] == category for item in skills):
                raise _error(f"duplicate skill category: {category}", number)
            skills.append({"category": category, "items": items})
    if not skills:
        raise CVParseError("SKILLS has no categories")
    return skills


def parse_cv(markdown: str) -> dict[str, Any]:
    """Parse a private CV into the public schema, rejecting malformed input."""

    sections = _sections(markdown)
    summary = _parse_summary(sections["SUMMARY"])
    return {
        "schemaVersion": SCHEMA_VERSION,
        **summary,
        "expertise": _parse_expertise(sections["AREAS OF EXPERTISE"]),
        "experience": _parse_entries(sections["EXPERIENCE"], "EXPERIENCE"),
        "education": _parse_education(sections["EDUCATION"]),
        "additionalExperience": _parse_entries(sections["ADDITIONAL EXPERIENCE"], "ADDITIONAL EXPERIENCE"),
        "research": _parse_entries(sections["RESEARCH EXPERIENCE"], "RESEARCH EXPERIENCE"),
        "skills": _parse_skills(sections["SKILLS"]),
    }


def _validate_source_markdown(source_path: Path) -> None:
    if source_path.is_symlink():
        raise CVParseError(f"CV source must not be a symlink: {source_path}")
    if not source_path.is_file():
        raise CVParseError(f"CV source is missing: {source_path}")


def _validate_pdf(pdf_path: Path) -> None:
    if pdf_path.is_symlink():
        raise CVParseError(f"PDF source must not be a symlink: {pdf_path}")
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise CVParseError(f"PDF is missing or empty: {pdf_path}")
    with pdf_path.open("rb") as pdf_file:
        if pdf_file.read(4) != b"%PDF":
            raise CVParseError(f"PDF does not begin with %PDF: {pdf_path}")


def _remove_output(path: Path) -> None:
    """Best-effort removal used to fail closed after any import failure."""

    try:
        if path.exists() or path.is_symlink():
            path.unlink()
    except FileNotFoundError:
        pass


def _remove_outputs(output_paths: list[Path]) -> None:
    for path in output_paths:
        _remove_output(path)


def _stage_json(output_path: Path, data: dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    staged_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as staged:
            staged_path = Path(staged.name)
            json.dump(data, staged, ensure_ascii=False, indent=2)
            staged.write("\n")
            staged.flush()
            os.fsync(staged.fileno())
        return staged_path
    except BaseException:
        if staged_path is not None:
            _remove_output(staged_path)
        raise


def _stage_pdf(source_pdf: Path, pdf_destination: Path) -> Path:
    pdf_destination.parent.mkdir(parents=True, exist_ok=True)
    staged_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=pdf_destination.parent,
            prefix=f".{pdf_destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as staged:
            staged_path = Path(staged.name)
            with source_pdf.open("rb") as source:
                shutil.copyfileobj(source, staged)
                staged.flush()
                os.fsync(staged.fileno())
        return staged_path
    except BaseException:
        if staged_path is not None:
            _remove_output(staged_path)
        raise


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def _validate_destinations(
    output_path: Path,
    pdf_destination: Path | None,
    source_path: Path,
    source_pdf: Path,
) -> None:
    """Reject destinations that could overwrite an input before cleanup starts."""

    destinations = [output_path] + ([pdf_destination] if pdf_destination is not None else [])
    if any(destination.is_symlink() for destination in destinations):
        raise CVParseError("output destinations must not be symlinks")
    if any(destination.exists() and destination.is_dir() for destination in destinations):
        raise CVParseError("output destinations must be files")
    if pdf_destination is not None and _same_path(output_path, pdf_destination):
        raise CVParseError("JSON and PDF destinations must be different files")
    for destination in destinations:
        if _same_path(destination, source_path) or _same_path(destination, source_pdf):
            raise CVParseError("output destination must not alias a CV source file")


def import_cv(source_dir: Path, output_path: Path, pdf_destination: Path | None = None) -> dict[str, Any]:
    """Import ``cv.md`` and stage validated JSON/PDF outputs before replacement.

    Both requested destinations are removed if validation, staging, or
    replacement fails. The two replacements are separate filesystem operations,
    so fail-closed cleanup does not cover a process kill between replacements.
    """

    source_dir = Path(source_dir).resolve()
    output_path = Path(output_path)
    pdf_destination = Path(pdf_destination) if pdf_destination is not None else None
    source_path = source_dir / "cv.md"
    source_pdf = source_dir / "Andre_Motta_Resume.pdf"
    _validate_destinations(output_path, pdf_destination, source_path, source_pdf)
    output_paths = [output_path] + ([pdf_destination] if pdf_destination is not None else [])
    staged_paths: list[Path] = []
    try:
        _validate_source_markdown(source_path)
        data = parse_cv(source_path.read_text(encoding="utf-8"))
        if pdf_destination is not None:
            _validate_pdf(source_pdf)

        staged_paths.append(_stage_json(output_path, data))
        if pdf_destination is not None:
            staged_paths.append(_stage_pdf(source_pdf, pdf_destination))

        os.replace(staged_paths[0], output_path)
        if pdf_destination is not None:
            os.replace(staged_paths[1], pdf_destination)
        return data
    except BaseException:
        _remove_outputs(output_paths)
        raise
    finally:
        for staged_path in staged_paths:
            _remove_output(staged_path)


def _default_fixture_path() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "cv.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--source-dir", type=Path, help="private CV checkout containing cv.md and the release PDF")
    mode.add_argument("--fixture", action="store_true", help="use the committed synthetic fixture for local/PR checks")
    parser.add_argument("--output", type=Path, default=Path(".generated/cv.json"))
    parser.add_argument(
        "--pdf-destination",
        type=Path,
        help="copy the real source PDF here after validating it (release mode only)",
    )
    args = parser.parse_args(argv)
    if args.fixture:
        if args.pdf_destination:
            parser.error("--pdf-destination is unavailable in --fixture mode")
        source_dir = _default_fixture_path().parent
    else:
        source_argument = args.source_dir or os.environ.get("CV_SOURCE_DIR")
        if not source_argument:
            parser.error("choose --fixture or --source-dir (or set CV_SOURCE_DIR)")
        source_dir = Path(source_argument)
        if not args.pdf_destination:
            parser.error("a real source requires --pdf-destination for a release import")
    try:
        import_cv(source_dir, args.output, args.pdf_destination)
    except (OSError, CVParseError, UnicodeError) as error:
        print(f"CV import failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated public CV written to {args.output}")
    if args.pdf_destination:
        print(f"Validated CV PDF copied to {args.pdf_destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
