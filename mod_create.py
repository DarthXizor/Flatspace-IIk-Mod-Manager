import importlib

from mod_remove_specific import scan_mods, MOD_ID_THRESHOLD

# ---------------------------------------------------------------------------
# IMPORTANT: FILE FORMAT NOTES (see also create_common.py)
# ---------------------------------------------------------------------------
# Flatspace IIk data files are Windows-native. All writes MUST be:
#   1. CRLF line endings (\r\n), not LF.
#   2. No UTF-8 BOM.
#   3. text= tag formatted as `text=[ITEM <NAME>]` (brackets, all caps,
#      no spaces inside the name portion).
# Violating any of these causes "Error: text not found in Items\<file>.txt"
# or the game refusing to load the modified data files.
#
# Genus codes (from the Technical Manual):
#   1=CARGO, 2=PACKAGE (unused here), 3=ARMOUR, 4=WEAPON, 5=TURRETWEAPON,
#   6=WEAPONAMMO, 7=ECMAMMO (removed from the menu), 8=MISSILE,
#   9=HYPERDRIVE, 10=THRUSTER, 11=GENERATOR, 12=SHIELD, 13=ECM, 14=HOOVER,
#   15=SCANNER, 16=RADAR, 17=ESCAPEPOD, 18=ROBOT, 19=USELESS (removed).
#
# Numeric ranges and per-genus field differences are documented in
# create_common.py and in each create_<genus>.py module.
#
# To add a new genus:
#   1. Create create_<name>.py exposing GENUS_KEY and create().
#   2. Add a Templates/<Name>.txt.
#   3. Add the entry to MOD_TYPES below. The dispatcher finds it by GENUS_KEY.
# ---------------------------------------------------------------------------


MOD_TYPES = (
    ("Cargo",           "CARGO",        1),
    ("Armour",          "ARMOUR",       3),
    ("Weapon",          "WEAPON",       4),
    ("Turret Weapon",   "TURRETWEAPON", 5),
    ("Weapon Ammo",     "WEAPONAMMO",   6),
    ("Missile",         "MISSILE",      8),
    ("Hyperdrive",      "HYPERDRIVE",   9),
    ("Thruster",        "THRUSTER",     10),
    ("Generator",       "GENERATOR",    11),
    ("Shield",          "SHIELD",       12),
    ("ECM",             "ECM",          13),
    ("Hoover",          "HOOVER",       14),
    ("Scanner",         "SCANNER",      15),
    ("Radar",           "RADAR",        16),
    ("Escape Pod",      "ESCAPEPOD",    17),
    ("Robot",           "ROBOT",        18),
)

CANCEL_WORD = "cancel"


def _get_next_id(game_path):
    mods = scan_mods(game_path)
    if not mods:
        return MOD_ID_THRESHOLD
    return max(m["id"] for m in mods) + 1


def _prompt_mod_type():
    while True:
        print()
        print("=" * 50)
        print(" What type of mod do you want to make?")
        print("=" * 50)
        for i, (label, key, code) in enumerate(MOD_TYPES, 1):
            print(f"  [{i:>2}] for {label}")
        print("=" * 50)
        print("  Type the number to select, or 'cancel' to go back.")
        print("=" * 50)
        raw = input("Select a type: ").strip()
        if raw.lower() == CANCEL_WORD:
            print("Cancelled.")
            return None, None
        if not raw.isdigit():
            print(f"Invalid option: {raw!r}. Please enter a number 1-{len(MOD_TYPES)}.")
            continue
        idx = int(raw)
        if 1 <= idx <= len(MOD_TYPES):
            label, key, code = MOD_TYPES[idx - 1]
            return key, code
        print(f"Invalid option: {raw!r}. Please enter a number 1-{len(MOD_TYPES)}.")


def _load_genus_module(genus_key):
    """
    Import create_<lowercase_key> if it exists and exposes matching GENUS_KEY.
    Returns the module, or None if no module is available yet.

    Only ModuleNotFoundError (the module genuinely not existing) is treated
    as 'not implemented'. Any other ImportError — e.g. a missing helper in
    create_common.py, or a broken import inside create_<name>.py — is
    re-raised so the real cause is visible.
    """
    module_name = f"create_{genus_key.lower()}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None
    if getattr(module, "GENUS_KEY", None) != genus_key:
        return None
    if not hasattr(module, "create"):
        return None
    return module


def create_mod_flow(game_path):
    print(f"\n[Create Mod] Scanning for existing mods in: {game_path}")

    mods = scan_mods(game_path)
    if mods:
        highest = max(m["id"] for m in mods)
        print(f"Found {len(mods)} existing mod(s); highest mod ID is {highest}.")
    else:
        print("No existing mods found.")

    next_id = _get_next_id(game_path)
    print(f"Next available mod ID: {next_id}")

    genus_key, genus_code = _prompt_mod_type()

    if genus_key is None:
        print("Mod creation cancelled.")
    else:
        module = _load_genus_module(genus_key)
        if module is None:
            print()
            print(f"Creation tree for GENUS_{genus_key} (genuscode={genus_code}) not yet implemented.")
        else:
            module.create(game_path, genus_key, genus_code, next_id)

    while True:
        print()
        print("=" * 50)
        print(" Create Mod")
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