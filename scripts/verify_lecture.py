#!/usr/bin/env python3
"""Check lecture route visibility and the generated original deck artifact."""

from __future__ import annotations

import argparse
import html
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


SLUG = 'ai-agents-in-ci-cd'
TITLE = 'AI Agents in CI/CD'
SLIDE_COUNT = 22
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def _png_dimensions(path: Path) -> tuple[int, int]:
    value = path.read_bytes()
    if not value.startswith(PNG_SIGNATURE) or value[12:16] != b'IHDR' or len(value) < 24:
        raise ValueError(f'invalid PNG signature or header: {path}')
    return struct.unpack('>II', value[16:24])


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


class _WebStageTextParser(HTMLParser):
    """Collect visible stage text while omitting the generated slide counter."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.content_depth = 0
        self.skipped_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get('class') or '').split())
        if self.content_depth == 0 and tag == 'div' and 'web-stage-content' in classes:
            self.content_depth = 1
            return
        if self.content_depth == 0:
            return
        self.content_depth += 1
        if self.skipped_depth:
            self.skipped_depth += 1
        elif 'web-stage-number' in classes:
            self.skipped_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self.content_depth == 0:
            return
        if self.skipped_depth:
            self.skipped_depth -= 1
        self.content_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.content_depth and not self.skipped_depth:
            self.parts.append(data)


def _normalized_characters(value: str) -> Counter[str]:
    return Counter(character for character in value if not character.isspace())


def _web_stage_text(markup: str) -> str:
    parser = _WebStageTextParser()
    parser.feed(markup)
    parser.close()
    return ''.join(parser.parts)


def _check_published(output: Path, source_assets: Path) -> None:
    talks_index = output / 'talks.html'
    chooser = output / 'talks' / f'{SLUG}.html'
    lecture_directory = output / 'talks' / SLUG
    original = lecture_directory / 'original.html'
    web = lecture_directory / 'web.html'
    presenter = lecture_directory / 'presenter.html'
    pdf = lecture_directory / 'slides.pdf'
    notes_pdf = lecture_directory / 'original.pdf'
    _assert(talks_index.is_file(), f'missing talks index route: {talks_index}')
    for path in (chooser, original, web, presenter, pdf, notes_pdf):
        _assert(path.is_file(), f'missing lecture preview route: {path}')
    _assert(TITLE in talks_index.read_text(encoding='utf-8'), 'talks index does not list the published lecture')
    home = output / 'index.html'
    _assert(home.is_file() and 'href="/talks.html"' in home.read_text(encoding='utf-8'), 'published Talks navigation is missing from the site')
    slide_directory = lecture_directory / 'slides'
    actual_slides = sorted((path.name for path in slide_directory.glob('*.png')), key=lambda name: int(Path(name).stem) if Path(name).stem.isdigit() else 0)
    expected_slides = [f'{number}.png' for number in range(1, SLIDE_COUNT + 1)]
    _assert(actual_slides == expected_slides, f'expected exactly {SLIDE_COUNT} rendered slide routes, found {actual_slides}')
    _assert(not any(path.name.startswith('transcript') for path in lecture_directory.rglob('*')), 'raw transcript must not be a public route')

    for path in (chooser, original, web):
        markup = path.read_text(encoding='utf-8')
        _assert('data-draft="true"' not in markup, f'published route still has a draft marker: {path}')
        _assert('Local draft preview' not in markup, f'published route still has a draft badge: {path}')
        _assert('noindex, nofollow' not in markup, f'published route still has a noindex directive: {path}')
    presenter_html = presenter.read_text(encoding='utf-8')
    _assert('data-presenter-app' in presenter_html, f'presenter app missing from {presenter}')
    _assert('noindex, nofollow' in presenter_html, f'presenter route must remain noindex: {presenter}')
    _assert('data-draft="true"' not in presenter_html and 'Local draft preview' not in presenter_html, f'published presenter route still has a draft marker: {presenter}')
    _assert('class="site-header"' not in presenter_html and 'class="site-footer"' not in presenter_html, f'presenter route must use quiet chrome: {presenter}')
    original_html = original.read_text(encoding='utf-8')
    _assert('data-lecture-viewer' in original_html, f'original viewer missing from {original}')
    web_html = web.read_text(encoding='utf-8')
    for number in range(1, SLIDE_COUNT + 1):
        _assert(f'id="slide-{number}"' in original_html, f'original fallback slide {number} missing')
        _assert(f'id="slide-{number}"' in web_html, f'HTML slide {number} missing')
        emitted_width, emitted_height = _png_dimensions(slide_directory / f'{number}.png')
        source_width, source_height = _png_dimensions(source_assets / f'slide-{number:02d}.png')
        _assert((emitted_width, emitted_height) == (source_width, source_height), f'slide {number} has dimensions {emitted_width}x{emitted_height}, expected source dimensions {source_width}x{source_height}')

    generated_pdf = source_assets / 'original.pdf'
    _assert(generated_pdf.is_file(), f'missing generated source PDF: {generated_pdf}')
    _assert(hashlib.sha256(pdf.read_bytes()).digest() == hashlib.sha256(generated_pdf.read_bytes()).digest(), 'published slide PDF does not match approved original.pdf')
    generated_notes_pdf = source_assets / 'presenter-notes.pdf'
    _assert(generated_notes_pdf.is_file(), f'missing presenter notes PDF: {generated_notes_pdf}')
    _assert(notes_pdf.read_bytes().startswith(b'%PDF-'), f'presenter notes route is not a PDF: {notes_pdf}')
    _assert(hashlib.sha256(notes_pdf.read_bytes()).digest() == hashlib.sha256(generated_notes_pdf.read_bytes()).digest(), 'presenter notes route does not match the approved presenter-notes.pdf')
    transcript_path = source_assets / 'transcript.json'
    _assert(transcript_path.is_file(), f'missing generated transcript: {transcript_path}')
    transcript = json.loads(transcript_path.read_text(encoding='utf-8'))
    original_text = html.unescape(original_html)
    cues_path = source_assets / 'presenter-cues.json'
    _assert(cues_path.is_file(), f'missing approved presenter cues: {cues_path}')
    cues = json.loads(cues_path.read_text(encoding='utf-8'))
    _assert(isinstance(cues, list) and len(cues) == SLIDE_COUNT, f'expected {SLIDE_COUNT} presenter cue records')
    presenter_text = html.unescape(presenter_html)
    for index, cue in enumerate(cues, start=1):
        _assert(isinstance(cue, dict) and cue.get('number') == index, f'presenter cue {index} has the wrong slide number')
        _assert(cue.get('title') and cue['title'] in presenter_text, f'presenter cue title is missing for slide {index}')
        for field in ('main_point', 'qualification', 'transition'):
            value = cue.get(field)
            _assert(isinstance(value, str) and value and value in presenter_text, f'presenter cue {field} is missing for slide {index}')
        cue_lines = cue.get('cues')
        _assert(isinstance(cue_lines, list) and len(cue_lines) == 4, f'presenter slide {index} must have four speaking cues')
        for line in cue_lines:
            _assert(isinstance(line, str) and line and line in presenter_text, f'presenter speaking cue is missing for slide {index}')
        article_section = cue.get('article_section')
        _assert(isinstance(article_section, dict), f'presenter article section is missing for slide {index}')
        for field in ('title', 'href'):
            value = article_section.get(field)
            _assert(isinstance(value, str) and value and value in presenter_text, f'presenter article section {field} is missing for slide {index}')
        _assert(f'data-presenter-slide="{index}"' in presenter_html, f'presenter slide {index} is missing')
    _assert('Original source slide 23' not in presenter_html and '/slides/23.png' not in presenter_html, 'presenter route references an invalid slide 23 thumbnail')
    for entry in transcript:
        for line in entry.get('text', []):
            if line:
                _assert(line in original_text, f'transcript text is missing from original HTML for slide {entry.get("slide")}')
        slide_number = entry.get('slide')
        start_match = re.search(rf'<figure[^>]+id="slide-{slide_number}"[^>]*>', web_html)
        _assert(start_match is not None, f'HTML slide {slide_number} is missing its figure')
        start = start_match.start()
        next_match = re.search(r'<figure[^>]+id="slide-\d+"[^>]*>', web_html[start_match.end():])
        end = start_match.end() + next_match.start() if next_match else len(web_html)
        web_slide_text = _web_stage_text(web_html[start:end])
        source_slide_text = ''.join(line for line in entry.get('text', []) if line.strip() != str(slide_number))
        source_characters = _normalized_characters(source_slide_text)
        web_characters = _normalized_characters(web_slide_text)
        missing = source_characters - web_characters
        added = web_characters - source_characters
        _assert(
            source_characters == web_characters,
            f'HTML slide {slide_number} differs from source text: missing={dict(missing)} added={dict(added)}',
        )
    for path in output.rglob('*'):
        if path.is_file() and path.suffix.lower() in {'.html', '.js', '.css', '.json', '.xml', '.txt'}:
            content = path.read_text(encoding='utf-8', errors='ignore')
            _assert('.wiki' not in content and 'transcript.json' not in content and 'presenter-cues.json' not in content, f'private lecture source reference found in {path}')
            _assert(f'/talks/{SLUG}/original.pdf' not in content and 'presenter-notes.pdf' not in content, f'unlisted presenter notes link found in {path}')
    for number in range(1, SLIDE_COUNT + 1):
        source_png = source_assets / f'slide-{number:02d}.png'
        _assert(source_png.is_file(), f'missing generated source slide: {source_png}')
        emitted_png = slide_directory / f'{number}.png'
        _assert(hashlib.sha256(emitted_png.read_bytes()).digest() == hashlib.sha256(source_png.read_bytes()).digest(), f'preview slide {number} does not match generated source image')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('output'))
    parser.add_argument('--source-assets', type=Path, default=Path('presentation-assets') / SLUG)
    parser.add_argument('--preview', action='store_true', help='check the local preview output (published lecture expectations remain the same)')
    args = parser.parse_args()
    try:
        _assert(args.output.is_dir(), f'output directory does not exist: {args.output}')
        _check_published(args.output, args.source_assets)
    except (OSError, ValueError) as error:
        print(f'verify-lecture: {error}', file=sys.stderr)
        return 1
    print(f'Lecture artifact checks passed ({"preview" if args.preview else "production"})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
