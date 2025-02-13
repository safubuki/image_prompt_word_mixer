"""
element_prompt_frame.py
追加プロンプトの選択および表示機能を提供するコンポーネントです。
"""

import tkinter as tk
from tkinter import ttk


class ElementPromptFrame(ttk.LabelFrame):
    """
    ElementPromptFrame クラスは、追加プロンプトの選択と表示機能を提供するコンポーネントです。
    """

    def __init__(self, master, element_prompts, on_element_select, on_text_change, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
            master (tk.Widget): 親ウィジェット
            element_prompts (list): 追加プロンプトのデータリスト
            on_element_select (function): ツリービュー選択時のコールバック関数
            on_text_change (function): テキスト変更時のコールバック関数
            *args, **kwargs: その他の引数
        """
        super().__init__(master, text="追加プロンプト", *args, **kwargs)
        self.element_prompts = element_prompts
        self.on_element_select = on_element_select
        self.on_text_change = on_text_change
        self.create_widgets()

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        """
        # 追加プロンプト選択部分
        select_frame = ttk.LabelFrame(self, text="追加プロンプトを選択（複数可）")
        select_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")

        # Subject入力欄
        subject_frame = ttk.Frame(select_frame)
        subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        subject_label = ttk.Label(subject_frame, text="主語:")
        subject_label.pack(side=tk.LEFT, padx=(0, 8))
        self.subject_entry = ttk.Entry(subject_frame, width=24)
        self.subject_entry.pack(side=tk.LEFT)
        self.subject_entry.insert(0, "被写体")  # 初期値設定

        # 追加プロンプト選択用Treeview
        self.tree = ttk.Treeview(select_frame, selectmode="extended", height=9)
        self.tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.tree.column("#0", width=350)
        self.tree.bind("<<TreeviewSelect>>", self.on_element_select)
        for category in self.element_prompts:
            parent = self.tree.insert("", tk.END, text=category["category"])
            # キー名 "prompts" -> "prompt_lists"、"name" -> "title" に変更
            for prompt in category["prompt_lists"]:
                self.tree.insert(parent, tk.END, text=prompt["title"])

        # 追加プロンプト表示部分
        display_frame = ttk.LabelFrame(self, text="追加プロンプトを表示")
        display_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.element_text = tk.Text(display_frame, height=7, width=50)
        self.element_text.grid(row=0, column=0, padx=5, pady=5)
        self.element_text.bind("<KeyRelease>", self.on_text_change)
