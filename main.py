from PyQt5.QtWidgets import QApplication
from pixel_pal import PixelPal
import sys

def main():
    """程序主入口"""
    app = QApplication(sys.argv)  # 必须先创建QApplication
    pet = PixelPal()
    pet.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()