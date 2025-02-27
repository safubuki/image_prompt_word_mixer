"""
app.py
Gemini Prompt Generatorアプリケーションの起動およびUI統合機能を提供するコンポーネントです。
"""
import os
import tkinter as tk

from template_manager import TemplateManager
from ui.app_menu import AppMenu
from ui.app_settings import AppSettings
from ui.app_ui_manager import AppUIManager


class PromptGeneratorApp:
    """
    PromptGeneratorApp クラスは、各UIコンポーネントの統合とプロンプト生成処理を管理します。
    
    引数:
      master (tk.Widget): メインウィジェット
       
    戻り値:
      なし
    """

    def __init__(self, master):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): メインウィジェット
          
        戻り値:
          なし
        """
        self.master = master
        # アプリケーションのタイトル設定
        self.master.title("Image Prompt Word-Mixer ")
        # ウィンドウサイズの固定（リサイズ不可）
        self.master.resizable(False, False)

        # テンプレートマネージャー初期化
        # プロンプト用JSONファイルを読み込み、データを管理するマネージャーを作成
        self.template_manager = TemplateManager("basic_prompts.json", "element_prompts.json")

        # 設定クラス初期化
        # APIキーなどのアプリケーション設定を管理するクラスを初期化
        self.app_settings = AppSettings(self.master)

        # UIマネージャー初期化
        # アプリケーションのUIコンポーネントを生成・管理するクラスを初期化
        self.ui_manager = AppUIManager(self.master, self.template_manager)
        # アプリケーションアイコンを設定
        self.ui_manager.set_icon()

        # メニュークラス初期化
        # アプリケーションのメニューバーを生成・管理するクラスを初期化
        # 各コンポーネントを連携させるために必要なオブジェクトを渡す
        self.app_menu = AppMenu(self.master, self.template_manager, self.ui_manager,
                                self.app_settings.open_api_key_dialog)


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
