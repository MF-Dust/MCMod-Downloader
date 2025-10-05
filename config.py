
# --- 程序信息 ---
PROGRAM_NAME = "Minecraft Mod Downloader"

# --- API 和网络设置 ---
MODRINTH_API_BASE = "https://api.modrinth.com/v2"
CURSEFORGE_API_BASE = "https://api.curseforge.com/v1"
CF_API_KEY = "$2a$10$bL4bIL5pUWqfcO7KQtnMReakwtfHbNKh6v1uTpKlzhwoueEJQnPnm"
CF_HEADERS = {'Accept': 'application/json', 'x-api-key': CF_API_KEY}

# --- 下载设置 ---
MAX_CONCURRENT_DOWNLOADS = 5
MODS_DOWNLOAD_DIR = "downloaded_mods"

# --- 游戏信息 ---
MINECRAFT_GAME_ID = 432
FORGE_MODLOADER_TYPE = 1
DEFAULT_MINECRAFT_VERSION = "1.20.1"