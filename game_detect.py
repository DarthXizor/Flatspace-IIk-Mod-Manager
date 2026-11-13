import os

EULA_FILENAME = "EULA.txt"
EULA_FIRST_LINE = "Flatspace IIk End User License Agreement"
GAME_EXE = "FlatspaceII.exe"

PRUNE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".cache",
    ".npm",
    "AppData",
    ".local/share/Trash",
    "proc",
    "sys",
    "dev",
}


def _verify_eula(game_root):
    """
    Sanity check: EULA.txt must exist in the game root and its first line
    must match the expected license header.

    Returns True if valid, False otherwise.
    """
    eula_path = os.path.join(game_root, EULA_FILENAME)
    if not os.path.isfile(eula_path):
        return False

    try:
        with open(eula_path, "r", encoding="utf-8-sig", errors="replace") as f:
            first_line = f.readline().rstrip("\r\n")
    except OSError:
        return False

    return first_line == EULA_FIRST_LINE


def _verify_game_path(candidate_path):
    """
    Validate that candidate_path is a Flatspace IIk install.

    Primary signature: FlatspaceII.exe
    Sanity check:      EULA.txt with the expected first line

    Returns absolute path or None.
    """
    if not candidate_path or not os.path.isdir(candidate_path):
        return None

    exe = os.path.join(candidate_path, GAME_EXE)
    if not os.path.isfile(exe):
        return None

    if not _verify_eula(candidate_path):
        return None

    return os.path.abspath(candidate_path)


def _scan_for_game(root):
    """
    Walk `root` recursively looking for Flatspace IIk.
    Prunes known-noise directories to keep the scan fast.
    """
    found = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]

        if GAME_EXE in filenames:
            result = _verify_game_path(dirpath)
            if result and result not in found:
                found.append(result)

    return found


def _get_scan_roots(os_type, extra_paths=None):
    """
    Build the list of root directories to scan based on OS type.
    """
    roots = []

    if extra_paths:
        roots.extend(extra_paths)

    if os_type == "Windows":
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            roots.append(user_profile)
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                roots.append(drive)

    elif os_type == "Linux":
        home = os.path.expanduser("~")
        if os.path.isdir(home):
            roots.append(home)
        for mount in ("/mnt", "/media", "/run/media"):
            if os.path.isdir(mount):
                roots.append(mount)

    return roots


def find_game_install(os_type, extra_paths=None):
    """
    Scan the filesystem for a Flatspace IIk install based on OS type.

    Args:
        os_type: 'Windows' or 'Linux' (from your OSDetect class)
        extra_paths: optional extra roots to scan (e.g. a user-picked drive)

    Returns:
        List of game root paths found (may be empty).
    """
    if os_type not in ("Windows", "Linux"):
        return []

    results = []
    seen = set()

    for root in _get_scan_roots(os_type, extra_paths):
        if not root or root in seen:
            continue
        seen.add(root)

        for game_path in _scan_for_game(root):
            if game_path not in results:
                results.append(game_path)

    return results