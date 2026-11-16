import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("BOT_TOKEN")
MINECRAFT_DIR = os.getenv("MINITORO_MINECRAFT_DIR")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

if not MINECRAFT_DIR:
    raise RuntimeError("MINITORO_MINECRAFT_DIR not set")

MINECRAFT_DIR = Path(MINECRAFT_DIR).resolve()

if not MINECRAFT_DIR.is_dir():
    raise FileNotFoundError(MINECRAFT_DIR)