import os
import json
import requests

from config import (
    MODRINTH_API_BASE, CURSEFORGE_API_BASE, CF_HEADERS,
    MINECRAFT_GAME_ID, FORGE_MODLOADER_TYPE
)
from utils import add_log, status_update, STATUS_DOWNLOADING

session = requests.Session()

def download_file_no_progress(url, filepath, headers=None):
    try:
        response = session.get(url, stream=True, headers=headers, timeout=20)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        add_log(f"[red]下载错误: {e}[/red]")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False
    
def attempt_modrinth_download(job, minecraft_version):
    """尝试从 Modrinth 下载模组"""
    mod = job['mod']; target_filepath = job['filepath']
    add_log(f"[Modrinth] 搜索 '{mod['name']}' for MC {minecraft_version}")
    try:
        search_url = f"{MODRINTH_API_BASE}/search"
        params = {'query': mod['name'], 'facets': f'[["categories:forge"],["versions:{minecraft_version}"]]'}
        response = session.get(search_url, params=params, timeout=10); response.raise_for_status()
        hits = response.json()['hits']
        if not hits: add_log(f"[Modrinth] 未找到 '{mod['name']}'"); return False

        project_id = hits[0]['project_id']
        versions_url = f"{MODRINTH_API_BASE}/project/{project_id}/version"
        params = {'loaders': json.dumps(['forge']), 'game_versions': json.dumps([minecraft_version])}
        response = session.get(versions_url, params=params, timeout=10); response.raise_for_status()
        versions = response.json()
        if not versions: add_log(f"[Modrinth] 未找到适用版本 for '{mod['name']}'"); return False

        file_to_download = next((f for v in versions for f in v['files'] if f.get('primary')), versions[0]['files'][0])
        if file_to_download:
            add_log(f"[Modrinth] 找到文件: [bold magenta]{file_to_download['filename']}[/bold magenta]")
            with status_update(job, STATUS_DOWNLOADING):
                return download_file_no_progress(file_to_download['url'], target_filepath)
        return False
    except Exception as e:
        add_log(f"[Modrinth] [red]请求失败: {e}[/red]"); return False

def attempt_curseforge_download(job, minecraft_version):
    """尝试从 CurseForge 下载模组"""
    mod = job['mod']; target_filepath = job['filepath']
    add_log(f"[CurseForge] 搜索 '{mod['name']}' for MC {minecraft_version}")
    try:
        search_params = {'gameId': MINECRAFT_GAME_ID, 'searchFilter': mod['name'], 'classId': 6}
        response = session.get(f"{CURSEFORGE_API_BASE}/mods/search", params=search_params, headers=CF_HEADERS, timeout=10); response.raise_for_status()
        search_results = response.json().get('data', [])
        if not search_results: add_log(f"[CurseForge] 未找到 '{mod['name']}'"); return False

        mod_id = search_results[0]['id']
        # 修改：使用传入的 minecraft_version
        files_params = {'gameVersion': minecraft_version, 'modLoaderType': FORGE_MODLOADER_TYPE}
        response = session.get(f"{CURSEFORGE_API_BASE}/mods/{mod_id}/files", params=files_params, headers=CF_HEADERS, timeout=10); response.raise_for_status()
        files = response.json().get('data', [])
        if not files: add_log(f"[CurseForge] 未找到适用文件 for '{mod['name']}'"); return False

        best_match = next((f for f in files if f['fileName'] == mod['filename']), files[0])
        if best_match and best_match.get('downloadUrl'):
            add_log(f"[CurseForge] 找到文件: [bold magenta]{best_match['fileName']}[/bold magenta]")
            with status_update(job, STATUS_DOWNLOADING):
                return download_file_no_progress(best_match['downloadUrl'], target_filepath, headers=CF_HEADERS)
        else:
            add_log(f"[CurseForge] 找到的文件无下载链接 for '{mod['name']}'"); return False
    except Exception as e:
        add_log(f"[CurseForge] [red]API 错误: {e}[/red]"); return False