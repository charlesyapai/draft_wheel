# draft_wheel/main.py
import tkinter as tk
from config.loader import ConfigRetrieval  # if you have that
from logic.draft_logic import DraftLogic
from gui.new_draft_gui import DraftGUI

def main():
    config_path = "data/draft_wheel_configs.yaml"
    cfg_obj = ConfigRetrieval(config_path)  # or read YAML manually
    cfg = cfg_obj.get_config()

    root = tk.Tk()
    root.geometry("1400x800")
    logic= DraftLogic(cfg)
    app= DraftGUI(root, cfg, logic)
    root.mainloop()

if __name__=="__main__":
    main()
