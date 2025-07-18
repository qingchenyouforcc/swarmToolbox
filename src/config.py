import sys

from pathlib import Path
from enum import Enum
from qfluentwidgets import QConfig, ConfigItem, OptionsValidator, setTheme
from qfluentwidgets import Theme as QtTheme
from loguru import logger

class Theme(str, Enum):
    """主题枚举"""

    AUTO = "Auto"
    LIGHT = "Light"
    DARK = "Dark"

class Config(QConfig):
    """应用程序配置类"""

    # 持久化配置项
    theme_mode = ConfigItem(
        "Appearance",
        "ThemeMode",
        Theme.AUTO,
        OptionsValidator([Theme.AUTO, Theme.LIGHT, Theme.DARK]),
    )

    def __init__(self, path: Path):
        # 指定配置文件路径
        super().__init__()
        self.file = path

    def set_theme(self, theme: Theme) -> None:
        """设置主题"""
        setTheme(QtTheme(theme.value))
        self.theme_mode.value = theme
        self.save()

IS_WINDOWS = sys.platform == "win32"

MAIN_PATH = Path.cwd()
DATA_DIR = MAIN_PATH / "data"
ASSETS_DIR = MAIN_PATH / "assets"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

CONFIG_PATH = DATA_DIR / "config.json"
cfg = Config(CONFIG_PATH)


if CONFIG_PATH.exists():
    cfg.load()
    
else:
    logger.info("未找到配置文件，正在应用默认主题: AUTO")
    cfg.set_theme(Theme.AUTO) 
    setTheme(QtTheme.AUTO)  
    
    