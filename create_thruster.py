import create_common as common

GENUS_KEY = "THRUSTER"

# v1.04 update raised the max thrust power from 1.0 to 10.0, specifically
# so modders could push capital ships at speeds comparable to smaller craft.
MAX_THRUST = 10.0

# Manual: thrust sound effect numbers range 0-93.
MAX_SFX = 93

# Manual: standard thrust fairies are 332-339.
THRUST_FAIRY_MIN = 332
THRUST_FAIRY_MAX = 339

# Manual: emitters 25-28 are designed for thrusters.
THRUST_EMITTER_MIN = 25
THRUST_EMITTER_MAX = 28


def create(game_path, genus_key, genus_code, next_id):
    """
    Thruster tree (genuscode=10).

    Thruster-specific fields (from the Technical Manual and base-game sample
    IDIOMTHRUSTER):
      thrust            : float, power of the thruster. Manual examples:
                          0.04 (smallest), 0.08 (2t VL Series), 0.144 (10t
                          Idiom), 0.224 (20t Idiom). v1.04 raised the
                          editable cap from 1.0 to 10.0 to allow heavy
                          capital ships to be moved at reasonable speed.
      energydrainperuse : int, energy per pulse. Typically 1 for thrusters.
      thrustsfxnumber   : int 0-93, thrust burn sound effect.
      thrustfairy       : int, engine glow sprite. Standard set is 332-339.
      thrustemitter     : int, particle effect. 25-28 are for thrusters.

    NOTE on mass vs thrust:
      The manual does NOT document a runtime formula linking thruster mass
      to ship acceleration. Ship mass matters in-game (heavier ships need
      higher thrust to move at the same speed; the v1.04 cap raise was
      specifically for capital ships), but the exact maths is unpublished.
      The stock thrusters loosely follow "roughly 0.008 more thrust per
      additional ton of thruster mass" — a design pattern, not an engine
      rule. We prompt for both values independently.

    Effect fields (thrustsfxnumber, thrustfairy, thrustemitter) are
    prompted because all thrusters share the same valid ranges — unlike
    weapon sub-types, there is no per-style template choice. The defaults
    in Templates/Thruster.txt are the TL-1 style, which the user can
    override to match any existing thruster's look.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Thruster-specific fields")

    thrust = common.prompt_float(
        f"  Thrust power (0.01-{MAX_THRUST:.1f}, e.g. 0.04 = smallest, 0.144 = 10t Idiom): ",
        min_value=0.01,
        max_value=MAX_THRUST,
    )
    if thrust is None:
        print("Cancelled.")
        return False

    energydrain = common.prompt_int(
        "  Energy drain per pulse (integer, 0-1000, typically 1 for thrusters): ",
        min_value=0,
        max_value=1000,
    )
    if energydrain is None:
        print("Cancelled.")
        return False

    print()
    print(" Effect fields (copy values from an existing thruster with the")
    print(" effect you want, or use the defaults for the TL-1 style).")

    sfx = common.prompt_int(
        f"  Thrust sound effect (integer, 0-{MAX_SFX}, e.g. 39-42 for thrusters): ",
        min_value=0,
        max_value=MAX_SFX,
    )
    if sfx is None:
        print("Cancelled.")
        return False

    fairy = common.prompt_int(
        f"  Thrust glow fairy (integer, {THRUST_FAIRY_MIN}-{THRUST_FAIRY_MAX} for standard thrusters): ",
        min_value=THRUST_FAIRY_MIN,
        max_value=THRUST_FAIRY_MAX,
    )
    if fairy is None:
        print("Cancelled.")
        return False

    emitter = common.prompt_int(
        f"  Thrust emitter (integer, {THRUST_EMITTER_MIN}-{THRUST_EMITTER_MAX} designed for thrusters): ",
        min_value=THRUST_EMITTER_MIN,
        max_value=THRUST_EMITTER_MAX,
    )
    if emitter is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "thrust": f"{thrust:.6f}",
        "energydrainperuse": str(energydrain),
        "thrustsfxnumber": str(sfx),
        "thrustfairy": str(fairy),
        "thrustemitter": str(emitter),
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Thruster", genus_key, genus_code, next_id, shared, genus_fields
    )