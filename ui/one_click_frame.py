"""
one_click_frame.py
ワンクリックで実行できる機能（定型テキストを迅速にコピーする等）のUIを提供するコンポーネントです。
"""

import json
import os
import tkinter as tk
from tkinter import ttk


class OneClickFrame(ttk.LabelFrame):
    """
    OneClickFrame クラスは、指定された定型テキストをワンクリックでコピーできるUIを提供します。
    左側に編集可能なテキストウィジェット、右側にコピー用ボタンと保存ボタン（計16行）が縦に並びます。
    """

    def __init__(self, master, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
            master (tk.Widget): 親ウィジェット
        """
        super().__init__(master, text="ワンクリック機能", *args, **kwargs)
        self.one_click_texts = self.load_one_click_texts()
        self.create_widgets()

    def load_one_click_texts(self):
        """
        one_click.jsonから定型テキストを読み込みます。
        読み込めない場合は、16行分の空文字列リストを返します。
        期待するJSONの構造: 文字列のリスト
        """
        json_path = "one_click.json"
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        while len(data) < 16:
                            data.append("")
                        return data[:16]
            except Exception as e:
                print(f"one_click.json の読み込みに失敗しました: {e}")
        return ["" for _ in range(16)]

    def save_one_click_texts(self):
        """
        one_click_texts の内容を one_click.json に保存します。
        """
        json_path = "one_click.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.one_click_texts, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"one_click.json の保存に失敗しました: {e}")

    def create_widgets(self):
        """
        UIウィジェットを生成します。
        """
        container = ttk.Frame(self)
        container.pack(padx=10, pady=10, fill="both", expand=True)

        self.text_widgets = []  # 各行のテキストウィジェットの参照

        for i in range(16):
            row_frame = ttk.Frame(container)
            row_frame.grid(row=i, column=0, sticky="ew", pady=5)
            # テキストウィジェット部分を拡張するための設定
            row_frame.columnconfigure(0, weight=1)

            # 左側：編集可能なテキストウィジェット（2行分表示、左右パディング均等）
            text_widget = tk.Text(row_frame, height=2, wrap="none")
            text_widget.grid(row=0, column=0, padx=(5, 5), sticky="ew")
            text_widget.insert("1.0", self.one_click_texts[i])
            self.text_widgets.append(text_widget)

            # 右側：コピー用ボタン
            copy_button = ttk.Button(row_frame, text="コピー", command=lambda idx=i: self.copy_text(idx))
            copy_button.grid(row=0, column=1, padx=5)

            # 右側：保存ボタン
            save_button = ttk.Button(row_frame, text="保存", command=lambda idx=i: self.save_text(idx))
            save_button.grid(row=0, column=2, padx=5)

    def copy_text(self, idx):
        """
        指定された行のテキストウィジェットの内容をクリップボードにコピーします。
        コピー時に確認ダイアログは表示しません。
        """
        text_content = self.text_widgets[idx].get("1.0", tk.END).strip()
        if text_content:
            self.clipboard_clear()
            self.clipboard_append(text_content)

    def save_text(self, idx):
        """
        指定された行のテキストウィジェットの内容を取得し、one_click_texts を更新してjsonに保存します。
        """
        new_text = self.text_widgets[idx].get("1.0", tk.END).strip()
        self.one_click_texts[idx] = new_text
        self.save_one_click_texts()
