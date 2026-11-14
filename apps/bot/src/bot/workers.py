import json


async def reload_uuid(minecraft_dir) -> None:
    usercache_file = minecraft_dir / "usercache.json"
    player_hash_file = minecraft_dir / "player_hash.json"

    if not usercache_file.is_file() or not player_hash_file.is_file():
        raise FileNotFoundError(f"Files not found {player_hash_file}, {usercache_file}")

    try:
        usercache = json.loads(usercache_file.read_text())
    except json.decoder.JSONDecodeError:
        usercache = []
    try:
        player_hash = json.loads(player_hash_file.read_text())
    except json.decoder.JSONDecodeError:
        player_hash = {}
    with open(player_hash_file, "r+") as phash:

        for data in usercache:
            uuids = player_hash.setdefault(data['name'], [])
            if data["uuid"] not in uuids:
                uuids.append(data["uuid"])

        json.dump(player_hash, phash, indent=4)
