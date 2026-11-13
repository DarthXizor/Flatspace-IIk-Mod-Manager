# Flatspace IIk Mod Manager

A Python tool for managing custom items in Flatspace IIk. It creates, lists, and removes item mods without you having to hand-edit the game's data files.

## What it does

- Finds your game automatically — scans the filesystem for a Flatspace IIk install and confirms it by checking for FlatspaceII.exe and the game's EULA.txt. If it can't find it, asks you for the path.
- Creates mods — walks you through building a new item of a chosen genus, writing the item file and updating the game's item lists in one go.
- Lists installed mods — shows every mod (ID 5000 and up) with its ID, filename, in-game name, and description.
- Removes one mod — pick by ID or filename; the item file and its entries in both item lists are removed.
- Removes all mods — deletes every mod in one pass.
- Preserves file format — writes CRLF line endings, keeps the original BOM state, and inserts new entries before the game's end-of-file marker, so the game accepts the files.

## File-creation issues this tool solves

The game's data files are Windows-native and its parser is strict about details that most editors and naive scripts silently change. During development we hit several failures where the game rejected mods that looked correct. If you have ever created a mod by hand or with a script and the game refused it, the cause was almost certainly one of the following.

### 1. Line endings (CRLF vs LF)

Symptom: The game reports that the text= field is missing from an item file that visibly contains it on the first line.

Cause: The game uses fgets(), which treats a line ending in bare LF (Unix-style \n) as truncated or empty. If the file's line endings change from Windows-native CRLF (\r\n) to LF, the parser fails on the very first line.

How it happens silently: Many editors and tools normalise line endings. Python's text-mode open() with newline="" writes whatever newline characters are in the string, so a naive write produces LF and breaks the file. The byte-size difference is a tell: rewriting a file from CRLF to LF shrinks it by one byte per line. In our case a backup was 35,640 bytes and the broken version was 34,733 bytes — 907 bytes lighter, roughly one per line.

What the tool does: Reads and writes data files as raw bytes, preserves each line's native terminator exactly as read, and never lets Python translate newlines.

### 2. UTF-8 BOM

Symptom: The game still cannot find the text= field even though the file has correct line endings.

Cause: A UTF-8 BOM (the bytes EF BB BF) at the start of the file prevents the parser from recognising the first field. Python's encoding="utf-8-sig" adds a BOM on write even when the file did not originally have one. The game's original files are pure ASCII with no BOM, so writing them back with utf-8-sig corrupts them invisibly.

What the tool does: Detects BOM presence at read time and preserves it. No BOM is ever added to an ASCII file.

### 3. The end-of-file marker

Symptom: Newly created items do not appear in game even though the data is present in the file.

Cause: Items0.txt and Items1.txt end with a ** END ** marker line. New entries must be inserted before this marker. Appending after it means the game never reads the new block.

What the tool does: Inserts every new entry immediately before the marker, leaving the marker as the final line.

### 4. Tag mismatch between files

Symptom: The item file exists and looks fine, but the game still does not load the item.

Cause: The bracketed tag in Items0.txt / Items1.txt must match the text=[...] line in the item file exactly. Spaces inside the name portion break the match — the game stores and looks up tags without spaces (e.g. ITEM TESTITEM, not ITEM TEST ITEM).

What the tool does: Strips spaces from the name portion and uppercases the tag when building it, so the item file and both item lists always use the same tag.

### 5. Double-bracketing

Symptom: The tag in Items0.txt / Items1.txt is wrapped in two sets of brackets (e.g. [[ITEM TESTITEM]]) and the game cannot link it to any item file.

Cause: Naive string concatenation adds brackets to a tag that already has them.

What the tool does: Builds the tag without brackets, and adds them exactly once at write time.

### 6. Duplicate IDs

Symptom: The new item does not appear, or another existing item disappears.

Cause: Item IDs must be unique. Duplicate IDs are rejected by the game, and the rejection is not always reported clearly.

What the tool does: Scans the Items/ folder before creating, picks the next free ID above the current highest mod ID (starting at 5000), and refuses to overwrite an existing file or tag.

### 7. File permissions (Linux / Proton)

Symptom: The game cannot read a newly created item file even though its content is correct.

Cause: On Linux, the game runs under Proton as a different user context from the one that wrote the file. If the new file ends up with stricter permissions than the base-game files, the game's process may open it but read zero bytes.

What the tool does: Mirrors the permissions of an existing sibling file in Items/ after writing, so the new file is readable by the same process that reads the stock items. (This applies to Linux only — Windows does not use Unix-style permissions.)

## Supported item types

| Menu | Type | Genus code |
| :--- | :--- | :--- |
| 1 | Cargo | 1 |
| 2 | Armour | 3 |
| 3 | Weapon (slug or energy) | 4 |
| 4 | Turret Weapon | 5 |
| 5 | Weapon Ammo | 6 |
| 6 | Missile | 8 |
| 7 | Hyperdrive | 9 |
| 8 | Thruster | 10 |
| 9 | Generator | 11 |
| 10 | Shield | 12 |
| 11 | ECM (EMP or Reprogrammer) | 13 |
| 12 | Hoover / Scoop | 14 |
| 13 | Scanner | 15 |
| 14 | Radar | 16 |
| 15 | Escape Pod | 17 |
| 16 | Robot | 18 |

Package, ECM Ammo, and Useless are not available in the menu.

## Requirements

- Python 3.14.4 — download here: https://www.python.org/downloads/
- No external libraries
- Flatspace IIk (Steam or standalone)

## Platform support

| Platform | Status |
| :--- | :--- |
| Linux (via Proton) | Tested and working |
| Windows | Untested — should work, not yet verified |

## Installation

1. Download or clone the repository.
2. Extract so the folder contains:

FlatSpace2KModManager.py
os_detect.py
game_detect.py
mod_create.py
mod_list.py
mod_remove_all.py
mod_remove_specific.py
create_common.py
create_cargo.py
create_armour.py
create_weapon.py
create_turretweapon.py
create_weaponammo.py
create_missile.py
create_hyperdrive.py
create_thruster.py
create_generator.py
create_shield.py
create_ecm.py
create_hoover.py
create_scanner.py
create_radar.py
create_escapepod.py
create_robot.py
Templates/

3. Run:

python3 FlatSpace2KModManager.py

The Templates/ folder must sit next to the Python files.

## Usage

### Main menu

==================================================
 Flatspace IIk Mod Manager
 Game: /path/to/Flatspace IIk
==================================================
  [1] Create Mod
  [2] List Mods
  [3] Remove Specific Mod
  [4] Remove All Mods
  [5] Exit
==================================================

### Creating a mod

1. Pick the item type.
2. Fill in the shared fields (name, description, mass, cost, on-sale probabilities).
3. Fill in the type-specific fields (e.g. damage and firing rate for a weapon, shield points for a shield).
4. Review the confirmation screen and confirm.

The tool picks the next free ID (starting at 5000), writes the item file into Items/, and adds the matching entry to both Items0.txt and Items1.txt.

For slug weapons and ECM flares, the ammo menu is built by scanning Items/ for compatible ammo items, so any ammo you create will show up there automatically.

### Removing mods

- Remove Specific Mod — shows a numbered list of installed mods; pick one by ID or filename.
- Remove All Mods — deletes every mod in one pass.

Both operations restore Items0.txt and Items1.txt to their pre-mod state.

## What it does not do

- Does not edit existing base-game items.
- Does not create Package, ECM Ammo, or Useless items.
- Does not modify the game executable.
- Does not download or install the game.

## AI Disclaimer
- AI was used to create this project. The AI was guided by me a human, that is very lazy, too lazy to manually code this project by hand blame any and all errors on me, as they would have been there if AI was not used. I am no genius wonder wiz, just a lazy potato.

## Safety

- Back up Data/Items0.txt, Data/Items1.txt, and the Items/ folder before creating your first mod.
- Every write is shown to you for confirmation first.
- The tool will not overwrite an existing item file or add a duplicate tag.

## License

GNU General Public License v3.0 (GPL-3.0). See the LICENSE file for full text, or read it at https://www.gnu.org/licenses/gpl-3.0.html

This tool is a community effort and is not affiliated with the original game's developer or publisher.
README_END
