# MyCode

**MyCode** is an OpenCode-inspired terminal coding agent for desktop Linux **x86_64 / AMD64**, powered by NVIDIA NIM's OpenAI-compatible API.

It targets Ubuntu, Debian, Linux Mint, Fedora, Arch and openSUSE. It is not an iPhone/iSH app.

## Requirements

- Linux x86_64 / AMD64
- Python 3.9+
- Network access
- NVIDIA NIM API key
- A terminal emulator

The current implementation uses Python's standard library. No Node.js, Docker, Rust, native compilation or separate server is required.

## Install

```sh
git clone https://github.com/szymtirihanu-collab/MyCode.git
cd MyCode
chmod +x mycode.py
./mycode.py
```

To open a specific project directory:

```sh
./mycode.py ~/Projects/my-project
```

If Python is missing:

- Ubuntu / Debian / Linux Mint: `sudo apt install python3`
- Fedora: `sudo dnf install python3`
- Arch: `sudo pacman -S python`
- openSUSE: `sudo zypper install python3`

On first launch, MyCode asks for the NVIDIA API key with hidden input. It stores the key outside the repository at `~/.config/mycode/config.json` and attempts to restrict permissions to owner-only (`0700` directory, `0600` file).

## Agent capabilities

The TUI uses a dark, centered landing screen and provides an interactive chat loop with NVIDIA NIM tool calling.

The agent can:
- List files and directories inside the selected workspace.
- Read project files and use their contents as context.
- Create or replace project files after showing an approval prompt.
- Run shell commands in the selected project directory after showing an approval prompt.
- Read a file outside the workspace only after a separate approval.
- Write outside the workspace only after a separate approval.

**Permissions are intentionally approval-gated.** MyCode does not silently get unrestricted access to the whole computer. Every file write and shell command requires confirmation. External file access also requires confirmation. Review each command and file path before approving it. Do not approve commands or changes you do not understand.

The agent's file and command tools depend on model/API support for OpenAI-compatible tool calling. If the selected model does not support tools, ordinary chat may work while agent actions do not.

## Commands

| Command | Action |
|---|---|
| `/help` | Show commands |
| `/new` | Start a new conversation |
| `/key` | Replace the local API key |
| `/test` | Test the API and list models |
| `/models` | List models exposed by the endpoint |
| `/model MODEL_ID` | Select a model |
| `/temperature 0.2` | Set temperature (0–2) |
| `/max 4096` | Set maximum output tokens |
| `/workspace PATH` | Switch project directory |
| `@path/to/file` | Include a project file in the prompt |
| `/exit` | Exit MyCode |

## NVIDIA NIM

- Base URL: `https://integrate.api.nvidia.com/v1`
- Default model: `deepseek-ai/deepseek-v4.1-flash`

Use `/models` to list models, or `/model MODEL_ID` to enter a model ID manually.

## Security

- Never paste your API key into chat messages, source files, screenshots or GitHub.
- The API key stays in the local config file and is not part of the repository.
- Project files you ask the agent to read are sent to the selected API provider.
- Do not point MyCode at directories containing private documents unless you intend to share relevant file contents with the API.
- Approval prompts are a safety boundary, not a guarantee that every shell command is harmless. Read commands before approving them.

## Status

This is an early development build. The TUI and approval-gated tools are implemented, but the project has not yet been tested against every NVIDIA NIM model or Linux distribution. Tool calling availability and behavior depend on the selected model/provider.
