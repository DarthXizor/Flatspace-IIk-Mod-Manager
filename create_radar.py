import create_common as common

GENUS_KEY = "RADAR"

# Manual: radarrange is a float from > 0 to 100. "Zero itself isn't
# permitted." Smallest stock radar = 10 units; largest = 46 units.
RADARRANGE_MIN = 0.1
RADARRANGE_MAX = 100.0

# Manual: blipsfxnumber 0-93. Standard is 43 (the blip/ping sound).
MAX_SFX = 93


def create(game_path, genus_key, genus_code, next_id):
    """
    Radar tree (genuscode=16).

    Radar-specific fields (from the Technical Manual and the base-game
    sample T1RADAR):
      radarrange    : float, detection range in units. Must be > 0.
                      Manual: smallest radar = 10, largest = 46. The visible
                      screen is about 6 units, so 10 is already well beyond
                      what the player can see.
      blipsfxnumber : int 0-93, the "ping" sound when a blip appears.
                      Manual: "currently 43 for all radars" — 43 is the
                      standard, and 0 would make it silent.

    No other genus-specific fields. Radar has no energy drain field in the
    base-game sample (unlike scanners), so energydrainperuse is not present
    and not prompted.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Radar-specific fields")

    print("  Range reference: visible screen ~6 units; smallest radar 10;")
    print("  largest radar 46. Range above ~46 has diminishing practical value.")
    radarrange = common.prompt_float(
        f"  Radar range (> 0, up to {RADARRANGE_MAX:.0f}, e.g. 10 = smallest): ",
        min_value=RADARRANGE_MIN,
        max_value=RADARRANGE_MAX,
    )
    if radarrange is None:
        print("Cancelled.")
        return False

    print()
    print(" Blip sound effect (the 'ping' when a ship is detected).")
    print("  43 is the standard for all radars; 0 makes it silent.")
    sfx = common.prompt_int(
        f"  Blip sound effect (integer, 0-{MAX_SFX}, default 43): ",
        min_value=0,
        max_value=MAX_SFX,
    )
    if sfx is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "radarrange": f"{radarrange:.6f}",
        "blipsfxnumber": str(sfx),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Radar", genus_key, genus_code, next_id, shared, genus_fields
    )