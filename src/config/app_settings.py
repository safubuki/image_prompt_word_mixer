"""
app_settings.py
アプリケーション設定の管理クラスです。
"""
import json
import os
import tkinter as tk
from tkinter import messagebox


class AppSettings:
    """
    APIキーなどのアプリケーション設定を管理します。
    
    引数:
      master (tk.Widget): メインウィンドウ
      api_key_path (str): APIキーファイルのパス
    """

    def __init__(self, master, api_key_path):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): メインウィンドウ
          api_key_path (str): APIキーファイルのパス
        """
        self.master = master
        self.api_key_path = api_key_path
        self.deepl_api_key = ""
        self.load_api_key()

    def load_api_key(self):
        """
        APIキーをファイルから読み込みます。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        try:
            if os.path.exists(self.api_key_path):
                with open(self.api_key_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.deepl_api_key = data.get("api_key", "")
            else:
                # settings フォルダ内を確認
                settings_dir = os.path.join(os.getcwd(), "settings")
                alt_path = os.path.join(settings_dir, "api_key.json")
                if os.path.exists(alt_path):
                    with open(alt_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.deepl_api_key = data.get("api_key", "")
                    # 将来の参照のために正しいパスを保存
                    self.api_key_path = alt_path
        except Exception:
            self.deepl_api_key = ""
