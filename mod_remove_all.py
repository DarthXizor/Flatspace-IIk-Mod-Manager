import os
import re

from mod_remove_specific import (
    ITEMS_DATA_FOLDER,
    ITEMS_DATA_FILES,
    ITEMS_FOLDER,
    MOD_ID_THRESHOLD,
    _read_item_id,
    _read_item_text_tag,
    _remove_block_from_items_file,
)


def _scan_items(items_dir):
    mods = []
    total = 0
    skipped = 0

    for entry in os.listdir(items_dir):
        if not entry.lower().endswith(".txt"):
            continue
        file_path = os.path.join(items_dir, entry)
        if not os.path.isfile(file_path):
            continue

        total += 1
        item_id = _read_item_id(file_path)
        if item_id is None:
            skipped += 1
            continue
        if item_id < MOD_ID_THRESHOLD:
            continue

        tag_name = _read_item_text_tag(file_path)
        if tag_name is None:
            skipped += 1
            print(f"Skipping {entry}: no valid text=[...] tag found.")
            continue
        mods.append((file_path, tag_name))

    return mods, total, skipped


def delete_mods(game_path):
    items_dir = os.path.join(game_path, ITEMS_FOLDER)
    data_files = [
        os.path.join(game_path, ITEMS_DATA_FOLDER, name)
        for name in ITEMS_DATA_FILES
    ]

    if not os.path.isdir(items_dir):
        print(f"Items folder not found at: {items_dir}")
        return 0

    mods, total, skipped = _scan_items(items_dir)

    print(f"Scanned {total} item file(s) in {items_dir}")
    if skipped:
        print(f"  ({skipped} file(s) had no parseable id or tag)")

    if not mods:
        print("No mods found or mods have ID's lower than 5000 and must be removed manually.")
        return 0

    deleted_count = 0
    for file_path, tag_name in mods:
        removed_from_data = False
        for data_file in data_files:
            if _remove_block_from_items_file(data_file, tag_name):
                removed_from_data = True

        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Failed to delete {os.path.basename(file_path)}: {e}")
            continue

        if removed_from_data:
            deleted_count += 1
        else:
            print(f"Deleted {os.path.basename(file_path)} but no matching entry "
                  f"in Items data files for [{tag_name}].")

    print(f"{deleted_count} Mods have been deleted.")
    return deleted_count