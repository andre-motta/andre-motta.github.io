#!/usr/bin/env python3
"""Unit tests for the public CV importer."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).with_name("import-cv.py")
SPEC = importlib.util.spec_from_file_location("import_cv", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - test bootstrap failure
    raise RuntimeError(f"cannot load {SCRIPT_PATH}")
IMPORT_CV = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORT_CV)


FIXTURE_PATH = Path(__file__).with_name("fixtures") / "cv.md"
PRIVATE_MARKERS = ("000-000-0000", "private@example.invalid", "Example Person")


class ImportCvTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markdown = FIXTURE_PATH.read_text(encoding="utf-8")

    def test_fixture_has_expected_public_schema(self) -> None:
        data = IMPORT_CV.parse_cv(self.markdown)
        self.assertEqual(data["schemaVersion"], 1)
        self.assertEqual(data["summary"].split()[0], "Example")
        self.assertEqual(len(data["expertise"]), 3)
        self.assertEqual(len(data["experience"]), 1)
        self.assertEqual(len(data["education"]), 1)
        self.assertEqual(len(data["additionalExperience"]), 1)
        self.assertEqual(len(data["research"]), 2)
        self.assertEqual(len(data["skills"]), 3)

    def test_yaml_header_is_discarded(self) -> None:
        data = IMPORT_CV.parse_cv(self.markdown)
        encoded = json.dumps(data)
        for marker in PRIVATE_MARKERS:
            self.assertNotIn(marker, encoded)
        self.assertNotIn("name", data)
        self.assertNotIn("email", data)
        self.assertNotIn("phone", data)

    def test_import_writes_json_without_copying_pdf_in_fixture_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / ".generated" / "cv.json"
            data = IMPORT_CV.import_cv(FIXTURE_PATH.parent, output)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), data)
            self.assertFalse((Path(directory) / "public").exists())

    def test_missing_section_is_rejected(self) -> None:
        malformed = self.markdown.replace("## SKILLS\n", "## OMITTED SKILLS\n", 1)
        with self.assertRaises(IMPORT_CV.CVParseError):
            IMPORT_CV.parse_cv(malformed)

    def test_unknown_heading_is_rejected(self) -> None:
        malformed = self.markdown.replace("## SKILLS\n", "## PRIVATE NOTES\n", 1)
        with self.assertRaises(IMPORT_CV.CVParseError):
            IMPORT_CV.parse_cv(malformed)

    def test_nested_heading_is_rejected(self) -> None:
        malformed = self.markdown.replace("## EXPERIENCE\n", "### EXPERIENCE\n", 1)
        with self.assertRaises(IMPORT_CV.CVParseError):
            IMPORT_CV.parse_cv(malformed)

    def test_unexpected_section_content_is_rejected(self) -> None:
        malformed = self.markdown.replace(
            '<ul class="expertise">\n', '<p>unexpected</p>\n<ul class="expertise">\n', 1
        )
        with self.assertRaises(IMPORT_CV.CVParseError):
            IMPORT_CV.parse_cv(malformed)

    def test_malformed_table_is_rejected(self) -> None:
        malformed = self.markdown.replace("| :--- | ---: |", "| --- |", 1)
        with self.assertRaises(IMPORT_CV.CVParseError):
            IMPORT_CV.parse_cv(malformed)

    def test_unclosed_front_matter_is_rejected(self) -> None:
        malformed = self.markdown.replace("---\n\n## SUMMARY", "## SUMMARY", 1)
        with self.assertRaises(IMPORT_CV.CVParseError):
            IMPORT_CV.parse_cv(malformed)

    def test_release_import_requires_a_real_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            source.mkdir()
            (source / "cv.md").write_text(self.markdown, encoding="utf-8")
            destination = Path(directory) / "public" / "extra" / "Andre_Motta_Resume.pdf"
            output = Path(directory) / "cv.json"
            output.write_text("stale json", encoding="utf-8")
            destination.parent.mkdir(parents=True)
            destination.write_bytes(b"stale pdf")
            with self.assertRaises(IMPORT_CV.CVParseError):
                IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

            (source / "Andre_Motta_Resume.pdf").write_bytes(b"not a pdf")
            output.write_text("stale json", encoding="utf-8")
            destination.write_bytes(b"stale pdf")
            with self.assertRaises(IMPORT_CV.CVParseError):
                IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

            (source / "Andre_Motta_Resume.pdf").write_bytes(b"%PDF-1.7\nfixture")
            IMPORT_CV.import_cv(source, output, destination)
            self.assertEqual(destination.read_bytes(), b"%PDF-1.7\nfixture")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schemaVersion"], 1)

    def _release_source(self, directory: str) -> tuple[Path, Path, Path]:
        root = Path(directory)
        source = root / "source"
        source.mkdir()
        (source / "cv.md").write_text(self.markdown, encoding="utf-8")
        (source / "Andre_Motta_Resume.pdf").write_bytes(b"%PDF-1.7\nfixture")
        output = root / "generated" / "cv.json"
        destination = root / "public" / "extra" / "Andre_Motta_Resume.pdf"
        output.parent.mkdir(parents=True)
        destination.parent.mkdir(parents=True)
        output.write_text("stale json", encoding="utf-8")
        destination.write_bytes(b"stale pdf")
        return source, output, destination

    def test_source_symlinks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            real_markdown = source / "cv.md"
            real_markdown.rename(source / "real-cv.md")
            os.symlink(source / "real-cv.md", real_markdown)
            with self.assertRaises(IMPORT_CV.CVParseError):
                IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            real_pdf = source / "Andre_Motta_Resume.pdf"
            real_pdf.rename(source / "real-resume.pdf")
            os.symlink(source / "real-resume.pdf", real_pdf)
            with self.assertRaises(IMPORT_CV.CVParseError):
                IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

    def test_destinations_cannot_alias_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            markdown_before = (source / "cv.md").read_bytes()
            destination_before = destination.read_bytes()
            with self.assertRaises(IMPORT_CV.CVParseError):
                IMPORT_CV.import_cv(source, source / "cv.md", destination)
            self.assertEqual((source / "cv.md").read_bytes(), markdown_before)
            self.assertEqual(destination.read_bytes(), destination_before)

        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            pdf_before = (source / "Andre_Motta_Resume.pdf").read_bytes()
            output_before = output.read_bytes()
            with self.assertRaises(IMPORT_CV.CVParseError):
                IMPORT_CV.import_cv(source, output, source / "Andre_Motta_Resume.pdf")
            self.assertEqual((source / "Andre_Motta_Resume.pdf").read_bytes(), pdf_before)
            self.assertEqual(output.read_bytes(), output_before)

    def test_json_staging_write_failure_cleans_its_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            def fail_after_partial_json_write(*args: object, **kwargs: object) -> None:
                del kwargs
                stream = args[1]
                stream.write("{\"partial\": true")  # type: ignore[union-attr]
                raise OSError("simulated JSON write failure")

            with patch.object(IMPORT_CV.json, "dump", side_effect=fail_after_partial_json_write):
                with self.assertRaises(OSError):
                    IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(list(output.parent.glob(f".{output.name}.*.tmp")))
            self.assertFalse(list(destination.parent.glob(f".{destination.name}.*.tmp")))
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

    def test_pdf_staging_copy_failure_cleans_its_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            def fail_after_partial_pdf_copy(source_file: object, destination_file: object, *args: object, **kwargs: object) -> None:
                del source_file, args, kwargs
                destination_file.write(b"%PDF-partial")  # type: ignore[union-attr]
                raise OSError("simulated PDF copy failure")

            with patch.object(IMPORT_CV.shutil, "copyfileobj", side_effect=fail_after_partial_pdf_copy):
                with self.assertRaises(OSError):
                    IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(list(output.parent.glob(f".{output.name}.*.tmp")))
            self.assertFalse(list(destination.parent.glob(f".{destination.name}.*.tmp")))
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

    def test_replacement_failure_removes_the_entire_output_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            with patch.object(IMPORT_CV.os, "replace", side_effect=[None, OSError("simulated replace failure")]):
                with self.assertRaises(OSError):
                    IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())

    def test_staging_failure_removes_the_entire_output_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, output, destination = self._release_source(directory)
            with patch.object(IMPORT_CV, "_stage_pdf", side_effect=OSError("simulated copy failure")):
                with self.assertRaises(OSError):
                    IMPORT_CV.import_cv(source, output, destination)
            self.assertFalse(output.exists())
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
