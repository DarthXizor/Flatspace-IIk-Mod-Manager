import create_common as common

GENUS_KEY = "TURRETWEAPON"


def create(game_path, genus_key, genus_code, next_id):
    """
    Turret weapon tree.

    Turrets are structurally identical to energy weapons (genuscode=5 vs 4):
    no ammo, drain the generator per shot. The only material difference in
    the item file is the genuscode, which the dispatcher passes in via
    genus_code. The template (Templates/TurretWeapon.txt) carries the
    turret's native effect fields, mirroring the energy-weapon template.

    Per the Technical Manual, TURRETWEAPON has the same fields as WEAPON:
      damage, firingrate, totalrange, lifetime, stundamage, shotvel,
      energydrainperuse, plus all the effect fields (muzzle/shot fairies,
      emitters, sfx numbers) which the template supplies.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    stats = common.prompt_common_weapon_stats()
    if stats is None:
        return False

    print()
    print(" Turret-weapon fields")
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
        game_path, "TurretWeapon", genus_key, genus_code, next_id, shared, genus_fields
    )