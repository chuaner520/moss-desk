from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AboutView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)
        
        title = QLabel("关于应用")
        title.setStyleSheet("font-size: 28px; color: #2628f3; font-weight: bold; margin: 32px 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("这是一个企业级桌面应用示例，展示了 PySide6 的各种功能。")
        desc.setStyleSheet("font-size: 18px; color: #2628f3; margin: 24px 0;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addStretch() 