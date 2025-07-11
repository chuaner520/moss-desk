import os
import subprocess
import signal
import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox, QFrame, QGridLayout, QSizePolicy, QScrollArea, QLineEdit
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QFontMetrics

TOOLS_META_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/mcp/tools/mcp_tools_meta.json'))
YO_MCP = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/mcp/yo_mcp.py'))
MCP_PIPE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/mcp/mcp_pipe.py'))

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background: transparent;')  # 设置主容器透明
        self.mcp_process = None
        self.cards = []  # 存储所有卡片
        self.card_min_width = 260  # 单个卡片最小宽度
        self.card_spacing = 24     # 卡片间距
        self.grid_cols = 3         # 默认列数

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)
        
        # 标题
        title = QLabel("MCP 工具列表")
        title.setStyleSheet("font-size: 28px; color: #2628f3; font-weight: bold; margin: 12px  0 0 0; border: none;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
  

        # 滚动区域包裹Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet('''
            QScrollArea {
                background: transparent;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: transparent;
                border: none;
                margin: 0px;
            }
            QScrollBar:vertical {
                width: 2px;
            }
            QScrollBar:horizontal {
                height: 2px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ced6db, stop:1 #ced6db);
                border-radius: 6px;
                min-height: 24px;
                min-width: 36px;
                border: none;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ced6db, stop:1 #ced6db);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0px; width: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        ''')
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet('background: transparent;')  # grid容器透明
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(self.card_spacing)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.grid_container)
        layout.addWidget(self.scroll)

        self.load_tools_from_json()
        self.relayout_cards()

        # 启动/结束MCP服务按钮
        self.start_btn = QPushButton("启动MCP服务")
        self.start_btn.setStyleSheet("background-color: #2628f3; color: white; font-size: 18px; padding: 12px 24px; border-radius: 6px;")
        self.start_btn.setFixedWidth(220)
        self.start_btn.clicked.connect(self.toggle_mcp_service)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

        self.status_label = QLabel("服务未启动")
        self.status_label.setStyleSheet("font-size: 14px; color: #888;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def load_tools_from_json(self):
        self.cards.clear()
        if not os.path.exists(TOOLS_META_PATH):
            return
        with open(TOOLS_META_PATH, 'r', encoding='utf-8') as f:
            all_meta = json.load(f)
        for tool_key, meta in all_meta.items():
            card = self.create_tool_card(meta)
            self.cards.append(card)

    def create_tool_card(self, meta):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("QFrame { background: #fff; border-radius: 12px; }")
        card.setMinimumWidth(self.card_min_width)
        card.setMaximumWidth(400)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 12, 18, 12)
        card_layout.setSpacing(18)

        # 封面（首字圆形）
        cover = QLabel(meta.get('cover', '?'))
        cover.setFixedSize(56, 56)
        cover.setAlignment(Qt.AlignCenter)
        cover.setStyleSheet("background: #2628f3; color: #fff; border-radius: 28px; font-size: 28px; font-weight: bold;")
        card_layout.addWidget(cover)

        # 标题和描述
        vbox = QVBoxLayout()
        title = QLabel(meta.get('title', ''))
        title.setStyleSheet("font-size: 16px; color: #222; font-weight: bold;")
        vbox.addWidget(title)
        desc = meta.get('desc', '')
        desc_label = QLabel()
        desc_label.setStyleSheet("font-size: 13px; color: #555; margin-top: 4px;")
        desc_label.setFixedHeight(22)
        desc_label.setMaximumHeight(22)
        desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        desc_label.setToolTip(desc)
        # 省略号文本，初始宽度200
        fm = QFontMetrics(desc_label.font())
        elided = fm.elidedText(desc, Qt.ElideRight, 200)
        desc_label.setText(elided)
        desc_label._full_text = desc  # 记录原文
        vbox.addWidget(desc_label)
        card_layout.addLayout(vbox)
        # 记录desc_label用于resize时更新
        card._desc_label = desc_label
        return card

    def relayout_cards(self):
        # 清空grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                w = item.widget()
                if w:
                    w.setParent(None)
        # 计算列数
        width = self.scroll.viewport().width()
        cols = max(1, width // (self.card_min_width + self.card_spacing))
        self.grid_cols = min(max(cols, 1), 6)  # 限制最大列数
        # 重新布局
        for idx, card in enumerate(self.cards):
            row = idx // self.grid_cols
            col = idx % self.grid_cols
            self.grid_layout.addWidget(card, row, col)
            # 动态更新desc省略号
            desc_label = getattr(card, '_desc_label', None)
            if desc_label:
                # 计算desc_label最大宽度
                card_width = card.width() or self.card_min_width
                maxw = card_width - 56 - 36  # 封面+间距
                fm = QFontMetrics(desc_label.font())
                elided = fm.elidedText(desc_label._full_text, Qt.ElideRight, maxw)
                desc_label.setText(elided)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_cards()

    def toggle_mcp_service(self):
        if self.mcp_process is None:
            # 启动服务，确保子进程在新进程组，避免killpg影响主进程
            try:
                self.mcp_process = subprocess.Popen(
                    ['python', MCP_PIPE, YO_MCP],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
                self.start_btn.setText("结束服务")
                self.status_label.setText("服务运行中")
                self.status_label.setStyleSheet("font-size: 14px; color: #27ae60;")

            except Exception as e:
                QMessageBox.critical(self, "启动失败", f"启动 MCP 服务失败：{e}")
                self.status_label.setText("启动失败")
                self.status_label.setStyleSheet("font-size: 14px; color: #e74c3c;")
        else:
            # 结束服务
            try:
                if self.mcp_process.poll() is None:
                    if os.name == 'nt':
                        self.mcp_process.terminate()
                    else:
                        os.killpg(os.getpgid(self.mcp_process.pid), signal.SIGTERM)
                self.mcp_process = None
                self.start_btn.setText("启动MCP服务")
                self.status_label.setText("服务未启动")
                self.status_label.setStyleSheet("font-size: 14px; color: #888;")
            except Exception as e:
                QMessageBox.critical(self, "结束失败", f"结束 MCP 服务失败：{e}") 