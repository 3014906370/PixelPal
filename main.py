from PyQt5.QtWidgets import QApplication
from pixel_pal import PixelPal
import sys
from config import load_config

def main():
    app = QApplication(sys.argv) 
    pet = PixelPal()
    
    CONFIG = load_config()
    if CONFIG.get("current_pet"):
        pet.changePet(CONFIG["current_pet"])
    
    pet.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()