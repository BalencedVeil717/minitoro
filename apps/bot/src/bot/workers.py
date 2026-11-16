import os
import json
import tempfile
from pathlib import Path


async def reload_uuid(minecraft_dir) -> None:
    usercache_file = minecraft_dir / "usercache.json"
    player_hash_file = minecraft_dir / "player_hash.json"

    if not usercache_file.is_file():
        raise FileNotFoundError(f"usercache.json not found: {usercache_file}")

    usercache = json.loads(usercache_file.read_text(encoding="utf-8"))

    if player_hash_file.is_file():
        player_hash = json.loads(player_hash_file.read_text(encoding="utf-8"))
    else:
        player_hash = {}

    for data in usercache:
        uuids = player_hash.setdefault(data['name'], [])
        if data["uuid"] not in uuids:
            uuids.append(data["uuid"])

    fd, temp_path = tempfile.mkstemp(dir=minecraft_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            json.dump(player_hash, tmp_file, indent=4)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(temp_path, player_hash_file)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


async def get_players(minecraft_dir: Path) -> list[str]:
    player_hash_file = minecraft_dir / "player_hash.json"

    if not player_hash_file.is_file():
        print(f"Files not found {player_hash_file}")
        return []

    try:
        players = json.loads(player_hash_file.read_text(encoding="utf-8")).keys()
    except json.decoder.JSONDecodeError:
        print("Cannot load player_hash.json")
        players = []

    return players
