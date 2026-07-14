import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from append_central_examples import append_central_examples, examples_from_metadata, extract_examples
from cleanup_run import cleanup
from collect_screenshot import collect
from crop_screenshots import crop_directory
from inject_try_it_yourself import build_section, build_urls, inject_try_it_yourself
from prepare_run import build_context, central_url, parse_coordinate, safe_slug
from run_lifecycle import matches_workspace_url, workspace_url
from start_code_server import build_command, isolated_environment
from validate_output import validate
from validate_browser_preflight import validate_preflight

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

    def test_context_has_isolated_lifecycle_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            context = build_context("ballerinax/mysql", Path(temp), {"version": "1.2.3"})
            self.assertEqual(context["browser"]["expected_viewport"], {"width": 1720, "height": 968})
            self.assertIsNone(context["code_server"]["endpoint"])
            self.assertFalse(context["code_server"]["started_by_run"])


class WorkflowTests(unittest.TestCase):
    def test_playwright_mcp_contract(self):
        config = json.loads((SCRIPTS.parents[2] / ".mcp.json").read_text(encoding="utf-8"))
        args = config["mcpServers"]["playwright"]["args"]
        for required in ("--browser=chromium", "--headless", "--isolated", "--viewport-size=1720x968"):
            self.assertIn(required, args)

    def test_isolated_startup_and_cleanup_contract(self):
        skill = SCRIPTS.parent
        instructions = (skill / "SKILL.md").read_text(encoding="utf-8")
        workflow = (skill / "references" / "connector-ui-workflow.md").read_text(encoding="utf-8")
        self.assertLess(instructions.index("scripts/start_code_server.py"), instructions.index("browser_close"))
        self.assertLess(instructions.index("browser_close"), instructions.index("validate_browser_preflight.py"))
        self.assertIn("cleanup_run.py --context CONTEXT_PATH --status completed --browser-closed", instructions)
        self.assertIn("The first browser tool call of every run must be `browser_close`", workflow)
        self.assertIn("1720x968", workflow)

    def test_workspace_url_and_code_server_command(self):
        with tempfile.TemporaryDirectory() as temp:
            context = build_context("ballerinax/mysql", Path(temp), {"version": "1.2.3"})
            context["code_server"]["endpoint"] = "http://127.0.0.1:45678"
            url = workspace_url(context)
            self.assertTrue(url.startswith("http://127.0.0.1:45678/?folder="))
            self.assertTrue(matches_workspace_url(url, context["sample_dir"]))
            self.assertFalse(matches_workspace_url("http://127.0.0.1:45678/", context["sample_dir"]))
            command = build_command(context, 45678, Path(temp) / "profile")
            self.assertIn("--bind-addr", command)
            self.assertIn("127.0.0.1:45678", command)
            self.assertIn("--user-data-dir", command)
            self.assertIn("--ignore-last-opened", command)
            self.assertNotIn("--new-window", command)
            self.assertIn(context["sample_parent_dir"], command)

    def test_code_server_child_does_not_inherit_editor_ipc(self):
        import os
        old_value = os.environ.get("VSCODE_IPC_HOOK_CLI")
        try:
            os.environ["VSCODE_IPC_HOOK_CLI"] = "/tmp/editor-ipc.sock"
            self.assertNotIn("VSCODE_IPC_HOOK_CLI", isolated_environment())
        finally:
            if old_value is None:
                os.environ.pop("VSCODE_IPC_HOOK_CLI", None)
            else:
                os.environ["VSCODE_IPC_HOOK_CLI"] = old_value

    def test_preflight_validation_and_cleanup_record(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")
        with tempfile.TemporaryDirectory() as temp:
            context = build_context("ballerinax/mysql", Path(temp), {"version": "1.2.3"})
            context_path = Path(context["context_path"])
            context["code_server"]["endpoint"] = "http://127.0.0.1:45678"
            context_path.write_text(json.dumps(context), encoding="utf-8")
            image = Path(temp) / "preflight.png"
            Image.new("RGB", (1720, 968), "white").save(image)
            result = validate_preflight(context_path, image, workspace_url(context))
            self.assertTrue(result["workspace_matches"])
            self.assertTrue(result["viewport_matches"])
            Image.new("RGB", (100, 100), "white").save(image)
            with self.assertRaisesRegex(ValueError, "Browser viewport"):
                validate_preflight(context_path, image, workspace_url(context))
            cleanup_result = cleanup(context_path, "partial", browser_closed=True)
            self.assertEqual(cleanup_result["reason"], "not-owned")
            updated = json.loads(context_path.read_text(encoding="utf-8"))
            self.assertIsNotNone(updated["browser"]["closed_at"])
            self.assertTrue((Path(updated["run_log_dir"]) / "cleanup.json").is_file())

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

    def test_examples_extraction_heading_variants_and_nested_content(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                marker = "#" * level
                next_marker = "#" * level
                nested = f"{'#' * (level + 1)} Nested\r\nKeep.\r\n" if level < 6 else ""
                readme = (
                    f"# Package\r\n\r\n{marker} eXaMpLe\r\n\r\n"
                    f"Intro.\r\n\r\n{nested}"
                    f"{next_marker} API Docs\r\nDrop."
                )
                expected = f"Intro.\n\n{'#' * (level + 1)} Nested\nKeep." if level < 6 else "Intro."
                self.assertEqual(extract_examples(readme), expected)

    def test_examples_metadata_edge_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            metadata = Path(temp) / "metadata.json"
            for payload in ({}, {"readme": ""}, {"readme": "# Package"}, {"readme": "## Examples\n\n"}):
                metadata.write_text(json.dumps(payload), encoding="utf-8")
                self.assertIsNone(examples_from_metadata(metadata))
            metadata.write_text(json.dumps({"readme": ["invalid"]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be a string"):
                examples_from_metadata(metadata)

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
            context = build_context(
                "ballerinax/mysql",
                root,
                {"version": "1.2.3", "readme": "# Package\n\n## Examples\n\nUse Central.\n"},
            )
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
            self.assertTrue(run["central_examples_found"])
            self.assertTrue(run["examples_added"])
            self.assertEqual(run["sample_name"], "mysql_connector_sample")
            self.assertTrue(run["devant_url"].endswith("/mysql_connector_sample"))
            self.assertTrue(run["github_url"].endswith("/mysql_connector_sample"))
            self.assertTrue(
                Path(context["doc_path"]).read_text(encoding="utf-8").endswith(
                    "## More code examples\n\nUse Central.\n"
                )
            )

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
            self.assertEqual(append_central_examples(doc, metadata), (True, True))
            self.assertEqual(append_central_examples(doc, metadata), (True, False))
            self.assertEqual(doc.read_text(encoding="utf-8").count("## More code examples"), 1)

    def test_central_examples_cli_writes_sandbox_markdown(self):
        with tempfile.TemporaryDirectory() as temp:
            context = build_context(
                "ballerinax/mysql",
                Path(temp),
                {"version": "1.2.3", "readme": "# Package\n\n## Examples\n\nUse Central.\n"},
            )
            doc = Path(context["doc_path"])
            doc.write_text("# Example\n\n## Try it yourself\n\nExact placeholder.\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "append_central_examples.py"), "--context", context["context_path"]],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"examples_found": True, "examples_added": True})
            self.assertTrue(doc.read_text(encoding="utf-8").endswith("## More code examples\n\nUse Central.\n"))

    def test_central_examples_conflicts_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            doc = root / "guide.md"
            metadata = root / "metadata.json"
            metadata.write_text(json.dumps({"readme": "## Examples\n\nExpected."}), encoding="utf-8")
            doc.write_text("# Example\n\n## More code examples\n\nDifferent.\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match"):
                append_central_examples(doc, metadata)
            metadata.write_text(json.dumps({"readme": "# Package"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "has no examples"):
                append_central_examples(doc, metadata)

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
