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

DEFAULT_ENTRY_COUNT = 20

class OneClickFrame(ttk.Frame):
    """
    OneClickFrameクラス
    ワンクリックで実行できる機能のUIを提供するコンポーネントです。

    引数:
        master: 親ウィジェット
        args: 追加パラメータ
        kwargs: 追加パラメータ

    戻り値:
        なし
    """
    def __init__(self, master, *args, **kwargs):
        """
        コンストラクタ。
        ウィジェットの初期化と作成を行います。

        引数:
            master: 親ウィジェット
            args: 追加パラメータ
            kwargs: 追加パラメータ

        戻り値:
            なし
        """
        super().__init__(master, *args, **kwargs)
        self.one_click_entries = self.load_one_click_entries()
        self.button_widgets = []
        self.current_index = None
        self.create_widgets()
    
    def create_widgets(self):
        """
        ウィジェットの作成を行います。

        引数:
            なし

        戻り値:
            なし
        """
        self.create_button_grid()
        self.create_editor_area()
    
    def create_button_grid(self):
        """
        ボタンをグリッド状に配置するUI部分を作成します。

        引数:
            なし

        戻り値:
            なし
        """
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10, fill="both", expand=True)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        for idx, entry in enumerate(self.one_click_entries):
            row = idx // 2
            col = idx % 2
            btn = ttk.Button(button_frame,
                             text=entry["title"],
                             width=20,
                             command=self.create_button_command(idx))
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.button_widgets.append(btn)
            button_frame.rowconfigure(row, weight=1)
    
    def create_editor_area(self):
        """
        編集用テキストボックスとボタンパネルを作成します。

        引数:
            なし

        戻り値:
            なし
        """
        edit_frame = ttk.Frame(self)
        edit_frame.pack(padx=10, pady=10, fill="x", expand=False)
        title_label = ttk.Label(edit_frame, text="ボタンタイトル:")
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_edit = tk.Text(edit_frame, height=1)
        self.title_edit.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.title_edit.bind("<Tab>", self.move_focus_to_edit)
        text_label = ttk.Label(edit_frame, text="定型文:")
        text_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.edit_text = tk.Text(edit_frame, height=5)
        self.edit_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        button_panel = ttk.Frame(edit_frame)
        button_panel.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="ns")
        save_btn = ttk.Button(button_panel, text="更新・保存", command=self.save_current_entry)
        save_btn.pack(side="top", fill="x")
        refresh_btn = ttk.Button(button_panel, text="Jsonリロード", command=self.refresh_entries)
        refresh_btn.pack(side="top", fill="x", pady=(5, 0))
        edit_frame.columnconfigure(1, weight=1)
    
    def load_one_click_entries(self):
        """
        one_click.jsonからワンクリックエントリーを読み込みます。
        必要に応じてエントリー数をDEFAULT_ENTRY_COUNTに合わせます。

        引数:
            なし

        戻り値:
            list: ワンクリックエントリーのリスト
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
                        while len(data) < DEFAULT_ENTRY_COUNT:
                            data.append({"title": "", "text": ""})
                        return data[:DEFAULT_ENTRY_COUNT]
            except Exception as e:
                print(f"one_click.json の読み込みに失敗しました: {e}")
        return [{"title": "", "text": ""} for _ in range(DEFAULT_ENTRY_COUNT)]
    
    def save_one_click_entries(self):
        """
        ワンクリックエントリーをone_click.jsonに保存します。

        引数:
            なし

        戻り値:
            なし
        """
        json_path = "one_click.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.one_click_entries, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"one_click.json の保存に失敗しました: {e}")
    
    def refresh_entries(self):
        """
        ワンクリックエントリーを再読み込みし、ボタン表示を更新します。

        引数:
            なし

        戻り値:
            なし
        """
        self.one_click_entries = self.load_one_click_entries()
        for idx, entry in enumerate(self.one_click_entries):
            self.button_widgets[idx].config(text=entry["title"])
    
    def create_button_command(self, index):
        """
        指定されたインデックスのボタン用コールバック関数を生成します。

        引数:
            index: int, ボタンのインデックス

        戻り値:
            function: コールバック関数
        """
        return lambda: self.on_button_click(index)
    
    def move_focus_to_edit(self, event):
        """
        Tabキー押下時に編集エリアにフォーカスを移します。

        引数:
            event: tkinter.Event

        戻り値:
            str: "break"
        """
        self.edit_text.focus_set()
        return "break"
    
    def on_button_click(self, index):
        """
        指定されたボタンがクリックされた際に、クリップボードに定型文をコピーし
        編集用テキストボックスに内容を表示します。

        引数:
            index: int, クリックされたボタンのインデックス

        戻り値:
            なし
        """
        self.current_index = index
        entry = self.one_click_entries[index]
        text_to_copy = entry["text"]
        title_to_copy = entry["title"]
        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        self.title_edit.delete("1.0", tk.END)
        self.title_edit.insert(tk.END, title_to_copy)
        self.edit_text.delete("1.0", tk.END)
        self.edit_text.insert(tk.END, text_to_copy)
    
    def save_current_entry(self):
        """
        現在選択中のエントリーの内容を更新し、保存します。

        引数:
            なし

        戻り値:
            なし
        """
        if self.current_index is not None:
            new_title = self.title_edit.get("1.0", tk.END).strip()
            new_text = self.edit_text.get("1.0", tk.END).strip()
            self.one_click_entries[self.current_index]["title"] = new_title
            self.one_click_entries[self.current_index]["text"] = new_text
            self.save_one_click_entries()
            self.one_click_entries = self.load_one_click_entries()
            self.button_widgets[self.current_index].config(text=new_title)
