"""
Discord Rich Presence - presets + fully customizable, straight from your terminal.

Usage:
    pip install pypresence
    python discord_activity.py

You need a Client ID from your own Discord application
(https://discord.com/developers/applications -> New Application -> Application ID).
The NAME of that application is the title Discord shows ("Playing <name>").

Editing presets: scroll down to the PRESETS block. You can add your own presets
or change the texts. Inside texts you can use {key}, which is replaced with what
you type in. If an answer is empty, that line is left out.

Images: set "large_image" / "small_image" to the name (key) of an image you
uploaded under Rich Presence -> Art Assets in your application (or an https URL
to an image). Leave empty for no image.
"""

import json
import os
import re
import sys
import time

try:
    from pypresence import Presence
except ImportError:
    print("pypresence is not installed. Run:  pip install pypresence")
    input("Press Enter to exit...")
    sys.exit(1)

try:
    from pypresence import ActivityType
except Exception:  # older pypresence versions
    ActivityType = None

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discord_activity_config.json")


# ======================================================================
# PRESETS - edit freely or add your own
# ----------------------------------------------------------------------
# name        : name shown in the menu
# type        : "playing" | "watching" | "listening" | "competing"
# questions   : list of (key, question, default value)
# details     : top line      (may contain {key})
# state       : bottom line   (may contain {key})
# timer       : "start" = elapsed time from now, "none" = no timer
# large_image / large_text / small_image / small_text : optional
# button      : optional (label, "{key}" holding the URL); empty answer = no button
# ======================================================================
PRESETS = [
    {
        "name": "GTA VI",
        "type": "playing",
        "questions": [
            ("activity", "What are you doing?", "Exploring Vice City"),
        ],
        "details": "Playing GTA VI",
        "state": "{activity}",
        "timer": "start",
        "large_image": "",
        "large_text": "GTA VI",
        "small_image": "",
        "small_text": "",
    },
    {
        "name": "FiveM",
        "type": "playing",
        "questions": [
            ("server", "Server name", ""),
            ("role", "Your role/character (e.g. Police, Taxi, Civilian)", ""),
        ],
        "details": "Playing FiveM - {server}",
        "state": "Role: {role}",
        "timer": "start",
        "large_image": "",
        "large_text": "FiveM",
        "small_image": "",
        "small_text": "",
    },
    {
        "name": "Watching YouTube",
        "type": "watching",
        "questions": [
            ("title", "Video title", ""),
            ("channel", "Channel you're watching", ""),
            ("url", "Video link (empty = no button)", ""),
        ],
        "details": "{title}",
        "state": "Watching {channel}",
        "timer": "start",
        "large_image": "",
        "large_text": "YouTube",
        "small_image": "",
        "small_text": "",
        "button": ("Watch video", "{url}"),
    },
    {
        "name": "Watching Twitch",
        "type": "watching",
        "questions": [
            ("title", "Stream title", ""),
            ("streamer", "Streamer name", ""),
            ("url", "Stream link (empty = no button)", ""),
        ],
        "details": "{title}",
        "state": "Watching {streamer}",
        "timer": "start",
        "large_image": "",
        "large_text": "Twitch",
        "small_image": "",
        "small_text": "",
        "button": ("Watch along", "{url}"),
    },
]
# ======================================================================


def ask(prompt, default=""):
    shown = f" [{default}]" if default else ""
    value = input(f"{prompt}{shown}: ").strip()
    return value if value else default


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"(Could not save settings: {e})")


def fill(template, answers):
    """Fills in {key}. If any answer is empty, returns '' (the line is left out)."""
    if not template:
        return ""
    keys = re.findall(r"{(\w+)}", template)
    for k in keys:
        if not answers.get(k):
            return ""
    return template.format(**answers)


def activity_type_value(name):
    if ActivityType is None:
        return None
    mapping = {
        "playing": "PLAYING",
        "listening": "LISTENING",
        "watching": "WATCHING",
        "competing": "COMPETING",
    }
    attr = mapping.get(name)
    return getattr(ActivityType, attr, None) if attr else None


def build_from_preset(preset, cfg):
    print(f"\n--- Preset: {preset['name']} ---")
    saved = cfg.get("preset_answers", {}).get(preset["name"], {})
    answers = {}
    for key, question, default in preset.get("questions", []):
        answers[key] = ask(question, saved.get(key, default))
    cfg.setdefault("preset_answers", {})[preset["name"]] = answers

    data = {}
    details = fill(preset.get("details", ""), answers)
    state = fill(preset.get("state", ""), answers)
    if details:
        data["details"] = details[:128]
    if state:
        data["state"] = state[:128]

    for img in ("large", "small"):
        image = preset.get(f"{img}_image", "")
        if image:
            data[f"{img}_image"] = image
            text = preset.get(f"{img}_text", "")
            if text:
                data[f"{img}_text"] = text

    if preset.get("timer") == "start":
        data["start"] = int(time.time())

    button = preset.get("button")
    if button:
        label, url_t = button
        url = fill(url_t, answers)
        if url.startswith("http"):
            data["buttons"] = [{"label": label[:32], "url": url}]
        elif url:
            print("  -> Invalid URL (must start with https://), button skipped.")

    atype = activity_type_value(preset.get("type", "playing"))
    return data, atype


def build_custom(cfg):
    """Fill in everything yourself."""
    last = cfg.get("last", {})
    print("\n--- Custom activity (Enter = skip / keep previous value) ---")
    data = {}

    details = ask("Top line (details)", last.get("details", ""))
    state = ask("Bottom line (state)", last.get("state", ""))
    large_image = ask("Large image (key or https URL)", last.get("large_image", ""))
    large_text = ask("Large image hover text", last.get("large_text", "")) if large_image else ""
    small_image = ask("Small image (key or https URL)", last.get("small_image", ""))
    small_text = ask("Small image hover text", last.get("small_text", "")) if small_image else ""

    atype_name = ask("Type (playing / watching / listening / competing)", last.get("type", "playing")).lower()

    timer = ask("Timer? (none / elapsed / countdown)", last.get("timer", "none")).lower()
    minutes = ""
    if timer == "countdown":
        minutes = ask("Minutes remaining", last.get("minutes", "10"))

    party = ask("Party size, e.g. 2/4 (empty = none)", last.get("party", ""))

    buttons = []
    for i in (1, 2):
        label = ask(f"Button {i} label (empty = no button)", last.get(f"b{i}_label", ""))
        if not label:
            continue
        url = ask(f"Button {i} URL (https://...)", last.get(f"b{i}_url", ""))
        if url.startswith("http"):
            buttons.append({"label": label[:32], "url": url})
        else:
            print("  -> Invalid URL, button skipped.")

    cfg["last"] = {
        "details": details, "state": state,
        "large_image": large_image, "large_text": large_text,
        "small_image": small_image, "small_text": small_text,
        "type": atype_name, "timer": timer, "minutes": minutes, "party": party,
        "b1_label": buttons[0]["label"] if len(buttons) > 0 else "",
        "b1_url": buttons[0]["url"] if len(buttons) > 0 else "",
        "b2_label": buttons[1]["label"] if len(buttons) > 1 else "",
        "b2_url": buttons[1]["url"] if len(buttons) > 1 else "",
    }

    if details:
        data["details"] = details[:128]
    if state:
        data["state"] = state[:128]
    if large_image:
        data["large_image"] = large_image
        if large_text:
            data["large_text"] = large_text
    if small_image:
        data["small_image"] = small_image
        if small_text:
            data["small_text"] = small_text

    now = int(time.time())
    if timer in ("elapsed", "since-now"):
        data["start"] = now
    elif timer == "countdown":
        try:
            data["end"] = now + int(float(minutes) * 60)
        except ValueError:
            print("  -> Invalid number of minutes, timer skipped.")

    if party and "/" in party:
        try:
            cur, mx = party.split("/")
            data["party_size"] = [int(cur), int(mx)]
        except ValueError:
            print("  -> Invalid party size, skipped.")

    if buttons:
        data["buttons"] = buttons

    return data, activity_type_value(atype_name)


def send(rpc, data, atype):
    """Sends the activity; falls back if your pypresence doesn't support activity_type."""
    if atype is not None:
        try:
            rpc.update(activity_type=atype, **data)
            return
        except TypeError:
            print("(Your pypresence version has no activity_type. Update with: pip install -U pypresence)")
    rpc.update(**data)


def show_menu():
    print("\n==== Choose a preset ====")
    for i, p in enumerate(PRESETS, 1):
        print(f"  {i}. {p['name']}")
    print("  0. Custom activity (fill in everything yourself)")
    print("  c. Clear activity")
    print("  q. Quit")
    return input("Choice: ").strip().lower()


def main():
    print("=" * 50)
    print("  Discord Activity - presets + full control")
    print("=" * 50)
    print("Make sure the Discord desktop app is open.\n")

    cfg = load_config()
    client_id = ask("Client ID (Application ID)", cfg.get("client_id", ""))
    if not client_id.isdigit():
        print("A Client ID only consists of digits. See the instructions at the top of this file.")
        input("Press Enter to exit...")
        return
    cfg["client_id"] = client_id
    save_config(cfg)

    rpc = Presence(client_id)
    try:
        rpc.connect()
    except Exception as e:
        print(f"\nCould not connect to Discord: {e}")
        print("Is the Discord desktop app running? (The web version does not work.)")
        input("Press Enter to exit...")
        return
    print("Connected to Discord!")

    while True:
        choice = show_menu()

        if choice == "q":
            break
        if choice == "c":
            try:
                rpc.clear()
                print("Activity cleared.")
            except Exception as e:
                print(f"Error: {e}")
            continue

        if choice == "0":
            data, atype = build_custom(cfg)
        elif choice.isdigit() and 1 <= int(choice) <= len(PRESETS):
            data, atype = build_from_preset(PRESETS[int(choice) - 1], cfg)
        else:
            print("Invalid choice.")
            continue

        save_config(cfg)

        if not data:
            print("Nothing entered, clearing activity.")
            try:
                rpc.clear()
            except Exception as e:
                print(f"Error: {e}")
            continue

        try:
            send(rpc, data, atype)
            print("\nActivity is now live! Keep this window open to keep it active.")
        except Exception as e:
            print(f"\nError while setting activity: {e}")

    try:
        rpc.clear()
        rpc.close()
    except Exception:
        pass
    print("Stopped. See you next time!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")