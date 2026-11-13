import create_common as common

GENUS_KEY = "SCANNER"

# Manual: energydrainperuse for scanners is per use; examples around 10-20.
MAX_ENERGYDRAIN = 1000

# Manual: sfx 0-93. Existing scanner sounds are 44-47.
MAX_SFX = 93


def _prompt_scanner_abilities():
    """
    Prompt for the six boolean ability flags. Each corresponds to a
    specific in-game scanner capability. Returns a dict of 'true'/'false'
    strings, or None on cancel.
    """
    print()
    print(" Scanner abilities (each adds a specific function)")
    print("  Pilot name            - identify the target's pilot")
    print("  Kill bounty           - return the pilot's dead-or-alive bounty")
    print("  Capture bounty        - return the pilot's alive-only bounty")
    print("  Cargo                 - return cargo type on scanned vessel")
    print("  Imports/exports       - return trading classes of stations")
    print("  Hyperspace tracking   - track a target on the hypermap")

    pilot_name = common.prompt_bool(
        "  Identify pilot name?", default=False
    )
    if pilot_name is None:
        return None

    bounty_dead = common.prompt_bool(
        "  Return kill bounty (dead-or-alive)?", default=False
    )
    if bounty_dead is None:
        return None

    bounty_alive = common.prompt_bool(
        "  Return capture bounty (alive only)?", default=False
    )
    if bounty_alive is None:
        return None

    cargo = common.prompt_bool(
        "  Scan cargo?", default=False
    )
    if cargo is None:
        return None

    imports_exports = common.prompt_bool(
        "  Scan station imports/exports?", default=False
    )
    if imports_exports is None:
        return None

    hyper_tracking = common.prompt_bool(
        "  Hyperspace tracking?", default=False
    )
    if hyper_tracking is None:
        return None

    return {
        "boolscannerpilotname": "true" if pilot_name else "false",
        "boolscannerpilotbountydead": "true" if bounty_dead else "false",
        "boolscannerpilotbountyalive": "true" if bounty_alive else "false",
        "boolscannercargo": "true" if cargo else "false",
        "boolscannerimportsexports": "true" if imports_exports else "false",
        "boolscannerhyperspacetracking": "true" if hyper_tracking else "false",
    }


def create(game_path, genus_key, genus_code, next_id):
    """
    Scanner tree (genuscode=15).

    Scanner-specific fields (from the Technical Manual and the base-game
    sample POLICESCANNER):
      energydrainperuse             : int, per-use energy. Manual: 10-20 typical.
      scansfxnumber                 : int 0-93. Manual: existing scanner sfx 44-47.
      boolscannerpilotname          : identify target's pilot.
      boolscannerpilotbountydead    : return kill bounty. (Manual prose calls
                                      this boolscannerpilotbountyhead, but the
                                      file field name is ...bountydead — the
                                      game reads the file name.)
      boolscannerpilotbountyalive   : return capture bounty.
      boolscannercargo              : scan cargo on a vessel.
      boolscannerimportsexports     : scan station imports/exports.
      boolscannerhyperspacetracking : track a target on the hypermap.

    Different stock scanners enable different combinations of these six
    flags. For example, POLICESCANNER enables pilotname + both bounties;
    BQ404SCANNER adds hyperspace tracking; ULTRASCANNER enables all six.

    The scanner sound effect (scansfxnumber) is NOT prompted — the template
    carries 44 (basic ID scanner) by default. If per-scanner sfx tuning is
    wanted later, add a prompt for it. For now the default is a valid,
    non-descript scanner sound.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Scanner-specific fields")

    energydrain = common.prompt_int(
        f"  Energy drain per use (integer, 0-{MAX_ENERGYDRAIN}, e.g. 10-20): ",
        min_value=0,
        max_value=MAX_ENERGYDRAIN,
    )
    if energydrain is None:
        print("Cancelled.")
        return False

    abilities = _prompt_scanner_abilities()
    if abilities is None:
        print("Cancelled.")
        return False

    # Sanity: a scanner with no abilities does nothing useful.
    if all(v == "false" for v in abilities.values()):
        print()
        print("  Warning: no scanner abilities were enabled. The scanner")
        print("  will do nothing when used. Continue anyway?")
        if not common.prompt_bool("  Continue?", default=False):
            print("Cancelled.")
            return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "energydrainperuse": str(energydrain),
    }
    genus_fields.update(abilities)
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Scanner", genus_key, genus_code, next_id, shared, genus_fields
    )