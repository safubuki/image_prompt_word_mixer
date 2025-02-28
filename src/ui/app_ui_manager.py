"""
app_ui_manager.py
アプリケーションのUIコンポーネント管理クラス
"""
import os
import tkinter as tk
from tkinter import ttk

# 相対インポートに修正
from src.ui.frames.basic_prompt_frame import BasicPromptFrame
from src.ui.frames.element_prompt_frame import ElementPromptFrame
from src.ui.frames.final_prompt_frame import FinalPromptFrame
from src.ui.frames.one_click_frame import OneClickFrame


class AppUIManager:
    """
    アプリケーションのUIコンポーネントを管理します。
    
    引数:
      master (tk.Widget): メインウィンドウ
      template_manager (TemplateManager): テンプレートマネージャ
    """

    def __init__(self, master, template_manager):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): メインウィンドウ
          template_manager (TemplateManager): テンプレートマネージャ
        """
        self.master = master
        self.template_manager = template_manager

        # プロンプトデータ取得
        self.basic_prompts = template_manager.get_basic_prompts()
        self.element_prompts = template_manager.get_element_prompts()

        # UIコンポーネント初期化
        self.create_notebook()
        self.create_ui_components()
        self.basic_frame.set_basic_prompt(0)

    def create_notebook(self):
        """
        Notebook タブを作成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=1, fill="both")
        self.prompt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.prompt_tab, text="プロンプト作成")
        self.one_click_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.one_click_tab, text="定型文簡単コピー")

    def create_ui_components(self):
        """
        UIコンポーネントを生成・配置します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.basic_frame = BasicPromptFrame(self.prompt_tab, self.basic_prompts,
                                            self.on_basic_select, self.on_text_change)
        self.basic_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.prompt_tab.columnconfigure(0, weight=1)

        self.element_frame = ElementPromptFrame(self.prompt_tab, self.element_prompts,
                                                self.on_element_select, self.on_text_change)
        self.element_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.prompt_tab.columnconfigure(1, weight=1)

        self.final_frame = FinalPromptFrame(self.prompt_tab)
        self.final_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # FinalPromptFrameに入力ソースを設定
        self.final_frame.set_input_sources(self.basic_frame, self.element_frame,
                                           self.template_manager)
        self.prompt_tab.rowconfigure(1, weight=1)

        self.variable_entries = self.basic_frame.variable_entries
        self.one_click_frame = OneClickFrame(self.one_click_tab)
        self.one_click_frame.pack(expand=1, fill="both", padx=10, pady=10)

    def refresh_ui_components(self):
        """
        UIコンポーネントのデータを最新の状態に更新します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        # 最新のプロンプトデータを取得
        self.basic_prompts = self.template_manager.get_basic_prompts()
        self.element_prompts = self.template_manager.get_element_prompts()

        # 各フレームの更新
        self.basic_frame.update_basic_prompts(self.basic_prompts)
        self.basic_frame.set_basic_prompt(0)
        self.element_frame.update_element_prompts(self.element_prompts)

        # one_click_frame の更新
        self.one_click_frame.refresh_entries()

    def on_basic_select(self, _):
        """
        基本プロンプト選択時の処理を行います。
        
        引数:
          _ : イベント引数
          
        戻り値:
          なし
        """
        self.final_frame.schedule_update()

    def on_element_select(self, _):
        """
        追加プロンプト選択時の処理を行います。
        
        引数:
          _ : イベント引数
          
        戻り値:
          なし
        """
        self.final_frame.schedule_update()

    def on_text_change(self, _):
        """
        テキスト変更時の処理を実行します。
        
        引数:
          _ : イベント引数
          
        戻り値:
          なし
        """
        self.final_frame.schedule_update()

    def set_icon(self):
        """
        アプリのアイコンを設定します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        icon_path = os.path.join("image", "turtle.ico")
        try:
            self.master.iconbitmap(icon_path)
        except tk.TclError:
            print(f"アイコンファイルが見つかりませんでした: {icon_path}")
