from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QIcon

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 作为子窗口，不使用独立窗口标志
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()
        
    # 通知状态定义
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 通知内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background: #2628f3;
                border-radius: 8px;
                border: none;
            }
        """)
        
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(6)
        
        # 图标容器
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            color: white;
            font-size: 11px;
            font-weight: bold;
            background: transparent;
        """)
        content_layout.addWidget(self.icon_label)
        
        # 文本内容容器
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        
        # 标题
        self.title_label = QLabel("复制成功")
        self.title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: white;
            margin: 0;
            padding: 0;
            background: transparent;
        """)
        text_layout.addWidget(self.title_label)
        
        # 消息
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            font-size: 10px;
            color: rgba(255, 255, 255, 0.9);
            margin: 0;
            padding: 0;
            background: transparent;
        """)
        self.message_label.setWordWrap(True)
        text_layout.addWidget(self.message_label)
        
        content_layout.addWidget(text_container)
        
        layout.addWidget(self.content_widget)
        
        # 设置固定宽度，高度自适应
        self.setFixedWidth(260)
        self.setMinimumHeight(45)
        self.setMaximumHeight(80)
        
        # 设置透明度效果
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # 默认状态
        self.current_status = self.SUCCESS
        
        # 动画
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(200)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self.on_fade_out_finished)
        
        # 移除位置移动动画，避免卡顿
        # self.move_animation = QPropertyAnimation(self, b"pos")
        # self.move_animation.setDuration(300)
        # self.move_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 自动隐藏定时器
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)
        
    def on_fade_out_finished(self):
        """淡出动画完成后的回调"""
        self.hide()
        # 通知管理器延迟重新排列其他通知
        if hasattr(self, 'notification_manager'):
            self.notification_manager.reposition_timer.start(50)
        
    def show_notification(self, message, title="复制成功", status=SUCCESS, duration=2000):
        """显示通知"""
        print(f"显示通知: {title} - {message} - {status}")  # 调试信息
        
        # 设置状态
        self.set_status(status)
        
        self.message_label.setText(message)
        self.title_label.setText(title)
        
        # 强制更新标签
        self.title_label.repaint()
        self.message_label.repaint()
        
        # 计算位置（右上角）
        if self.parent():
            parent_rect = self.parent().rect()
            notification_width = 260  # 固定宽度
            x = parent_rect.width() - notification_width - 20
            y = 28 + 16  # titlebar高度28 + 16px间距
            self.move(x, y)
            
            # 确保通知显示在最上层
            self.raise_()
            
            # 强制更新显示
            self.update()
            self.parent().update()
        
        # 显示动画
        self.show()
        self.fade_in_animation.start()
        
        # 设置自动隐藏
        self.hide_timer.start(duration)
        
    def set_status(self, status):
        """设置通知状态"""
        self.current_status = status
        self.update_style()
        
    def update_style(self):
        """根据状态更新样式"""
        status_config = {
            self.SUCCESS: {
                'background': '#10b981',
                'icon': '✓',
                'title': '成功'
            },
            self.ERROR: {
                'background': '#ef4444',
                'icon': '✕',
                'title': '错误'
            },
            self.WARNING: {
                'background': '#f59e0b',
                'icon': '⚠',
                'title': '警告'
            },
            self.INFO: {
                'background': '#3b82f6',
                'icon': 'ℹ',
                'title': '信息'
            }
        }
        
        config = status_config.get(self.current_status, status_config[self.SUCCESS])
        
        # 更新背景色
        self.content_widget.setStyleSheet(f"""
            QWidget {{
                background: {config['background']};
                border-radius: 8px;
                min-width: 200px;
                max-width: 300px;
                border: none;
            }}
        """)
        
        # 更新图标
        self.icon_label.setText(config['icon'])
        
    def fade_out(self):
        """淡出动画"""
        self.fade_out_animation.start()

class NotificationManager:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.notifications = []
        self.max_notifications = 3
        self.notification_height = 60  # 默认高度
        self.notification_spacing = 10
        
        # 查找主窗口
        self.main_window = self.find_main_window(parent_widget)
        
        # 添加延迟重新定位定时器
        self.reposition_timer = QTimer()
        self.reposition_timer.setSingleShot(True)
        self.reposition_timer.timeout.connect(self._delayed_reposition)
        
    def find_main_window(self, widget):
        """查找主窗口"""
        current = widget
        while current:
            # 检查是否是主窗口（有setWindowTitle方法且是QMainWindow）
            if hasattr(current, 'setWindowTitle') and hasattr(current, 'centralWidget'):
                return current
            current = current.parent()
        return None
        
    def show_notification(self, message, title="复制成功", status=NotificationWidget.SUCCESS, duration=2000):
        """显示通知"""
        # 创建新通知，使用主窗口作为父窗口
        parent = self.main_window if self.main_window else self.parent_widget
        notification = NotificationWidget(parent)
        
        # 确保通知在主窗口的中央部件上显示
        if self.main_window and hasattr(self.main_window, 'centralWidget'):
            central_widget = self.main_window.centralWidget()
            notification.setParent(central_widget)
        
        # 设置通知管理器引用
        notification.notification_manager = self
        
        notification.show_notification(message, title, status, duration)
        
        # 添加到通知列表
        self.notifications.append(notification)
        
        # 延迟重新排列通知位置，避免频繁计算
        self.reposition_timer.start(50)
        
        # 清理过期通知
        self.cleanup_notifications()
        
    def show_success(self, message, title="成功", duration=2000):
        """显示成功通知"""
        self.show_notification(message, title, NotificationWidget.SUCCESS, duration)
        
    def show_error(self, message, title="错误", duration=3000):
        """显示错误通知"""
        self.show_notification(message, title, NotificationWidget.ERROR, duration)
        
    def show_warning(self, message, title="警告", duration=2500):
        """显示警告通知"""
        self.show_notification(message, title, NotificationWidget.WARNING, duration)
        
    def show_info(self, message, title="信息", duration=2000):
        """显示信息通知"""
        self.show_notification(message, title, NotificationWidget.INFO, duration)
        
    def reposition_notifications(self):
        """重新排列通知位置"""
        parent = self.main_window if self.main_window else self.parent_widget
        if not parent:
            return
            
        # 使用主窗口的中央部件来计算位置
        if self.main_window and hasattr(self.main_window, 'centralWidget'):
            central_widget = self.main_window.centralWidget()
            parent_rect = central_widget.rect()
        else:
            parent_rect = parent.rect()
            
        # 确保窗口有有效尺寸
        if parent_rect.width() <= 0 or parent_rect.height() <= 0:
            return
            
        start_x = parent_rect.width() - 280  # 通知宽度 + 边距
        start_y = 20
        
        # 只处理可见的通知
        visible_notifications = [n for n in self.notifications if n.isVisible()]
        
        for i, notification in enumerate(visible_notifications):
            # 动态计算每个通知的高度
            notification_height = notification.height()
            target_y = start_y + i * (notification_height + self.notification_spacing)
            
            # 直接移动，不使用动画，避免卡顿
            notification.move(start_x, target_y)
            
    def cleanup_notifications(self):
        """清理隐藏的通知"""
        # 移除已隐藏的通知
        self.notifications = [n for n in self.notifications if n.isVisible()]
        
        # 限制最大通知数量
        if len(self.notifications) > self.max_notifications:
            oldest = self.notifications.pop(0)
            oldest.hide()
            oldest.deleteLater()
            
        # 延迟重新排列剩余通知
        self.reposition_timer.start(50)
        
    def _delayed_reposition(self):
        """延迟重新定位通知"""
        self.reposition_notifications()