"""Regression tests for skill scripts and repository tooling (stdlib unittest).

Run: python3 -m unittest discover -s tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EX = os.path.join(ROOT, "examples")


def run(*args):
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True, cwd=ROOT)


class VersionDetect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = run("skills/healthcare-version-detect/scripts/detect_versions.py", EX, "--json")
        assert r.returncode == 0, r.stderr
        cls.data = json.loads(r.stdout)

    def test_hl7v2_versions_per_interface(self):
        self.assertEqual(set(self.data["hl7v2.MSH-12"]), {"2.3.1", "2.5.1"})

    def test_fhir_core_and_igs_independent(self):
        self.assertIn("4.0.1 (R4)", self.data["fhir.fhirVersion"])
        self.assertIn("5.0.0", self.data["fhir.sushi.fhirVersion"])
        self.assertIn("hl7.fhir.us.core#6.1.0", self.data["fhir.ig_dependencies"])

    def test_x12_and_ncpdp(self):
        self.assertIn("00501", self.data["x12.ISA12"])
        self.assertIn("005010X222A1", self.data["x12.GS08"])
        self.assertIn("2017071", self.data["ncpdp.script_version"])

    def test_dicom_meta_only(self):
        self.assertTrue(any(k.startswith("1.2.840.10008.1.2.1 ") for k in self.data["dicom.transfer_syntax"]))
        self.assertNotIn("TEST^PATIENT", json.dumps(self.data))  # never prints patient attributes

    def test_ccda_release(self):
        self.assertIn("2015-08-01", self.data["ccda.us_realm_header"])


class Hl7Inspector(unittest.TestCase):
    def inspect(self, msg, *extra):
        with tempfile.NamedTemporaryFile("w", suffix=".hl7", delete=False, newline="") as f:
            f.write(msg)
        r = run("skills/hl7v2-message-inspector/scripts/hl7v2_inspect.py", f.name, "--json", *extra)
        os.unlink(f.name)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_new_message_on_old_version_is_flagged(self):
        out = self.inspect("MSH|^~\\&|A|B|C|D|2026||OMI^O23^OMI_O23|1|P|2.3\rPID|1||TEST1\r")
        text = " ".join(out["warnings"])
        self.assertIn("OMI is not defined in v2.3", text)
        self.assertIn("MSH-9.3", text)

    def test_truncation_char_before_27(self):
        out = self.inspect("MSH|^~\\&#|A|B|C|D|2026||ADT^A01|1|P|2.5.1\r")
        self.assertTrue(any("truncation" in w for w in out["warnings"]))

    def test_clean_251_message(self):
        out = self.inspect(open(os.path.join(EX, "hl7v2/2.5.1/omi_o23.hl7"), newline="").read())
        self.assertEqual(out["declared_version_MSH12"], "2.5.1")
        self.assertEqual(out["warnings"], [])

    def test_phi_masked_by_default(self):
        r = run("skills/hl7v2-message-inspector/scripts/hl7v2_inspect.py", os.path.join(EX, "hl7v2/2.3.1/adt_a01.hl7"))
        self.assertNotIn("PATIENT^ONE", r.stdout)


class X12AndCcda(unittest.TestCase):
    def test_x12_tr3(self):
        r = run("skills/x12-transaction-analyzer/scripts/x12_inspect.py", os.path.join(EX, "x12/005010X222A1/837p.edi"))
        self.assertIn("-> 837P", r.stdout)
        self.assertNotIn("NOTE: ISA12", r.stdout)

    def test_ccda_inventory(self):
        r = run("skills/ccda-document-review/scripts/ccda_templates.py", os.path.join(EX, "ccda/2.1/ccd.xml"))
        self.assertIn("2015-08-01", r.stdout)


class RepoTooling(unittest.TestCase):
    def test_build_check_clean(self):
        r = run(".github/scripts/build.py", "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_content_lint_clean(self):
        r = run(".github/scripts/content_lint.py")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_installer_both_tools(self):
        with tempfile.TemporaryDirectory() as d:
            r = run("scripts/install.py", d, "--tool", "both", "--plugin", "all")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(d, ".github/agents/fhir-engineer.agent.md")))
            self.assertTrue(os.path.exists(os.path.join(d, ".claude/agents/fhir-engineer.md")))
            self.assertTrue(os.path.exists(os.path.join(d, ".github/healthcare-profile.yml")))
            self.assertIn("healthcare-copilot:begin", open(os.path.join(d, "CLAUDE.md")).read())

    def test_marketplace_matches_plugins(self):
        m = json.load(open(os.path.join(ROOT, ".github/plugin/marketplace.json")))
        self.assertEqual({p["name"] for p in m["plugins"]}, set(os.listdir(os.path.join(ROOT, "plugins"))))
        for p in m["plugins"]:
            agents = os.path.join(ROOT, p["source"], "com.github.copilot", "agents")
            for f in os.listdir(agents) if os.path.isdir(agents) else []:
                self.assertIn("Version resolution protocol (embedded)", open(os.path.join(agents, f)).read())


if __name__ == "__main__":
    unittest.main()
