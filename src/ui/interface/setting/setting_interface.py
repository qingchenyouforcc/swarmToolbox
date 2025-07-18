from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SettingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingInterface")
        
        # 添加最基本的布局
        layout = QVBoxLayout(self)
        label = QLabel("设置页面", self)
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(label)