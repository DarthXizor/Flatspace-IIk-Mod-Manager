import create_common as common

GENUS_KEY = "ARMOUR"


def create(game_path, genus_key, genus_code, next_id):
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Armour-specific fields")
    armourpoints = common.prompt_int(
        f"  Armour points (integer, 0-{common.MAX_ARMOURPOINTS}): ",
        min_value=0,
        max_value=common.MAX_ARMOURPOINTS,
    )
    if armourpoints is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {"armourpoints": str(armourpoints)}
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Armour", genus_key, genus_code, next_id, shared, genus_fields
    )