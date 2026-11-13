import os
import re

from mod_remove_specific import scan_mods

ITEMS_DATA_FOLDER = "Data"
ITEMS_DATA_FILES = ("Items0.txt", "Items1.txt")
END_MARKER = "** END **"


def _parse_items_file(path):
    """
    Parse an Items0.txt / Items1.txt file into a dict:
        { TAGNAME: {'name': str, 'description': str} }

    Only the region before the ** END ** marker is parsed.
    """
    entries = {}
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return entries

    current_tag = None
    current_lines = []

    def flush():
        if current_tag is None:
            return
        content = [ln.rstrip("\r\n") for ln in current_lines]
        while content and not content[0].strip():
            content.pop(0)
        name = content[0].strip() if content else ""
        description_lines = content[1:] if len(content) > 1 else []
        while description_lines and not description_lines[0].strip():
            description_lines.pop(0)
        description = " ".join(ln.strip() for ln in description_lines if ln.strip())
        entries[current_tag] = {"name": name, "description": description}

    for line in lines:
        stripped = line.strip()
        if stripped == END_MARKER:
            break
        if stripped.startswith("[") and stripped.endswith("]"):
            flush()
            current_tag = stripped[1:-1]
            current_lines = []
        else:
            if current_tag is not None:
                current_lines.append(line)
    flush()

    return entries


def _load_item_entries(game_path):
    merged = {}
    for fname in ITEMS_DATA_FILES:
        path = os.path.join(game_path, ITEMS_DATA_FOLDER, fname)
        entries = _parse_items_file(path)
        for tag, data in entries.items():
            if tag in merged:
                if not merged[tag]["description"] and data["description"]:
                    merged[tag]["description"] = data["description"]
                if not merged[tag]["name"] and data["name"]:
                    merged[tag]["name"] = data["name"]
            else:
                merged[tag] = data
    return merged


def _wrap(text, width=70, indent="      "):
    if not text:
        return indent + "(no description)"
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if not current:
            current = w
        elif len(current) + 1 + len(w) <= width:
            current += " " + w
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return "\n".join(indent + ln for ln in lines)


def list_mods_flow(game_path):
    mods = scan_mods(game_path)
    entries = _load_item_entries(game_path)

    print()
    print("=" * 50)
    if mods:
        print(f" Mods installed: {len(mods)}")
        print("=" * 50)
        for m in mods:
            entry = entries.get(m["tag"], {})
            item_name = entry.get("name") or "(not found in Items*.txt)"
            description = entry.get("description") or ""
            print()
            print(f"  ID:         {m['id']}")
            print(f"  File Name:  {m['name']}")
            print(f"  Item Name:  {item_name}")
            print(f"  Description:")
            print(_wrap(description))
            print("  " + "-" * 46)
    else:
        print(" Mods installed: 0")
        print("=" * 50)
        print(" No mods found or mods have ID's lower than 5000.")
    print("=" * 50)

    while True:
        print()
        print("=" * 50)
        print(" List Mods - Complete")
        print("=" * 50)
        print("  [1] Return to Main Menu")
        print("  [2] Exit Program")
        print("=" * 50)
        choice = input("Select an option: ").strip()

        if choice == "1":
            return
        elif choice == "2":
            print("Exiting.")
            raise SystemExit(0)
        else:
            print(f"Invalid option: {choice!r}. Please choose 1-2.")