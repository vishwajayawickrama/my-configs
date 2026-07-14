import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from collect_screenshot import collect
from crop_screenshots import crop_directory
from finalize_run import append_examples, extract_examples
from inject_try_it_yourself import build_section, build_urls, inject_try_it_yourself
from prepare_run import build_context, central_url, parse_coordinate, safe_slug
from validate_output import validate

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def valid_document(prefix):
    images = "\n".join(
        "![Milestone {0}](../screenshots/{1}_screenshot_{0:02d}_{2}.png)".format(
            number,
            prefix,
            ["palette", "connection_form", "connections_list", "operations_panel", "operation_form", "completed_flow"][number - 1],
        )
        for number in range(1, 7)
    )
    return """# Example

## What you'll build

This example connects to MySQL and lists rows. It keeps connection settings configurable.

**Operations used:**
- **List rows** : Lists rows from a table.

## Architecture

```mermaid
flowchart LR
    A((User)) --> B[List rows] --> C[MySQL connector] --> D((MySQL))
```

## Prerequisites

- Access to a MySQL database.

## Setting up the MySQL integration

> **New to WSO2 Integrator?** Follow the [Create a New Integration](../../../../develop/create-integrations/create-new-integration.md) guide to set up your integration first, then return here to add the connector.

## Adding the MySQL connector

### Step 1: Open the connector palette

Select **Add Connection**.

## Configuring the MySQL connection

### Step 2: Configure the connection

Enter connection settings.

### Step 3: Save the connection

Select **Save**.

### Step 4: Set actual values for your configurables

Select **Configurations** under **Data Mappers**.

- **host** (`string`) : Database host name.

## Configuring the MySQL List rows operation

### Step 5: Add an automation

Select **Automation**.

### Step 6: Configure the operation

Select **List rows**.

### Step 7: Review the completed flow

Review the flow.

{images}
""".format(images=images)


class CoordinateTests(unittest.TestCase):
    def test_parses_latest_and_explicit_version(self):
        self.assertEqual(parse_coordinate("ballerinax/mysql"), ("ballerinax", "mysql", "latest"))
        self.assertEqual(
            parse_coordinate("ballerinax/sap.businessone:1.2.3"),
            ("ballerinax", "sap.businessone", "1.2.3"),
        )

    def test_rejects_bare_name(self):
        with self.assertRaises(ValueError):
            parse_coordinate("mysql")

    def test_url_and_slug(self):
        self.assertEqual(
            central_url("ballerinax", "sap.businessone", "1.2.3"),
            "https://api.central.ballerina.io/2.0/registry/packages/ballerinax/sap.businessone/1.2.3",
        )
        self.assertEqual(safe_slug("ballerinax", "sap.businessone"), "ballerinax-sap-businessone")

    def test_sample_name_and_directory_are_authoritative(self):
        with tempfile.TemporaryDirectory() as temp:
            context = build_context(
                "ballerinax/sap-business.one", Path(temp), {"version": "1.2.3"}
            )
            self.assertEqual(context["sample_name"], "sap_business_one_connector_sample")
            self.assertEqual(Path(context["sample_dir"]).name, context["sample_name"])


class WorkflowTests(unittest.TestCase):
    def test_canonical_document_template_contract(self):
        skill = SCRIPTS.parent
        template = (skill / "assets" / "templates" / "connector-example-doc.md").read_text(encoding="utf-8")
        contract = (skill / "references" / "documentation-contract.md").read_text(encoding="utf-8")
        style = (skill / "references" / "microsoft-writing-style.md").read_text(encoding="utf-8")
        required = [
            "# Example",
            "## What you'll build",
            "## Architecture",
            "## Setting up the {{CONNECTOR_DISPLAY_NAME}} integration",
            "## Adding the {{CONNECTOR_DISPLAY_NAME}} connector",
            "## Configuring the {{CONNECTOR_DISPLAY_NAME}} connection",
            "## Configuring the {{CONNECTOR_DISPLAY_NAME}} {{OPERATION_DISPLAY_NAME}} operation",
            "Set actual values for your configurables",
        ]
        self.assertTrue(all(value in template for value in required))
        self.assertEqual(
            [f"{number:02d}" for number in range(1, 7)],
            [value for value in __import__("re").findall(r"_screenshot_(\d{2})_", template)],
        )
        self.assertIn("assets/templates/connector-example-doc.md", contract)
        self.assertIn("Use **select**, not click", style)

    def test_startup_cleanup_contract(self):
        workflow = (SCRIPTS.parent / "references" / "connector-ui-workflow.md").read_text(encoding="utf-8")
        cleanup = workflow[
            workflow.index("## Clean the VS Code workspace") : workflow.index("## Package and operation discovery")
        ]
        required = [
            "## Clean the VS Code workspace",
            "Git repository found on parent",
            "global right-side secondary sidebar",
            "Chat or Copilot panel",
            "integrated terminal",
            "Close all initial editor tabs",
            "If the **Welcome** tab is still open",
            "### Clean-frame gate before screenshot 01",
        ]
        positions = [cleanup.index(value) for value in required]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Do not confuse the global VS Code Chat/Copilot secondary sidebar", cleanup)
        self.assertIn("do not hide these elements later by cropping the image", workflow)

    def test_examples_extraction(self):
        readme = "# Package\n\n## Examples\n\nUse this example.\n\n## API Docs\nNope"
        self.assertEqual(extract_examples(readme), "Use this example.")

    def test_collect_and_validate_complete_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = build_context("ballerinax/mysql", root, {"version": "1.2.3", "readme": ""})
            prefix = context["image_prefix"]
            source = root / "source.png"
            source.write_bytes(PNG)
            suffixes = ["palette", "connection_form", "connections_list", "operations_panel", "operation_form", "completed_flow"]
            for number, suffix in enumerate(suffixes, 1):
                destination = Path(context["screenshots_dir"]) / f"{prefix}_screenshot_{number:02d}_{suffix}.png"
                collect(source, destination)
            Path(context["doc_path"]).write_text(valid_document(prefix), encoding="utf-8")
            sample = Path(context["sample_dir"])
            (sample / "Ballerina.toml").write_text("[package]\norg='test'\nname='sample'\nversion='0.1.0'\n", encoding="utf-8")
            (sample / "main.bal").write_text("public function main() {}\n", encoding="utf-8")
            self.assertTrue(
                inject_try_it_yourself(
                    Path(context["doc_path"]), sample, context["sample_name"]
                )
            )
            self.assertEqual(validate(context), [])

    def test_try_it_yourself_markdown_sandbox_and_idempotency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = build_context("ballerinax/mysql", root, {"version": "1.2.3"})
            doc = Path(context["doc_path"])
            doc.write_text("# Example\n\n## Operation\n\nDone.\n", encoding="utf-8")
            sample = Path(context["sample_dir"])
            self.assertTrue(inject_try_it_yourself(doc, sample, context["sample_name"]))
            self.assertFalse(inject_try_it_yourself(doc, sample, context["sample_name"]))
            self.assertEqual(doc.read_text(encoding="utf-8").count("## Try it yourself"), 1)
            self.assertIn(build_section("mysql_connector_sample"), doc.read_text(encoding="utf-8"))
            devant_url, github_url = build_urls("mysql_connector_sample")
            expected_path = "integrator-default-profile/connectors/mysql_connector_sample"
            self.assertTrue(devant_url.endswith(expected_path))
            self.assertTrue(github_url.endswith(expected_path))

    def test_try_it_yourself_precedes_examples(self):
        with tempfile.TemporaryDirectory() as temp:
            context = build_context("ballerinax/mysql", Path(temp), {"version": "1.2.3"})
            doc = Path(context["doc_path"])
            doc.write_text("# Example\n\n## More code examples\n\nExample.\n", encoding="utf-8")
            inject_try_it_yourself(doc, Path(context["sample_dir"]), context["sample_name"])
            text = doc.read_text(encoding="utf-8")
            self.assertLess(text.index("## Try it yourself"), text.index("## More code examples"))

    def test_finalizer_records_deterministic_sample_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = build_context("ballerinax/mysql", root, {"version": "1.2.3", "readme": ""})
            prefix = context["image_prefix"]
            source = root / "source.png"
            source.write_bytes(PNG)
            for number, suffix in enumerate(
                ["palette", "connection_form", "connections_list", "operations_panel", "operation_form", "completed_flow"], 1
            ):
                collect(source, Path(context["screenshots_dir"]) / f"{prefix}_screenshot_{number:02d}_{suffix}.png")
            Path(context["doc_path"]).write_text(valid_document(prefix), encoding="utf-8")
            sample = Path(context["sample_dir"])
            (sample / "Ballerina.toml").write_text("[package]\norg='test'\nname='sample'\nversion='0.1.0'\n", encoding="utf-8")
            (sample / "main.bal").write_text("public function main() {}\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "finalize_run.py"), "--context", context["context_path"], "--skip-crop"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run = json.loads((Path(context["run_log_dir"]) / "run.json").read_text(encoding="utf-8"))
            self.assertTrue(run["try_it_yourself_added"])
            self.assertEqual(run["sample_name"], "mysql_connector_sample")
            self.assertTrue(run["devant_url"].endswith("/mysql_connector_sample"))
            self.assertTrue(run["github_url"].endswith("/mysql_connector_sample"))

    def test_validator_rejects_template_and_style_leaks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = build_context("ballerinax/mysql", root, {"version": "1.2.3", "readme": ""})
            prefix = context["image_prefix"]
            source = root / "source.png"
            source.write_bytes(PNG)
            for number, suffix in enumerate(
                ["palette", "connection_form", "connections_list", "operations_panel", "operation_form", "completed_flow"], 1
            ):
                collect(source, Path(context["screenshots_dir"]) / f"{prefix}_screenshot_{number:02d}_{suffix}.png")
            invalid = valid_document(prefix).replace("Select **Save**.", "Click **Save**.", 1)
            invalid = invalid.replace("This example connects", "{{WHAT_YOU_WILL_BUILD}} This example connects")
            Path(context["doc_path"]).write_text(invalid, encoding="utf-8")
            sample = Path(context["sample_dir"])
            (sample / "Ballerina.toml").write_text("[package]\norg='test'\nname='sample'\nversion='0.1.0'\n", encoding="utf-8")
            (sample / "main.bal").write_text("public function main() {}\n", encoding="utf-8")
            inject_try_it_yourself(Path(context["doc_path"]), sample, context["sample_name"])
            errors = validate(context)
            self.assertTrue(any("template placeholders" in error for error in errors))
            self.assertTrue(any("nonpreferred UI terminology" in error for error in errors))

    def test_run_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_context("ballerinax/mysql", root, {"version": "1.2.3"})
            with self.assertRaises(FileExistsError):
                build_context("ballerinax/mysql", root, {"version": "1.2.3"})

    def test_crop_and_examples_postprocessing(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            screenshots = root / "screenshots"
            screenshots.mkdir()
            image_path = screenshots / "sample.png"
            Image.new("RGB", (100, 80), "white").save(image_path)
            self.assertEqual(crop_directory(screenshots), 1)
            with Image.open(image_path) as image:
                self.assertEqual(image.size, (100, 30))

            doc = root / "guide.md"
            metadata = root / "metadata.json"
            doc.write_text("# Example\n", encoding="utf-8")
            metadata.write_text(
                json.dumps({"readme": "# Package\n\n## Examples\n\nUse this example.\n"}),
                encoding="utf-8",
            )
            self.assertTrue(append_examples(doc, metadata))
            self.assertFalse(append_examples(doc, metadata))
            self.assertEqual(doc.read_text(encoding="utf-8").count("## More code examples"), 1)

    def test_rejects_old_or_mismatched_try_it_yourself_links(self):
        with tempfile.TemporaryDirectory() as temp:
            context = build_context("ballerinax/mysql", Path(temp), {"version": "1.2.3"})
            doc = Path(context["doc_path"])
            doc.write_text("# Example\n", encoding="utf-8")
            inject_try_it_yourself(doc, Path(context["sample_dir"]), context["sample_name"])
            old = doc.read_text(encoding="utf-8").replace(
                "integrator-default-profile/connectors/", "connectors/"
            )
            doc.write_text(old, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match"):
                inject_try_it_yourself(doc, Path(context["sample_dir"]), context["sample_name"])


if __name__ == "__main__":
    unittest.main()
