from PyQt5.QtWidgets import (QMainWindow, QListWidget, QPushButton, 
                            QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, 
                            QLabel, QListWidgetItem, QSplitter, QApplication,
                            QInputDialog, QMessageBox, QDialog)  # 添加QDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon
import os
import shutil
from PyQt5.QtWidgets import QInputDialog, QMessageBox
import sqlite3
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMenu, 
                            QSystemTrayIcon, QAction, QVBoxLayout, QSlider)  # Added QSlider
from PyQt5.QtCore import Qt
# 管理器类 - 用于管理所有的像素小伴
# 该类的作用是提供一个统一的接口，用于操作所有的像素小伴，方便其他模块调用。
# 该类的方法包括：
#   - init: 初始化管理器，创建一个空的像素小伴列表。    
#   - add_pet: 添加一个像素小伴，包括名称和帧目录。
#   - delete_pet: 删除一个像素小伴，根据名称删除。
#   - get_all_pets: 获取所有像素小伴的信息，返回一个字典，键为名称，值为帧目录。
#   - get_pet: 获取指定名称的像素小伴的信息，返回帧目录。
#   - update_pet: 更新像素小伴的信息，根据名称更新帧目录。
#   - load_pets: 从数据库加载所有像素小伴的信息。
#   - save_pets: 保存所有像素小伴的信息到数据库。
#   - rename_pet: 重命名像素小伴，根据名称更新帧目录。
class PixelPalManager(QMainWindow): 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("像素小伴管理器")  # 原"桌宠管理器"
        # 设置窗口图标
        self.setWindowIcon(QIcon("img/icon.png"))
        # 获取屏幕尺寸并计算居中位置
        screen = QApplication.primaryScreen().geometry()
        width = 870
        height = 630
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)
        self.initUI()
        
    def initUI(self):
        
        # Initialize the main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 添加窗口样式 - 设置白色背景
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QMessageBox {
            background-color: white;
            }
            QMessageBox QLabel {
                color: #333;
            }
        """)
        
        # 主布局使用水平分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧列表区域
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.pet_list = QListWidget()
        self.pet_list.setFixedWidth(200)  # 固定列表宽度
        self.pet_list.itemClicked.connect(self.on_pet_selected)
        left_layout.addWidget(self.pet_list)
        
        # 添加按钮区域
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加")
        del_btn = QPushButton("删除")
        rename_btn = QPushButton("重命名")  # 新增重命名按钮
        add_btn.clicked.connect(self.add_pet)
        del_btn.clicked.connect(self.del_pet)
        rename_btn.clicked.connect(self.rename_pet)  # 连接重命名方法
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(rename_btn)  # 添加按钮到布局
        left_layout.addLayout(btn_layout)
        
        left_panel.setLayout(left_layout)
        
        # 右侧预览区域
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(400, 400)  # 放大预览区域
        right_layout.addWidget(self.preview_label)
        
        right_panel.setLayout(right_layout)
        
        # 添加左右面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        self.load_pets()
        
    def on_pet_selected(self, item):
        # 先停止之前的动画定时器
        if hasattr(self.preview_label, 'timer'):
            self.preview_label.timer.stop()
        
        pet_name = item.text()
        main_window = self.parent()
        frames_dir = main_window.db.get_pet(pet_name)
        self.setup_preview_animation(frames_dir)

    def setup_preview_animation(self, frames_dir):
        """设置预览动画"""
        # 加载动画帧
        frames = []
        frame_files = sorted(
            [f for f in os.listdir(frames_dir) if f.endswith('.png')],
            key=lambda x: int(x.split('.')[0].replace('frame', ''))
        )
        
        for frame_file in frame_files:
            pixmap = QPixmap(os.path.join(frames_dir, frame_file))
            # 缩放图片到合适大小并保持透明区域
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            frames.append(pixmap)
        
        # 设置新的动画定时器
        timer = QTimer(self.preview_label)
        current_frame = 0
        def update_frame():
            nonlocal current_frame
            if frames:
                # 创建透明背景的QPixmap
                transparent_pixmap = QPixmap(400, 400)
                transparent_pixmap.fill(Qt.transparent)
                
                # 计算居中位置
                x = (400 - frames[current_frame].width()) // 2
                y = (400 - frames[current_frame].height()) // 2
                
                # 在透明背景上绘制居中图片
                painter = QPainter(transparent_pixmap)
                painter.drawPixmap(x, y, frames[current_frame])
                painter.end()
                
                self.preview_label.setPixmap(transparent_pixmap)
                current_frame = (current_frame + 1) % len(frames)
        
        timer.timeout.connect(update_frame)
        timer.start(100)
        self.preview_label.timer = timer  # 保存定时器引用
        
    def update_pet_list(self):
        """更新宠物列表显示"""
        self.pet_list.clear()
        main_window = self.parent()  # 获取父窗口引用
        pets = main_window.db.get_all_pets()  # 通过父窗口访问db
        for pet in pets:
            self.pet_list.addItem(pet)
            
    def add_pet(self):
        folder = QFileDialog.getExistingDirectory(self, "选择宠物动画帧文件夹")
        if folder:
            main_window = self.parent()
            
            # 获取当前所有宠物
            existing_pets = main_window.db.get_all_pets()
            
            # 查找可用的文件夹名称
            folder_num = 1
            while f"pet{folder_num}_frames" in [os.path.basename(os.path.dirname(p)) for p in existing_pets.values()]:
                folder_num += 1
            
            # 获取用户自定义的宠物名称
            dialog = QInputDialog(self)
            dialog.setWindowTitle("宠物命名")
            dialog.setLabelText("请输入宠物显示名称:")
            dialog.setTextValue(f"宠物{folder_num}")
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                    font-family: 'Microsoft YaHei';
                }
                QLabel {
                    font-size: 16px;
                    color: #333;
                }
                QLineEdit {
                    font-size: 16px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            
            ok = dialog.exec_() == QDialog.Accepted
            pet_name = dialog.textValue() if ok else ""
            
            if ok and pet_name:
                if not main_window.db.get_pet(pet_name):
                    # 创建目标文件夹
                    target_folder = f"img/pet{folder_num}_frames"
                    os.makedirs(target_folder, exist_ok=True)
                    
                    # 复制文件到目标文件夹
                    for file in os.listdir(folder):
                        if file.endswith('.png'):
                            shutil.copy2(os.path.join(folder, file), target_folder)
                    
                    # 保存到数据库
                    main_window.db.add_pet(pet_name, target_folder + "/")
                    self.pet_list.addItem(pet_name)
                    self.load_pets()
                    self.update_pet_list()  # 更新管理界面列表
                    main_window.initPet()   # 通知主窗口刷新宠物列表
                else:
                    QMessageBox.warning(self, "错误", "该名称已存在")

    def del_pet(self):
        current_item = self.pet_list.currentItem()
        if current_item:
            pet_name = current_item.text()
            main_window = self.parent()
            # 检查是否是当前正在使用的宠物
            if pet_name == main_window.current_pet:
                QMessageBox.warning(self, "警告", "无法删除正在使用的宠物，请先切换到其他宠物")
                return
            # 确认删除
            reply = QMessageBox.question(self, "确认删除", f"确定要删除宠物 '{pet_name}' 吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            # 先从数据库获取实际文件夹路径
            frames_dir = main_window.db.get_pet(pet_name)
            if frames_dir:
                # 删除数据库记录
                main_window.db.delete_pet(pet_name)
                # 删除对应的文件夹
                try:
                    shutil.rmtree(frames_dir.rstrip('/'))  # 移除末尾的斜杠
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"删除文件夹失败: {str(e)}")
                # 从列表移除
                self.pet_list.takeItem(self.pet_list.row(current_item))
                main_window.initPet()  # 重新初始化以下宠物。
            shutil.rmtree(f"img/{pet_name}_frames", ignore_errors=True)

    def load_pets(self):
        """Load all pets from database and populate the list"""
        main_window = self.parent()
        self.pet_list.clear()
        
        pets = main_window.db.get_all_pets()
        for pet_name in pets:
            item = QListWidgetItem(pet_name)
            self.pet_list.addItem(item)
        
        # 自动选择并预览第一个宠物
        if self.pet_list.count() > 0:
            first_item = self.pet_list.item(0)
            self.pet_list.setCurrentItem(first_item)
            self.on_pet_selected(first_item)

    def rename_pet(self):
        current_item = self.pet_list.currentItem()
        if current_item:
            old_name = current_item.text()
            
            # 创建对话框但不立即执行
            dialog = QInputDialog(self)
            dialog.setWindowTitle("重命名宠物")
            dialog.setLabelText("输入新名称:")
            dialog.setTextValue(old_name)
            
            # 设置对话框样式
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    font-family: 'Microsoft YaHei';
                    font-size: 16px;
                    color: #333;
                }
                QLineEdit {
                    font-family: 'Microsoft YaHei';
                    font-size: 16px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            
            # 使用exec_()而不是getText()来保持对话框模态
            if dialog.exec_() == QDialog.Accepted:
                new_name = dialog.textValue()
                if new_name and new_name != old_name:
                    try:
                        main_window = self.parent()
                        frames_dir = main_window.db.get_pet(old_name)
                        if frames_dir:
                            main_window.db.update_pet(old_name, new_name, frames_dir)
                            current_item.setText(new_name)
                            main_window.pets = main_window.db.get_all_pets()
                    except sqlite3.IntegrityError:
                        QMessageBox.warning(self, "错误", "该名称已存在")
