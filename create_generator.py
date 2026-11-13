import create_common as common

GENUS_KEY = "GENERATOR"

# Manual: maxenergy must be positive. The smallest stock generator uses 1024;
# large generators use several thousand. Cap at 1,000,000 to prevent overflow.
MAX_MAXENERGY = 1_000_000

# Manual: rechargerate must range from 0 to 10. It's a fine balance because a
# high rate with low-drain equipment makes energy management trivial.
RECHARGERATE_MIN = 0
RECHARGERATE_MAX = 10


def create(game_path, genus_key, genus_code, next_id):
    """
    Generator tree (genuscode=11).

    Generator-specific fields (from the Technical Manual and the base-game
    sample COREGENERATOR):
      maxenergy    : int, battery capacity. Must be positive. Manual example:
                     1024 (smallest Core Generator); larger generators use
                     several thousand.
      rechargerate : int 0-10, energy gained per frame. Manual notes: 1 for
                     solar generators, up to 4 for the largest. High values
                     make energy management trivial, so keep it low.

    No energydrainperuse field: the manual does not list generators among the
    genera that use it, and the sample confirms it's absent.

    boolgenerateforplayer defaults to true for generators: the manual
    explicitly says generators (along with thrusters and hyperdrives) are
    eligible as starting equipment. boolgenerateforai defaults to true as
    with all equipment.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Generator-specific fields")

    maxenergy = common.prompt_int(
        f"  Max energy capacity (integer, 1-{MAX_MAXENERGY}, e.g. 1024 = smallest Core): ",
        min_value=1,
        max_value=MAX_MAXENERGY,
    )
    if maxenergy is None:
        print("Cancelled.")
        return False

    print()
    print(" Recharge rate (0-10, energy units gained per frame)")
    print("  Manual notes: 1 for solar generators, up to 4 for the largest.")
    print("  High values make energy management trivial, so keep it low.")
    rechargerate = common.prompt_int(
        f"  Recharge rate ({RECHARGERATE_MIN}-{RECHARGERATE_MAX}, e.g. 2 = smallest Core): ",
        min_value=RECHARGERATE_MIN,
        max_value=RECHARGERATE_MAX,
    )
    if rechargerate is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "maxenergy": str(maxenergy),
        "rechargerate": str(rechargerate),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Generator", genus_key, genus_code, next_id, shared, genus_fields
    )