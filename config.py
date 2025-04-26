from PyQt5.QtWidgets import QMessageBox,QApplication
import sys
import os
import json

def get_config_path():
    # 使用AppData目录存储配置文件
    appdata_dir = os.getenv('APPDATA')
    config_dir = os.path.join(appdata_dir, 'PixelPal')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'pixelpal_config.json')

CONFIG_FILE = get_config_path()

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {
            "autostart": True, 
            "current_pet": None,
            "is_frozen": False,
            "is_topmost": True
        }

CONFIG = load_config()

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"配置已保存在{CONFIG_FILE}")
    except Exception as e:
        print(f"保存配置失败: {str(e)}")
