"""
one_click_frame.py
ワンクリックで実行できる機能のUIを提供するコンポーネントです。
この画面ではタブでカテゴリ（例: 良く使う、表情、品質向上）を分類し、
各タブ内に従来の定型文コピー機能を配置します。
ボタンをクリックすると該当エントリーのタイトルと定型文が編集領域に反映され、
クリップボードへコピーされます。
"""
import json
import os
import tkinter as tk
from tkinter import ttk

from src.core.one_click_manager import DEFAULT_ENTRY_COUNT, OneClickManager


class OneClickFrame(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        """
        コンストラクタ。
        ウィジェットの初期化と作成を行います。
        
        引数:
          master (tk.Widget): 親ウィジェット
          *args: その他の引数（なし）
          **kwargs: キーワード引数（なし）
        
        戻り値:
          なし
        """
        super().__init__(master, *args, **kwargs)
        self.manager = OneClickManager()  # ロジック部分の管理クラス
        # 各カテゴリごとのボタンウィジェットを格納する辞書
        self.button_widgets = {}
        self.create_widgets()
        # 上下左右キーでボタン位置移動のバインド
        self.bind_all("<Up>", lambda event: self.move_selected_button("up"))
        self.bind_all("<Down>", lambda event: self.move_selected_button("down"))
        self.bind_all("<Left>", lambda event: self.move_selected_button("left"))
        self.bind_all("<Right>", lambda event: self.move_selected_button("right"))

    def create_widgets(self):
        """
        UIウィジェットの作成を行います。
        
        引数:
          なし
        
        戻り値:
          なし
        """
        self.create_tab_notebook()  # カテゴリごとのタブ作成
        self.create_editor_area()  # エディタ部分作成（全カテゴリ共通）

    def create_tab_notebook(self):
        """
        カテゴリごとにタブを作成し、それぞれにボタンのグリッドを配置します。
        
        引数:
          なし
        
        戻り値:
          なし
        """
        # タブの幅を固定するスタイル設定
        style = ttk.Style()
        # TNotebook.Tabに固定幅（例: 幅15）と余白を設定（必要に応じて調整してください）
        style.configure("TNotebook.Tab", padding=[2, 1], width=15)

        self.tab_notebook = ttk.Notebook(self)
        self.tab_notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # 管理クラスからカテゴリ一覧を取得
        categories = list(self.manager.one_click_entries.keys())

        for category in categories:
            frame = ttk.Frame(self.tab_notebook)
            self.tab_notebook.add(frame, text=category)
            self.button_widgets[category] = []
            # 2列グリッド用の設定
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            entries = self.manager.one_click_entries.get(category, [])
            for idx, entry in enumerate(entries):
                row = idx // 2
                col = idx % 2
                btn = ttk.Button(frame,
                                 text=entry["title"],
                                 width=20,
                                 command=self.create_button_command(category, idx))
                btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                self.button_widgets[category].append(btn)
                frame.rowconfigure(row, weight=1)

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
        # ボタンパネルの作成
        button_panel = ttk.Frame(edit_frame)
        button_panel.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="ns")
        save_btn = ttk.Button(button_panel, text="更新・保存", command=self.save_current_entry)
        save_btn.pack(side="top", fill="x")
        edit_frame.columnconfigure(1, weight=1)
        # 矢印キーによるボタン位置変更ヒントの表示（目立ちすぎないよう小さくグレーで表示）
        hint_label = ttk.Label(edit_frame,
                               text="※矢印キーでボタン位置を移動できます",
                               font=("Arial", 8),
                               foreground="gray")
        hint_label.grid(row=2, column=1, sticky="e", padx=5, pady=(2, 0))

    def create_button_command(self, category, index):
        """
        指定されたカテゴリとインデックスのボタン用コールバック関数を生成します。
        
        引数:
          category (str): カテゴリ名
          index (int): エントリーのインデックス
        
        戻り値:
          function: 生成されたコールバック関数
        """
        return lambda: self.on_button_click(category, index)

    def move_focus_to_edit(self, event):
        """
        Tabキー押下時に編集エリアにフォーカスを移します。
        
        引数:
          event: イベントオブジェクト（なしの場合は「なし」）
        
        戻り値:
          str: "break"
        """
        self.edit_text.focus_set()
        return "break"

    def on_button_click(self, category, index):
        """
        指定されたカテゴリとインデックスのボタンがクリックされた際に、
        クリップボードに定型文をコピーし、編集用テキストボックスに内容を表示します。
        
        引数:
          category (str): カテゴリ名
          index (int): エントリーのインデックス
        
        戻り値:
          なし
        """
        entry = self.manager.get_entry(category, index)
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
        if self.manager.current_category is not None and self.manager.current_index is not None:
            new_title = self.title_edit.get("1.0", tk.END).strip()
            new_text = self.edit_text.get("1.0", tk.END).strip()

            category = self.manager.current_category
            index = self.manager.current_index

            # 管理クラスを通じてエントリーを更新
            self.manager.update_entry(category, index, new_title, new_text)

            # ボタンの表示を更新
            if category in self.button_widgets and index < len(self.button_widgets[category]):
                self.button_widgets[category][index].config(text=new_title)

    def move_selected_button(self, direction):
        """
        上下左右キー押下時に、選択中のボタン位置を移動します。
        
        引数:
          direction (str): "up"、"down"、"left"、"right"
        
        戻り値:
          なし
        """
        if self.manager.current_category is None or self.manager.current_index is None:
            return

        category = self.manager.current_category
        current_index = self.manager.current_index

        # 管理クラスを通じて移動先インデックスを取得
        target_index = self.manager.get_target_index(current_index, direction)
        if target_index is None:
            return

        # エントリーを入れ替える
        if self.manager.swap_entries(category, current_index, target_index):
            # ボタンの表示内容を更新
            entries = self.manager.one_click_entries[category]
            self.button_widgets[category][current_index].config(
                text=entries[current_index]["title"])
            self.button_widgets[category][target_index].config(text=entries[target_index]["title"])

    def refresh_entries(self):
        """
        ワンクリックエントリーを再読み込みし、各カテゴリのボタン表示を更新します。
        
        引数:
          なし
        
        戻り値:
          なし
        """
        # 現在のタブをすべて削除
        for tab in self.tab_notebook.tabs():
            self.tab_notebook.forget(tab)

        # ボタンウィジェット辞書をクリア
        self.button_widgets.clear()

        # エントリーを再読み込み
        self.manager = OneClickManager()

        # タブを再作成
        self.create_tab_notebook()

    def load_entries(self):
        """
        JSONファイルから定型文エントリーをロードします。
        
        引数:
          なし
          
        戻り値:
          dict: ロードされたエントリー
        """
        try:
            settings_dir = os.path.join(os.getcwd(), "settings")
            json_path = os.path.join(settings_dir, "one_click.json")
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"定型文の読み込みに失敗しました: {e}")
            return {}
