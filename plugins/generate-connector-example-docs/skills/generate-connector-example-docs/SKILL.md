---
name: generate-connector-example-docs
description: Generate validated WSO2 Integrator connector example documentation, six low-code UI screenshots, and a preserved sample project from a full Ballerina Central package coordinate such as ballerinax/mysql or ballerinax/mysql:1.16.0. Use when Codex needs to create or regenerate connector example guides through the WSO2 Integrator UI. Do not use for triggers, batch generation, publishing, commits, deployments, or pull requests.
---

# Generate Connector Example Docs

Create the integration and documentation directly in the current agent. Never start a nested agent, call an LLM API, publish artifacts, or run git commands.

## Inputs

Require a full Central coordinate in one of these forms:

- `organization/package`
- `organization/package:version`

Reject a bare package name. Treat an omitted version as `latest`. Accept optional user guidance for operation or authentication choices; it overrides the workflow's default selection heuristics.

## Run the workflow

1. Resolve this skill directory and run `scripts/prepare_run.py COORDINATE --root "$PWD"`. Stop on invalid input, missing Central metadata, or an existing completed or nonempty output directory.
2. Read the emitted context JSON. Use its absolute `run_dir`, `sample_dir`, `screenshots_dir`, and `doc_path` values throughout the run.
3. Check `node`, `npx`, `python3`, Pillow (`python3 -c "import PIL"`), `code-server`, and the `wso2.wso2-integrator` code-server extension (`code-server --list-extensions`). Ask before installing a missing prerequisite or downloading Chromium. Install Pillow only from `scripts/requirements.txt`. Do not install silently.
4. Reuse a healthy code-server on a user-specified port or port 8080. Otherwise start `code-server --auth none --bind-addr 127.0.0.1:PORT SAMPLE_PARENT`, redirect output to `run-log/code-server.log`, and record its PID. Stop only a server started by this run.
5. Read `references/connector-ui-workflow.md` completely before browser interaction. Complete its clean-workspace gate before connector work: close the global Chat/Copilot secondary sidebar, integrated terminal, Welcome tab, unrelated editor/source tabs, and transient popups while keeping the WSO2 Integrator visual editor open. Do not capture screenshot 01 until a fresh snapshot verifies the clean frame. Follow the reference through all six milestones. Use the bundled `playwright` MCP tools; do not use unsafe browser code execution.
6. After every `browser_take_screenshot` call, immediately run `scripts/collect_screenshot.py RETURNED_PATH SCREENSHOTS_DIR/FILENAME`. Keep filenames sequential from `01` through `06`.
7. Make `sample_dir` the project root: `Ballerina.toml` and the generated `.bal` files must live directly within it. If the UI creates a named project elsewhere or one level deeper, copy that project's contents into `sample_dir` before finalization.
8. Read `references/documentation-contract.md` and `references/microsoft-writing-style.md` completely before writing. Copy `assets/templates/connector-example-doc.md` to `doc_path`, then replace every placeholder with facts from the completed workflow. Remove template comments and inapplicable conditional sections. Do not author from a blank file, create an intermediate execution prompt, or use a second model for enforcement.
9. Run `scripts/finalize_run.py --context CONTEXT_PATH`. If it reports validation failures, correct the guide or artifacts and rerun until it succeeds.
10. Stop the code-server process only when this run started it. Report the guide, screenshot directory, sample directory, resolved package version, and validation status.

## Safety and boundaries

- Keep all generated files under `artifacts/<organization>-<package>/` in the invocation root.
- Never overwrite a prior run automatically.
- Never put credentials or secret values in the guide, screenshots, sample, logs, or config files. Leave configurable values empty or use obvious non-secret placeholders.
- Do not add `Try it yourself` links because this workflow does not publish the sample.
- Do not create branches, commits, pushes, deployments, issues, or pull requests.
- Do not support trigger packages or batch queues in this skill.
