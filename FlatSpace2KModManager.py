import sys
import traceback

from os_detect import OSDetect
from game_detect import find_game_install
from mod_remove_all import delete_mods
from mod_remove_specific import remove_specific_mod_flow
from mod_list import list_mods_flow
from mod_create import create_mod_flow


MENU_OPTIONS = (
    ("1", "Create Mod"),
    ("2", "List Mods"),
    ("3", "Remove Specific Mod"),
    ("4", "Remove All Mods"),
    ("5", "Exit"),
)


def print_menu(game_path):
    print()
    print("=" * 50)
    print(" Flatspace IIk Mod Manager")
    print(f" Game: {game_path}")
    print("=" * 50)
    for key, label in MENU_OPTIONS:
        print(f"  [{key}] {label}")
    print("=" * 50)


def run_menu(game_path):
    while True:
        print_menu(game_path)
        try:
            choice = input("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if choice == "1":
            safe_call(create_mod, game_path)
        elif choice == "2":
            safe_call(list_mods, game_path)
        elif choice == "3":
            safe_call(remove_specific_mod, game_path)
        elif choice == "4":
            safe_call(remove_all_mods, game_path)
        elif choice == "5":
            print("Exiting.")
            return
        else:
            print(f"Invalid option: {choice!r}. Please choose 1-5.")


def safe_call(func, game_path):
    print(f"\n--- Running {func.__name__} ---")
    try:
        func(game_path)
    except SystemExit:
        raise
    except Exception:
        print("ERROR: handler raised an exception:")
        traceback.print_exc()
    print("--- Done ---\n")


def create_mod(game_path):
    print(f"\n[Create Mod] Scanning: {game_path}")
    create_mod_flow(game_path)


def list_mods(game_path):
    print(f"\n[List Mods] Scanning: {game_path}")
    list_mods_flow(game_path)


def remove_specific_mod(game_path):
    print(f"\n[Remove Specific Mod] Scanning: {game_path}")
    remove_specific_mod_flow(game_path)


def remove_all_mods(game_path):
    print(f"\n[Remove All Mods] Scanning: {game_path}")
    result = delete_mods(game_path)
    print(f"[Remove All Mods] Result: {result} mod(s) removed.")

    while True:
        print()
        print("=" * 50)
        print(" Remove All Mods - Complete")
        print("=" * 50)
        print("  [1] Return to Main Menu")
        print("  [2] Exit Program")
        print("=" * 50)
        choice = input("Select an option: ").strip()

        if choice == "1":
            return
        elif choice == "2":
            print("Exiting.")
            sys.exit(0)
        else:
            print(f"Invalid option: {choice!r}. Please choose 1-2.")


def find_game():
    os_detect = OSDetect()
    if not os_detect.is_supported:
        print(f"Unsupported OS: {os_detect.raw_system}")
        sys.exit(1)

    game_paths = find_game_install(os_detect.os)
    if not game_paths:
        print("Flatspace IIk not found automatically.")
        user_path = input("Enter game directory (or blank to exit): ").strip()
        if not user_path:
            sys.exit(1)
        game_paths = find_game_install(os_detect.os, extra_paths=[user_path])

    if not game_paths:
        print("Could not locate a valid Flatspace IIk install. Exiting.")
        sys.exit(1)

    if len(game_paths) == 1:
        return game_paths[0]

    print("Multiple installs found:")
    for i, p in enumerate(game_paths, 1):
        print(f"  [{i}] {p}")
    while True:
        sel = input("Select install: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(game_paths):
            return game_paths[int(sel) - 1]
        print("Invalid selection.")


def main():
    game_path = find_game()
    print(f"Using game install: {game_path}")
    run_menu(game_path)


if __name__ == "__main__":
    main()