import os
import json
import sys
import time
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn

# 修改：导入 DEFAULT_MINECRAFT_VERSION
from config import MODS_DOWNLOAD_DIR, MAX_CONCURRENT_DOWNLOADS, DEFAULT_MINECRAFT_VERSION
from downloader import attempt_modrinth_download, attempt_curseforge_download
from tui import (
    console, layout, select_modlist_file_tui,
    make_header, make_mod_table, make_log_panel, make_footer
)
from utils import (
    add_log, status_update, shared_data_lock,
    STATUS_PENDING, STATUS_SKIPPED, STATUS_SUCCESS, STATUS_FAILED
)

# 版本推断函数
def infer_game_version(modlist):
    """通过分析文件名来推断最常见的Minecraft版本。"""
    # 正则表达式用于匹配 "1.19.2", "mc1.20.1" 等版本号
    version_pattern = re.compile(r'(?:mc)?(\d+\.\d+(?:\.\d+)?)')
    versions_found = []

    for mod in modlist:
        filename = mod.get('filename', '')
        matches = version_pattern.findall(filename)
        versions_found.extend(matches)

    if not versions_found:
        add_log(f"[yellow]无法从文件名推断版本，将使用默认值: {DEFAULT_MINECRAFT_VERSION}[/yellow]")
        return DEFAULT_MINECRAFT_VERSION

    # 使用 Counter 找出最常见的版本号
    most_common_version = Counter(versions_found).most_common(1)[0][0]
    return most_common_version

def process_single_job(job, progress, task_id, counts, minecraft_version):
    """处理单个模组下载任务的函数，将被线程池调用"""
    if os.path.exists(job['filepath']):
        add_log(f"文件 '{job['mod']['filename']}' 已存在, 跳过。")
        job['status'], job['style'] = STATUS_SKIPPED
        with shared_data_lock: counts['skipped'] += 1
    else:
        # 传递 minecraft_version
        if attempt_modrinth_download(job, minecraft_version):
            job['status'], job['style'] = STATUS_SUCCESS
            with shared_data_lock: counts['success'] += 1
        else:
            add_log(f"-> Modrinth 失败, 尝试 CurseForge...")
            # 传递 minecraft_version
            if attempt_curseforge_download(job, minecraft_version):
                job['status'], job['style'] = STATUS_SUCCESS
                with shared_data_lock: counts['success'] += 1
            else:
                job['status'], job['style'] = STATUS_FAILED
                with shared_data_lock: counts['failed'] += 1
                add_log(f"[bold red]!! 下载失败: '{job['mod']['name']}'[/bold red]")

    progress.update(task_id, advance=1)

def main():
    """程序主入口"""
    modlist_file = select_modlist_file_tui()
    if modlist_file is None: sys.exit(0)

    try:
        with open(modlist_file, 'r', encoding='utf-8') as f:
            modlist = json.load(f)
    except Exception as e:
        console.print(f"[bold red]错误: 读取或解析文件 '{modlist_file}'失败: {e}[/bold red]")
        sys.exit(1)

    # 在加载列表后，立即推断游戏版本
    inferred_version = infer_game_version(modlist)
    console.print(f"[bold green]成功加载模组列表，检测到游戏版本为: {inferred_version}[/bold green]")
    time.sleep(2) # 让用户有时间看到版本信息

    if not os.path.exists(MODS_DOWNLOAD_DIR):
        os.makedirs(MODS_DOWNLOAD_DIR)

    jobs = [{'mod': mod, 'filepath': os.path.join(MODS_DOWNLOAD_DIR, mod['filename']), 'status': STATUS_PENDING[0], 'style': STATUS_PENDING[1]} for mod in modlist]
    counts = {"success": 0, "failed": 0, "skipped": 0}
    progress = Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))
    task_id = progress.add_task("总体进度", total=len(jobs))

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
        for job in jobs:
            executor.submit(process_single_job, job, progress, task_id, counts, inferred_version)

        with Live(layout, screen=True, redirect_stderr=False) as live:
            while not progress.finished:
                layout["header"].update(make_header())
                layout["table"].update(make_mod_table(jobs))
                layout["log"].update(make_log_panel())
                layout["footer"].update(make_footer(progress, counts))
                time.sleep(0.1)

    console.print("\n[bold green]所有任务已完成！[/bold green]")
    final_panel = make_mod_table(jobs)
    if len(final_panel.renderable.rows) > 0:
        console.print(final_panel)

    success, failed, skipped = counts['success'], counts['failed'], counts['skipped']
    console.print(f"最终统计 -> [green]成功: {success}[/] | [red]失败: {failed}[/] | [dim]跳过: {skipped}[/]")

if __name__ == "__main__":
    main()