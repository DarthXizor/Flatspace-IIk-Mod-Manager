import create_common as common

GENUS_KEY = "CARGO"


def create(game_path, genus_key, genus_code, next_id):
    shared = common.prompt_shared_fields(genus_key)
    if shared is None:
        return False
    return common.write_mod(
        game_path, "Cargo", genus_key, genus_code, next_id, shared, genus_fields={}
    )
