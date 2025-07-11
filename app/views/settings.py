from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)
        
        # 标题
        title = QLabel("设置")
        title.setStyleSheet("font-size: 28px; color: #2628f3; font-weight: bold; margin: 32px 0; border: none;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 设置选项
        settings_container = QWidget()
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(16)
        
        # 主题设置
        theme_layout = QHBoxLayout()
        theme_label = QLabel("主题模式:")
        theme_label.setStyleSheet("font-size: 16px; color: #333;")
        theme_btn = QPushButton("浅色模式")
        theme_btn.setStyleSheet("background-color: #2628f3; color: white; font-size: 14px; padding: 8px 16px; border-radius: 4px;")
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_btn)
        theme_layout.addStretch()
        settings_layout.addLayout(theme_layout)
        
        # 语言设置
        lang_layout = QHBoxLayout()
        lang_label = QLabel("语言:")
        lang_label.setStyleSheet("font-size: 16px; color: #333;")
        lang_btn = QPushButton("中文")
        lang_btn.setStyleSheet("background-color: #2628f3; color: white; font-size: 14px; padding: 8px 16px; border-radius: 4px;")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(lang_btn)
        lang_layout.addStretch()
        settings_layout.addLayout(lang_layout)
        
        layout.addWidget(settings_container)
        layout.addStretch() 