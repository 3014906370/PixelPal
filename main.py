from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from pixel_pal import PixelPal
import sys
from config import load_config

def main():
    app = QApplication(sys.argv) 
    # 添加全局样式设置
    app.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: black;
        }
    """)
    
    pet = PixelPal()
    CONFIG = load_config()
    if CONFIG.get("current_pet"):
        pet.changePet(CONFIG["current_pet"])
    
    pet.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()