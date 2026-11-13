import create_common as common

GENUS_KEY = "HYPERDRIVE"

# Manual: hyperjumpforce range is 0 to 50000.
MAX_HYPERJUMPFORCE = 50000.0

# Manual: default recharge is 1750 frames (35 s at 50 fps). Lower = faster.
# The manual doesn't state a hard upper bound; 10000 is a practical cap.
MAX_HYPERDRIVECHARGE = 10000


def _prompt_hyperjumpforce():
    """
    Prompt for hyperjumpforce. The manual's formula is:
        max jump range (light years) = hyperjumpforce / vessel mass * 100
    We show the range at two reference masses so the user can judge the
    drive's effectiveness without doing the maths themselves.
    """
    print()
    print(" Hyperjump force (drive power)")
    print(" Jump range = hyperjumpforce / ship mass * 100 light years")
    print(" Reference: 320 = smallest Gray Hyperdrive; higher = longer range.")
    while True:
        value = common.prompt_float(
            f"  Hyperjump force (0-{MAX_HYPERJUMPFORCE:.0f}, e.g. 640): ",
            min_value=0.0,
            max_value=MAX_HYPERJUMPFORCE,
        )
        if value is None:
            return None
        # Show what this force yields at two common masses as a sanity hint.
        range_20t = value / 20.0 * 100.0
        range_40t = value / 40.0 * 100.0
        print(f"    At 20t: {range_20t:.1f} light years")
        print(f"    At 40t: {range_40t:.1f} light years")
        confirm = common.prompt_bool("  Use this value?", default=True)
        if confirm is None:
            return None
        if confirm:
            return value


def create(game_path, genus_key, genus_code, next_id):
    """
    Hyperdrive tree (genuscode=9).

    Fields from the Technical Manual and the base-game sample HYPERDRIVE1:
      hyperjumpforce    : float, 0-50000. Determines max jump range via
                          hyperjumpforce / vessel mass * 100.
      hyperdriverecharge: int, default 1750 frames (35 s at 50 fps).
                          Scales linearly with jump distance; lower = faster.
      energydrainperuse : int, currently 0 for all hyperdrives. Not prompted.
      boolgenerateforplayer defaults to true for hyperdrives, since they are
                          eligible as starting equipment (per the manual).
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    force = _prompt_hyperjumpforce()
    if force is None:
        print("Cancelled.")
        return False

    print()
    print(" Recharge time")
    print(f"  Default is 1750 frames (35 s at 50 fps). Lower = faster.")
    recharge = common.prompt_int(
        f"  Recharge time in frames (1-{MAX_HYPERDRIVECHARGE}, e.g. 1750): ",
        min_value=1,
        max_value=MAX_HYPERDRIVECHARGE,
    )
    if recharge is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "hyperjumpforce": f"{force:.6f}",
        "hyperdriverecharge": str(recharge),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Hyperdrive", genus_key, genus_code, next_id, shared, genus_fields
    )