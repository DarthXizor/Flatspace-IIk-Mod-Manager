import create_common as common

GENUS_KEY = "MISSILE"

MAX_TECHLEVEL = 100
MAX_MISSILEAGILITY = 2048.0
MAX_NUCLEARDAMAGE = 1_000_000.0


def _prompt_agility():
    """
    Missile agility. The manual specifies typical values:
      512  = poor
      1024 = medium
      1536 = good
      2048 = very agile
    Accepts any float in [0, MAX_MISSILEAGILITY].
    """
    print()
    print(" Missile agility (higher = tighter turning circle)")
    print("  Typical values: 512 (poor), 1024 (medium), 1536 (good), 2048 (max)")
    return common.prompt_float(
        f"  Missile agility (0-{MAX_MISSILEAGILITY:.0f}, e.g. 1024): ",
        min_value=0.0,
        max_value=MAX_MISSILEAGILITY,
    )


def create(game_path, genus_key, genus_code, next_id):
    """
    Missile tree (genuscode=8).

    Missiles share the shared fields (name, description, mass, cost,
    on-sale probabilities) and the two boolgenerate* flags with other
    equipment, but their stat fields differ from WEAPON:
      - no firingrate, no totalrange, no ammoid
      - no startsfxnumber / stopsfxnumber / firesfxnumber
      - instead: techlevel, missileagility, warhead, nucleardamage,
                 launchsfxnumber
      - shotvel is signed (-1.0..1.0), typical 0.1
      - lifetime is typically 1000 for missiles
      - terminationexplosion should be true for all missiles

    Effect fields (muzzlefairy, shotfairy, glowfairy, emitters,
    muzzlealphavel, launchsfxnumber) are NOT prompted; they come from
    Templates/Missile.txt, which carries the Tiger Missile's visuals.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Missile-specific fields")

    damage = common.prompt_int(
        f"  Damage per hit (integer, 0-{common.MAX_DAMAGE}, e.g. 150): ",
        min_value=0,
        max_value=common.MAX_DAMAGE,
    )
    if damage is None:
        print("Cancelled.")
        return False

    lifetime = common.prompt_int(
        f"  Lifetime in frames (integer, 1-{common.MAX_LIFETIME}, missiles typically 1000): ",
        min_value=1,
        max_value=common.MAX_LIFETIME,
    )
    if lifetime is None:
        print("Cancelled.")
        return False

    shotvel = common.prompt_signed_float(
        "  Shot velocity (-1.0 to 1.0, missiles typically 0.1): ",
        min_value=-1.0,
        max_value=1.0,
    )
    if shotvel is None:
        print("Cancelled.")
        return False

    agility = _prompt_agility()
    if agility is None:
        print("Cancelled.")
        return False

    techlevel = common.prompt_int(
        f"  Tech level (integer, 0-{MAX_TECHLEVEL}, e.g. 1): ",
        min_value=0,
        max_value=MAX_TECHLEVEL,
    )
    if techlevel is None:
        print("Cancelled.")
        return False

    stundamage = common.prompt_bool("  Stun damage instead of lethal?", default=False)
    if stundamage is None:
        print("Cancelled.")
        return False

    nuclear = common.prompt_bool(
        "  Nuclear warhead? (kills target + splash damage)", default=False
    )
    if nuclear is None:
        print("Cancelled.")
        return False

    if nuclear:
        nucleardamage = common.prompt_float(
            f"  Nuclear splash damage (0-{MAX_NUCLEARDAMAGE:.0f}, e.g. 50000): ",
            min_value=0.0,
            max_value=MAX_NUCLEARDAMAGE,
        )
        if nucleardamage is None:
            print("Cancelled.")
            return False
        warhead = 1
    else:
        warhead = 0
        nucleardamage = 0.0

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "damage": str(damage),
        "lifetime": str(lifetime),
        "shotvel": f"{shotvel:.6f}",
        "missileagility": f"{agility:.6f}",
        "techlevel": str(techlevel),
        "stundamage": "true" if stundamage else "false",
        "warhead": str(warhead),
        "nucleardamage": f"{nucleardamage:.6f}",
        "terminationexplosion": "true",
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Missile", genus_key, genus_code, next_id, shared, genus_fields
    )