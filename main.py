from PyQt5.QtWidgets import QApplication
from pixel_pal import PixelPal
import sys
import os
import json
from pathlib import Path

# 修改配置文件路径为工作目录下
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pixelpal_config.json")

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        print(f"配置文件{CONFIG_FILE}加载失败，使用默认配置")
        return {
            "autostart": True, 
            "current_pet": None,
            "is_frozen": False,  # 新增固定不动状态
            "is_topmost": True   # 新增置顶状态
        }

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# 主程序入口
def main():
    """程序主入口"""
    app = QApplication(sys.argv) 
    pet = PixelPal()
    
    # 加载配置
    config = load_config()
    if config.get("current_pet"):
        pet.changePet(config["current_pet"])
    
    pet.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()