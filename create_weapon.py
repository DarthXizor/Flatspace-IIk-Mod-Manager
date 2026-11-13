import os

import create_common as common

GENUS_KEY = "WEAPON"
GENUS_WEAPONAMMO = 6


def _read_item_field(item_file_path, field_name):
    try:
        with open(item_file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            for line in f:
                line = line.rstrip("\r\n")
                if line.lower().startswith(field_name.lower() + "="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        return None
    return None


def _scan_ammo_items(game_path):
    items_dir = os.path.join(game_path, common.ITEMS_FOLDER)
    if not os.path.isdir(items_dir):
        return []

    ammo = []
    for entry in os.listdir(items_dir):
        if not entry.lower().endswith(".txt"):
            continue
        file_path = os.path.join(items_dir, entry)
        if not os.path.isfile(file_path):
            continue

        genus_raw = _read_item_field(file_path, "genuscode")
        if genus_raw is None or not genus_raw.isdigit():
            continue
        if int(genus_raw) != GENUS_WEAPONAMMO:
            continue

        id_raw = _read_item_field(file_path, "id")
        if id_raw is None or not id_raw.isdigit():
            continue

        tag = _read_item_field(file_path, "text") or "(unknown tag)"
        if tag.startswith("[") and tag.endswith("]"):
            tag = tag[1:-1]

        ammo.append({
            "id": int(id_raw),
            "tag": tag,
            "name": os.path.splitext(entry)[0],
        })

    ammo.sort(key=lambda a: a["id"])
    return ammo


def _prompt_ammo_selection(game_path):
    ammo_items = _scan_ammo_items(game_path)

    if not ammo_items:
        print()
        print("=" * 50)
        print(" No ammo items found.")
        print("=" * 50)
        print(" You need to create custom ammo first before being able to")
        print(" select custom ammo for this weapon.")
        print("=" * 50)
        return None

    while True:
        print()
        print("=" * 50)
        print(" Ammo selection")
        print("=" * 50)
        print(" Note: You need to create custom ammo first before being able")
        print(" to select custom ammo for this weapon.")
        print("=" * 50)
        for i, ammo in enumerate(ammo_items, 1):
            print(f"  [{i:>2}] {ammo['tag']}  (id={ammo['id']}, {ammo['name']})")
        print("=" * 50)
        print("  Type the number to select, or 'cancel' to go back.")
        print("=" * 50)

        raw = input("Select ammo: ").strip()
        if raw.lower() == common.CANCEL_WORD:
            print("Cancelled.")
            return None

        if not raw.isdigit():
            print(f"Invalid option: {raw!r}. Please enter a number 1-{len(ammo_items)}.")
            continue

        idx = int(raw)
        if 1 <= idx <= len(ammo_items):
            selected = ammo_items[idx - 1]
            print(f"Selected ammo: {selected['tag']} (id={selected['id']})")
            return selected["id"]

        print(f"Invalid option: {raw!r}. Please enter a number 1-{len(ammo_items)}.")


def _prompt_subtype():
    while True:
        print()
        print("=" * 50)
        print(" Weapon sub-type")
        print("=" * 50)
        print("  [1] Slug   - projectile weapon, consumes ammo")
        print("  [2] Energy - beam/plasma weapon, drains generator")
        print("=" * 50)
        print("  Type the number to select, or 'cancel' to go back.")
        print("=" * 50)
        raw = input("Select a sub-type: ").strip()
        if raw.lower() == common.CANCEL_WORD:
            print("Cancelled.")
            return None
        if raw == "1":
            return "slug"
        if raw == "2":
            return "energy"
        print(f"Invalid option: {raw!r}. Please choose 1-2.")


def _slug_tree(game_path, genus_key, genus_code, next_id):
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    stats = common.prompt_common_weapon_stats()
    if stats is None:
        return False

    print()
    print(" Slug-weapon fields")
    maxammo = common.prompt_int(
        f"  Max ammo (0 = infinite, else 1-{common.MAX_MAXAMMO}, e.g. 100): ",
        min_value=0,
        max_value=common.MAX_MAXAMMO,
    )
    if maxammo is None:
        print("Cancelled.")
        return False

    ammoid = _prompt_ammo_selection(game_path)
    if ammoid is None:
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "damage": str(stats["damage"]),
        "firingrate": str(stats["firingrate"]),
        "totalrange": f"{stats['totalrange']:.6f}",
        "lifetime": str(stats["lifetime"]),
        "shotvel": f"{stats['shotvel']:.6f}",
        "stundamage": "true" if stats["stundamage"] else "false",
        "maxammo": str(maxammo),
        "ammoid": str(ammoid),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "WeaponSlug", genus_key, genus_code, next_id, shared, genus_fields
    )


def _energy_tree(game_path, genus_key, genus_code, next_id):
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    stats = common.prompt_common_weapon_stats()
    if stats is None:
        return False

    print()
    print(" Energy-weapon fields")
    energydrain = common.prompt_int(
        f"  Energy drain per use (integer, 0-{common.MAX_ENERGYDRAIN}, e.g. 100): ",
        min_value=0,
        max_value=common.MAX_ENERGYDRAIN,
    )
    if energydrain is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "damage": str(stats["damage"]),
        "firingrate": str(stats["firingrate"]),
        "totalrange": f"{stats['totalrange']:.6f}",
        "lifetime": str(stats["lifetime"]),
        "shotvel": f"{stats['shotvel']:.6f}",
        "stundamage": "true" if stats["stundamage"] else "false",
        "energydrainperuse": str(energydrain),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "WeaponEnergy", genus_key, genus_code, next_id, shared, genus_fields
    )


def create(game_path, genus_key, genus_code, next_id):
    subtype = _prompt_subtype()
    if subtype is None:
        return False
    if subtype == "slug":
        return _slug_tree(game_path, genus_key, genus_code, next_id)
    return _energy_tree(game_path, genus_key, genus_code, next_id)