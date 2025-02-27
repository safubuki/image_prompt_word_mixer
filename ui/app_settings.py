"""
app_settings.py
アプリケーション設定の管理クラスです。
"""
import json
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
            with open(self.api_key_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.deepl_api_key = data.get("api_key", "")
        except Exception:
            self.deepl_api_key = ""

    def open_api_key_dialog(self):
        """
        APIキー設定ダイアログを表示します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        dialog = tk.Toplevel(self.master)
        dialog.title("APIキー設定")
        tk.Label(dialog, text="DeepLのAPIキーを設定してください。\n保存ボタンを押すとapi_key.jsonに保存します。").pack(padx=10,
                                                                                          pady=5)
        entry = tk.Entry(dialog, width=50)
        entry.pack(padx=10, pady=5)
        try:
            with open(self.api_key_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            current_key = data.get("api_key", "")
        except Exception:
            current_key = ""
        entry.insert(0, current_key)
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=5)

        def save_api_key():
            new_key = entry.get()
            try:
                with open(self.api_key_path, "w", encoding="utf-8") as f:
                    json.dump({"api_key": new_key}, f, ensure_ascii=False, indent=4)
                self.reload_api_key()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")

        tk.Button(button_frame, text="保存", command=save_api_key).pack(side="left", padx=5)
        tk.Button(button_frame, text="キャンセル", command=dialog.destroy).pack(side="left", padx=5)

    def reload_api_key(self):
        """
        APIキーを再読み込みします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        try:
            with open(self.api_key_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.deepl_api_key = data.get("api_key", "")
            print("APIキーを設定しました。")
        except Exception as e:
            print(f"APIキーの設定に失敗しました: {e}")
            self.deepl_api_key = ""
