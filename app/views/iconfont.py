from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QGridLayout, QScrollArea, QMessageBox, QApplication, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QClipboard, QFontDatabase
from app.utils.notification import NotificationManager
import os, re

ICONS_PER_PAGE = 60

class IconItem(QWidget):
    def __init__(self, icon_data, parent=None):
        super().__init__(parent)
        self.icon_data = icon_data
        # 确保不会创建独立窗口
        self.setWindowFlags(Qt.Widget)
        # 确保有父窗口
        # if not parent:
            # print("警告: IconItem没有父窗口")
        self.setup_ui()
        
    @staticmethod
    def patch_unicode_param(s):
        import re
        return re.sub(r'\\([a-fA-F0-9]{4})', r'\\u\1', s)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)  # 增加间距
        
        # 图标显示 - 用真实Unicode字符
        try:
            unicode_str = self.icon_data['uni'].strip('"').replace('\\', '')
            unicode_char = chr(int(unicode_str, 16))
        except Exception as e:
            print(f"解码失败: {self.icon_data['uni']} - {e}")
            unicode_char = "?"
        # 创建图标预览容器 - 只包含图标本身
        icon_container = QWidget(self)
        icon_container.setStyleSheet("background: #f5f7fa; border-radius: 4px; padding: 12px; min-height: 45px;")
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        icon_label = QLabel(unicode_char, icon_container)  # 预览用真实字符
        icon_label.setWindowFlags(Qt.Widget)
        remix_font = QFont("remixicon")
        remix_font.setPointSize(20)
        icon_label.setFont(remix_font)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: #2628f3; background: transparent;")
        icon_label.setCursor(Qt.PointingHandCursor)
        icon_label.mousePressEvent = lambda event: self.copy_unicode()
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)
        
        # 英文名 - 在图标预览区域外，独立显示
        name_label = QLabel(self.icon_data['name'], self)  # 明确指定父窗口
        name_label.setWindowFlags(Qt.Widget)  # 确保不会创建独立窗口
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            font-size: 11px; 
            color: #333; 
            font-weight: bold; 
            margin-top: 8px;
            margin-bottom: 4px;
            background: #f8f9fa;
            border-radius: 3px;
            padding: 4px 6px;
        """)
        name_label.setWordWrap(False)
        name_label.setToolTip(self.icon_data['name'])  # 鼠标悬停显示完整名称
        name_label.setCursor(Qt.PointingHandCursor)
        name_label.mousePressEvent = lambda event: self.copy_name()
        layout.addWidget(name_label)
        
        # Unicode - 支持省略号
        param_unicode = self.patch_unicode_param(self.icon_data['uni'])
        uni_label = QLabel(param_unicode, self)  # 参数用\uXXXX字符串
        uni_label.setWindowFlags(Qt.Widget)
        uni_label.setAlignment(Qt.AlignCenter)
        uni_label.setStyleSheet("""
            font-size: 9px; 
            color: #90a4ae; 
            background: transparent;
            margin-top: 2px;
        """)
        uni_label.setWordWrap(False)
        uni_label.setToolTip(param_unicode)
        uni_label.setCursor(Qt.PointingHandCursor)
        uni_label.mousePressEvent = lambda event: self.copy_unicode()
        layout.addWidget(uni_label)
        
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px;
            }
            QWidget:hover {
                border: 2px solid #2628f3;
                background: #f8f9fa;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 点击卡片其他区域复制unicode
            self.copy_unicode()
        super().mousePressEvent(event)
        
    def copy_name(self):
        """复制英文名"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.icon_data['name'])
        # 显示通知
        if hasattr(self, 'parent') and self.parent():
            # 向上查找IconFontView实例
            current = self.parent()
            while current and not isinstance(current, IconFontView):
                current = current.parent()
            if current:
                current.notification_manager.show_success(
                    f"已复制英文名: {self.icon_data['name']}", 
                    "复制成功"
                )
        
    def copy_unicode(self):
        r"""复制unicode参数（以\uXXXX格式）"""
        clipboard = QApplication.clipboard()
        param_unicode = self.patch_unicode_param(self.icon_data['uni'])
        clipboard.setText(param_unicode)
        # 显示通知
        if hasattr(self, 'parent') and self.parent():
            current = self.parent()
            while current and not isinstance(current, IconFontView):
                current = current.parent()
            if current:
                current.notification_manager.show_success(
                    f"已复制Unicode参数: {param_unicode}",
                    "复制成功"
                )
        
    def copy_icon_name(self):
        """保持向后兼容的方法"""
        self.copy_unicode()

class ResponsiveGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 确保不会创建独立窗口
        self.setWindowFlags(Qt.Widget)
        # 设置网格背景色
        self.setStyleSheet("background-color: #f5f7fa;")
        self.grid = QGridLayout(self)
        self.grid.setSpacing(16)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.items = []
        self.item_width = 120  # 每个item的基础宽度
        self.item_height = 120  # 每个item的基础高度
        self.min_cols = 3  # 最少3列
        self.max_cols = 12  # 最多12列
        
        # 添加窗体变化检测
        self.last_size = None
        self.layout_update_timer = QTimer()
        self.layout_update_timer.setSingleShot(True)
        self.layout_update_timer.timeout.connect(self._perform_layout_update)
        
    def add_item(self, item):
        # 确保item有正确的父窗口
        if item.parent() != self:
            item.setParent(self)
        self.items.append(item)
        self.update_layout()
        
    def clear_items(self):
        # 安全地清空items，避免widget被销毁
        for item in self.items:
            if item and item.parent() == self:
                self.grid.removeWidget(item)
        self.items.clear()
        
    def update_layout(self):
        """立即执行布局更新"""
        # 停止定时器，立即执行
        self.layout_update_timer.stop()
        self._perform_layout_update()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # 检查窗体大小是否真的发生了变化
        current_size = self.size()
        if self.last_size != current_size:
            self.last_size = current_size
            print(f"窗体大小变化: {current_size}")
            # 使用防抖机制，避免频繁更新
            self.layout_update_timer.start(50)
        
    def _validate_layout(self, cols, actual_item_width, spacing, available_width):
        """验证布局计算的正确性"""
        # 验证公式: available_width = cols * actual_item_width + (cols - 1) * spacing
        calculated_width = cols * actual_item_width + (cols - 1) * spacing
        if abs(calculated_width - available_width) > 5:  # 允许5px的误差
            print(f"布局验证失败: 计算宽度 {calculated_width} != 可用宽度 {available_width}")
            return False
        return True
        
    def _perform_layout_update(self):
        """执行实际的布局更新"""
        if not self.items:
            return
            
        # 获取实际可用宽度（考虑父窗口的布局变化）
        total_width = self.width()
        
        # 动态计算边距和滚动条宽度
        scrollbar_width = 8  # 固定滚动条宽度
        margins = 32  # 左右边距
        available_width = total_width - margins - scrollbar_width
        
        if available_width <= 0:
            print(f"可用宽度不足: {available_width}, 总宽度: {total_width}")
            return
            
        # 根据可用宽度动态调整布局参数
        if available_width < 400:
            base_item_width = 100  # 小屏幕
            spacing = 12
        elif available_width < 800:
            base_item_width = 120  # 中等屏幕
            spacing = 16
        else:
            base_item_width = 140  # 大屏幕
            spacing = 20
            
        # 计算每行能放多少个item
        # 公式: available_width = cols * item_width + (cols - 1) * spacing
        # 解出: cols = (available_width + spacing) / (item_width + spacing)
        cols = max(self.min_cols, min(self.max_cols, 
                                     (available_width + spacing) // (base_item_width + spacing)))
        
        # 计算实际item宽度（平均分配剩余空间）
        total_spacing = (cols - 1) * spacing
        actual_item_width = (available_width - total_spacing) // cols
        
        # 确保item宽度合理，如果太小就减少列数
        min_item_width = 80
        while actual_item_width < min_item_width and cols > self.min_cols:
            cols -= 1
            total_spacing = (cols - 1) * spacing
            actual_item_width = (available_width - total_spacing) // cols
        
        # 验证布局计算的正确性
        if not self._validate_layout(cols, actual_item_width, spacing, available_width):
            print("布局验证失败，跳过更新")
            return
        
        print(f"布局计算: 总宽度 {total_width}, 可用宽度 {available_width}, 列数 {cols}, item宽度 {actual_item_width}, 间距 {spacing}")
        
        # 安全地清空现有布局
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item and item.widget():
                self.grid.removeWidget(item.widget())
        
        # 重新排列并设置item大小
        for idx, item in enumerate(self.items):
            row, col = divmod(idx, cols)
            self.grid.addWidget(item, row, col)
            # 设置item固定大小
            item.setFixedSize(actual_item_width, self.item_height)
            
        # 强制更新布局
        self.grid.update()
        self.updateGeometry()
        
        # 确保父窗口也更新布局
        if self.parent():
            self.parent().updateGeometry()

class IconFontView(QWidget):
    def __init__(self):
        super().__init__()
        # 设置页面背景色
        # self.setStyleSheet("background-color: #fff;")
        # 确保字体已加载
        self.ensure_font_loaded()
        
        # 初始化通知管理器
        self.notification_manager = NotificationManager(self)
        
        # 添加搜索防抖定时器
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("图标库")
        title.setStyleSheet("font-size: 24px; color: #2628f3; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)
        
        subtitle = QLabel("点击任意图标项可复制英文名")
        subtitle.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 16px;")
        layout.addWidget(subtitle)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_label.setStyleSheet("font-size: 14px; color: #333; margin-right: 8px;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入英文名或unicode搜索，如 home、\\uebba ...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #2628f3;
            }
        """)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 分页控制
        page_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀ 上一页")
        self.next_btn = QPushButton("下一页 ▶")
        self.page_label = QLabel()
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #2628f3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #2628f3;
                }
                QPushButton:disabled {
                    background: #ccc;
                }
            """)
            
        self.page_label.setStyleSheet("font-size: 14px; color: #666; margin: 0 16px;")
        
        page_layout.addWidget(self.prev_btn)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(self.next_btn)
        page_layout.addStretch()
        
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        layout.addLayout(page_layout)
        
        # 自定义滚动区域 - 隐藏滚动条
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        # 使用响应式网格
        self.grid_widget = ResponsiveGridWidget()
        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)
        
        # 加载图标数据
        self.icons = self.load_icons()
        self.filtered_icons = self.icons
        self.page = 0
        self.refresh()

    def ensure_font_loaded(self):
        """确保 remixicon 字体已加载"""
        font_path = os.path.join(os.path.dirname(__file__), '../assets/fonts/remixicon.ttf')
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                print(f"警告: 无法加载字体文件 {font_path}")
            else:
                print(f"字体加载成功: {font_path}")
        else:
            print(f"警告: 字体文件不存在 {font_path}")

    def load_icons(self):
        css_path = os.path.join(os.path.dirname(__file__), '../assets/fonts/remixicon.css')
        icon_re = re.compile(r'\.ri-([\w\-]+):before \{ content: "(\\[a-fA-F0-9]+)"; \}')
        icons = []
        try:
            with open(css_path, encoding='utf-8') as f:
                for line in f:
                    m = icon_re.search(line)
                    if m:
                        name, uni = m.group(1), m.group(2)
                        icons.append({'name': name, 'uni': uni})
            print(f"成功加载 {len(icons)} 个图标")
        except Exception as e:
            print(f"加载图标文件失败: {e}")
        return icons

    def refresh(self):
        try:
            # 清空现有内容
            self.grid_widget.clear_items()
            
            # 分页计算
            total = len(self.filtered_icons)
            start = self.page * ICONS_PER_PAGE
            end = min(start + ICONS_PER_PAGE, total)
            icons = self.filtered_icons[start:end]
            
            # 更新分页信息
            total_pages = max(1, (total - 1) // ICONS_PER_PAGE + 1)
            self.page_label.setText(f"第 {self.page + 1} / {total_pages} 页  共 {total} 个图标")
            self.prev_btn.setEnabled(self.page > 0)
            self.next_btn.setEnabled(end < total)
            
            # 创建图标项 - 只创建当前页的图标
            for icon in icons:
                try:
                    icon_item = IconItem(icon)
                    self.grid_widget.add_item(icon_item)
                except Exception as e:
                    print(f"创建图标项失败: {e}")
                    continue
                    
            # 立即更新布局，不使用定时器
            self.grid_widget.update_layout()
            
        except Exception as e:
            print(f"刷新过程中出现错误: {e}")
            # 出错时尝试恢复
            try:
                self.filtered_icons = self.icons
                self.page = 0
                QTimer.singleShot(0, self.refresh)
            except:
                print("恢复失败")

    def copy_name(self, name):
        clipboard = QApplication.clipboard()
        clipboard.setText(name)
        # 移除弹窗，改为静默复制

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.refresh()

    def next_page(self):
        total = len(self.filtered_icons)
        total_pages = max(1, (total - 1) // ICONS_PER_PAGE + 1)
        if self.page < total_pages - 1:
            self.page += 1
            self.refresh()

    def on_search(self, text):
        # 直接使用传入的text参数，不需要重新设置输入框
        self.search_timer.start(300) # 延迟300ms执行搜索

    def perform_search(self):
        try:
            search_text = self.search_input.text()
            print(f"执行搜索: '{search_text}'")
            
            if not search_text:
                self.filtered_icons = self.icons
                print(f"清空搜索，显示所有 {len(self.icons)} 个图标")
            else:
                # 限制搜索结果数量，避免渲染卡顿
                filtered = []
                for icon in self.icons:
                    if search_text.lower() in icon['name'].lower() or search_text.lower() in icon['uni'].lower():
                        filtered.append(icon)
                        # 限制最多显示200个结果，避免卡顿
                        if len(filtered) >= 200:
                            break
                
                self.filtered_icons = filtered
                print(f"搜索结果: {len(filtered)} 个图标")
                
            # 重置页码并验证
            self.page = 0
            total = len(self.filtered_icons)
            total_pages = max(1, (total - 1) // ICONS_PER_PAGE + 1)
            
            # 确保页码在有效范围内
            if self.page >= total_pages:
                self.page = max(0, total_pages - 1)
                
            print(f"页码: {self.page + 1}/{total_pages}, 总图标数: {total}")
            
            # 立即执行refresh，不使用定时器
            self.refresh()
            
        except Exception as e:
            print(f"搜索过程中出现错误: {e}")
            # 出错时恢复显示所有图标
            self.filtered_icons = self.icons
            self.page = 0
            self.refresh()
            
    def showEvent(self, event):
        """显示事件，确保布局正确"""
        super().showEvent(event)
        # 显示时更新布局
        QTimer.singleShot(0, self.update_layout) 

    def update_layout(self):
        pass  # TODO: 实现布局更新逻辑 