import os
import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt

from config import PROGRAM_NAME
from utils import (
    log_messages, shared_data_lock,
    STATUS_SUCCESS, STATUS_SKIPPED, STATUS_SEARCHING,
    STATUS_DOWNLOADING, STATUS_PENDING, STATUS_FAILED
)

# 初始化 TUI 组件
console = Console()
layout = Layout()
layout.split(
    Layout(name="header", size=3),
    Layout(ratio=1, name="main"),
    Layout(size=5, name="footer"),
)
layout["main"].split_row(Layout(name="table"), Layout(name="log", ratio=2, minimum_size=50))

def select_modlist_file_tui():
    """扫描当前目录并显示一个TUI让用户选择文件"""
    console.clear()
    console.print(Panel(Text(PROGRAM_NAME, justify="center", style="bold blue")))
    potential_files = [f for f in os.listdir('.') if f.endswith(('.json', '.txt'))]
    if not potential_files:
        console.print("[bold red]错误: 在当前目录下没有找到 .json 或 .txt 模组列表文件。[/bold red]")
        return None

    table = Table(title="请选择一个模组列表文件", border_style="green")
    table.add_column("选项", style="cyan", justify="right")
    table.add_column("文件名", style="magenta")
    for i, filename in enumerate(potential_files):
        table.add_row(str(i + 1), filename)
    
    console.print(table)
    console.print("输入数字并按 Enter 键选择, 或输入 'q' 退出。")
    while True:
        choice = Prompt.ask("[bold]你的选择是[/bold]")
        if choice.lower() == 'q': return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(potential_files):
                selected_file = potential_files[index]
                console.print(f"你选择了: [bold green]{selected_file}[/bold green]")
                time.sleep(1)
                return selected_file
            else: console.print("[red]无效的数字，请重试。[/red]")
        except ValueError: console.print("[red]请输入一个有效的数字。[/red]")

def make_header():
    return Panel(Text(f"{PROGRAM_NAME} (并发版)", justify="center", style="bold blue"), border_style="blue")

def make_mod_table(jobs):
    visible_jobs = [j for j in jobs if j['status'] not in (STATUS_SUCCESS[0], STATUS_SKIPPED[0])]
    sort_order = { STATUS_SEARCHING[0]: 0, STATUS_DOWNLOADING[0]: 1, STATUS_PENDING[0]: 2, STATUS_FAILED[0]: 3 }
    sorted_jobs = sorted(visible_jobs, key=lambda j: sort_order.get(j['status'], 99))

    table = Table(title=f"进行中 & 失败的任务: {len(sorted_jobs)}", border_style="gray50")
    table.add_column("模组名", style="magenta", no_wrap=True)
    table.add_column("版本", style="yellow")
    table.add_column("状态", justify="right")

    for job in sorted_jobs:
        table.add_row(job['mod']['name'], job['mod']['version'], Text(job['status'], style=job['style']))
    
    return Panel(table, title="[bold]任务状态[/bold]", border_style="green")

def make_log_panel():
    with shared_data_lock:
        log_text = Text.from_markup("\n".join(log_messages))
    return Panel(log_text, title="[bold]实时日志[/bold]", border_style="yellow")

def make_footer(progress, counts):
    success, failed, skipped = counts['success'], counts['failed'], counts['skipped']
    summary = f"[green]成功: {success}[/] | [red]失败: {failed}[/] | [dim]跳过: {skipped}[/]"
    footer_layout = Layout()
    footer_layout.split_column(Layout(progress, name="progress", size=3), Layout(Panel(Text(summary, justify="center")), name="summary"))
    return footer_layout