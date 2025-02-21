"""
one_click_frame.py
ワンクリックで実行できる機能のUIを提供するコンポーネントです。
この画面はボタンのみの画面で、ボタンには one_click.json で指定されたタイトルが表示され、
ボタンをクリックすると、対応する定型文がクリップボードにコピーされ、画面下部の編集用テキストボックスに
それぞれ「ボタンタイトル」と「定型文」が表示されます。これらは編集可能で、保存更新ボタンを押すと
その内容で更新が保存され、即時ボタン表示も更新されます。
"""
import json
import os
import tkinter as tk
from tkinter import ttk


class OneClickFrame(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        """
        コンストラクタ

        引数:
            master (tk.Widget): 親ウィジェット
        """
        super().__init__(master, *args, **kwargs)
        # one_click.jsonからエントリをロードする（エントリ数は16件）
        self.one_click_entries = self.load_one_click_entries()
        # 各ボタンの参照を保持（後でボタン表記更新に利用）
        self.button_widgets = []
        # 現在選択中のエントリのインデックス（初期状態は None）
        self.current_index = None
        self.create_widgets()

    def load_one_click_entries(self):
        """
        one_click.jsonからエントリを読み込みます。
        読み込めない場合は、20件のデフォルトエントリ（空文字列）を返します。
        期待するJSONの構造: オブジェクトのリスト [{"title": "ボタンタイトル", "text": "定型文"}, ...]
        """
        json_path = "one_click.json"
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for entry in data:
                            if "title" not in entry:
                                entry["title"] = ""
                            if "text" not in entry:
                                entry["text"] = ""
                        # エントリ数が20件に満たなければ補完
                        while len(data) < 20:
                            data.append({"title": "", "text": ""})
                        return data[:20]
            except Exception as e:
                print(f"one_click.json の読み込みに失敗しました: {e}")
        return [{"title": "", "text": ""} for _ in range(20)]

    def save_one_click_entries(self):
        """
        現在の one_click_entries の内容を one_click.json に保存します。
        """
        json_path = "one_click.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.one_click_entries, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"one_click.json の保存に失敗しました: {e}")

    def create_widgets(self):
        """
        UIウィジェットを生成します。
        """
        # 上部：ボタン群を配置するフレーム（2列×10行）
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10, fill="both", expand=True)
        # グリッド各列に重みを与える
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # 各エントリ分のボタンを生成（2列×10行、合計20個）
        for idx, entry in enumerate(self.one_click_entries):
            row = idx // 2  # 0～9行になる
            col = idx % 2
            btn = ttk.Button(button_frame,
                             text=entry["title"],
                             command=lambda index=idx: self.on_button_click(index))
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.button_widgets.append(btn)
            button_frame.rowconfigure(row, weight=1)

        # 下部：編集用エリア（タイトル用と定型文用テキストボックス、保存更新ボタン）はそのまま
        edit_frame = ttk.Frame(self)
        edit_frame.pack(padx=10, pady=10, fill="x", expand=False)
        title_label = ttk.Label(edit_frame, text="ボタンタイトル:")
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_edit = tk.Text(edit_frame, height=1)
        self.title_edit.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        text_label = ttk.Label(edit_frame, text="定型文:")
        text_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.edit_text = tk.Text(edit_frame, height=5)
        self.edit_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        save_btn = ttk.Button(edit_frame, text="保存更新", command=self.save_current_entry)
        save_btn.grid(row=1, column=2, padx=5, pady=5)
        edit_frame.columnconfigure(1, weight=1)

    def on_button_click(self, index):
        """
        ボタン押下時の処理
        指定されたエントリの定型文とボタンタイトルをクリップボードにコピーし、
        編集用テキストボックスに表示します。

        引数:
            index (int): 選択されたエントリのインデックス
        """
        self.current_index = index
        entry = self.one_click_entries[index]
        text_to_copy = entry["text"]
        title_to_copy = entry["title"]
        # クリップボードに定型文をコピー
        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        # 編集用テキストボックスに表示（タイトルと定型文）
        self.title_edit.delete("1.0", tk.END)
        self.title_edit.insert(tk.END, title_to_copy)
        self.edit_text.delete("1.0", tk.END)
        self.edit_text.insert(tk.END, text_to_copy)

    def save_current_entry(self):
        """
        編集用テキストボックスの内容を現在選択されているエントリに反映し、保存します。
        ボタンタイトルと定型文の両方を更新して保存し、再度jsonを読み込み、
        対応するボタンの表示を更新します。
        """
        if self.current_index is not None:
            new_title = self.title_edit.get("1.0", tk.END).strip()
            new_text = self.edit_text.get("1.0", tk.END).strip()
            # 更新
            self.one_click_entries[self.current_index]["title"] = new_title
            self.one_click_entries[self.current_index]["text"] = new_text
            # JSONに保存
            self.save_one_click_entries()
            # 再読み込みして最新状態に更新
            self.one_click_entries = self.load_one_click_entries()
            # 対応するボタンのタイトルを更新（リアルタイムに反映）
            self.button_widgets[self.current_index].config(text=new_title)
