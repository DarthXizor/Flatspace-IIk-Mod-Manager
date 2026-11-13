import create_common as common

GENUS_KEY = "ROBOT"


def create(game_path, genus_key, genus_code, next_id):
    """
    Robot tree (genuscode=18).

    Robot-specific fields (from the Technical Manual and the base-game
    sample SECURITYROBOT3):
      boolmaintenance : true if the robot can repair ship systems.
      boolmedical     : true if the robot can heal injured crew.
      boolsecurity    : true if the robot can act as a guard / pacify
                        unruly passengers.

    A robot can have any combination of these three abilities. Some stock
    robots have one capability (a medical robot, a security robot), some
    have more than one (the ALLROBOT "Automatic Man"/"Automatic Woman"
    are doctors, engineers, cooks, translators and security guards, so all
    three flags would be true). Some have none (pure pets).

    No energy drain, no ammo. Robots occupy a ship slot and perform their
    role passively.

    The base-game sample (Security Robot 3) has boolgenerateforai=false,
    matching the manual's general advice that robots are used by the AI as
    needed — but the template default is also false, so the user can opt in
    for AI generation if they want their custom robot on NPC ships.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Robot abilities (each adds a passive function)")
    print("  Maintenance - repairs ship systems over time")
    print("  Medical     - heals injured crew")
    print("  Security    - guards / pacifies unruly passengers")

    maintenance = common.prompt_bool(
        "  Can repair the ship? (maintenance)", default=False
    )
    if maintenance is None:
        print("Cancelled.")
        return False

    medical = common.prompt_bool(
        "  Can heal crew? (medical)", default=False
    )
    if medical is None:
        print("Cancelled.")
        return False

    security = common.prompt_bool(
        "  Can act as a guard? (security)", default=False
    )
    if security is None:
        print("Cancelled.")
        return False

    # Sanity: a robot with no abilities is a pet-shaped paperweight.
    if not (maintenance or medical or security):
        print()
        print("  Warning: no robot abilities were enabled. This robot will")
        print("  do nothing except occupy a slot. (A pet-like robot might")
        print("  be intended — those are valid too.)")
        if not common.prompt_bool("  Continue anyway?", default=True):
            print("Cancelled.")
            return False

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "boolmaintenance": "true" if maintenance else "false",
        "boolmedical": "true" if medical else "false",
        "boolsecurity": "true" if security else "false",
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Robot", genus_key, genus_code, next_id, shared, genus_fields
    )