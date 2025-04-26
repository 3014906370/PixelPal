import sys
import os
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMenu, 
                            QSystemTrayIcon, QAction, QVBoxLayout,QMessageBox)
from PyQt5.QtGui import QPixmap, QMovie, QIcon  # Added QIcon to imports
from PyQt5.QtCore import Qt, QTimer, QPoint
from db_manager import PetDB
import json 
from config import CONFIG, save_config
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
#   - toggleTop: 切换窗口置顶状态。


class PixelPal(QWidget):  
    def __init__(self):
        super().__init__()
        self.db = PetDB()
        self.current_pet = None
        self.CONFIG = CONFIG
        self.initUI()
        self.initPet()
        self.initTray()
        if not self.CONFIG.get("is_frozen", False):  # 只有非固定状态才初始化移动
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
            print(self.current_pet)  # 调试输出
            #保存配置文件
            self.CONFIG["current_pet"] = pet
            save_config(self.CONFIG)
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
    def initMovement(self):
        self.direction = QPoint(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        self.speed = 2
        self.is_moving = True  # 添加移动状态标志
        
        self.moveTimer = QTimer(self)
        self.moveTimer.timeout.connect(self.movePet)
        self.moveTimer.start(30)
        
        self.changeDirTimer = QTimer(self)
        self.changeDirTimer.timeout.connect(self.randomDirection)
        self.changeDirTimer.start(3000)
        
        # 新增随机停止计时器
        self.stopTimer = QTimer(self)
        self.stopTimer.timeout.connect(self.toggleMovement)
        self.stopTimer.start(random.randint(5000, 10000))  # 5-10秒随机停止

    def toggleMovement(self):
        """随机切换移动/停止状态"""
        if self.is_moving:
            self.moveTimer.stop()
            self.is_moving = False
            # 设置下次恢复移动的时间(2-5秒)
            QTimer.singleShot(random.randint(2000, 5000), self.resumeMovement)
        else:
            self.resumeMovement()
            
    def resumeMovement(self):
        """恢复移动"""
        self.moveTimer.start()
        self.is_moving = True
        # 设置下次停止的时间(5-10秒)
        self.stopTimer.start(random.randint(5000, 10000))

    def movePet(self):
        """Handle pet movement"""
        screen = QApplication.primaryScreen().geometry()
        new_x = self.x() + self.direction.x() * self.speed
        new_y = self.y() + self.direction.y() * self.speed
        
        # 修改边缘检测逻辑，增加缓冲区域
        edge_buffer = 2  # 5像素的缓冲区域
        if new_x <= edge_buffer or new_x >= screen.width() - self.width() - edge_buffer:
            self.direction.setX(-self.direction.x())
            new_x = max(edge_buffer, min(new_x, screen.width() - self.width() - edge_buffer))
            
        if new_y <= edge_buffer or new_y >= screen.height() - self.height() - edge_buffer:
            self.direction.setY(-self.direction.y())
            new_y = max(edge_buffer, min(new_y, screen.height() - self.height() - edge_buffer))
            
        self.move(new_x, new_y)

    def randomDirection(self):
        """Randomly change movement direction"""
        self.direction = QPoint(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        
    def initTray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon("img/icon.png"))
        self.tray.setToolTip("像素小伴")
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
        
        # 添加开机自启动选项
        autostartAction = QAction("开机自启动", self)
        autostartAction.setCheckable(True)
        autostartAction.setChecked(self.check_autostart())
        autostartAction.triggered.connect(self.toggle_autostart)
        self.trayMenu.addAction(autostartAction)
        
        showAction = QAction("显示", self)
        showAction.triggered.connect(self.showNormal)
        self.trayMenu.addAction(showAction)
        
        quitAction = QAction("退出", self)
        quitAction.triggered.connect(self.quitApp)
        self.trayMenu.addAction(quitAction)
        
        self.tray.setContextMenu(self.trayMenu)
        self.tray.show()

    def check_autostart(self):
        """检查是否设置了开机自启动"""
        startup_folder = os.path.join(os.getenv('APPDATA'), 
                                    'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        shortcut_path = os.path.join(startup_folder, 'PixelPal.lnk')
        return os.path.exists(shortcut_path)
    
    def toggle_autostart(self, checked):
        """切换开机自启动设置"""
        startup_folder = os.path.join(os.getenv('APPDATA'), 
                                    'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        shortcut_path = os.path.join(startup_folder, 'PixelPal.lnk')
        
        if checked:
            # 创建快捷方式
            import winshell
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.WorkingDirectory = os.path.dirname(sys.executable)
            shortcut.IconLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "icon.ico").replace("/", "\\") + ",0"
            print("调试shortcut.IconLocation：",shortcut.IconLocation)
            shortcut.save()
        else:
            # 删除快捷方式
            try:
                os.remove(shortcut_path)
            except:
                pass

    def quitApp(self):
        # 保存当前所有设置
        config = {
            "autostart": self.check_autostart(),
            "current_pet": self.current_pet,
            "is_frozen": not hasattr(self, 'moveTimer') or not self.moveTimer.isActive(),
            "is_topmost": bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        }
        self.CONFIG.update(config)
        print("调试config：",config)  # 调试输出
        save_config(self.CONFIG)
        # 安全停止所有定时器
        if hasattr(self, 'animTimer'):
            self.animTimer.stop()
        if hasattr(self, 'moveTimer'):
            self.moveTimer.stop()
        if hasattr(self, 'changeDirTimer'):
            self.changeDirTimer.stop()
        # 关闭托盘图标
        if hasattr(self, 'tray'):
            self.tray.hide()
        # 退出应用程序
        QApplication.quit()

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
            if not hasattr(self, 'moveTimer'):
                self.initMovement()  # 如果定时器不存在则重新初始化
            else:
                self.moveTimer.start(30)
                if hasattr(self, 'changeDirTimer'):
                    self.changeDirTimer.start(3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = PixelPal()
    pet.show()
    sys.exit(app.exec_())


    
    