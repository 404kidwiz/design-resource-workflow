# Design Resource Workflow

A portable Agent Skill that helps coding assistants choose from [40 design resources](references/catalog.md), turn a reference into a project-specific brief, implement only the required components, and verify the result. Based on [this X post](https://x.com/himanshubuildss/status/2107877395348996471), with categorization and safeguards added here. The catalog contains links, not scraped content or 40 globally installed packages.

## Install (macOS / Linux)

Requires Git and Python 3.9+. Review `install.py` before running it.

```sh
git clone https://github.com/404kidwiz/design-resource-workflow.git "$HOME/.local/share/design-resource-workflow"
python3 "$HOME/.local/share/design-resource-workflow/install.py" --dry-run
python3 "$HOME/.local/share/design-resource-workflow/install.py"
python3 "$HOME/.local/share/design-resource-workflow/install.py" --verify
```

The installer links this checkout into global Agent Skill folders for Hermes, Codex, Claude Code, Cursor, Gemini CLI/Antigravity, OpenCode, OpenClaude, Grok, ZCode, and the shared `~/.agents/skills` and `~/.skills` directories. It creates directories when absent, never overwrites an unrelated skill, and can be rerun. **A link resolving is not proof an application loaded the skill**; restart the relevant CLI/IDE and ask it to use `design-resource-workflow` to check runtime discovery. Antigravity uses Gemini's global skill directory on the tested Mac; other versions may differ. Tools without Agent Skill support can still read `SKILL.md` directly.

For one tool only:

```sh
python3 install.py --tools codex --dry-run
python3 install.py --tools codex
python3 install.py --tools codex --verify
```

`python3 install.py --help` lists options. `--mode copy` makes managed copies when symlinks are unavailable; rerun after each update. `--home PATH` targets another home directory and is used for tests. If a target already holds a different `design-resource-workflow`, the installer stops at that target and leaves it untouched.

## Install (Windows PowerShell)

Requires Git and Python 3.9+ (`py -3`). Auto mode uses managed copies because symlink creation may require additional privileges.

```powershell
git clone https://github.com/404kidwiz/design-resource-workflow.git "$env:LOCALAPPDATA\design-resource-workflow"
py -3 "$env:LOCALAPPDATA\design-resource-workflow\install.py" --dry-run
py -3 "$env:LOCALAPPDATA\design-resource-workflow\install.py"
py -3 "$env:LOCALAPPDATA\design-resource-workflow\install.py" --verify
```

Windows tool support and paths vary by version; the installer verifies files at the listed paths, not that each installed application discovers them. Use `--tools` to target your actual clients. This repo does not install any CLI or IDE.

## Update or refine

Edit `SKILL.md` for behavior and `references/catalog.md` for links. On another machine:

```sh
git -C "$HOME/.local/share/design-resource-workflow" pull --ff-only
python3 "$HOME/.local/share/design-resource-workflow/install.py"
python3 "$HOME/.local/share/design-resource-workflow/install.py" --verify
```

Symlink installs see edits immediately; managed copies need a rerun. Re-run the tests before publishing refinements: `python3 -m unittest discover -s tests -v`. Run the changed tool's native skill listing or a bounded read-only prompt to check runtime discovery.

## Boundaries

- 36 of the 40 sites answered an automated HEAD request in the initial check. Four returned HTTP 403 to automation; this does not establish browser availability. Check live access and licensing when selecting a resource.
- Components, Anime.js, Three.js and similar libraries belong **only in a chosen project**, under its lockfile, after reviewing compatibility, accessibility and license. Hosted builders and paid prompt packs require their own accounts and terms.
- 21st.dev's optional MCP needs account authentication; this installer does not handle tokens, change MCP configuration or claim to repair disconnected clients. Configure MCP separately from [21st.dev's official page](https://21st.dev/mcp) if needed; never commit credentials.
- `--verify` checks the skill files at each path. It cannot guarantee runtime loading inside every CLI/IDE or authenticate an external service.

[MIT license](LICENSE).
