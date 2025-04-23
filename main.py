from PyQt5.QtWidgets import QApplication
from pixel_pal import PixelPal
import sys
# 主程序入口
def main():
    """程序主入口"""
    app = QApplication(sys.argv) 
    pet = PixelPal()
    pet.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()