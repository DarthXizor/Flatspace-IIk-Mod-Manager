
import os
import re

from mod_remove_specific import (
    _read_data_raw,
    _split_lines,
    _join_lines,
    _write_data_raw,
    _detect_terminator,
)

# ---------------------------------------------------------------------------
# Shared helpers for every genus creation tree.
#
# File-format notes and genus codes live in mod_create.py (the dispatcher).
# This module provides prompt primitives, the byte-safe Items*.txt writer,
# and the shared mod writer that every genus calls at the end.
#
# Numeric caps are re-declared here so genus modules can import them without
# circular deps on mod_create.py.
# ---------------------------------------------------------------------------

MAX_MASS = 1_000_000
MAX_COST = 2_000_000_000
MAX_ARMOURPOINTS = 10000
MAX_DAMAGE = 1_000_000
MAX_FIRINGRATE = 1000
MAX_TOTALRANGE = 1_000_000.0
MAX_LIFETIME = 100_000
MAX_MAXAMMO = 1_000_000
MAX_AMMOID = 2_000_000_000
MAX_ENERGYDRAIN = 1_000_000

CANCEL_WORD = "cancel"
END_MARKER = "** END **"

ITEMS_FOLDER = "Items"
DATA_FOLDER = "Data"
ITEMS_DATA_FILES = ("Items0.txt", "Items1.txt")

# Script-relative Templates/ directory (used by every genus module).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "Templates")


# ---------------------------------------------------------------- prompts


def prompt_text(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if raw.lower() == CANCEL_WORD:
            return None
        if raw or allow_blank:
            return raw
        print("Input cannot be blank. Type 'cancel' to abort.")


def prompt_int(prompt, min_value=0, max_value=None):
    while True:
        raw = input(prompt).strip()
        if raw.lower() == CANCEL_WORD:
            return None
        if not raw.isdigit():
            print(f"Invalid input {raw!r}; must be a non-negative integer.")
            continue
        value = int(raw)
        if value < min_value:
            print(f"Value must be >= {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be <= {max_value}.")
            continue
        return value


def prompt_float(prompt, min_value=0.0, max_value=None):
    pattern = re.compile(r"^\d+(\.\d+)?$")
    while True:
        raw = input(prompt).strip()
        if raw.lower() == CANCEL_WORD:
            return None
        if not pattern.match(raw):
            print(f"Invalid input {raw!r}; must be a non-negative number (e.g. 10.5).")
            continue
        value = float(raw)
        if value < min_value:
            print(f"Value must be >= {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be <= {max_value}.")
            continue
        return value


def prompt_signed_float(prompt, min_value=-1.0, max_value=1.0):
    pattern = re.compile(r"^-?\d+(\.\d+)?$")
    while True:
        raw = input(prompt).strip()
        if raw.lower() == CANCEL_WORD:
            return None
        if not pattern.match(raw):
            print(f"Invalid input {raw!r}; must be a number (e.g. 0.2 or -0.1).")
            continue
        value = float(raw)
        if value < min_value:
            print(f"Value must be >= {min_value}.")
            continue
        if value > max_value:
            print(f"Value must be <= {max_value}.")
            continue
        return value


def prompt_bool(prompt, default=False):
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        raw = input(f"{prompt} {suffix}: ").strip().lower()
        if raw == CANCEL_WORD:
            return None
        if raw == "":
            return default
        if raw in ("y", "yes", "true", "1"):
            return True
        if raw in ("n", "no", "false", "0"):
            return False
        print(f"Invalid input {raw!r}; enter y or n (or 'cancel').")


def prompt_shared_fields(genus_key):
    """
    Name, description, mass, cost, three on-sale probabilities.
    Returns dict of raw values, or None on cancel.
    """
    print()
    print("=" * 50)
    print(f" Create {genus_key.capitalize()} - Step 2: Item details")
    print("=" * 50)

    display_name = prompt_text("Item name (shown in-game): ")
    if display_name is None:
        print("Cancelled.")
        return None

    description = prompt_text("Item description: ")
    if description is None:
        print("Cancelled.")
        return None

    mass = prompt_int(
        f"Mass (integer, 0-{MAX_MASS}, e.g. 1): ",
        min_value=0,
        max_value=MAX_MASS,
    )
    if mass is None:
        print("Cancelled.")
        return None

    cost = prompt_int(
        f"Cost (integer, 0-{MAX_COST}, e.g. 100): ",
        min_value=0,
        max_value=MAX_COST,
    )
    if cost is None:
        print("Cancelled.")
        return None

    print()
    print(" On-sale probabilities (0-100). Higher = more common.")
    print(" Set 0 to make the item unavailable at that station type.")
    base_prob = prompt_int("  Standard station probability: ", min_value=0, max_value=100)
    if base_prob is None:
        print("Cancelled.")
        return None

    police_prob = prompt_int("  Police station probability:   ", min_value=0, max_value=100)
    if police_prob is None:
        print("Cancelled.")
        return None

    pirate_prob = prompt_int("  Pirate station probability:   ", min_value=0, max_value=100)
    if pirate_prob is None:
        print("Cancelled.")
        return None

    return {
        "display_name": display_name,
        "description": description,
        "mass": mass,
        "cost": cost,
        "base_prob": base_prob,
        "police_prob": police_prob,
        "pirate_prob": pirate_prob,
    }


def prompt_generate_flags():
    """
    The two boolgenerate* flags used by armour and weapons.
    Returns dict of string values ('true'/'false'), or None on cancel.
    """
    generate_for_ai = prompt_bool("  Generate for AI ships?", default=True)
    if generate_for_ai is None:
        print("Cancelled.")
        return None

    generate_for_player = prompt_bool(
        "  Generate for player starting ships?", default=False
    )
    if generate_for_player is None:
        print("Cancelled.")
        return None

    return {
        "boolgenerateforai": "true" if generate_for_ai else "false",
        "boolgenerateforplayer": "true" if generate_for_player else "false",
    }


def prompt_common_weapon_stats():
    """
    Weapon stats shared by slug and energy sub-types.
    Returns dict, or None on cancel.
    """
    print()
    print(" Weapon-specific fields")

    damage = prompt_int(
        f"  Damage per hit (integer, 0-{MAX_DAMAGE}, e.g. 10): ",
        min_value=0,
        max_value=MAX_DAMAGE,
    )
    if damage is None:
        print("Cancelled.")
        return None

    firingrate = prompt_int(
        f"  Firing rate (integer, 1-{MAX_FIRINGRATE}, lower is faster): ",
        min_value=1,
        max_value=MAX_FIRINGRATE,
    )
    if firingrate is None:
        print("Cancelled.")
        return None

    totalrange = prompt_float(
        f"  Total range (positive, up to {MAX_TOTALRANGE}, e.g. 10.0): ",
        min_value=0.01,
        max_value=MAX_TOTALRANGE,
    )
    if totalrange is None:
        print("Cancelled.")
        return None

    lifetime = prompt_int(
        f"  Projectile lifetime (integer, 1-{MAX_LIFETIME}, e.g. 50): ",
        min_value=1,
        max_value=MAX_LIFETIME,
    )
    if lifetime is None:
        print("Cancelled.")
        return None

    shotvel = prompt_signed_float(
        "  Shot velocity (-1.0 to 1.0, e.g. 0.2): ",
        min_value=-1.0,
        max_value=1.0,
    )
    if shotvel is None:
        print("Cancelled.")
        return None

    stundamage = prompt_bool("  Stun damage instead of lethal?", default=False)
    if stundamage is None:
        print("Cancelled.")
        return None

    return {
        "damage": damage,
        "firingrate": firingrate,
        "totalrange": totalrange,
        "lifetime": lifetime,
        "shotvel": shotvel,
        "stundamage": stundamage,
    }


# ---------------------------------------------------------------- tag/filename


def build_mod_tag(item_name):
    normalised = "".join(item_name.split()).upper()
    return f"ITEM {normalised}"


def build_mod_filename(item_name, item_id):
    token = "".join(ch for ch in item_name if ch.isalnum())
    return f"{token}{item_id}.txt"


# ---------------------------------------------------------------- templates


def template_path(template_name):
    return os.path.join(TEMPLATES_DIR, f"{template_name}.txt")


def read_template(template_name):
    path = template_path(template_name)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Template not found: {path}\n"
            f"(Templates folder should be next to the mod manager: {TEMPLATES_DIR})"
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_item_file(template_text, replacements):
    out_lines = []
    for line in template_text.splitlines():
        key = line.split("=", 1)[0].strip() if "=" in line else None
        if key in replacements:
            out_lines.append(f"{key}={replacements[key]}")
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n"


# ---------------------------------------------------------------- data files


def existing_data_tags(game_path):
    tags = set()
    for fname in ITEMS_DATA_FILES:
        path = os.path.join(game_path, DATA_FOLDER, fname)
        try:
            has_bom, body = _read_data_raw(path)
        except OSError:
            continue
        entries = _split_lines(body)
        marker = END_MARKER.encode("utf-8")
        for line_body, _ in entries:
            if line_body.strip() == marker:
                break
            s = line_body.strip()
            if s.startswith(b"[") and s.endswith(b"]"):
                tags.add(s[1:-1].decode("utf-8", errors="replace"))
    return tags


def append_item_entry(game_path, tag_name, display_name, description):
    for fname in ITEMS_DATA_FILES:
        path = os.path.join(game_path, DATA_FOLDER, fname)
        try:
            has_bom, body = _read_data_raw(path)
        except OSError:
            continue

        entries = _split_lines(body)
        term = _detect_terminator(body)

        marker = END_MARKER.encode("utf-8")
        end_index = len(entries)
        for i, (line_body, _) in enumerate(entries):
            if line_body.strip() == marker:
                end_index = i
                break

        block_lines = [
            f"[{tag_name}]",
            display_name,
            description,
            "",
        ]
        new_entries = [(line.encode("utf-8"), term) for line in block_lines]

        combined = entries[:end_index] + new_entries + entries[end_index:]
        new_body = _join_lines(combined)

        try:
            _write_data_raw(path, has_bom, new_body)
        except OSError as e:
            print(f"Failed to update {fname}: {e}")
            raise


# ---------------------------------------------------------------- mod writer


def write_mod(game_path, template_name, genus_key, genus_code, next_id, shared, genus_fields):
    """
    Shared final step for every genus:
      - collision checks
      - render template, write CRLF, no BOM
      - append display block to Items0/Items1
    """
    display_name = shared["display_name"]
    tag_name = build_mod_tag(display_name)
    bracketed_tag = f"[{tag_name}]"
    filename = build_mod_filename(display_name, next_id)

    items_dir = os.path.join(game_path, ITEMS_FOLDER)
    target_path = os.path.join(items_dir, filename)

    if os.path.exists(target_path):
        print(f"\nA file named {filename} already exists in Items/.")
        print("Delete or rename it before creating a mod with the same name.")
        return False

    existing = existing_data_tags(game_path)
    if tag_name in existing:
        print(f"\nThe tag [{tag_name}] already exists in Data/Items0.txt or Data/Items1.txt.")
        print("That usually means a previous mod with this name was partially created.")
        print("Run 'Remove Specific Mod' or clean the data files manually, then try again.")
        return False

    try:
        template_text = read_template(template_name)
    except FileNotFoundError as e:
        print(e)
        return False

    replacements = {
        "text": bracketed_tag,
        "id": str(next_id),
        "genuscode": str(genus_code),
        "mass": str(shared["mass"]),
        "cost": str(shared["cost"]),
        "onsaleinbaseprobability": str(shared["base_prob"]),
        "onsaleinpolicebaseprobability": str(shared["police_prob"]),
        "onsaleinpiratebaseprobability": str(shared["pirate_prob"]),
    }
    replacements.update(genus_fields)

    content = render_item_file(template_text, replacements)

    print()
    print("=" * 50)
    print(" About to write:")
    print("=" * 50)
    print(f"  File:          Items/{filename}")
    print(f"  Template:      Templates/{template_name}.txt")
    print(f"  Tag:           {bracketed_tag}")
    print(f"  In-game name:  {display_name}")
    print(f"  ID:            {next_id}")
    print(f"  Genus:         {genus_key} (genuscode={genus_code})")
    print(f"  Mass:          {shared['mass']}")
    print(f"  Cost:          {shared['cost']}")
    print(f"  On sale:")
    print(f"    Standard:    {shared['base_prob']}%")
    print(f"    Police:      {shared['police_prob']}%")
    print(f"    Pirate:      {shared['pirate_prob']}%")
    for key, value in genus_fields.items():
        print(f"  {key + ':':<22} {value}")
    print(f"  Data:          insert block BEFORE ** END ** (line endings preserved)")
    print("=" * 50)
    confirm = input("Proceed? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return False

    crlf_content = content.replace("\n", "\r\n")
    try:
        with open(target_path, "wb") as f:
            f.write(crlf_content.encode("ascii", errors="replace"))
    except OSError as e:
        print(f"Failed to write {target_path}: {e}")
        return False

    try:
        append_item_entry(game_path, tag_name, display_name, shared["description"])
    except OSError as e:
        print(f"Item file written, but failed to update Items data files: {e}")
        return False

    print()
    print(f"Created {filename} and updated Data/Items0.txt, Data/Items1.txt.")
    print(f"  Tag written:   {bracketed_tag}")
    print(f"  Display name:  {display_name}")
    return True