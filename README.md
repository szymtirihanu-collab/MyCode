# MyCode

**MyCode** is a native-hosted terminal AI coding assistant for standard desktop/server Linux on **x86_64 (AMD64)**, powered by NVIDIA NIM's OpenAI-compatible API.

This project targets normal Linux distributions such as Ubuntu, Debian, Linux Mint, Fedora, Arch, and openSUSE. It is not an iSH/iPhone app.

## Requirements

- Linux x86_64 / AMD64
- Python 3.9 or newer
- Network access
- An NVIDIA NIM API key

No Node.js, Docker, Rust, native compilation, or separate server is required. The current version uses Python's standard library.

## Install and run

Clone the repository and start MyCode:

```sh
git clone https://github.com/szymtirihanu-collab/MyCode.git
cd MyCode
chmod +x mycode.py
./mycode.py
```

If Python is not installed:

- Ubuntu / Debian / Linux Mint: `sudo apt install python3`
- Fedora: `sudo dnf install python3`
- Arch Linux: `sudo pacman -S python`
- openSUSE: `sudo zypper install python3`

On first launch, MyCode asks for your NVIDIA API key using a hidden password prompt. The key is stored outside the repository in:

```
~/.config/mycode/config.json
```

MyCode attempts to restrict the config directory to owner-only access (mode `0700`) and the config file to `0600`.

## Commands

| Command | Action |
|---|---|
| `/help` | Show commands |
| `/key` | Replace the API key |
| `/delete-key` | Delete the locally stored key |
| `/test` | Test the API connection |
| `/models` | Fetch available models |
| `/model MODEL_ID` | Select a model |
| `/temperature 0.2` | Set temperature (0–2) |
| `/max 4096` | Set maximum output tokens |
| `/workspace PATH` | Set the project directory |
| `/attach PATH` | Add a file to the conversation context |
| `/detach PATH` | Remove an attached file |
| `/attachments` | List attached files |
| `/clear` | Clear conversation history |
| `/exit` | Exit MyCode |

Type a normal message to chat. Attached files are read locally and included in API requests. Do not attach passwords, private keys, API tokens, or other sensitive files.

## NVIDIA NIM

- API base: `https://integrate.api.nvidia.com/v1`
- Default model: `qwen/qwen2.5-coder-32b-instruct`

Use `/models` to query models exposed by the endpoint, or `/model MODEL_ID` to enter a model ID manually.

## Security

- Never paste your API key into chat messages, source files, screenshots, or GitHub.
- The API key is stored locally outside the repository; it is never intentionally written into project files.
- Attached file contents are sent to NVIDIA NIM as part of your prompt.
- MyCode v0.1 does not execute shell commands or modify project files automatically. Review generated code before using it.

## Current status

v0.1 provides local key management, model discovery, connection testing, streaming chat, settings, and read-only file context. Approval-based file editing and terminal tools are planned for a later version.
