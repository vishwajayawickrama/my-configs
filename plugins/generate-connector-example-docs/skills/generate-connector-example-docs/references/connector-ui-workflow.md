# Connector UI workflow

## Contents

1. Operating rules
2. Clean the VS Code workspace
3. Package and operation discovery
4. Project creation
5. Connection workflow
6. Operation workflow
7. Screenshot protocol
8. Recovery rules

## Operating rules

- Work only through the WSO2 Integrator low-code UI in code-server, except for inspecting or minimally repairing the generated sample files.
- Use `browser_snapshot` before every interaction. Use screenshot calls only for the six documentation milestones.
- Use targets or element references from the latest snapshot. Refresh the snapshot after navigation, saving, opening a panel, or any failed interaction.
- Close helper panels, dropdowns, dialogs, source tabs, and overlays before screenshots unless the named milestone requires that panel.
- Never allow the global VS Code secondary sidebar, Chat/Copilot panel, integrated terminal, Welcome tab, or unrelated editor tab to appear in a milestone screenshot.
- Prefer device-independent UI actions: select, enter, expand, and save.
- Never enter real secrets. Bind credential and endpoint fields to configurables and leave their actual values empty.
- Preserve the default authentication variant unless the user explicitly requests another supported variant.
- Use the exact visible UI label when documenting a field or operation.
- Do not delegate, open another agent, call an LLM API, publish, or use git.

## Clean the VS Code workspace

Treat workspace cleanup as a blocking gate. Do not begin connector work or take screenshot 01 until every verification below passes.

### Before opening WSO2 Integrator

1. Navigate to the code-server URL and wait for the VS Code interface to finish loading.
2. If a **Git repository found on parent** popup appears, select **Never**.
3. Close the global right-side secondary sidebar where GitHub Copilot or **Chat** is docked. Prefer its visible close control; otherwise press **Ctrl+Alt+B** or use **View → Appearance → Secondary Side Bar**.
4. If a Chat or Copilot panel remains anywhere, select that panel's specific × close button or hide it from the **View** menu.
5. Close the integrated terminal when it is visible at the bottom of the editor.
6. Close all initial editor tabs with each tab's specific × or **View → Close All Editors**. This includes automatically opened source files and any stale **Welcome** tab.
7. Call `browser_snapshot` and verify that no popup, global Chat/Copilot panel, secondary sidebar, terminal, source editor, split editor, or initial editor tab remains.

### After the integration opens

1. Wait until the WSO2 Integrator project tree and visual design surface are loaded.
2. If the **Welcome** tab is still open, select the × on the **Welcome** tab itself. Do not use a generic close command that might close the active WSO2 Integrator visual editor.
3. Close any `.bal` or unrelated editor tab that opened during project creation by selecting that tab's own ×.
4. Keep the WSO2 Integrator visual editor and project sidebar open.
5. Call `browser_snapshot` and verify all of the following:
   - The **Welcome** tab is absent.
   - The global Chat/Copilot panel and secondary sidebar are absent.
   - The integrated terminal is absent.
   - No source or unrelated editor tab and no split editor is visible.
   - The WSO2 Integrator visual design surface remains visible.

### Clean-frame gate before screenshot 01

Immediately before opening the connector palette, take one more snapshot and repeat the after-integration verification. If any global panel or unrelated tab returned, close it and verify again. Only then open **Add Connection** and capture screenshot 01.

Do not confuse the global VS Code Chat/Copilot secondary sidebar with a WSO2 Integrator connection, operation, helper, or configuration side panel. Close the global Chat/Copilot UI permanently; keep a WSO2 Integrator panel open only when the current workflow step or named screenshot milestone requires it.

## Package and operation discovery

Use Central metadata and the connector card to determine the human-readable connector name. Choose one representative primary operation that demonstrates the connector's core purpose and can be configured without destructive external actions.

Use this preference order:

1. Follow an operation named by the user.
2. Prefer a safe read, list, get, search, send, or create operation commonly shown in package examples.
3. Avoid delete, irreversible administration, or operations that require unavailable external state.
4. If multiple operations remain equally suitable, choose the first clearly documented primary operation and state the choice in the run summary.

Build the project without calling the external service. The goal is a valid integration design and reproducible documentation, not a live credentialed transaction.

## Project creation

1. Complete the **Before opening WSO2 Integrator** cleanup gate.
2. Open WSO2 Integrator and create a new integration under the run's `sample_dir`.
3. Use a filesystem-safe project name derived from the package, ending in `_connector_sample`.
4. Wait until the integration design surface is fully loaded.
5. Complete the **After the integration opens** cleanup gate.
6. Confirm the project tree and design canvas are visible before adding artifacts.

## Connection workflow

### Milestone 1: Connector palette

1. Pass the **Clean-frame gate before screenshot 01**.
2. Select **Add Connection** from the **Connections** area or open **+ Add Artifact** and choose **Connection**.
3. Snapshot and confirm that the connector palette is unobstructed and no global Chat/Copilot sidebar, Welcome tab, terminal, source tab, or unrelated editor is visible.
4. Capture screenshot 01 immediately, before searching or selecting a connector.
5. Enter the exact Central package name in the search field.
6. Select the matching connector card and confirm that its connection form opens.

### Configure fields

- Bind every visible non-boolean connection field, required or optional, to a descriptive camelCase configurable.
- Select boolean values directly from their true/false dropdowns. Do not switch booleans to expression mode.
- Select enum/type dropdown values directly. Do not create configurables for type selections.
- For a scalar field, open its helper panel, choose **Configurables**, create the correct primitive type, save it, and close the helper. Confirm the configurable was inserted into the intended field.
- Leave sensitive configurable defaults empty. Use non-secret placeholders only when the UI requires a value.
- For record-typed fields, first create all nested configurables. Switch the record field to **Expression**, then enter a bare Ballerina record expression such as `{auth: {username: userName, password: password}}`. Do not quote the whole record or configurable identifiers.
- Preserve the form's default authentication type unless the user explicitly directs otherwise.

Audit the complete form from top to bottom before saving. Verify that each non-boolean input is bound, no secret is visible, and no error marker is present.

### Milestone 2: Completed connection form

1. Close helper panels and overlays.
2. Scroll the form container to the top with a safe DOM scroll operation if needed.
3. Snapshot and confirm the form is unobstructed.
4. Capture screenshot 02 before selecting **Save** or **Add**.
5. Record every configured field's visible display label for the guide.

### Milestone 3: Saved connection

1. Save the connection.
2. Navigate to the integration-level design canvas if the UI shows a project overview or source file.
3. Confirm the saved connection appears in **Connections** or on the canvas.
4. Capture screenshot 03.
5. Open **Configurations** and confirm every created configurable appears. Leave values empty. A separate screenshot is not required.

## Operation workflow

### Add an entry point

Add an **Automation** entry point unless the selected connector or user guidance requires another supported entry point. Drill into the detailed flow until **Start**, the intervening **+** node, and **Error Handler** are visible.

To activate a nested canvas **+** node:

1. Snapshot with bounding boxes.
2. Confirm the detailed automation flow rather than the project-level design card.
3. Select the exact **+** node between **Start** and **Error Handler**.
4. Snapshot again and confirm the node palette opened before continuing.

### Milestone 4: Expanded operations

1. Expand the saved connection in the node palette.
2. Ensure its available operations are visible before selecting one.
3. Capture screenshot 04.
4. Select the chosen primary operation.

### Configure the operation

- Fill every required operation input with a safe representative value, configurable reference, or record configuration.
- For records, enable only representative fields necessary to make the example understandable and structurally valid.
- Keep literal examples obviously non-secret.
- Preserve the generated result variable when the operation returns a value, or rename it to a concise descriptive name.
- Document field names using their visible labels, not internal accessible names.

### Milestone 5: Completed operation form

1. Close record editors, helper panels, and unrelated source tabs.
2. Scroll the operation form to the top.
3. Snapshot and verify all configured values and no error markers.
4. Capture screenshot 05 before saving.
5. Save the operation.

If the operation returns a value, add a low-code log step that surfaces the result. Prefer the UI's log operation. Use a minimal direct `.bal` edit only when the UI cannot express the required log step; inspect the actual result variable and keep the source valid.

### Milestone 6: Completed flow

1. Close every `.bal` source tab and split editor.
2. Navigate back to the detailed automation flow.
3. Confirm the complete chain is visible: **Start** to connector operation to log step when applicable to **Error Handler**.
4. Confirm there are no error indicators.
5. Capture screenshot 06.

## Screenshot protocol

Use the package-derived underscore prefix for every image:

```text
<prefix>_screenshot_01_palette.png
<prefix>_screenshot_02_connection_form.png
<prefix>_screenshot_03_connections_list.png
<prefix>_screenshot_04_operations_panel.png
<prefix>_screenshot_05_operation_form.png
<prefix>_screenshot_06_completed_flow.png
```

After every screenshot tool call, copy the returned temporary file immediately with `collect_screenshot.py`. Never pass an absolute destination or directory separators as the MCP screenshot filename.

Every milestone screenshot must exclude the global Chat/Copilot secondary sidebar, integrated terminal, Welcome tab, source tabs, unrelated editor tabs, popups, and split editors. Correct the UI state before capture; do not hide these elements later by cropping the image.

## Recovery rules

- If an element reference is stale, take a new snapshot; never repeat the stale reference blindly.
- If a save produces validation errors, reopen the form and correct them before proceeding.
- If the wrong canvas is visible, select the automation card or integration design entry and verify the detailed flow.
- If a configurable is injected into the wrong field, restore that field from the helper panel before continuing.
- If code-server or the extension crashes, preserve logs and artifacts, restart only infrastructure owned by this run, and resume from the latest verified milestone.
- If the package or connector card cannot be found, stop with evidence rather than substituting a different connector.
