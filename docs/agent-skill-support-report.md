# Agent Skills, Plugins & Marketplaces Across Major Agent Harnesses

*A comparison of how Claude Code, OpenAI Codex, Google Antigravity, OpenCode, Cursor, Gemini CLI, and GitHub Copilot support Agent Skills, plugin bundling, and marketplace distribution.*

---

## Summary Comparison Table

| Harness | Skills Support | Skills Location | Plugin Support | What a Plugin Bundles | Marketplace Support | Marketplace Mechanism |
|---|---|---|---|---|---|---|
| **Claude Code** | ✅ Native | `.claude/skills/` (project), `~/.claude/skills/` (global) | ✅ Native | Skills, agents, commands, hooks, MCP servers | ✅ Native | `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json`; `/plugin marketplace add`, `/plugin install` |
| **OpenAI Codex (CLI + ChatGPT)** | ✅ Native | REPO/USER/ADMIN/SYSTEM tiers; `.agents/skills/`, `~/.codex/skills/` | ✅ Native (added ~Mar 2026) | Skills, MCP servers, "apps" (connectors), hooks | ✅ Native | `.codex-plugin/plugin.json`; repo-scoped or personal `marketplace.json` under `.agents/plugins/`; `/plugins` in CLI |
| **Google Antigravity** | ✅ Native | `.agents/skills/` (project); `~/.gemini/config/skills/` (IDE global); `~/.gemini/antigravity-cli/skills/` (CLI global); legacy `.agent/skills/` supported | ✅ Native | Skills, rules, MCP servers, hooks | ⚠️ Built-in catalog, no open third-party marketplace | Custom plugins use `.agents/plugins/` (workspace), `~/.gemini/config/plugins/` (IDE global), or `~/.gemini/antigravity-cli/plugins/` (CLI global). |
| **OpenCode** | ✅ Native (via Agent Skills spec) | `.agents/skills/` (aliases with other tools) | ✅ Native (JS/TS plugin modules) | Custom tools, hooks (event/lifecycle), auth providers — **not** a bundling format for skills | ⚠️ Community only | No first-party marketplace; community sites (opencode.cafe) and third-party CLIs (`opencode-marketplace`) fill the gap |
| **Cursor** | ✅ Native | `.cursor/skills/` (project), global config dir | ✅ Native (added ~Feb 2026) | Skills, rules, subagents, MCP servers, hooks | ✅ Native, curated | `.cursor-plugin/marketplace.json` + `.cursor-plugin/plugin.json`; manually reviewed before listing at cursor.com/marketplace |
| **Gemini CLI** | ✅ Native | `.gemini/skills/` or `.agents/skills/` alias (project/user) | ⚠️ "Extensions" only (broader, older concept) | MCP servers, context files (`GEMINI.md`), slash commands, skills | ⚠️ Extensions Gallery (not a true plugin marketplace) | No `marketplace.json`; one Git repo = one extension installed via `gemini extensions install <url>` |
| **GitHub Copilot (CLI / cloud agent)** | ✅ Native (added Dec 2025) | `.agents/skills/`, `~/.copilot/skills/` | ✅ Native | Agents, skills, hooks, MCP servers (`.mcp.json`), LSP config | ✅ Native | `marketplace.json` in `.github/plugin/` (or legacy `.claude-plugin/` shim); `copilot plugin marketplace add`, `copilot plugin install` |
| **Cross-tool (Open Agent Skills CLI)** | ✅ (delivers skills only, to 70+ agents) | Per-agent conventional path (see agent's own column) | ❌ Not applicable | — | ❌ Not applicable | `npx skills add owner/repo`; discovers `SKILL.md` via conventional paths, catalog walk, or recursive fallback |

---

## Per-Harness Detail

### Claude Code
The reference implementation most others have converged toward. A marketplace repo hosts `.claude-plugin/marketplace.json`, listing one or more plugins; each plugin can bundle skills, subagents, slash commands, hooks, and MCP servers. Install flow: `/plugin marketplace add owner/repo` → `/plugin install plugin-name@marketplace-name`. Auto-update exists but is a per-user, per-marketplace toggle — off by default for third-party marketplaces.

### OpenAI Codex
Codex shipped a native plugin system in **March 2026**, converging on the same three-layer shape as Claude Code and Cursor: skill (workflow), app (service connector), MCP server (custom tools). Manifest is `.codex-plugin/plugin.json`; marketplaces are `marketplace.json` files, either repo-scoped (`$REPO_ROOT/.agents/plugins/marketplace.json`) or personal (`~/.agents/plugins/marketplace.json`). OpenAI's own `$plugin-creator` skill scaffolds a plugin and a local marketplace entry. Distinct from **ChatGPT Apps/Connectors**, which is a separate, broader ecosystem.

### Google Antigravity
Antigravity supports the open Agent Skills spec directly. The current workspace path is `.agents/skills/`, while `.agent/skills/` remains a backward-compatible alias. Global paths differ by surface: the IDE uses `~/.gemini/config/skills/`, while Antigravity CLI uses `~/.gemini/antigravity-cli/skills/`. It also supports native plugins that bundle skills, rules, MCP servers, and hooks, with corresponding workspace, IDE-global, and CLI-global plugin locations. Antigravity provides built-in customization catalogs, but its documentation does not define an open third-party marketplace manifest comparable to Claude Code or Codex.[19][20][21]

### OpenCode
OpenCode's "plugin" concept is different in kind from the others: a plugin is a **JavaScript/TypeScript module** that hooks into lifecycle events (`tool.execute.before`, `chat.message`, `session.idle`, etc.) or registers custom tools/auth providers — it is a code-extension mechanism, not a skill-bundling format. Skills are supported separately via the Agent Skills spec. There is no official OpenCode marketplace; the ecosystem relies on community sites (opencode.cafe) and unofficial CLIs.

### Cursor
Cursor introduced plugins and a curated marketplace in **February 2026**. A plugin bundles skills, rules (`.mdc` files), subagents, MCP servers, and hooks under `.cursor-plugin/plugin.json`; multi-plugin repos add `.cursor-plugin/marketplace.json`. Unlike Claude Code and Codex, **every Cursor Marketplace plugin is manually reviewed by the Cursor team before listing** — there's no fully open self-publish flow for the official marketplace (team/enterprise "private marketplaces" are also available).

### Gemini CLI
Gemini CLI's unit of distribution is the **Extension** — an older, broader concept (predates the Agent Skills rollout) that can bundle MCP server configs, `GEMINI.md` context, custom slash commands, and, since ~early 2026, skills. There is no `marketplace.json` equivalent: a Git repo installs as **one** extension from its root (`gemini extensions install <url>`). The **Extensions Gallery** (geminicli.com/extensions) functions as a discovery surface but isn't a plugin-manifest-based marketplace the way Claude Code, Codex, Cursor, or Copilot have. A GitHub issue on the `google-gemini/gemini-cli` repo explicitly requests a Claude-Code-style plugin/marketplace system, confirming this gap is known and unresolved as of this report.

### GitHub Copilot
Copilot's stack closely mirrors Claude Code's: skills (Dec 2025) → plugins → marketplaces, added as three interlocking features. A plugin manifest (`plugin.json`) can declare `agents/`, `skills/`, `hooks.json`, `.mcp.json`, and `lsp.json`. Marketplaces are `marketplace.json` files placed at `.github/plugin/` (Copilot CLI also reads the `.claude-plugin/` location as a legacy shim, easing cross-listing). Install via `copilot plugin marketplace add owner/repo` then `copilot plugin install plugin@marketplace`, or declaratively via `enabledPlugins` in settings. Enterprise admins can push organization-wide "plugin standards."

### Cross-tool: Open Agent Skills CLI (`npx skills`, Vercel)
Not a harness itself — a **distribution tool** that installs bare `SKILL.md` skills into 70+ agent tools' conventional skill directories (Claude Code, Codex, Cursor, Antigravity, OpenCode, Gemini CLI, and many more), without any plugin bundling (no MCP, no hooks). It discovers skills via known container paths (`skills/`, `.claude/skills/`, etc.) and falls back to a full recursive repository scan if nothing is found in those locations — useful for repos (like `ballerina-library`) that nest skills under a non-standard folder.

---

## Similarities Across Harnesses

1. **Shared foundation — the open Agent Skills spec.** Every harness above reads the same artifact: a folder with a `SKILL.md` containing YAML frontmatter (`name`, `description`) plus markdown instructions and optional scripts/references. This is what makes cross-tool distribution (`npx skills add`) possible at all.
2. **Convergent three-layer plugin architecture.** Claude Code, Codex, Antigravity, Cursor, and Copilot have all converged on essentially the same shape: **skill** (workflow/instructions) + **MCP server** (tool access) + optional **hooks/agents/commands/rules**, bundled under a `plugin.json`-style manifest.
3. **`marketplace.json` as the recurring distribution primitive.** Claude Code, Codex, Cursor, and Copilot all use a `marketplace.json` file (in slightly different paths: `.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `.github/plugin/`) listing one or more plugins by name and source path — different vendors, nearly identical idea.
4. **Consistent CLI/slash-command install pattern.** `<tool> plugin marketplace add <repo>` → `<tool> plugin install <name>@<marketplace>` (or the equivalent `/plugin` slash commands) shows up nearly verbatim across Claude Code, Codex, and Copilot.
5. **Marketplace support still differs.** Antigravity now has plugin bundles and built-in customization catalogs but no documented open third-party marketplace manifest; Gemini CLI uses Extensions, and OpenCode's plugin is a JS/TS lifecycle extension rather than a skill bundle.
6. **Versioning/update mechanics are inconsistent and mostly manual by default.** Where auto-update exists (Claude Code, Codex, Copilot), it's typically opt-in per user/marketplace rather than forced — teams wanting guaranteed currency generally still need an explicit update step or centrally managed settings.

---

## References

[1] Anthropic, "Create and distribute a plugin marketplace," *Claude Code Docs*. Available: https://code.claude.com/docs/en/plugin-marketplaces

[2] OpenAI, "Codex Skills," *OpenAI Developers*. Available: https://developers.openai.com/codex/skills

[3] OpenAI, "Codex Plugins," *OpenAI Developers*. Available: https://developers.openai.com/codex/plugins

[4] OpenAI, "Build plugins," *ChatGPT Learn*. Available: https://developers.openai.com/codex/plugins/build/

[5] Vercel, "skills — The open agent skills tool," *GitHub repository*. Available: https://github.com/vercel-labs/skills

[6] "Plugin Architecture," *DeepWiki — guanyang/antigravity-skills*. Available: https://deepwiki.com/guanyang/antigravity-skills/9.3-plugin-architecture

[7] "Plugins," *OpenCode Docs*. Available: https://opencode.ai/docs/plugins/

[8] Cursor, "Plugins," *Cursor Docs*. Available: https://cursor.com/docs/plugins

[9] Cursor, "Plugins Reference," *Cursor Docs*. Available: https://cursor.com/docs/reference/plugins

[10] Cursor, "Extend Cursor with plugins," *Cursor Blog*. Available: https://cursor.com/blog/marketplace

[11] Google, "Agent Skills," *Gemini CLI Docs*. Available: https://geminicli.com/docs/cli/skills/

[12] "Add Plugin/Extension System with Marketplace (similar to Claude Code)," *GitHub Issue, google-gemini/gemini-cli #17426*. Available: https://github.com/google-gemini/gemini-cli/issues/17426

[13] Google, "Getting Started with Gemini CLI Extensions," *Google Codelabs*. Available: https://codelabs.developers.google.com/getting-started-gemini-cli-extensions

[14] GitHub, "About agent skills," *GitHub Docs*. Available: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills

[15] GitHub, "About GitHub Copilot plugins," *GitHub Docs*. Available: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins

[16] GitHub, "Creating a plugin marketplace for GitHub Copilot CLI," *GitHub Docs*. Available: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace

[17] "Agent Skills, Plugins and Marketplace: The Complete Guide," *CodeBytes*. Available: https://chris-ayers.com/posts/agent-skills-plugins-marketplace/

[18] "Agent Skills Overview," *Agent Skills*. Available: https://agentskills.io/home

[19] Google, "Agent Skills," *Antigravity Documentation*. Available: https://antigravity.google/docs/skills

[20] Google, "Plugins," *Antigravity Documentation*. Available: https://antigravity.google/docs/plugins

[21] Google, "Plugins & skills," *Antigravity CLI Documentation*. Available: https://antigravity.google/docs/cli-plugins
