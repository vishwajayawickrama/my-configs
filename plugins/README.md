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

## Use from Antigravity and compatible agents

Opening this repository as a workspace exposes the connector documentation skill through
`.agents/skills/generate-connector-example-docs` and the Playwright MCP server through
`.agents/mcp_config.json`. Both paths are relative symlinks to this plugin, so the Codex plugin
remains the single source of truth.

Antigravity uses both workspace paths directly. Other agents that support the shared
`.agents/skills` convention can discover the skill, but may require their own MCP configuration
format. Reload the workspace or start a new conversation after pulling changes.

### Install globally for Antigravity CLI

To make the skill available when `agy` runs outside this repository, link it into the CLI's
global skill directory:

```sh
mkdir -p ~/.gemini/antigravity-cli/skills
ln -sfn ~/Codes/my-configs/plugins/generate-connector-example-docs/skills/generate-connector-example-docs \
  ~/.gemini/antigravity-cli/skills/generate-connector-example-docs
```

Global MCP servers are configured separately in `~/.gemini/config/mcp_config.json`. Merge the
`playwright` server from this plugin's `.mcp.json` into that file; do not replace other configured
servers. The Antigravity IDE uses `~/.gemini/config/skills/` for global skills and is not installed
by the CLI commands above.

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
