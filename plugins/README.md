# Codex plugins

Installable Codex plugins stored in this repository. The repo marketplace is defined at `.agents/plugins/marketplace.json`.

## Install the marketplace

Add this repository as a local marketplace once:

```sh
codex plugin marketplace add ~/Codes/my-configs
```

Then install the connector documentation plugin:

```sh
codex plugin add generate-connector-example-docs@my-configs
```

Start a new Codex thread after installation so the bundled skill and Playwright MCP tools are loaded.

## Generate connector documentation

Invoke the skill with a full Ballerina Central coordinate:

```text
$generate-connector-example-docs generate an example guide for ballerinax/mysql
```

An explicit package version is also supported:

```text
$generate-connector-example-docs generate an example guide for ballerinax/mysql:1.16.0
```

The plugin creates a preserved sample project, six screenshots, a validated Markdown guide, deterministic **Try it yourself** links, a verbatim **More code examples** section from cached Ballerina Central metadata when available, and run metadata under `artifacts/<organization>-<package>/` in the repository where Codex is running. The links target the sample's canonical future location under `wso2/integration-samples/tree/main/integrator-default-profile/connectors/`; the plugin does not publish, commit, deploy, or create pull requests.

## Prerequisites

The workflow requires Node.js, Python, code-server, and the `wso2.wso2-integrator` code-server extension. It reports missing prerequisites and asks before installing them. Screenshot cropping uses the pinned Pillow dependency in the skill's `scripts/requirements.txt`.

## Update a local installation

After changing the plugin, refresh its Codex cache version with the plugin creator's `update_plugin_cachebuster.py`, reinstall `generate-connector-example-docs@my-configs`, and start a new thread.
