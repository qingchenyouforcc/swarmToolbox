from pathlib import Path
from qfluentwidgets import QConfig
from typing import TYPE_CHECKING

from src.config import DATA_DIR

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow


class AppContext(QConfig):
    def __init__(self, path: Path):
        # 指定配置文件路径
        super().__init__()
        self.file = path

        # 运行时状态
        self.main_window: 'MainWindow | None' = None


CONFIG_PATH = DATA_DIR / "config.json"
app_context = AppContext(CONFIG_PATH)
