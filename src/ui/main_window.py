from PyQt6 import QtGui
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentWindow, 
    SplashScreen, 
    MessageBox,
    SystemThemeListener,
    Theme,
    FluentIcon as FIF,
    NavigationItemPosition,
)
from loguru import logger

from src.config import ASSETS_DIR, cfg
from src.ui.interface.home.home_interface import HomeInterface
from src.ui.interface.setting.setting_interface import SettingInterface

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        # 系统主题监听器
        self.themeListener = SystemThemeListener(self)
        
        self.setObjectName("demoWindow")
        # 使用默认图标，如果main.ico不存在的话
        icon_path = ASSETS_DIR / "main.ico"
        if icon_path.exists():
            icon = QtGui.QIcon(str(icon_path))
        else:
            # 使用默认应用图标
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)

        self.setWindowIcon(icon)
        
        # 创建启动页面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(64, 64))
        
        # 设置初始窗口大小
        desktop = QApplication.primaryScreen()
        if desktop:  # 确保 desktop 对象不是 None
            self.resize(QSize(680, 530)) 
        # self.resize(QSize(desktop.availableGeometry().width() // 2, desktop.availableGeometry().height() // 2))
        else:  # 如果获取不到主屏幕信息，给一个默认大小
            self.resize(QSize(680, 530))
            
        # TODO 实现按照配置文件主题切换，bug没修好
        # 临时方案：按照系统主题修改
        cfg.set_theme(Theme.AUTO) 
        logger.info("应用默认主题: AUTO")

        self.show()   

        # 添加子界面
        self.addSubInterface(
            interface=HomeInterface(self),
            icon=FIF.HOME,
            text="主页",
            position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            interface=SettingInterface(self),
            icon=FIF.SETTING,
            text="设置",
            position=NavigationItemPosition.BOTTOM,
        )

        self.setWindowTitle("swarmToolbox")
            
        # 隐藏启动页面
        self.splashScreen.finish()

    def closeEvent(self, event):  # pyright: ignore[reportIncompatibleMethodOverride]
        try:
            logger.info("正在弹出退出确认对话框...")

            w = MessageBox("即将关闭整个程序", "您确定要这么做吗？", self)
            w.setDraggable(False)

            if w.exec():
                logger.info("用户确认退出，程序即将关闭。")
                event.accept()
                self.themeListener.terminate()
                self.themeListener.deleteLater()
                QApplication.quit()
            else:
                logger.info("用户取消了退出操作。")
                event.ignore()

        except Exception:
            logger.exception("在退出确认过程中发生错误")
