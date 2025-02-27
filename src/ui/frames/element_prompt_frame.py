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
        self.element_prompts = element_prompts
        super().__init__(master, text="追加プロンプト", *args, **kwargs)
        self.on_select_callback = on_element_select
        self.on_text_change_callback = on_text_change
        self.create_widgets()
        # ElementPromptFrame 自体のグリッド行と列に重みを設定して拡大を有効にする
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.element_prompt_content = ""

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
        self.subject_entry.bind("<KeyRelease>", self.on_text_change)

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
        self.element_prompt_content = ""
        if self.on_text_change_callback:
            self.on_text_change_callback(None)

    def on_element_select(self, event):
        """
        追加プロンプト選択時の処理を行います。
        
        引数:
          event: イベントオブジェクト
          
        戻り値:
          なし
        """
        selection = event.widget.selection()
        selected_texts = []
        seen_keys = set()
        parent_ids = list(self.tree.get_children(""))

        for item in selection:
            parent = self.tree.parent(item)
            if parent:
                try:
                    category_index = parent_ids.index(parent)
                except ValueError:
                    continue
                category_data = self.element_prompts["categories"][category_index]
                item_text = self.tree.item(item, "text")
                for prompt in category_data["prompt_lists"]:
                    if prompt["title"] == item_text:
                        key = (category_data["category"], prompt["title"], prompt["prompt"])
                        if key not in seen_keys:
                            seen_keys.add(key)
                            selected_texts.append(prompt["prompt"])
                        break

        element_prompt_raw = "\n".join(selected_texts)
        subject_val = self.subject_entry.get().strip()

        # template_manager がインスタンス変数として存在しないので、クラスを呼び出し側から利用してもらう
        self.element_prompt_content = element_prompt_raw
        self.subject_value = subject_val

        if self.on_select_callback:
            self.on_select_callback(event)

    def on_text_change(self, event):
        """
        テキスト変更時の処理を実行します。
        
        引数:
          event: イベントオブジェクト
          
        戻り値:
          なし
        """
        if self.on_text_change_callback:
            self.on_text_change_callback(event)

    def update_element_prompts(self, element_prompts):
        """
        追加プロンプトの一覧を更新します。
        
        引数:
          element_prompts (dict): 更新する追加プロンプトのデータ
          
        戻り値:
          なし
        """
        self.element_prompts = element_prompts
        self.default_subject = element_prompts.get("default_subject", "被写体")
        self.categories = element_prompts.get("categories", [])

        # ツリービューをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        # ツリービューを再構築
        for category in self.categories:
            parent = self.tree.insert("", tk.END, text=category.get("category", ""))
            for prompt in category.get("prompt_lists", []):
                self.tree.insert(parent, tk.END, text=prompt.get("title", ""))

        # 主語を更新
        self.subject_entry.delete(0, tk.END)
        self.subject_entry.insert(0, self.default_subject)

    def get_prompt_content(self):
        """
        現在選択されている追加プロンプトの内容と主語を取得します。
        
        引数:
          なし
          
        戻り値:
          tuple: (追加プロンプト内容, 主語)
        """
        return self.element_prompt_content, self.subject_entry.get().strip()
