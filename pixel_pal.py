import sys
import os
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMenu, 
                            QSystemTrayIcon, QAction, QVBoxLayout)
from PyQt5.QtGui import QPixmap, QMovie, QIcon  # Added QIcon to imports
from PyQt5.QtCore import Qt, QTimer, QPoint
from db_manager import PetDB
# 该类的作用是提供一个主窗口，用于显示宠物的动画。
# 该类的方法包括：
#   - initUI: 初始化窗口，设置窗口标题、样式、透明背景等。
#   - initPet: 初始化宠物信息，从数据库中获取所有宠物信息，并设置当前宠物。
#   - initTray: 初始化系统托盘，添加菜单和图标。
#   - initMovement: 初始化宠物的移动和方向。
#   - initAnimation: 初始化宠物的动画，从当前宠物的帧目录中获取所有图片，并设置定时器。
#   - updateFrame: 更新当前帧，从当前宠物的帧目录中获取所有图片，并设置定时器。
#   - changePet: 切换宠物，根据名称切换当前宠物，并更新动画。
#   - showMenu: 显示菜单，添加菜单选项，包括切换宠物、退出程序等。
#   - showTrayIcon: 显示系统托盘图标，添加菜单选项，包括切换宠物、退出程序等。
#   - mousePressEvent: 鼠标按下事件，用于拖动窗口。
#   - mouseMoveEvent: 鼠标移动事件，用于拖动窗口。
#   - randomDirection: 随机改变宠物的移动方向。
#   - movePet: 处理宠物的移动，根据当前方向和速度移动宠物。
#   - changeDir: 改变宠物的移动方向，根据当前方向和速度改变方向。
#   - updateFrame: 更新当前帧，从当前宠物的帧目录中获取所有图片，并设置定时器。
#   - updateAnimation: 更新动画，从当前宠物的帧目录中获取所有图片，并设置定时器。
#   - showEvent: 显示事件，用于更新窗口大小。
#   - closeEvent: 关闭事件，用于停止定时器和退出程序。
#   - trayIconActivated: 系统托盘图标激活事件，用于处理菜单选项。
#   - trayIconMessageClicked: 系统托盘图标消息点击事件，用于处理菜单选项。
#   - trayIconContextMenu: 系统托盘图标右键菜单事件，用于处理菜单选项。
#   - trayIconDoubleClicked: 系统托盘图标双击事件，用于处理菜单选项。
#   - trayIconTriggered: 系统托盘图标触发事件，用于处理菜单选项。
#   - trayIconMessage: 系统托盘图标消息事件，用于处理菜单选项。
#   - trayIconAboutToShow: 系统托盘图标即将显示事件，用于处理菜单选项。
#   - trayIconShown: 系统托盘图标显示事件，用于处理菜单选项。
#   - trayIconHidden: 系统托盘图标隐藏事件，用于处理菜单选项。

class PixelPal(QWidget):  
    def __init__(self):
        super().__init__()
        self.db = PetDB()
        self.current_pet = None  # Initialize current_pet first
        self.initUI()
        self.initPet()  # This will set current_pet
        self.initTray()
        self.initMovement()
        self.initAnimation()  # Now current_pet will be available
        
    def initUI(self):
        self.setWindowTitle("像素小伴")  # 添加这行
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.defaultSize = self.size()  # 记录默认大小
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.petLabel = QLabel(self)
        self.layout.addWidget(self.petLabel)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        
    def initPet(self):
        """重新加载宠物列表"""
        self.pets = self.db.get_all_pets()
        if not self.pets:
            self._init_default_pets()
        if not hasattr(self, 'current_pet') or self.current_pet not in self.pets:
            self.current_pet = next(iter(self.pets))

    def _init_default_pets(self):
        default_pets = {
            "像素小伴1": "img/pet1_frames/",
            "像素小伴2": "img/pet2_frames/"
        }
        for name, path in default_pets.items():
            os.makedirs(path, exist_ok=True)
            self.db.add_pet(name, path)
        self.pets = default_pets

    def changePet(self, pet):
        if pet in self.pets:
            self.current_pet = pet
            # 完全重置动画
            if hasattr(self, 'animTimer'):
                self.animTimer.stop()
            self.initAnimation()  # 重新初始化动画
            self.updateFrame()    # 立即更新显示
        
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
    def initMovement(self):  # This method was defined but might have indentation issues
        self.direction = QPoint(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        self.speed = 2
        
        self.moveTimer = QTimer(self)
        self.moveTimer.timeout.connect(self.movePet)
        self.moveTimer.start(30)
        
        self.changeDirTimer = QTimer(self)
        self.changeDirTimer.timeout.connect(self.randomDirection)
        self.changeDirTimer.start(3000)

    def movePet(self):
        """Handle pet movement"""
        screen = QApplication.primaryScreen().geometry()
        new_x = self.x() + self.direction.x() * self.speed
        new_y = self.y() + self.direction.y() * self.speed
        
        if new_x <= 0 or new_x >= screen.width() - self.width():
            self.direction.setX(-self.direction.x())
        if new_y <= 0 or new_y >= screen.height() - self.height():
            self.direction.setY(-self.direction.y())
            
        self.move(new_x, new_y)

    def randomDirection(self):
        """Randomly change movement direction"""
        self.direction = QPoint(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        
    def quitApp(self):
            # 停止所有定时器
            self.animTimer.stop()
            self.moveTimer.stop()
            self.changeDirTimer.stop()
            # 退出应用程序
            QApplication.quit()
    def show_manager(self):
        from manager import PetManager
        self.manager = PetManager(self)
        self.manager.show()
    def showMenu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                padding: 8px;
            }
            QMenu::item {
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                color: #333;
                padding: 8px 25px 8px 15px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e0f0ff;
                color: #0066cc;
            }
            QMenu::item:disabled {
                color: #999;
            }
            QMenu::separator {
                height: 1px;
                background: #e0e0e0;
                margin: 5px 0;
            }
        """)
        
        # 添加置顶按钮
        topAction = QAction("置顶", self)
        topAction.setCheckable(True)
        topAction.setChecked(self.windowFlags() & Qt.WindowStaysOnTopHint)
        topAction.triggered.connect(self.toggleTop)
        menu.addAction(topAction)
        
        # 添加固定按钮
        freezeAction = QAction("固定不动", self)
        freezeAction.setCheckable(True)
        freezeAction.setChecked(not hasattr(self, 'moveTimer') or not self.moveTimer.isActive())
        freezeAction.triggered.connect(self.toggleFreeze)
        menu.addAction(freezeAction)

        # 添加管理宠物按钮
        managerAction = QAction("管理宠物", self)
        managerAction.triggered.connect(self.show_manager)
        menu.addAction(managerAction)

        # 添加隐藏按钮
        hideAction = QAction("隐藏", self)
        hideAction.triggered.connect(self.hide)
        menu.addAction(hideAction)
        
        # 添加宠物切换菜单
        petMenu = menu.addMenu("更换宠物")
        for pet in self.pets:
            action = QAction(pet, self)
            action.triggered.connect(lambda _, p=pet: self.changePet(p))
            petMenu.addAction(action)
            
        # 添加退出按钮
        exitAction = QAction("退出", self)
        exitAction.triggered.connect(self.quitApp)
        menu.addAction(exitAction)
        

        
        menu.exec_(self.mapToGlobal(pos))
    def initTray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon("img/icon.png"))
        self.tray.setToolTip("像素小伴")  # 添加这行
        self.trayMenu = QMenu()
        self.trayMenu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding: 8px;
            }
            QMenu::item {
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                color: #333;
                padding: 8px 25px 8px 15px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e0f0ff;
                color: #0066cc;
            }
        """)
        
        showAction = QAction("显示", self)
        showAction.triggered.connect(self.showNormal)
        self.trayMenu.addAction(showAction)
        
        quitAction = QAction("退出", self)
        quitAction.triggered.connect(self.quitApp)
        self.trayMenu.addAction(quitAction)
        
        self.tray.setContextMenu(self.trayMenu)
        self.tray.show()
    def initAnimation(self):
        # 加载当前宠物的所有帧
        self.frames = []
        frames_dir = self.pets[self.current_pet]
        
        # 按数字顺序获取所有.png文件
        frame_files = sorted(
            [f for f in os.listdir(frames_dir) if f.endswith('.png')],
            key=lambda x: int(x.split('.')[0].replace('frame', ''))
        )
        
        # 预加载所有帧
        for frame_file in frame_files:
            self.frames.append(QPixmap(os.path.join(frames_dir, frame_file)))
        
        # 动画定时器
        if hasattr(self, 'animTimer'):
            self.animTimer.stop()
        self.animTimer = QTimer(self)
        self.animTimer.timeout.connect(self.updateFrame)
        self.animTimer.start(100)
        self.current_frame = 0

    def updateFrame(self):
        if not self.frames:
            return
            
        # 平滑过渡到下一帧
        next_frame = (self.current_frame + 1) % len(self.frames)
        self.petLabel.setPixmap(self.frames[next_frame])
        self.current_frame = next_frame
        self.adjustSize()

    def toggleTop(self):
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
    def quitApp(self):
            # 停止所有定时器
            self.animTimer.stop()
            self.moveTimer.stop()
            self.changeDirTimer.stop()
            # 退出应用程序
            QApplication.quit()
    def show_manager(self):
        from manager import PixelPalManager
        self.manager = PixelPalManager(self)
        self.manager.show()
    def toggleFreeze(self, checked):
        """切换固定/移动状态"""
        if checked:
            # 停止移动
            if hasattr(self, 'moveTimer'):
                self.moveTimer.stop()
            if hasattr(self, 'changeDirTimer'):
                self.changeDirTimer.stop()
        else:
            # 恢复移动
            if hasattr(self, 'moveTimer'):
                self.moveTimer.start(30)
            if hasattr(self, 'changeDirTimer'):
                self.changeDirTimer.start(3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = PixelPal()
    pet.show()
    sys.exit(app.exec_())


    
    