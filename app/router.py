from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSizeGrip, QFrame, QGraphicsDropShadowEffect, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
from app.views.home import HomeView
from app.views.about import AboutView
from app.views.iconfont import IconFontView
from app.views.settings import SettingsView
from PySide6.QtCore import Qt, QPoint, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCursor, QIcon, QFontDatabase, QFont, QColor, QPainterPath, QRegion, QLinearGradient, QBrush, QPalette, QPainter
import os
from PySide6.QtCore import QTimer
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QEvent, QPropertyAnimation, QPointF
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QRadioButton, QLabel, QStyle
from PySide6.QtGui import QFont
from app.utils.notification import NotificationManager

BORDER_WIDTH = 6
SIDEBAR_WIDTH = 180
SIDEBAR_COLLAPSED = 48
ANIMATION_DURATION = 200  # ms

class SidebarButton(QPushButton):
    """自定义侧边栏按钮，支持悬停效果，可选居中，支持icon和文字分离"""
    def __init__(self, icon_code="", text_label="", parent=None, centered=False):
        super().__init__(parent)
        self.icon_code = icon_code
        self.text_label = text_label
        self.centered = centered
        self.is_hovered = False
        self.is_selected = False
        self.setMouseTracking(True)
        self.update_text(expanded=True)

    def update_text(self, expanded=True):
        if expanded and self.text_label:
            self.setText(f"{self.icon_code}  {self.text_label}")
        else:
            self.setText(self.icon_code)

    def enterEvent(self, event):
        self.is_hovered = True
        self.update_style()
        if not self.is_selected:
            self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update_style()
        super().leaveEvent(event)

    def update_style(self):
        if self.centered:
            base_style = """
                border: none;
                background: transparent;
                font-size: 18px;
                text-align: center;
                padding-left: 0;
                border-radius: 0;
            """
        else:
            base_style = """
                border: none;
                background: transparent;
                font-size: 16px;
                text-align: left;
                padding-left: 16px;
                border-radius: 0;
            """
        if self.is_selected:
            self.setStyleSheet(base_style + "color: white; background: #2628f3;")
            self.setCursor(Qt.ArrowCursor)
        elif self.is_hovered:
            self.setStyleSheet(base_style + "color: #2628f3; background: #f5f5f5;")
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setStyleSheet(base_style + "color: #2628f3;")
            self.setCursor(Qt.ArrowCursor)

class TitleBarButton(QPushButton):
    """只用于全屏按钮，支持悬停效果"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.is_hovered = False
        self.setMouseTracking(True)
        self.setFont(QFont("remixicon"))
        self.setFixedSize(32, 28)
        self.update_style()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update_style()
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update_style()
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def update_style(self):
        style = "border: none; font-size: 18px; color: #2628f3; background: transparent;"
        if self.is_hovered:
            style = "border: none; font-size: 18px; color: #2628f3; background: #f5f5f5;"
        self.setStyleSheet(style)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置自定义ToolTip内容（带图标）
        def tooltip_with_icon(text):
            return f'<span style="position:relative;display:inline-block;">' \
                   f'<span id="icon" style="font-family:remixicon;font-size:14px;vertical-align:middle;display:inline-block;margin-right:8px;">\uf045</span>' \
                   f'<span style="vertical-align:middle;">{text}</span></span>'
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(900, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # 设置窗口圆角效果
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
        """)
        self._drag_pos = None
        self._drag_offset = None
        self._resizing = False
        self._resize_dir = None
        self.sidebar_expanded = True
        self._sidebar_anim = None
        self.current_route = "home"  # 当前选中的路由
        
        # 创建圆角遮罩
        self.create_rounded_mask()
        
        # 加载 remixicon 字体
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'remixicon.ttf')
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
        remix_font = QFont("remixicon")

        # 主布局：水平分栏
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(SIDEBAR_WIDTH)
        self.sidebar.setMaximumWidth(SIDEBAR_WIDTH)
        self.sidebar.setStyleSheet("#sidebar { background: #fff; border-right: 1px solid #f7f7ff; }")
        
        # 添加侧边栏阴影效果
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(15)
        sidebar_shadow.setXOffset(2)
        sidebar_shadow.setYOffset(0)
        sidebar_shadow.setColor(QColor(0, 0, 0, 30))
        self.sidebar.setGraphicsEffect(sidebar_shadow)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 展开/收起按钮
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFont(remix_font)
        self.toggle_btn.setText("\uf4f6")  # menu-fold-3-fill
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setStyleSheet("border: none; font-size: 22px; color: #2628f3; background: transparent;")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_btn, alignment=Qt.AlignLeft)

        # 菜单按钮（使用自定义按钮类）
        self.btn_home = SidebarButton("\uee2b", "首页")
        self.btn_about = SidebarButton("\uf10c", "关于")
        self.btn_iconfont = SidebarButton("\uea43", "图标库")
        self.btn_home.setFont(remix_font)
        self.btn_about.setFont(remix_font)
        self.btn_iconfont.setFont(remix_font)
        
        # 设置按钮样式
        # self.update_button_styles()  # 移除这里的调用，放到所有按钮初始化后

        for btn in (self.btn_home, self.btn_about, self.btn_iconfont):
            btn.setFixedHeight(40)
            sidebar_layout.addWidget(btn)
        self.btn_home.clicked.connect(lambda: self.route("home"))
        self.btn_about.clicked.connect(lambda: self.route("about"))
        self.btn_iconfont.clicked.connect(lambda: self.route("iconfont"))
        sidebar_layout.addStretch()

        main_layout.addWidget(self.sidebar)

        # 右侧主内容区
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 顶部自定义窗口按钮
        titlebar_widget = QWidget()
        titlebar_widget.setFixedHeight(28)
        titlebar_widget.setStyleSheet("background: white; border-bottom: 1px solid #f7f7ff;")
        
        # 添加顶部窗口阴影效果
        titlebar_shadow = QGraphicsDropShadowEffect()
        titlebar_shadow.setBlurRadius(15)
        titlebar_shadow.setXOffset(0)
        titlebar_shadow.setYOffset(2)
        titlebar_shadow.setColor(QColor(0, 0, 0, 30))
        titlebar_widget.setGraphicsEffect(titlebar_shadow)
        titlebar = QHBoxLayout(titlebar_widget)
        titlebar.setContentsMargins(0, 0, 0, 0)
        titlebar.setSpacing(0)
        titlebar.addStretch()
        
        # 设置按钮（放在窗口控制按钮之前）
        self.btn_settings = SidebarButton(centered=True)
        self.btn_settings.setFont(remix_font)
        self.btn_settings.setText("\uf0e6")
        self.btn_settings.setFixedSize(32, 28)
        self.btn_settings.clicked.connect(lambda: self.route("settings"))
        self.btn_settings.update_style()
        titlebar.addWidget(self.btn_settings)
        
        # 刷新按钮（紧跟设置按钮右侧）
        self.btn_refresh = SidebarButton(centered=True)
        self.btn_refresh.setFont(remix_font)
        self.btn_refresh.setText("\uf064")
        self.btn_refresh.setFixedSize(32, 28)
        self.btn_refresh.clicked.connect(self.refresh_current_route)
        self.btn_refresh.update_style()
        titlebar.addWidget(self.btn_refresh)
        
        # 收起按钮（最小化）
        self.btn_min = SidebarButton(centered=True)
        self.btn_min.setFont(remix_font)
        self.btn_min.setText("—")
        self.btn_min.setFixedSize(32, 28)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_min.update_style()
        titlebar.addWidget(self.btn_min)
        # 最大化/还原按钮用TitleBarButton
        self.btn_max = TitleBarButton()
        self.btn_max.setFont(remix_font)
        self.btn_max.setFixedSize(32, 28)
        self.btn_max.clicked.connect(self.toggle_max_restore)
        if self.isMaximized():
            self.btn_max.setText("\ued9a")
        else:
            self.btn_max.setText("\ued9b")
        self.btn_max.update_style()
        titlebar.addWidget(self.btn_max)
        btn_close = QPushButton("×")
        self.btn_close = SidebarButton(centered=True)
        self.btn_close.setFont(remix_font)
        self.btn_close.setText("\ueb99")
        self.btn_close.setFixedSize(32, 28)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.update_style()
        titlebar.addWidget(self.btn_close)
        content_layout.addWidget(titlebar_widget)

        # 页面堆栈
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        # 懒加载页面：只存类，不存实例
        self.views = {
            "home": HomeView,
            "about": AboutView,
            "iconfont": IconFontView,
            "settings": SettingsView,
        }
        self._page_instances = {}
        self.route("home")

        main_layout.addWidget(content_widget)

        # 右下角缩放控件
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent;")
        self.size_grip.setFixedSize(16, 16)
        self.size_grip.raise_()

        # 所有按钮初始化后再调用
        self.update_button_styles()
        self.update_sidebar_texts()  # 新增：初始化时同步文字显示

        # 全局自定义ToolTip样式（更小字号、更大padding、圆角、灰色字体、左侧有黑色图标，图标有浅灰圆背景且居中）
        QApplication.instance().setStyleSheet(QApplication.instance().styleSheet() + """
QToolTip {
    background: #fff;
    color: #888;
    border-radius: 12px;
    padding: 10px 20px 10px 44px;
    font-size: 11px;
    min-width: 90px;
    border: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    position: relative;
}
QToolTip QLabel#icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    border-radius: 10px;
    background: #f2f3f5;
    color: #111;
    font-family: remixicon;
    font-size: 13px;
    text-align: center;
    line-height: 20px;
    display: inline-block;
}
""")
        # 初始化通知管理器
        self.notification_manager = NotificationManager(self)

    def create_rounded_mask(self):
        """创建圆角遮罩"""
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def update_button_styles(self):
        """更新按钮样式，根据选中状态设置不同的样式"""
        # 设置选中状态
        self.btn_home.is_selected = (self.current_route == "home")
        self.btn_about.is_selected = (self.current_route == "about")
        self.btn_iconfont.is_selected = (self.current_route == "iconfont")
        
        # 更新样式
        self.btn_home.update_style()
        self.btn_about.update_style()
        self.btn_iconfont.update_style()
        
        # 更新顶部设置按钮样式
        self.btn_settings.is_selected = (self.current_route == "settings")
        self.btn_settings.update_style()

    def update_sidebar_texts(self):
        expanded = self.sidebar_expanded
        self.btn_home.update_text(expanded)
        self.btn_about.update_text(expanded)
        self.btn_iconfont.update_text(expanded)
        # toggle_btn 只切换icon
        if expanded:
            self.toggle_btn.setText("\uf4f6")  # menu-fold-3-fill
        else:
            self.toggle_btn.setText("\uf4f8")  # menu-unfold-3-fill

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - self.size_grip.width(), self.height() - self.size_grip.height())
        # 重新创建圆角遮罩
        self.create_rounded_mask()

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.create_rounded_mask()
            self.btn_max.setText("\ued9b")
            self.btn_max.update_style()
        else:
            self.showMaximized()
            self.setMask(QRegion())
            self.btn_max.setText("\ued9a")
            self.btn_max.update_style()
            # 全屏时弹出通知
            self.notification_manager.show_info("按Esc可以退出全屏", "提示", 2500)

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        start = self.sidebar.minimumWidth()
        end = SIDEBAR_WIDTH if self.sidebar_expanded else SIDEBAR_COLLAPSED
        # 动画
        if self._sidebar_anim:
            self._sidebar_anim.stop()
        self._sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self._sidebar_anim.setDuration(ANIMATION_DURATION)
        self._sidebar_anim.setStartValue(start)
        self._sidebar_anim.setEndValue(end)
        self._sidebar_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._sidebar_anim.start()
        # 动画结束后切换文字显示
        QTimer.singleShot(ANIMATION_DURATION, self.update_sidebar_texts)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            if self._on_edge(pos):
                self._resizing = True
                self._resize_dir = self._get_resize_dir(pos)
                self._drag_pos = event.globalPosition().toPoint()
                self._start_geom = self.geometry()
            elif self._on_titlebar(pos):
                self._drag_pos = event.globalPosition().toPoint()
                self._drag_offset = self._drag_pos - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self._resizing and self._resize_dir:
            self._resize_window(event.globalPosition().toPoint())
        elif self._drag_pos and self._drag_offset:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        else:
            self._update_cursor(pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._drag_offset = None
        self._resizing = False
        self._resize_dir = None
        super().mouseReleaseEvent(event)

    def _on_titlebar(self, pos):
        # 只允许在主内容区顶部拖动
        sidebar_w = self.sidebar.minimumWidth()
        titlebar_h = 40
        return sidebar_w <= pos.x() <= self.width() and 0 <= pos.y() <= titlebar_h

    def _on_edge(self, pos):
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        return (
            x < BORDER_WIDTH or x > w - BORDER_WIDTH or
            y < BORDER_WIDTH or y > h - BORDER_WIDTH
        )

    def _get_resize_dir(self, pos):
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        dirs = []
        if x < BORDER_WIDTH:
            dirs.append('l')
        if x > w - BORDER_WIDTH:
            dirs.append('r')
        if y < BORDER_WIDTH:
            dirs.append('t')
        if y > h - BORDER_WIDTH:
            dirs.append('b')
        return ''.join(dirs)

    def _resize_window(self, global_pos):
        dx = global_pos.x() - self._drag_pos.x()
        dy = global_pos.y() - self._drag_pos.y()
        geom = QRect(self._start_geom)
        if 'l' in self._resize_dir:
            geom.setLeft(geom.left() + dx)
        if 'r' in self._resize_dir:
            geom.setRight(geom.right() + dx)
        if 't' in self._resize_dir:
            geom.setTop(geom.top() + dy)
        if 'b' in self._resize_dir:
            geom.setBottom(geom.bottom() + dy)
        minw, minh = 400, 300
        if geom.width() < minw:
            geom.setWidth(minw)
        if geom.height() < minh:
            geom.setHeight(minh)
        self.setGeometry(geom)

    def _update_cursor(self, pos):
        dir = self._get_resize_dir(pos)
        if dir in ('l', 'r'):
            self.setCursor(Qt.SizeHorCursor)
        elif dir in ('t', 'b'):
            self.setCursor(Qt.SizeVerCursor)
        elif dir in ('lt', 'rb'):
            self.setCursor(Qt.SizeFDiagCursor)
        elif dir in ('rt', 'lb'):
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def route(self, name):
        self.current_route = name
        if name not in self._page_instances:
            page_instance = self.views[name]()
            self._page_instances[name] = page_instance
            self.stack.addWidget(page_instance)
        self.stack.setCurrentWidget(self._page_instances[name])
        self.update_button_styles() 

    def close(self):
        dlg = CloseConfirmDialog(self)
        result = dlg.exec()
        if result == 1:
            super().close()
        elif result == 2:
            self.showMinimized()
        # result == 0 时什么都不做

    def keyPressEvent(self, event):
        from PySide6.QtGui import QKeySequence
        if self.isMaximized() and event.key() == Qt.Key_Escape:
            self.toggle_max_restore()
            event.accept()
            return
        # 移除 Ctrl+Q 关闭弹窗逻辑
        super().keyPressEvent(event)

    def refresh_current_route(self):
        # 刷新当前页面实例（重新实例化并替换）
        name = self.current_route
        if name in self._page_instances:
            page = self._page_instances.pop(name)
            self.stack.removeWidget(page)
            page.deleteLater()
        page_instance = self.views[name]()
        self._page_instances[name] = page_instance
        self.stack.addWidget(page_instance)
        self.stack.setCurrentWidget(page_instance)
        self.update_button_styles()

class CustomRadioButton(QRadioButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.icon_label = QLabel(self)
        self.icon_label.setText("\ueb7b")
        remix_font = QFont("remixicon")
        remix_font.setPointSize(11)
        self.icon_label.setFont(remix_font)
        self.icon_label.setStyleSheet("color: white; background: transparent;")
        self.icon_label.setFixedSize(14, 14)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.hide()
        self.toggled.connect(self._update_icon)
        self._update_icon(self.isChecked())

    def showEvent(self, event):
        super().showEvent(event)
        self._move_icon_to_indicator()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._move_icon_to_indicator()

    def _move_icon_to_indicator(self):
        opt = self.styleOption()
        indicator_rect = self.style().subElementRect(QStyle.SE_RadioButtonIndicator, opt, self)
        # 视觉微调，部分平台indicator本身就有1px偏移
        offset_x = 0
        offset_y = 1  # 可根据实际视觉效果调整
        x = indicator_rect.x() + (indicator_rect.width() - self.icon_label.width()) // 2 + offset_x
        y = indicator_rect.y() + (indicator_rect.height() - self.icon_label.height()) // 2 + offset_y
        self.icon_label.move(x, y)

    def styleOption(self):
        from PySide6.QtWidgets import QStyleOptionButton
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        return opt

    def _update_icon(self, checked):
        self.icon_label.setVisible(checked)

class CloseConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setFixedSize(320, 220)
        self.setStyleSheet("border-radius: 12px; background: transparent;")
        # 渐变背景
        self.bg_color1 = QColor("#e3eaff")
        self.bg_color2 = QColor("#ffffff")
        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        # 标题
        title = QLabel("温馨提示", self)
        title.setStyleSheet("font-size: 20px; color: #2628f3; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignHCenter)
        # 内容
        content = QLabel("是否确认关闭", self)
        content.setStyleSheet("font-size: 15px; color: #333; margin-top: 8px;")
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content, alignment=Qt.AlignHCenter)
        # 单选按钮
        from PySide6.QtWidgets import QButtonGroup
        radio_layout = QHBoxLayout()
        self.radio_close = CustomRadioButton("直接关闭", self)
        self.radio_min = CustomRadioButton("收起", self)
        radio_style = """
            QRadioButton {
                font-size: 14px;
                color: #2628f3;
                padding: 2px 8px;
            }
            QRadioButton::indicator {
                width: 14px; height: 14px;
                border-radius: 7px;
                border: 1.5px solid #b3c6f7;
                background: #fff;
                margin-right: 6px;
            }
            QRadioButton::indicator:hover {
                border: 1.5px solid #2628f3;
            }
            QRadioButton::indicator:checked {
                background: #2628f3;
                border: 1.5px solid #2628f3;
            }
        """
        self.radio_close.setStyleSheet(radio_style)
        self.radio_min.setStyleSheet(radio_style)
        self.radio_close.setCursor(Qt.PointingHandCursor)
        self.radio_min.setCursor(Qt.PointingHandCursor)
        self.radio_close.setChecked(True)
        radio_group = QButtonGroup(self)
        radio_group.addButton(self.radio_close)
        radio_group.addButton(self.radio_min)
        radio_layout.addWidget(self.radio_close)
        radio_layout.addWidget(self.radio_min)
        layout.addLayout(radio_layout)
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("取消", self)
        btn_ok = QPushButton("确认", self)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #f5f7fa; color: #2628f3; font-size: 15px; border-radius: 6px; padding: 8px 24px; border: 1px solid #e3eaff;
            }
            QPushButton:hover {
                background: #e3eaff;
            }
        """)
        btn_ok.setStyleSheet("""
            QPushButton {
                background: #2628f3; color: white; font-size: 15px; border-radius: 6px; padding: 8px 24px;
            }
            QPushButton:hover {
                background: #1a1cc7;
            }
        """)
        btn_cancel.clicked.connect(lambda: self.done(0))
        btn_ok.clicked.connect(self._on_ok)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
        # 提示音
        self.sound = QSoundEffect(self)
        self.sound.setSource(QUrl.fromLocalFile("/System/Library/Sounds/Funk.aiff"))
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.bg_color1)
        gradient.setColorAt(1, self.bg_color2)
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
    def _on_ok(self):
        if self.radio_close.isChecked():
            self.done(1)  # 直接关闭
        else:
            self.done(2)  # 收起

    def showEvent(self, event):
        QApplication.instance().installEventFilter(self)
        super().showEvent(event)
    def closeEvent(self, event):
        QApplication.instance().removeEventFilter(self)
        super().closeEvent(event)
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.isVisible():
                pos = event.globalPosition().toPoint() if hasattr(event, 'globalPosition') else event.globalPos()
                if not self.geometry().contains(pos):
                    self.play_alert()
                    return True
        return super().eventFilter(obj, event)
    def play_alert(self):
        self.sound.play() 