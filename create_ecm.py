import create_common as common

GENUS_KEY = "ECM"

# ECM sub-types supported here. Flare launchers (ecmtype=0) are deliberately
# excluded: flares require an ammo item (ammoid > 0), and this tree focuses
# on the digital, ammo-free devices. If flares are added later, reinstate a
# flare branch that scans Items/ for genuscode=7 (ECMAMMO).
ECM_EMP = 1
ECM_REPROGRAMMER = 2

# Manual: techlevel 0-100. Higher defeats higher-tech missiles.
MAX_TECHLEVEL = 100

# Manual: ecmradiussquared 0-1000. Standard 36 (6^2) = visible screen.
MAX_RADIUS_SQUARED = 1000.0

# Manual: sfx 0-93.
MAX_SFX = 93

# Manual: energydrainperuse is very high for EMP (several thousand),
# lower for reprogrammers.
MAX_ENERGYDRAIN = 5000


def _prompt_ecm_type():
    """Pick the ECM sub-type (EMP or Reprogrammer). Returns 1 or 2, or None."""
    while True:
        print()
        print("=" * 50)
        print(" ECM sub-type")
        print("=" * 50)
        print("  [1] EMP device    - destroys nearby missiles, huge energy drain")
        print("  [2] Reprogrammer  - redirects missiles, lower energy drain")
        print("=" * 50)
        print("  Type the number to select, or 'cancel' to go back.")
        print("=" * 50)
        raw = input("Select an ECM sub-type: ").strip()
        if raw.lower() == common.CANCEL_WORD:
            print("Cancelled.")
            return None
        if raw == "1":
            return ECM_EMP
        if raw == "2":
            return ECM_REPROGRAMMER
        print(f"Invalid option: {raw!r}. Please choose 1-2.")


def _prompt_emp_fields():
    """EMP: high energy drain, radius-based, no ammo."""
    print()
    print(" EMP device: destroys nearby missiles with an EM pulse.")
    print(" Energy drain is very high (typically 512-2000); radius default 36.")
    energydrain = common.prompt_int(
        f"  Energy drain per use (integer, 0-{MAX_ENERGYDRAIN}, e.g. 512): ",
        min_value=0,
        max_value=MAX_ENERGYDRAIN,
    )
    if energydrain is None:
        return None

    radius = common.prompt_float(
        f"  Radius squared (0-{MAX_RADIUS_SQUARED:.0f}, standard 36 = visible screen): ",
        min_value=0.0,
        max_value=MAX_RADIUS_SQUARED,
    )
    if radius is None:
        return None

    return {
        "ecmtype": str(ECM_EMP),
        "energydrainperuse": str(energydrain),
        "ammoid": "0",
        "ecmradiussquared": f"{radius:.6f}",
    }


def _prompt_reprogrammer_fields():
    """Reprogrammer: lower energy drain, radius-based, no ammo."""
    print()
    print(" Reprogrammer: redirects missiles to the user's primary target.")
    print(" Energy drain is lower than EMP (typically a few hundred); radius 36.")
    energydrain = common.prompt_int(
        f"  Energy drain per use (integer, 0-{MAX_ENERGYDRAIN}, e.g. 100): ",
        min_value=0,
        max_value=MAX_ENERGYDRAIN,
    )
    if energydrain is None:
        return None

    radius = common.prompt_float(
        f"  Radius squared (0-{MAX_RADIUS_SQUARED:.0f}, standard 36 = visible screen): ",
        min_value=0.0,
        max_value=MAX_RADIUS_SQUARED,
    )
    if radius is None:
        return None

    return {
        "ecmtype": str(ECM_REPROGRAMMER),
        "energydrainperuse": str(energydrain),
        "ammoid": "0",
        "ecmradiussquared": f"{radius:.6f}",
    }


def create(game_path, genus_key, genus_code, next_id):
    """
    ECM tree (genuscode=13), EMP and Reprogrammer only.

    ECM-specific fields (from the Technical Manual and the base-game sample
    ROCKEMP):
      ecmtype           : int, 1=EMP, 2=reprogrammer. (0=flare excluded here.)
      ecmradiussquared  : float 0-1000, squared radius of effect. Standard 36
                          (6^2) = about the visible screen.
      techlevel         : int 0-100. Higher defeats higher-tech missiles.
      ammoid            : int, always 0 for EMP/reprogrammer (no ammo used).
      triggersfxnumber  : int 0-93, sound effect. 84=flare, 85=EMP typical.
      energydrainperuse : int. Very high for EMP (several thousand), lower
                          for reprogrammers.

    Flare launchers (ecmtype=0) are not offered. They require an ammo item
    (ammoid > 0), and this tree focuses on the ammo-free digital devices.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    ecm_type = _prompt_ecm_type()
    if ecm_type is None:
        return False

    if ecm_type == ECM_EMP:
        subtype_fields = _prompt_emp_fields()
    else:
        subtype_fields = _prompt_reprogrammer_fields()

    if subtype_fields is None:
        print("Cancelled.")
        return False

    print()
    print(" Common ECM fields")

    techlevel = common.prompt_int(
        f"  Tech level (integer, 0-{MAX_TECHLEVEL}, e.g. 1 = basic): ",
        min_value=0,
        max_value=MAX_TECHLEVEL,
    )
    if techlevel is None:
        print("Cancelled.")
        return False

    sfx = common.prompt_int(
        f"  Trigger sound effect (integer, 0-{MAX_SFX}, e.g. 85 = EMP): ",
        min_value=0,
        max_value=MAX_SFX,
    )
    if sfx is None:
        print("Cancelled.")
        return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = dict(subtype_fields)
    genus_fields["techlevel"] = str(techlevel)
    genus_fields["triggersfxnumber"] = str(sfx)
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "ECM", genus_key, genus_code, next_id, shared, genus_fields
    )