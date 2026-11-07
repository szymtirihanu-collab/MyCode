# MyCode

A lightweight terminal AI coding assistant for **iSH Shell on iPhone** and Alpine Linux, powered by NVIDIA NIM's OpenAI-compatible API.

## Goals

- Python standard library only (no Node.js, Docker, native extensions, or background server).
- Configure, test, replace, or delete your NVIDIA API key locally.
- Browse models exposed by the configured NIM endpoint and select a model by ID.
- Stream chat responses in the terminal.
- Attach local source files as context for coding help.
- Keep credentials out of the repository.

## Requirements

- Python 3.9+
- Network access from iSH
- An NVIDIA NIM API key

## Run

```sh
python3 mycode.py
```

On first launch, MyCode asks for your NVIDIA API key using a hidden password prompt. The key is stored in:

```
~/.config/mycode/config.json
```

MyCode attempts to restrict this file to owner-only access (mode `0600`). It is not stored in the project directory.

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

Type a normal message to chat. Attached files are read locally and included in the next requests; do not attach secrets, private keys, or other sensitive files.

## Default API

- Base URL: `https://integrate.api.nvidia.com/v1`
- Default model: `qwen/qwen2.5-coder-32b-instruct`

You can override the base URL with `/base URL` during a session. The default NVIDIA endpoint is recommended.

## Security notes

- Never paste your API key into chat messages, source files, screenshots, or GitHub.
- Do not commit `config.json`; it is stored outside the repository and ignored if copied into the project.
- Attached file contents are sent to the selected API provider as part of your prompt.
- MyCode does not execute shell commands or modify project files automatically. It provides coding assistance and file context; review generated code before using it.

## Current status

MyCode v0.1 is the initial terminal-chat foundation: local key management, model discovery, connection testing, streaming responses, settings, and file context. More advanced project-editing and approval-based tools can be added in later versions.
