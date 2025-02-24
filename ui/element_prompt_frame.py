"""
element_prompt_frame.py
追加プロンプトの選択および表示機能を提供するコンポーネントです。
"""

import tkinter as tk
from tkinter import ttk


class ElementPromptFrame(ttk.LabelFrame):
    """
    ElementPromptFrame クラスは、追加プロンプトの選択と表示機能を提供するコンポーネントです。
    
    引数:
      master (tk.Widget): 親ウィジェット
      element_prompts (dict): 追加プロンプトのデータ（"default_subject" と "categories" を含む）
      on_element_select (function): ツリービュー選択時のコールバック関数
      on_text_change (function): テキスト変更時のコールバック関数
      *args, **kwargs: その他
      
    戻り値:
      なし
    """

    def __init__(self, master, element_prompts, on_element_select, on_text_change, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): 親ウィジェット
          element_prompts (dict): 追加プロンプトのデータ
          on_element_select (function): ツリービュー選択時のコールバック関数
          on_text_change (function): テキスト変更時のコールバック関数
          *args, **kwargs: その他
          
        戻り値:
          なし
        """
        # element_prompts は辞書となっているため、default_subject と categories に分ける
        self.default_subject = element_prompts.get("default_subject", "被写体")
        self.categories = element_prompts.get("categories", [])
        super().__init__(master, text="追加プロンプト", *args, **kwargs)
        self.on_element_select = on_element_select
        self.on_text_change = on_text_change
        self.create_widgets()
        # ElementPromptFrame 自体のグリッド行と列に重みを設定して拡大を有効にする
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.create_select_frame()

    def create_select_frame(self):
        """
        追加プロンプト選択部分のウィジェットを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        select_frame = ttk.LabelFrame(self, text="追加プロンプトを選択（Ctrlキーで複数可）")
        select_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")
        select_frame.columnconfigure(0, weight=1)
        select_frame.columnconfigure(1, weight=0)

        # 主語入力部
        subject_frame = ttk.Frame(select_frame)
        subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        subject_label = ttk.Label(subject_frame, text="主語:")
        subject_label.pack(side=tk.LEFT, padx=(0, 8))
        self.subject_entry = ttk.Entry(subject_frame, width=24)
        self.subject_entry.pack(side=tk.LEFT)
        # element_prompts.json から読み込んだ default_subject をセット
        self.subject_entry.insert(0, self.default_subject)

        # select_frame の右側に「選択解除」ボタンを配置
        deselect_btn = ttk.Button(select_frame, text="選択解除", command=self.clear_selection)
        deselect_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # Treeview部分（テキストボックス削除によりツリー表示領域を拡大）
        self.tree = ttk.Treeview(select_frame, selectmode="extended")
        self.tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.tree.column("#0", width=350)
        self.tree.bind("<<TreeviewSelect>>", self.on_element_select)
        for category in self.categories:
            parent = self.tree.insert("", tk.END, text=category.get("category", ""))
            for prompt in category.get("prompt_lists", []):
                self.tree.insert(parent, tk.END, text=prompt.get("title", ""))
        # ツリー部分を拡大するため、select_frame の row 1 に weight を設定
        select_frame.rowconfigure(1, weight=1)

    def clear_selection(self):
        """
        Treeview の選択を解除します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.tree.selection_remove(self.tree.selection())
