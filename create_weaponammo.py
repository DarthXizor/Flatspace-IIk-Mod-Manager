import create_common as common

GENUS_KEY = "WEAPONAMMO"


def create(game_path, genus_key, genus_code, next_id):
    """
    Weapon Ammo tree (genuscode=6).

    The base-game sample (MinigunAmmo) confirms ammo items use ONLY the
    shared fields — no genus-specific parameters:
        text, id, genuscode, onsalein*probability,
        boolintegral, boolmineral, boolgenerateforai, boolgenerateforplayer,
        boolispet, mass, cost, guildrank, guildtype, maxammo

    The template (Templates/WeaponAmmo.txt) carries the base-game defaults
    for the fields the user doesn't prompt for:
        genuscode=6
        boolintegral=false
        boolmineral=false
        boolgenerateforai=false
        boolgenerateforplayer=false
        boolispet=false
        guildrank=0
        guildtype=0
        maxammo=0

    Only the shared fields (name, description, mass, cost, three on-sale
    probabilities) are prompted. Ammo created here automatically appears
    in the slug-weapon ammo selection menu (create_weapon._prompt_ammo_selection),
    because that menu scans Items/ for genuscode=6 at runtime.
    """
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False

    return common.write_mod(
        game_path,
        "WeaponAmmo",
        genus_key,
        genus_code,
        next_id,
        shared,
        genus_fields={},
    )