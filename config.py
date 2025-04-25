from PyQt5.QtWidgets import QMessageBox
import sys
import os
import json

def get_config_path():
    """获取正确的配置文件路径，兼容打包和开发模式"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "pixelpal_config.json")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "pixelpal_config.json")

CONFIG_FILE = get_config_path()

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        QMessageBox.warning(None, "错误", f"加载配置失败: {str(e)}")
        return {
            "autostart": True, 
            "current_pet": None,
            "is_frozen": False,
            "is_topmost": True
        }

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        QMessageBox.warning(None, "错误", f"保存配置失败: {str(e)}")