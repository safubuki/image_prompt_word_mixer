"""
basic_prompt_frame.py
基本プロンプトの選択、テンプレート表示および変数入力機能を提供するコンポーネントです。
"""

import tkinter as tk
from tkinter import ttk


class BasicPromptFrame(ttk.LabelFrame):
    """
    BasicPromptFrame クラスは、基本プロンプトの選択、テンプレート表示および変数入力を提供するコンポーネントです。
    """

    def __init__(self, master, basic_prompts, on_basic_select, on_text_change, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
            master (tk.Widget): 親ウィジェット
            basic_prompts (list): 基本プロンプトのデータリスト
            on_basic_select (function): コンボボックス選択時のコールバック関数
            on_text_change (function): テキスト変更時のコールバック関数
            *args, **kwargs: その他の引数
        """
        super().__init__(master, text="基本プロンプト", *args, **kwargs)
        self.basic_prompts = basic_prompts
        self.on_basic_select = on_basic_select
        self.on_text_change = on_text_change
        self.variable_entries = {}
        self.create_widgets()

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        """
        # 基本プロンプト選択部分
        basic_select_frame = ttk.LabelFrame(self, text="基本プロンプトを選択")
        basic_select_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.basic_combobox = ttk.Combobox(basic_select_frame,
                                           values=[prompt["name"] for prompt in self.basic_prompts],
                                           width=48)
        self.basic_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.basic_combobox.bind("<<ComboboxSelected>>", self.on_basic_select)

        # 基本プロンプトテキスト表示部分
        template_frame = ttk.LabelFrame(self, text="基本プロンプト テンプレート表示")
        template_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.basic_text = tk.Text(template_frame, height=10, width=50)
        self.basic_text.grid(row=0, column=0, padx=5, pady=5)
        self.basic_text.bind("<KeyRelease>", self.on_text_change)

        # 変数設定部分
        self.variable_frame = ttk.LabelFrame(self, text="変数設定")
        self.variable_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

    def update_variable_entries(self, variables):
        """
        変数入力欄を更新します。
        
        引数:
            variables (dict): プロンプトに含まれる変数とその初期値の辞書
        """
        # 既存ウィジェットの削除
        for widget in self.variable_frame.winfo_children():
            widget.destroy()
        self.variable_entries.clear()

        # 列設定：左と右の2列、中央にスペーサーを配置
        self.variable_frame.columnconfigure(0, weight=1)
        self.variable_frame.columnconfigure(1, minsize=20)
        self.variable_frame.columnconfigure(2, weight=1)

        for i, (var, default_value) in enumerate(variables.items()):
            row, col = divmod(i, 2)
            use_col = 0 if col == 0 else 2
            label = ttk.Label(self.variable_frame, text=var)
            label.grid(row=row * 2, column=use_col, padx=5, pady=0, sticky="w")
            entry = ttk.Entry(self.variable_frame)
            entry.grid(row=row * 2 + 1, column=use_col, padx=5, pady=5, sticky="ew")
            entry.insert(0, default_value)
            entry.bind("<KeyRelease>", self.on_text_change)
            self.variable_entries[var] = entry
