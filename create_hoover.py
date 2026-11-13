import create_common as common

GENUS_KEY = "HOOVER"

# Manual: hoovermass is an integer. 0 for tractor beams/vaporisers, 5 for
# cargo containers, 10 for lifepods, higher for asteroids/vessels.
MAX_HOOVERMASS = 1_000_000


def _prompt_hoovermass():
    print()
    print(" Hoovers mass threshold (max vessel/pod/asteroid mass it can scoop)")
    print("  Reference: 0 = tractor beam / vaporiser (no mass scooping)")
    print("             5 = cargo containers")
    print("             10 = lifepods")
    print("             higher = asteroids, small vessels")
    return common.prompt_int(
        f"  Hoover mass (integer, 0-{MAX_HOOVERMASS}, e.g. 10 for lifepods): ",
        min_value=0,
        max_value=MAX_HOOVERMASS,
    )


def create(game_path, genus_key, genus_code, next_id):
    """
    Hoover/scoop tree (genuscode=14).

    Only the following fields are prompted (behavioural):
      hoovermass                    : int, max mass the scoop can assimilate.
      boolhooverscoopcrewascrew     : scoop live people as crew (lifesaving)
      boolhooverscoopcrewasmeat     : scoop live people as meat (processing)
      boolhooverscoopcargoascargo   : scoop cargo intact (plain cargo scoop)
      boolhooverscoopcargoasrefined : scoop cargo refined (mining scoop)

    All effect and beam-timing fields come from Templates/Hoover.txt and are
    NOT prompted, so every created scoop uses the sample document's visual and
    audio defaults (matching LIFESAVERSCOOP):
      hooveralpha     = 0.800000
      hooveralphavel  = -0.050000
      hooverrate      = 4
      hooverfairy     = 69
      hooveremitter   = 31
      hoovervel       = 0.050000
      hooversfxnumber = 50

    energydrainperuse is fixed at 0 (manual: zero for hoovers) via the template.

    The two crew flags must NOT both be true. The two cargo flags must NOT
    both be true. If a crew flag pair is both false, people are vaporised.
    If a cargo flag pair is both false, cargo is vaporised.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    print()
    print(" Hoover-specific fields")

    hoovermass = _prompt_hoovermass()
    if hoovermass is None:
        print("Cancelled.")
        return False

    print()
    print(" Scoop behaviour (each pair: at most one true; both false = destroy)")

    scoop_crew_as_crew = common.prompt_bool(
        "  Scoop live people as crew? (lifesaving)", default=False
    )
    if scoop_crew_as_crew is None:
        print("Cancelled.")
        return False

    scoop_crew_as_meat = False
    if scoop_crew_as_crew:
        print("    -> live people scooped will be captured as crew.")
        print("    (scoop crew as meat disabled, crew-as-crew is on)")
    else:
        scoop_crew_as_meat = common.prompt_bool(
            "  Scoop live people as meat? (mining scoop behaviour)", default=False
        )
        if scoop_crew_as_meat is None:
            print("Cancelled.")
            return False
        if scoop_crew_as_meat:
            print("    -> live people scooped will be processed into meat.")
        else:
            print("    -> live people scooped will be vaporised.")

    scoop_cargo_as_cargo = common.prompt_bool(
        "  Scoop cargo intact? (plain cargo scoop)", default=True
    )
    if scoop_cargo_as_cargo is None:
        print("Cancelled.")
        return False

    scoop_cargo_as_refined = False
    if scoop_cargo_as_cargo:
        print("    -> cargo scooped will be added intact.")
        print("    (scoop cargo as refined disabled, cargo-as-cargo is on)")
    else:
        scoop_cargo_as_refined = common.prompt_bool(
            "  Scoop cargo as refined? (mining scoop behaviour)", default=False
        )
        if scoop_cargo_as_refined is None:
            print("Cancelled.")
            return False
        if scoop_cargo_as_refined:
            print("    -> cargo scooped will be added as refined goods.")
        else:
            print("    -> cargo scooped will be vaporised.")

    gen_flags = common.prompt_generate_flags()
    if gen_flags is None:
        return False

    genus_fields = {
        "hoovermass": str(hoovermass),
        "boolhooverscoopcrewascrew": "true" if scoop_crew_as_crew else "false",
        "boolhooverscoopcrewasmeat": "true" if scoop_crew_as_meat else "false",
        "boolhooverscoopcargoascargo": "true" if scoop_cargo_as_cargo else "false",
        "boolhooverscoopcargoasrefined": "true" if scoop_cargo_as_refined else "false",
    }
    genus_fields.update(gen_flags)

    return common.write_mod(
        game_path, "Hoover", genus_key, genus_code, next_id, shared, genus_fields
    )