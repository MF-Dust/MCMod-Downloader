import threading
from contextlib import contextmanager

# --- 共享状态变量 ---
log_messages = []
MAX_LOG_LINES = 15
shared_data_lock = threading.Lock()

# --- 状态定义 ---
STATUS_PENDING = ("待定", "dim")
STATUS_SEARCHING = ("搜索中...", "yellow")
STATUS_DOWNLOADING = ("下载中...", "cyan")
STATUS_SUCCESS = ("✓ 成功", "green")
STATUS_FAILED = ("✗ 失败", "bold red")
STATUS_SKIPPED = ("- 跳过", "dim bold")

# --- 辅助函数 ---
def add_log(message: str):
    """向全局日志中添加一条消息 (线程安全)"""
    with shared_data_lock:
        log_messages.append(message)
        if len(log_messages) > MAX_LOG_LINES:
            log_messages.pop(0)

@contextmanager
def status_update(job: dict, status_tuple: tuple):
    """一个上下文管理器，用于在操作期间更新任务状态"""
    job['status'], job['style'] = status_tuple
    yield