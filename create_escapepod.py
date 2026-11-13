import create_common as common

GENUS_KEY = "ESCAPEPOD"

# Manual: escapepodhullid values used by stock pods are 200, 201, 202 — the
# three hulls that the game treats as usable escape craft. The manual notes
# that theoretically any hull could be an escape pod, but "it would really
# be no fun to 'escape' into an asteroid, Battlestation or Starcity", so we
# restrict to the three known-safe hulls and allow the user to pick.
VALID_HULL_IDS = (200, 201, 202)

# Manual: escapeprobability is a percentage; existing pods are ~99.
ESCAPEPROB_MIN = 0
ESCAPEPROB_MAX = 100


def _prompt_hull_id():
    """
    Pick one of the three stock escape-pod hull IDs.
    """
    print()
    print("=" * 50)
    print(" Escape pod hull")
    print("=" * 50)
    print("  [1] Hull 200 - Genie Escape Pod")
    print("  [2] Hull 201 - (Xanadu or similar; second stock hull)")
    print("  [3] Hull 202 - Wolf Escape Pod")
    print("=" * 50)
    print("  Type the number to select, or 'cancel' to go back.")
    print("=" * 50)
    while True:
        raw = input("Select a hull: ").strip()
        if raw.lower() == common.CANCEL_WORD:
            print("Cancelled.")
            return None
        if raw == "1":
            return 200
        if raw == "2":
            return 201
        if raw == "3":
            return 202
        print(f"Invalid option: {raw!r}. Please choose 1-3.")


def create(game_path, genus_key, genus_code, next_id):
    """
    Escape pod tree (genuscode=17).

    Escape-pod-specific fields (from the Technical Manual and the base-game
    sample WOLFESCAPEPOD):
      escapepodhullid    : int, one of the three stock escape-pod hulls
                           (200, 201, 202). The manual warns that non-escape
                           hulls are theoretically possible but "would
                           really be no fun", so we restrict to the three
                           known-safe values.
      escapeprobability  : int 0-100, percentage chance of a successful
                           ejection when the parent ship is destroyed.
                           Stock pods use ~99.

    No energy drain, no ammo. Escape pods fire once when the ship dies; there
    is no runtime economy attached to them beyond their purchase cost.

    boolgenerateforplayer defaults to false: escape pods are not in the
    "starting equipment" category (only generators, thrusters and hyperdrives
    use that flag per the manual).
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    hull_id = _prompt_hull_id()
    if hull_id is None:
        return False

    print()
    print(" Escape probability (chance of a successful ejection)")
    print("  Stock pods use ~99. Lower values make ejection riskier.")
    probability = common.prompt_int(
        f"  Escape probability (integer, {ESCAPEPROB_MIN}-{ESCAPEPROB_MAX}, e.g. 99): ",
        min_value=ESCAPEPROB_MIN,
        max_value=ESCAPEPROB_MAX,
    )
    if probability is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "escapepodhullid": str(hull_id),
        "escapeprobability": str(probability),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "EscapePod", genus_key, genus_code, next_id, shared, genus_fields
    )