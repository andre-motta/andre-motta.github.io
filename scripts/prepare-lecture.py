#!/usr/bin/env python3
"""Prepare reviewed lecture assets for the local preview or a release.

The original presentation is accepted as an exported PDF or as a PPTX. A PPTX
is converted with the supplied bundled LibreOffice binary and its visible text
runs are extracted into a local transcript. A PDF needs an explicit transcript
input because the bundled runtime does not provide a reliable PDF text
extractor. Raw presentation sources remain outside this repository's public
asset directories.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


EXPECTED_SLIDES = 22
RASTER_WIDTH = 1920
RASTER_HEIGHT = 1082
BUNDLED_SOFFICE = Path('/home/alustosa/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice')
BUNDLED_PDFTOPPM = Path('/home/alustosa/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm')
SLIDE_RE = re.compile(r'^ppt/slides/slide(\d+)\.xml$')
XML_NAMESPACES = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


class LecturePreparationError(ValueError):
    """Raised when a source or generated lecture asset is invalid."""


def _tool_path(value: Path, label: str) -> Path:
    if not value.is_absolute():
        raise LecturePreparationError(f'--{label} must be an absolute path')
    if not value.is_file() or not os.access(value, os.X_OK):
        raise LecturePreparationError(f'{label} is not an executable file: {value}')
    return value


def _run(command: list[str], label: str) -> None:
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except (OSError, subprocess.CalledProcessError) as error:
        output = getattr(error, 'stdout', '') or ''
        detail = output.strip()
        suffix = f': {detail}' if detail else ''
        raise LecturePreparationError(f'{label} failed{suffix}') from error


def _slide_sort_key(path: Path) -> int:
    match = re.search(r'(\d+)$', path.stem)
    return int(match.group(1)) if match else 0


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _validate_transcript(value: Any, source: Path) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise LecturePreparationError(f'transcript must be an array: {source}')
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict) or not isinstance(item.get('slide'), int) or isinstance(item.get('slide'), bool) or not isinstance(item.get('text'), list) or not all(isinstance(line, str) for line in item['text']):
            raise LecturePreparationError(f'transcript entry {index} must contain an integer slide and string array text: {source}')
        entries.append({'slide': item['slide'], 'text': item['text']})
    slide_numbers = [entry['slide'] for entry in entries]
    if len(entries) != EXPECTED_SLIDES or sorted(slide_numbers) != list(range(1, EXPECTED_SLIDES + 1)):
        raise LecturePreparationError(f'transcript must contain one entry for each of {EXPECTED_SLIDES} slides: {source}')
    return sorted(entries, key=lambda entry: entry['slide'])


def _read_transcript(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise LecturePreparationError(f'cannot read transcript {path}: {error}') from error
    return _validate_transcript(value, path)


def _extract_pptx_transcript(path: Path) -> list[dict[str, Any]]:
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as error:
        raise LecturePreparationError(f'cannot open PPTX source {path}: {error}') from error
    with archive:
        slide_members: list[tuple[int, str]] = []
        for name in archive.namelist():
            match = SLIDE_RE.fullmatch(name)
            if match:
                slide_members.append((int(match.group(1)), name))
        slide_members.sort()
        if [number for number, _ in slide_members] != list(range(1, EXPECTED_SLIDES + 1)):
            raise LecturePreparationError(f'PPTX source must contain exactly {EXPECTED_SLIDES} numbered slides: {path}')

        entries: list[dict[str, Any]] = []
        for number, name in slide_members:
            try:
                root = ElementTree.fromstring(archive.read(name))
            except (KeyError, ElementTree.ParseError) as error:
                raise LecturePreparationError(f'cannot parse slide {number} in {path}: {error}') from error
            text: list[str] = []
            for paragraph in root.findall('.//a:p', XML_NAMESPACES):
                runs = paragraph.findall('.//a:t', XML_NAMESPACES)
                if runs:
                    # Preserve each XML text run exactly, including whitespace
                    # and line fragments deliberately split by the deck author.
                    text.extend(run.text or '' for run in runs)
                else:
                    text.append('')
            entries.append({'slide': number, 'text': text})
    return entries


def _convert_pptx(path: Path, soffice: Path, temporary_directory: Path) -> Path:
    profile = temporary_directory / 'libreoffice-profile'
    profile.mkdir()
    _run(
        [
            str(soffice),
            f'-env:UserInstallation={profile.as_uri()}',
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            str(temporary_directory),
            str(path),
        ],
        'LibreOffice conversion',
    )
    converted = temporary_directory / f'{path.stem}.pdf'
    if not converted.is_file():
        candidates = sorted(temporary_directory.glob('*.pdf'))
        if len(candidates) != 1:
            raise LecturePreparationError(f'LibreOffice did not produce one PDF for {path}')
        converted = candidates[0]
    return converted


def _render_pdf(pdf: Path, pdftoppm: Path, temporary_directory: Path) -> list[Path]:
    rendered_directory = temporary_directory / 'rendered'
    rendered_directory.mkdir()
    prefix = rendered_directory / 'slide'
    _run([str(pdftoppm), '-png', '-scale-to-x', str(RASTER_WIDTH), '-scale-to-y', str(RASTER_HEIGHT), str(pdf), str(prefix)], 'PDF rasterization')
    rendered = sorted(rendered_directory.glob('slide-*.png'), key=_slide_sort_key)
    if len(rendered) != EXPECTED_SLIDES:
        raise LecturePreparationError(f'original PDF must render exactly {EXPECTED_SLIDES} slides, found {len(rendered)}')
    return rendered


def _write_outputs(pdf: Path, rendered: list[Path], transcript: list[dict[str, Any]], destination: Path) -> None:
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    parent = destination.parent
    staging = Path(tempfile.mkdtemp(prefix=f'.{destination.name}.stage-', dir=parent))
    backup: Path | None = None
    try:
        # Stage every byte before touching the current destination. This also
        # keeps a source PDF usable when it is the destination's old
        # original.pdf file.
        shutil.copy2(pdf, staging / 'original.pdf')
        for number, rendered_path in enumerate(rendered, start=1):
            shutil.copy2(rendered_path, staging / f'slide-{number:02d}.png')
        (staging / 'transcript.json').write_text(json.dumps(transcript, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        staged_outputs = sorted(staging.glob('slide-*.png'), key=_slide_sort_key)
        if not (staging / 'original.pdf').is_file() or len(staged_outputs) != EXPECTED_SLIDES or not (staging / 'transcript.json').is_file():
            raise LecturePreparationError('staged lecture output is incomplete')

        if destination.exists():
            backup = Path(tempfile.mkdtemp(prefix=f'.{destination.name}.backup-', dir=parent))
            backup.rmdir()
            os.replace(destination, backup)
        os.replace(staging, destination)
        staging = Path()
    except OSError as error:
        if backup and not destination.exists() and backup.exists():
            os.replace(backup, destination)
        raise LecturePreparationError(f'cannot install generated lecture assets: {error}') from error
    finally:
        if staging and staging != Path() and staging.exists():
            shutil.rmtree(staging)
        if backup and backup.exists():
            shutil.rmtree(backup)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='absolute or relative source PDF or PPTX')
    parser.add_argument('--transcript', type=Path, help='JSON transcript for a PDF source')
    parser.add_argument('--pptx', type=Path, help='PPTX used only to extract transcript text for a PDF source')
    parser.add_argument('--soffice', type=Path, default=BUNDLED_SOFFICE, help='absolute bundled LibreOffice executable')
    parser.add_argument('--pdftoppm', type=Path, default=BUNDLED_PDFTOPPM, help='absolute bundled pdftoppm executable')
    parser.add_argument('--destination', type=Path, default=Path('.generated/lecture'), help='generated asset directory')
    return parser


def main() -> int:
    args = _parser().parse_args()
    source = args.source.resolve()
    if not source.is_file():
        print(f'prepare-lecture: source does not exist: {source}', file=sys.stderr)
        return 2
    suffix = source.suffix.lower()
    if suffix not in {'.pdf', '.pptx'}:
        print('prepare-lecture: --source must end in .pdf or .pptx', file=sys.stderr)
        return 2
    try:
        pdftoppm = _tool_path(args.pdftoppm, 'pdftoppm')
        destination = args.destination.resolve()
        for label, candidate in [('source', source), ('transcript', args.transcript), ('pptx', args.pptx)]:
            if candidate and _is_within(candidate.resolve(), destination):
                raise LecturePreparationError(f'--{label} must be outside the destination directory because generated output is installed atomically: {candidate.resolve()}')
        transcript: list[dict[str, Any]]
        with tempfile.TemporaryDirectory(prefix='lecture-prepare-') as temporary_name:
            temporary_directory = Path(temporary_name)
            if suffix == '.pptx':
                if args.pptx or args.transcript:
                    raise LecturePreparationError('--pptx and --transcript are only used with a PDF source')
                soffice = _tool_path(args.soffice, 'soffice')
                pdf = _convert_pptx(source, soffice, temporary_directory)
                transcript = _extract_pptx_transcript(source)
            else:
                if args.pptx and args.transcript:
                    raise LecturePreparationError('provide either --pptx or --transcript for a PDF source, not both')
                if args.pptx:
                    pptx = args.pptx.resolve()
                    if not pptx.is_file() or pptx.suffix.lower() != '.pptx':
                        raise LecturePreparationError(f'--pptx must point to a PPTX file: {pptx}')
                    transcript = _extract_pptx_transcript(pptx)
                elif args.transcript:
                    transcript = _read_transcript(args.transcript.resolve())
                else:
                    raise LecturePreparationError('--transcript or --pptx is required when --source is a PDF')
                pdf = source
            rendered = _render_pdf(pdf, pdftoppm, temporary_directory)
            _write_outputs(pdf, rendered, transcript, destination)
    except (LecturePreparationError, OSError) as error:
        print(f'prepare-lecture: {error}', file=sys.stderr)
        return 2
    print(f'Prepared {EXPECTED_SLIDES} lecture slides and transcript in {args.destination}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
