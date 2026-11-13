import os
import re

ITEMS_DATA_FOLDER = "Data"
ITEMS_DATA_FILES = ("Items0.txt", "Items1.txt")
ITEMS_FOLDER = "Items"
MOD_ID_THRESHOLD = 5000
CANCEL_WORD = "cancel"
END_MARKER = "** END **"

_BOM = b"\xef\xbb\xbf"


def _read_item_id(item_file_path):
    try:
        with open(item_file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            for _ in range(5):
                line = f.readline()
                if not line:
                    break
                line = line.rstrip("\r\n")
                if line.lower().startswith("id="):
                    value = line.split("=", 1)[1].strip()
                    try:
                        return int(value)
                    except ValueError:
                        return None
    except OSError:
        return None
    return None


def _read_item_text_tag(item_file_path):
    try:
        with open(item_file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            first_line = f.readline().rstrip("\r\n")
    except OSError:
        return None
    if not first_line.lower().startswith("text="):
        return None
    match = re.match(r"text=\[([^\]]+)\]", first_line)
    return match.group(1) if match else None


# ---- byte-exact data file I/O --------------------------------------------

def _read_data_raw(path):
    """
    Read an ItemsX.txt as raw bytes. Returns (has_bom, body_bytes) where
    body_bytes excludes any BOM.
    """
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(_BOM):
        return True, raw[len(_BOM):]
    return False, raw


def _detect_terminator(body):
    """
    Determine the line terminator used by a file body.
    Prefers CRLF if any \\r\\n appears, else LF.
    """
    if b"\r\n" in body:
        return b"\r\n"
    return b"\n"


def _split_lines(body):
    """
    Split body bytes into (line_body, term) pairs.
    line_body excludes the terminator; term is b'\\r\\n', b'\\n', or b'' at EOF.
    """
    entries = []
    start = 0
    n = len(body)
    while start < n:
        nl = body.find(b"\n", start)
        if nl == -1:
            entries.append((body[start:], b""))
            start = n
        else:
            chunk = body[start:nl]
            if chunk.endswith(b"\r"):
                entries.append((chunk[:-1], b"\r\n"))
            else:
                entries.append((chunk, b"\n"))
            start = nl + 1
    return entries


def _join_lines(entries):
    return b"".join(body + term for body, term in entries)


def _write_data_raw(path, has_bom, body):
    """Write body back with or without a BOM, exactly as received."""
    with open(path, "wb") as f:
        if has_bom:
            f.write(_BOM)
        f.write(body)


def _remove_block_from_items_file(path, tag_name):
    """
    Remove the [TAGNAME] block from ItemsX.txt, only scanning before ** END **.
    Preserves BOM presence and line-ending style exactly.
    """
    try:
        has_bom, body = _read_data_raw(path)
    except OSError:
        return False

    entries = _split_lines(body)

    end_index = len(entries)
    marker = END_MARKER.encode("utf-8")
    for i, (line_body, _) in enumerate(entries):
        if line_body.strip() == marker:
            end_index = i
            break

    header_bracketed = b"[" + tag_name.encode("utf-8") + b"]"

    start = None
    end = None
    for i in range(end_index):
        line_body = entries[i][0].strip()
        if start is None:
            if line_body == header_bracketed:
                start = i
        else:
            if line_body.startswith(b"[") and line_body.endswith(b"]"):
                end = i
                break
    if start is None:
        return False
    if end is None:
        end = end_index

    new_entries = entries[:start] + entries[end:]
    new_body = _join_lines(new_entries)

    try:
        _write_data_raw(path, has_bom, new_body)
    except OSError:
        return False
    return True


def scan_mods(game_path):
    items_dir = os.path.join(game_path, ITEMS_FOLDER)
    if not os.path.isdir(items_dir):
        print(f"Items folder not found at: {items_dir}")
        return []

    mods = []
    for entry in os.listdir(items_dir):
        if not entry.lower().endswith(".txt"):
            continue
        file_path = os.path.join(items_dir, entry)
        if not os.path.isfile(file_path):
            continue

        item_id = _read_item_id(file_path)
        if item_id is None or item_id < MOD_ID_THRESHOLD:
            continue

        tag = _read_item_text_tag(file_path)
        if tag is None:
            print(f"Skipping {entry}: no valid text=[...] tag found.")
            continue

        name = os.path.splitext(entry)[0]
        mods.append({
            "id": item_id,
            "file": file_path,
            "name": name,
            "tag": tag,
        })

    mods.sort(key=lambda m: m["id"])
    return mods


def _find_mod(mods, user_input):
    raw = user_input.strip()
    if not raw:
        return None

    if raw.isdigit():
        target_id = int(raw)
        for m in mods:
            if m["id"] == target_id:
                return m

    target_name = raw.lower()
    if target_name.endswith(".txt"):
        target_name = target_name[:-4]
    for m in mods:
        if m["name"].lower() == target_name:
            return m

    return None


def delete_specific_mod(game_path, mod):
    data_files = [
        os.path.join(game_path, ITEMS_DATA_FOLDER, name)
        for name in ITEMS_DATA_FILES
    ]

    removed_from_data = False
    for data_file in data_files:
        if _remove_block_from_items_file(data_file, mod["tag"]):
            removed_from_data = True

    try:
        os.remove(mod["file"])
    except OSError as e:
        print(f"Failed to delete {os.path.basename(mod['file'])}: {e}")
        return False

    if not removed_from_data:
        print(f"Deleted {os.path.basename(mod['file'])} but no matching entry "
              f"in Items data files for [{mod['tag']}].")
        return False

    return True


def _print_mod_list(mods):
    print()
    print("=" * 50)
    print(f" Mods found: {len(mods)}")
    print("=" * 50)
    for m in mods:
        print(f"  ID: {m['id']}  Name: {m['name']}")
    print("=" * 50)


def _delete_one_mod(game_path):
    mods = scan_mods(game_path)

    if not mods:
        print("No mods found or mods have ID's lower than 5000 and must be removed manually.")
        return False

    _print_mod_list(mods)

    while True:
        raw = input(
            f"Which mod should be deleted? (ID or .txt filename, or '{CANCEL_WORD}' to cancel): "
        ).strip()

        if raw.lower() == CANCEL_WORD:
            print("Cancelled.")
            return False

        if not raw:
            print(f"Please enter an ID, filename, or '{CANCEL_WORD}'.")
            continue

        mod = _find_mod(mods, raw)
        if mod is None:
            print(f"No mod matches {raw!r}. Please enter a valid ID or filename, or '{CANCEL_WORD}'.")
            continue

        print(f"Selected: ID {mod['id']}  Name: {mod['name']}")
        confirm = input("Delete this mod? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return False

        success = delete_specific_mod(game_path, mod)
        if success:
            print(f"Mod '{mod['name']}' (ID {mod['id']}) deleted.")
        else:
            print(f"Mod '{mod['name']}' (ID {mod['id']}) could not be fully deleted; see messages above.")
        return success


def _post_action_menu(has_mods):
    while True:
        print()
        print("=" * 50)
        print(" Remove Specific Mod")
        print("=" * 50)
        if has_mods:
            print("  [1] Delete a mod")
            print("  [2] Return to Main Menu")
            print("  [3] Exit Program")
        else:
            print("  [1] Return to Main Menu")
            print("  [2] Exit Program")
        print("=" * 50)
        choice = input("Select an option: ").strip()

        if has_mods:
            if choice == "1":
                return "delete"
            elif choice == "2":
                return "menu"
            elif choice == "3":
                print("Exiting.")
                raise SystemExit(0)
            else:
                print(f"Invalid option: {choice!r}. Please choose 1-3.")
        else:
            if choice == "1":
                return "menu"
            elif choice == "2":
                print("Exiting.")
                raise SystemExit(0)
            else:
                print(f"Invalid option: {choice!r}. Please choose 1-2.")


def remove_specific_mod_flow(game_path):
    while True:
        _delete_one_mod(game_path)

        remaining_mods = scan_mods(game_path)
        action = _post_action_menu(has_mods=bool(remaining_mods))

        if action == "menu":
            return