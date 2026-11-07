#!/usr/bin/env python3
"""MyCode - NVIDIA NIM coding assistant for Linux x86_64 and other Python platforms."""

import getpass
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

APP_DIR = Path.home() / ".config" / "mycode"
CONFIG_PATH = APP_DIR / "config.json"
DEFAULT_BASE = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "qwen/qwen2.5-coder-32b-instruct"
SYSTEM_PROMPT = (
    "You are MyCode, a careful and practical coding assistant. "
    "Help the user understand, write, debug, and improve software. "
    "When proposing changes, show complete usable code and explain where it belongs. "
    "Never claim to have changed local files or run commands unless the user did so."
)


def read_config():
    defaults = {
        "api_key": "",
        "base_url": DEFAULT_BASE,
        "model": DEFAULT_MODEL,
        "temperature": 0.2,
        "max_tokens": 4096,
    }
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            saved = json.load(handle)
        if isinstance(saved, dict):
            defaults.update(saved)
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as exc:
        print("Config could not be read:", exc)
    return defaults


def save_config(config):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        APP_DIR.chmod(0o700)
    except OSError:
        pass
    temp_path = CONFIG_PATH.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    try:
        temp_path.chmod(0o600)
    except OSError:
        pass
    temp_path.replace(CONFIG_PATH)
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass


def request_json(url, api_key, timeout=45):
    headers = {
        "Authorization": "Bearer " + api_key,
        "Accept": "application/json",
        "User-Agent": "MyCode/0.1",
    }
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError("HTTP {}: {}".format(exc.code, detail[:1200]))
    except urllib.error.URLError as exc:
        raise RuntimeError("Network error: {}".format(exc.reason))
    except TimeoutError:
        raise RuntimeError("Request timed out.")


def stream_chat(config, messages):
    url = config["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"],
        "stream": True,
    }
    headers = {
        "Authorization": "Bearer " + config["api_key"],
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "User-Agent": "MyCode/0.1",
    }
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers=headers, method="POST"
    )
    pieces = []
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line or line.startswith(":") or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                    choices = event.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")
                    if isinstance(content, str) and content:
                        print(content, end="", flush=True)
                        pieces.append(content)
                except json.JSONDecodeError:
                    continue
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError("HTTP {}: {}".format(exc.code, detail[:1600]))
    except urllib.error.URLError as exc:
        raise RuntimeError("Network error: {}".format(exc.reason))
    except TimeoutError:
        raise RuntimeError("Request timed out.")
    print()
    return "".join(pieces)


def ensure_key(config):
    if config.get("api_key"):
        return
    print("NVIDIA NIM API key required.")
    key = getpass.getpass("Paste API key (input hidden): ").strip()
    if not key:
        print("No key entered. Add one later with /key.")
        return
    config["api_key"] = key
    save_config(config)
    print("Key saved locally.")


def show_help():
    print("""
MyCode commands
  /help                 Show this help
  /key                  Replace the locally stored NVIDIA API key
  /delete-key           Delete the locally stored API key
  /test                 Test the API connection
  /models               List models available from the API
  /model MODEL_ID       Select a model
  /temperature VALUE    Set temperature from 0 to 2
  /max TOKENS           Set maximum output tokens
  /base URL             Set API base URL
  /workspace PATH       Set the project directory
  /attach PATH          Attach a text file as coding context
  /detach PATH          Detach a file
  /attachments          List attached files
  /clear                Clear chat history and attached files
  /exit                 Exit MyCode

Send any other text to chat with the selected model.
""")


def safe_workspace_path(workspace, raw_path):
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = workspace / candidate
    candidate = candidate.resolve()
    root = workspace.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("That path is outside the selected workspace.")
    return candidate


def main():
    config = read_config()
    ensure_key(config)
    workspace = Path.cwd().resolve()
    attached = {}
    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("\n  MYCODE  /  NVIDIA NIM")
    print("  Platform: Linux / x86_64 (Python)")
    print("  Model: {}".format(config["model"]))
    print("  Workspace: {}".format(workspace))
    print("  Type /help for commands.\n")

    while True:
        try:
            user_text = input("\033[96mYou > \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not user_text:
            continue

        if user_text == "/exit":
            print("Bye.")
            break
        if user_text == "/help":
            show_help()
            continue
        if user_text == "/key":
            key = getpass.getpass("New NVIDIA API key (input hidden): ").strip()
            if key:
                config["api_key"] = key
                save_config(config)
                print("Key updated locally.")
            else:
                print("Key unchanged.")
            continue
        if user_text == "/delete-key":
            config["api_key"] = ""
            save_config(config)
            print("Stored key deleted.")
            continue
        if user_text == "/test":
            if not config.get("api_key"):
                print("Add a key first with /key.")
                continue
            try:
                data = request_json(config["base_url"].rstrip("/") + "/models", config["api_key"])
                models = data.get("data", [])
                print("Connection successful. API returned {} model(s).".format(len(models)))
            except Exception as exc:
                print("Connection failed:", exc)
            continue
        if user_text == "/models":
            if not config.get("api_key"):
                print("Add a key first with /key.")
                continue
            try:
                data = request_json(config["base_url"].rstrip("/") + "/models", config["api_key"])
                models = data.get("data", [])
                if not models:
                    print("No model list returned by this endpoint.")
                for item in models:
                    print("  " + str(item.get("id", "(unknown id)")))
            except Exception as exc:
                print("Could not fetch models:", exc)
            continue
        if user_text.startswith("/model "):
            model = user_text[7:].strip()
            if model:
                config["model"] = model
                save_config(config)
                print("Model set to " + model)
            continue
        if user_text.startswith("/temperature "):
            try:
                value = float(user_text.split(None, 1)[1])
                if not 0 <= value <= 2:
                    raise ValueError()
                config["temperature"] = value
                save_config(config)
                print("Temperature set to", value)
            except ValueError:
                print("Use a number from 0 to 2.")
            continue
        if user_text.startswith("/max "):
            try:
                value = int(user_text.split(None, 1)[1])
                if not 1 <= value <= 131072:
                    raise ValueError()
                config["max_tokens"] = value
                save_config(config)
                print("Maximum output tokens set to", value)
            except ValueError:
                print("Use a whole number from 1 to 131072.")
            continue
        if user_text.startswith("/base "):
            value = user_text[6:].strip().rstrip("/")
            if value.startswith(("https://", "http://")):
                config["base_url"] = value
                save_config(config)
                print("API base URL updated.")
            else:
                print("Base URL must start with http:// or https://.")
            continue
        if user_text.startswith("/workspace "):
            try:
                candidate = Path(user_text[11:].strip()).expanduser().resolve()
                if not candidate.is_dir():
                    print("That directory does not exist.")
                else:
                    workspace = candidate
                    attached.clear()
                    print("Workspace set to", workspace)
            except OSError as exc:
                print("Could not set workspace:", exc)
            continue
        if user_text.startswith("/attach "):
            try:
                path = safe_workspace_path(workspace, user_text[8:].strip())
                if not path.is_file():
                    print("File not found.")
                    continue
                if path.stat().st_size > 100000:
                    print("File is over 100 KB; not attaching it.")
                    continue
                content = path.read_text(encoding="utf-8", errors="replace")
                attached[str(path.relative_to(workspace))] = content
                print("Attached {} ({} characters).".format(path.name, len(content)))
            except Exception as exc:
                print("Could not attach file:", exc)
            continue
        if user_text.startswith("/detach "):
            name = user_text[8:].strip()
            if name in attached:
                del attached[name]
                print("Detached", name)
            else:
                print("That file is not attached.")
            continue
        if user_text == "/attachments":
            if attached:
                for name in attached:
                    print("  " + name)
            else:
                print("No attached files.")
            continue
        if user_text == "/clear":
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            attached.clear()
            print("Conversation and attachments cleared.")
            continue
        if user_text.startswith("/"):
            print("Unknown command. Type /help.")
            continue

        if not config.get("api_key"):
            print("No API key. Add one with /key.")
            continue

        message = user_text
        if attached:
            chunks = ["\n\n[LOCAL FILE CONTEXT - read only]"]
            for name, content in attached.items():
                chunks.append("\n--- " + name + " ---\n" + content)
            message += "\n".join(chunks)
        history.append({"role": "user", "content": message})
        print("\033[92mMyCode > \033[0m", end="", flush=True)
        try:
            answer = stream_chat(config, history)
            history.append({"role": "assistant", "content": answer})
        except Exception as exc:
            print("\nRequest failed:", exc)
            history.pop()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("MyCode stopped:", error, file=sys.stderr)
        sys.exit(1)
