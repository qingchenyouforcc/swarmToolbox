from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("homeInterface")
        
        # 添加最基本的布局
        layout = QVBoxLayout(self)
        label = QLabel("欢迎使用 SwarmToolbox", self)
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(label)