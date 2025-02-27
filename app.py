"""
app.py
Gemini Prompt Generatorアプリケーションの起動およびUI統合機能を提供するコンポーネントです。
"""
import os
import tkinter as tk

from src.core.template_manager import TemplateManager  # インポートパスを更新
from src.ui.app_menu import AppMenu
from src.ui.app_settings import AppSettings
from src.ui.app_ui_manager import AppUIManager


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

        # 設定ファイルパスの修正
        settings_dir = os.path.join(os.getcwd(), "settings")
        basic_prompts_path = os.path.join(settings_dir, "basic_prompts.json")
        element_prompts_path = os.path.join(settings_dir, "element_prompts.json")
        api_key_path = os.path.join(settings_dir, "api_key.json")

        # テンプレートマネージャー初期化
        # プロンプト用JSONファイルを読み込み、データを管理するマネージャーを作成
        self.template_manager = TemplateManager(basic_prompts_path, element_prompts_path)

        # 設定クラス初期化
        # APIキーなどのアプリケーション設定を管理するクラスを初期化
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
