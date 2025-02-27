"""
app_menu.py
アプリケーションのメニューバーを管理するクラスです。
"""
import os
import subprocess
import tkinter as tk
from tkinter import messagebox


class AppMenu:
    """
    アプリケーションのメニューバーを管理します。
    
    引数:
      master (tk.Widget): メインウィンドウ
      template_manager (TemplateManager): テンプレートマネージャー
      ui_manager (AppUIManager): UIマネージャー
      api_key_callback (callable): APIキー設定時のコールバック関数
      config_dir (str): 設定ファイルディレクトリ
    """

    def __init__(self, master, template_manager, ui_manager, api_key_callback, config_dir):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): メインウィンドウ
          template_manager (TemplateManager): テンプレートマネージャー
          ui_manager (AppUIManager): UIマネージャー
          api_key_callback (callable): APIキー設定時のコールバック関数
          config_dir (str): 設定ファイルディレクトリ
        """
        self.master = master
        self.template_manager = template_manager
        self.ui_manager = ui_manager
        self.api_key_callback = api_key_callback
        self.config_dir = config_dir
        self.create_menu()

    def create_menu(self):
        """
        メニューバーを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)

        # ファイルパスを設定ディレクトリ内に指定
        basic_prompts_path = os.path.join(self.config_dir, "basic_prompts.json")
        element_prompts_path = os.path.join(self.config_dir, "element_prompts.json")
        one_click_path = os.path.join(self.config_dir, "one_click.json")

        file_menu.add_command(label="基本プロンプト編集",
                              command=lambda: self.open_json_editor(basic_prompts_path))
        file_menu.add_command(label="追加プロンプト編集",
                              command=lambda: self.open_json_editor(element_prompts_path))
        file_menu.add_command(label="定型文編集", command=lambda: self.open_json_editor(one_click_path))
        # 定型文ファイルの後、区切り線を追加
        file_menu.add_separator()
        # 編集結果反映機能を統合して全設定ファイルを反映
        file_menu.add_command(label="編集内容を反映", command=self.reload_json)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label="APIキー設定", command=self.api_key_callback)
        menubar.add_cascade(label="設定", menu=setting_menu)
        self.master.config(menu=menubar)

    def open_json_editor(self, file_path):
        """
        指定されたJSONファイルをエディタで開きます。
        
        引数:
          file_path (str): ファイルパス
          
        戻り値:
          なし
        """
        try:
            subprocess.Popen(["notepad", file_path])
        except Exception as e:
            messagebox.showerror("エラー", f"{file_path} の起動に失敗しました: {e}")

    def reload_json(self):
        """
        JSONファイルを再読み込みし、UIを更新します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        try:
            # テンプレートマネージャーの更新
            self.template_manager.reload_templates()

            # UIの更新
            self.ui_manager.refresh_ui_components()

            messagebox.showinfo("情報", "全ての編集結果が反映されました。")
        except Exception as e:
            messagebox.showerror("エラー", f"編集結果の反映に失敗しました: {e}")
