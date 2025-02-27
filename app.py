"""
app.py
Gemini Prompt Generatorアプリケーションの起動およびUI統合機能を提供するコンポーネントです。
"""
import os
import tkinter as tk

from src.app_menu import AppMenu
from src.app_settings import AppSettings
from src.app_ui_manager import AppUIManager
from src.template_manager import TemplateManager  # インポートパスを更新


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

        # configフォルダのパスを作成
        config_dir = os.path.join(os.getcwd(), "config")

        # configフォルダが存在しない場合は作成
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # テンプレートマネージャー初期化
        # プロンプト用JSONファイルを読み込み、データを管理するマネージャーを作成
        basic_prompts_path = os.path.join(config_dir, "basic_prompts.json")
        element_prompts_path = os.path.join(config_dir, "element_prompts.json")
        self.template_manager = TemplateManager(basic_prompts_path, element_prompts_path)

        # 設定クラス初期化
        # APIキーなどのアプリケーション設定を管理するクラスを初期化
        api_key_path = os.path.join(config_dir, "api_key.json")
        self.app_settings = AppSettings(self.master, api_key_path)

        # UIマネージャー初期化
        # アプリケーションのUIコンポーネントを生成・管理するクラスを初期化
        self.ui_manager = AppUIManager(self.master, self.template_manager)
        # アプリケーションアイコンを設定
        self.ui_manager.set_icon()

        # メニュークラス初期化
        # アプリケーションのメニューバーを生成・管理するクラスを初期化
        # 各コンポーネントを連携させるために必要なオブジェクトを渡す
        one_click_path = os.path.join(config_dir, "one_click.json")
        self.app_menu = AppMenu(self.master, self.template_manager, self.ui_manager,
                                self.app_settings.open_api_key_dialog, config_dir)


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
