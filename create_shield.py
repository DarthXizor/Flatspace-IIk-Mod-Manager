import create_common as common

GENUS_KEY = "SHIELD"

# Manual: maxshield can range from 1 to 10000. Tetron shields start at 100
# and grow by 100 with each upgrade.
MAXSHIELD_MIN = 1
MAXSHIELD_MAX = 10000

# Manual: energydrainperuse is 1 for almost all shield units. A generous
# upper bound allows unusual designs without risking overflow.
MAX_ENERGYDRAIN = 1000


def create(game_path, genus_key, genus_code, next_id):
    """
    Shield tree (genuscode=12).

    Shield-specific fields (from the Technical Manual and the base-game
    sample TETRONSHIELD):
      maxshield         : int 1-10000, maximum shield value in armour/damage
                          units. Manual examples: 50 (Warhawk), 100+ (Tetron,
                          growing by 100 per upgrade).
      energydrainperuse : int, energy used as the shield recharges. The
                          manual says this is 1 for almost all shield units,
                          so the prompt defaults to 1 but allows tuning.

    No rechargerate field for shields — the manual describes shield recharge
    purely in terms of energydrainperuse, and the sample confirms it's absent.

    boolgenerateforplayer defaults to false for shields: the manual says only
    generators, thrusters and hyperdrives should set this true; all other
    equipment is chosen from profession-based starting lists.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Shield-specific fields")

    maxshield = common.prompt_int(
        f"  Max shield value (integer, {MAXSHIELD_MIN}-{MAXSHIELD_MAX}, "
        f"e.g. 50 = Warhawk, 100+ = Tetron): ",
        min_value=MAXSHIELD_MIN,
        max_value=MAXSHIELD_MAX,
    )
    if maxshield is None:
        print("Cancelled.")
        return False

    energydrain = common.prompt_int(
        "  Energy drain per recharge (integer, typically 1 for shields): ",
        min_value=0,
        max_value=MAX_ENERGYDRAIN,
    )
    if energydrain is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "maxshield": str(maxshield),
        "energydrainperuse": str(energydrain),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Shield", genus_key, genus_code, next_id, shared, genus_fields
    )