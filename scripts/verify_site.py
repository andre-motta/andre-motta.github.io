#!/usr/bin/env python3
"""Verify a built Astro site without requiring browser or third-party packages."""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROUTES = (
    "index.html",
    "about.html",
    "archives.html",
    "projects.html",
    "cv.html",
    "privacy.html",
    "authors.html",
    "author/andre-lustosa.html",
    "categories.html",
    "tags.html",
    "blog/2025/welcome.html",
    "category/general.html",
    "tag/introduction.html",
    "tag/meta.html",
    "feeds/all.atom.xml",
    "feeds/general.atom.xml",
    "llms.txt",
    "robots.txt",
)
FORBIDDEN_PATH_PARTS = {
    ".cv-source",
    ".generated",
    ".wiki",
    "AGENTS.md",
    "README.md",
    ".agents",
    ".codex",
    "SKILL.md",
    "content",
    "docs",
    "src",
}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data"}
REJECT_SCHEMES = {"javascript"}
MARKDOWN_LINK_RE = re.compile(r"\[(?:\\.|[^\]\\])*\]\(\s*(?:<([^>]+)>|([^\s)]+))")
SITE_HOST = "alustos.us"
GOATCOUNTER_SCRIPT = "https://gc.zgo.at/count.js"
GOATCOUNTER_ENDPOINT = "https://alustosa.goatcounter.com/count"


class MarkupParser(HTMLParser):
    """Collect links, IDs, and draft markers from generated markup."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.draft_markers = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if "id" in attributes and attributes["id"]:
            self.ids.add(attributes["id"])
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.links.append(html.unescape(value))
        if attributes.get("data-draft", "").lower() == "true":
            self.draft_markers += 1


def output_files(output: Path) -> list[Path]:
    return [path for path in output.rglob("*") if path.is_file()]


def frontmatter(source: Path) -> str:
    text = source.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return ""
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def frontmatter_value(source: Path, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$", frontmatter(source), flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def draft_routes() -> dict[str, str]:
    """Return generated routes and titles for draft Markdown source files."""
    routes: dict[str, str] = {}
    content_root = ROOT / "src" / "content"
    if not content_root.is_dir():
        return routes
    for source in content_root.rglob("*.md"):
        if frontmatter_value(source, "draft") != "true":
            continue
        slug = frontmatter_value(source, "slug") or source.stem
        date_value = frontmatter_value(source, "date")
        if source.parent == content_root / "articles" and date_value:
            try:
                year = date.fromisoformat(date_value).year
            except ValueError:
                continue
            route = f"blog/{year}/{slug}.html"
        else:
            route = f"{slug}.html"
        routes[route] = frontmatter_value(source, "title") or slug
    return routes


def check_required_routes(output: Path, errors: list[str], preview: bool, drafts: dict[str, str]) -> None:
    for route in REQUIRED_ROUTES:
        if not (output / route).is_file():
            if not preview and route in drafts:
                continue
            errors.append(f"missing required route: /{route}")


def check_exclusions(output: Path, files: list[Path], errors: list[str]) -> None:
    for path in output.rglob("*"):
        if path.is_symlink():
            errors.append(f"symlink in public artifact: {path.relative_to(output)}")
    for path in files:
        relative_parts = set(path.relative_to(output).parts)
        if relative_parts & FORBIDDEN_PATH_PARTS:
            errors.append(f"forbidden source or documentation in output: {path.relative_to(output)}")
        if path.name.endswith((".pyc", ".map")):
            errors.append(f"unexpected intermediate artifact: {path.relative_to(output)}")


def check_cname(output: Path, errors: list[str]) -> None:
    cname = output / "CNAME"
    if not cname.is_file():
        errors.append("missing CNAME")
    elif cname.read_text(encoding="utf-8").strip() != "alustos.us":
        errors.append("CNAME does not contain exactly alustos.us")


def check_cv(output: Path, allow_missing_cv: bool, errors: list[str]) -> None:
    pdf = output / "extra" / "Andre_Motta_Resume.pdf"
    if not pdf.is_file():
        if not allow_missing_cv:
            errors.append("missing fetched public CV PDF")
        return
    if pdf.read_bytes()[:4] != b"%PDF":
        errors.append("public CV PDF does not begin with %PDF")


def resolve_local_target(source: Path, target: str, output: Path) -> Path | None:
    split = urlsplit(target)
    if split.scheme in REJECT_SCHEMES:
        raise ValueError(f"unsafe javascript URL: {target}")
    if split.scheme in SKIP_SCHEMES or split.scheme or target.startswith("//"):
        return None
    if not split.path:
        return source if split.fragment and source.suffix == ".html" else None
    raw_path = unquote(split.path)
    if raw_path.startswith("/"):
        candidate = output / raw_path.lstrip("/")
    else:
        candidate = source.parent / raw_path
    candidate = candidate.resolve()
    try:
        candidate.relative_to(output.resolve())
    except ValueError:
        raise ValueError(f"local link escapes output: {target}")
    if candidate.is_dir():
        candidate /= "index.html"
    if not candidate.exists() and candidate.suffix == "":
        html_candidate = candidate.with_suffix(".html")
        if html_candidate.exists():
            candidate = html_candidate
    return candidate


def check_links(output: Path, files: list[Path], allow_missing_cv: bool, errors: list[str]) -> None:
    markup_files = [path for path in files if path.suffix in {".html", ".xml", ".css"}]
    parsed: dict[Path, MarkupParser] = {}
    links_by_file: dict[Path, list[str]] = {}
    for path in markup_files:
        parser = MarkupParser()
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".html":
            parser.feed(text)
        else:
            parser.links = re.findall(r"(?:href|src)=[\"']([^\"']+)", text, flags=re.IGNORECASE)
        parsed[path] = parser
        links_by_file[path] = parser.links

    for source, links in links_by_file.items():
        for link in links:
            try:
                target = resolve_local_target(source, link, output)
            except ValueError as error:
                errors.append(f"invalid local link in {source.relative_to(output)}: {error}")
                continue
            if target is None:
                continue
            if not target.is_file():
                if allow_missing_cv and target == output / "extra" / "Andre_Motta_Resume.pdf":
                    continue
                errors.append(f"broken local link in {source.relative_to(output)}: {link}")
                continue
            fragment = urlsplit(link).fragment
            if fragment and target.suffix == ".html":
                target_parser = parsed.get(target)
                if target_parser is None:
                    target_parser = MarkupParser()
                    target_parser.feed(target.read_text(encoding="utf-8", errors="replace"))
                    parsed[target] = target_parser
                if unquote(fragment) not in target_parser.ids:
                    errors.append(f"missing fragment #{fragment} in {target.relative_to(output)}")


def check_llms(output: Path, allow_missing_cv: bool, drafts: dict[str, str], errors: list[str]) -> None:
    """Validate same-site Markdown links and public-only article discovery."""
    llms = output / "llms.txt"
    if not llms.is_file():
        return

    text = llms.read_text(encoding="utf-8", errors="replace")
    for match in MARKDOWN_LINK_RE.finditer(text):
        link = (match.group(1) or match.group(2) or "").strip()
        split = urlsplit(link)
        internal = not split.scheme and not split.netloc
        if split.netloc:
            internal = split.netloc.lower() == SITE_HOST and split.scheme in {"http", "https"}
            if internal and split.scheme != "https":
                errors.append(f"llms.txt contains a non-canonical internal link: {link}")
        if not internal:
            continue

        target_reference = split.path if split.scheme or split.netloc else link
        try:
            target = resolve_local_target(llms, target_reference, output)
        except ValueError as error:
            errors.append(f"invalid local link in llms.txt: {error}")
            continue
        if target is None or target.is_file():
            continue
        if allow_missing_cv and target == output / "extra" / "Andre_Motta_Resume.pdf":
            continue
        errors.append(f"broken local link in llms.txt: {link}")

    for route, title in drafts.items():
        escaped_title = title.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
        if route in text or title in text or escaped_title in text:
            errors.append(f"llms.txt references non-public article content: /{route}")


def check_analytics(output: Path, files: list[Path], preview: bool, errors: list[str]) -> None:
    """Ensure analytics is present only in the canonical production artifact."""
    html_files = [path for path in files if path.suffix == ".html"]
    loader_pages = 0
    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        has_script = GOATCOUNTER_SCRIPT in text or GOATCOUNTER_ENDPOINT in text
        if preview and has_script:
            errors.append(f"preview output contains GoatCounter analytics: {path.relative_to(output)}")
        if not preview and GOATCOUNTER_SCRIPT in text and GOATCOUNTER_ENDPOINT in text:
            loader_pages += 1
    if not preview and html_files and loader_pages != len(html_files):
        errors.append(f"production output has GoatCounter loader on {loader_pages} of {len(html_files)} HTML pages")


def check_drafts(output: Path, files: list[Path], preview: bool, drafts: dict[str, str], errors: list[str]) -> None:
    draft_count = 0
    for path in files:
        if path.suffix != ".html":
            continue
        parser = MarkupParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        draft_count += parser.draft_markers
    markup_files = [path for path in files if path.suffix in {".html", ".xml"}]
    for route, title in drafts.items():
        route_path = output / route
        if preview:
            if not route_path.is_file():
                errors.append(f"preview is missing draft route: /{route}")
            elif route_path.suffix == ".html":
                parser = MarkupParser()
                parser.feed(route_path.read_text(encoding="utf-8", errors="replace"))
                if parser.draft_markers == 0:
                    errors.append(f"preview draft route lacks its draft marker: /{route}")
        elif route_path.exists():
            errors.append(f"production output contains draft route: /{route}")
        if not preview:
            for path in markup_files:
                text = path.read_text(encoding="utf-8", errors="replace")
                if route in text or title in text:
                    errors.append(f"production output references draft content in {path.relative_to(output)}: /{route}")
                    break
    if draft_count and not preview:
        errors.append(f"production output contains {draft_count} draft marker(s)")
    if preview:
        print(f"preview draft markers: {draft_count}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="built output directory (default: output, or output-preview with --preview)")
    parser.add_argument("--preview", action="store_true", help="verify a draft-inclusive preview output")
    parser.add_argument("--allow-missing-cv", action="store_true", help="allow the PDF to be absent for fixture PR builds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output = (ROOT / args.output) if args.output and not args.output.is_absolute() else (args.output or ROOT / ("output-preview" if args.preview else "output"))
    output = output.resolve()
    errors: list[str] = []
    if not output.is_dir():
        print(f"site verification failed: output directory does not exist: {output}", file=sys.stderr)
        return 1
    files = output_files(output)
    drafts = draft_routes()
    check_required_routes(output, errors, args.preview, drafts)
    check_exclusions(output, files, errors)
    check_cname(output, errors)
    check_cv(output, args.allow_missing_cv, errors)
    check_links(output, files, args.allow_missing_cv, errors)
    check_llms(output, args.allow_missing_cv, drafts, errors)
    check_analytics(output, files, args.preview, errors)
    check_drafts(output, files, args.preview, drafts, errors)
    if errors:
        print("site verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"site verification passed: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
