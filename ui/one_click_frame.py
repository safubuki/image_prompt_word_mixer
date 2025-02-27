"""
one_click_frame.py
ワンクリックで実行できる機能のUIを提供するコンポーネントです。
この画面ではタブでカテゴリ（例: 良く使う、表情、品質向上）を分類し、
各タブ内に従来の定型文コピー機能を配置します。
ボタンをクリックすると該当エントリーのタイトルと定型文が編集領域に反映され、
クリップボードへコピーされます。
※ one_click.json は、各カテゴリごとにエントリーリストを保持する辞書形式で保存・読み出しします。
"""
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

DEFAULT_ENTRY_COUNT = 20
# DEFAULT_CATEGORIESは初期値としてのみ使用し、実際の表示はJSONに基づく
DEFAULT_CATEGORIES = ["よく使う", "表情", "品質向上"]
MAX_CATEGORIES = 7  # カテゴリタブの最大数


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
        self.one_click_entries = self.load_one_click_entries()
        # 各カテゴリごとのボタンウィジェットを格納する辞書
        self.button_widgets = {}
        self.current_category = None
        self.current_index = None
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

        # one_click.jsonから読み込んだカテゴリを使用
        categories = list(self.one_click_entries.keys())

        for category in categories:
            frame = ttk.Frame(self.tab_notebook)
            self.tab_notebook.add(frame, text=category)
            self.button_widgets[category] = []
            # 2列グリッド用の設定
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            entries = self.one_click_entries.get(category, [{
                "title": "",
                "text": ""
            } for _ in range(DEFAULT_ENTRY_COUNT)])
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
        # ※リロードボタンはapp.py側に統合するため削除
        edit_frame.columnconfigure(1, weight=1)
        # ※矢印キーによるボタン位置変更ヒントの表示（目立ちすぎないよう小さくグレーで表示）
        hint_label = ttk.Label(edit_frame,
                               text="※矢印キーでボタン位置を移動できます",
                               font=("Arial", 8),
                               foreground="gray")
        hint_label.grid(row=2, column=1, sticky="e", padx=5, pady=(2, 0))

    def load_one_click_entries(self):
        """
        one_click.jsonから各カテゴリごとのワンクリックエントリーを読み込みます。
        読み込みデータがリストの場合は旧形式として先頭カテゴリに割り当て、
        その他は空エントリーとします。
        
        引数:
          なし
        
        戻り値:
          dict: カテゴリごとにエントリーリストを格納した辞書
        """
        json_path = "one_click.json"
        data = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    if isinstance(json_data, dict):
                        # 新形式の場合：カテゴリごとの辞書形式
                        categories = list(json_data.keys())

                        # カテゴリ数が上限を超える場合は警告
                        if len(categories) > MAX_CATEGORIES:
                            messagebox.showwarning(
                                "警告",
                                f"カテゴリタブは{MAX_CATEGORIES}つまでしか設定できません。先頭{MAX_CATEGORIES}個のみ読み込みます。")
                            categories = categories[:MAX_CATEGORIES]

                        # 有効なカテゴリのみ処理
                        for cat in categories:
                            entries = json_data.get(cat, [])
                            for entry in entries:
                                if "title" not in entry:
                                    entry["title"] = ""
                                if "text" not in entry:
                                    entry["text"] = ""
                            while len(entries) < DEFAULT_ENTRY_COUNT:
                                entries.append({"title": "", "text": ""})
                            data[cat] = entries[:DEFAULT_ENTRY_COUNT]

                    elif isinstance(json_data, list):
                        # 旧形式の場合：先頭カテゴリに割り当て、他は空エントリー
                        entries = json_data
                        while len(entries) < DEFAULT_ENTRY_COUNT:
                            entries.append({"title": "", "text": ""})
                        data[DEFAULT_CATEGORIES[0]] = entries[:DEFAULT_ENTRY_COUNT]
                        for cat in DEFAULT_CATEGORIES[1:]:
                            data[cat] = [{
                                "title": "",
                                "text": ""
                            } for _ in range(DEFAULT_ENTRY_COUNT)]

                    # 少なくとも1つのカテゴリがあることを保証
                    if not data:
                        for cat in DEFAULT_CATEGORIES:
                            data[cat] = [{
                                "title": "",
                                "text": ""
                            } for _ in range(DEFAULT_ENTRY_COUNT)]

                    return data
            except Exception as e:
                print(f"one_click.json の読み込みに失敗しました: {e}")

        # ファイルが存在しない場合、デフォルトカテゴリで初期化
        for cat in DEFAULT_CATEGORIES:
            data[cat] = [{"title": "", "text": ""} for _ in range(DEFAULT_ENTRY_COUNT)]
        return data

    def save_one_click_entries(self):
        """
        ワンクリックエントリーをone_click.jsonに保存します。
        カテゴリ数が上限を超える場合は警告を表示します。
        
        引数:
          なし
        
        戻り値:
          なし
        """
        # カテゴリ数をチェック
        if len(self.one_click_entries) > MAX_CATEGORIES:
            messagebox.showwarning("警告", f"カテゴリタブは{MAX_CATEGORIES}つまでしか設定できません。")
            # 最大数に制限
            categories = list(self.one_click_entries.keys())[:MAX_CATEGORIES]
            limited_entries = {}
            for cat in categories:
                limited_entries[cat] = self.one_click_entries[cat]
            self.one_click_entries = limited_entries

        json_path = "one_click.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.one_click_entries, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"one_click.json の保存に失敗しました: {e}")

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
        self.one_click_entries = self.load_one_click_entries()

        # タブを再作成
        self.create_tab_notebook()

        # 現在選択中のカテゴリが残っているか確認
        if self.current_category not in self.one_click_entries:
            self.current_category = None
            self.current_index = None

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
        self.current_category = category
        self.current_index = index
        entry = self.one_click_entries[category][index]
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
        if self.current_category is not None and self.current_index is not None:
            new_title = self.title_edit.get("1.0", tk.END).strip()
            new_text = self.edit_text.get("1.0", tk.END).strip()
            self.one_click_entries[self.current_category][self.current_index]["title"] = new_title
            self.one_click_entries[self.current_category][self.current_index]["text"] = new_text
            self.save_one_click_entries()
            self.one_click_entries = self.load_one_click_entries()
            self.button_widgets[self.current_category][self.current_index].config(text=new_title)

    def move_selected_button(self, direction):
        """
        上下左右キー押下時に、選択中のボタン位置を移動します。
        移動先が有効な場合、one_click_entries の該当エントリーの位置を入れ替え、
        ボタン表示および json 保存データの順序も更新します。
        
        引数:
          direction (str): "up"、"down"、"left"、"right"
        
        戻り値:
          なし
        """
        if self.current_category is None or self.current_index is None:
            return

        target_index = self.get_target_index(self.current_index, direction)
        if target_index is None:
            return

        # one_click_entries 内のエントリーを入れ替え
        entries = self.one_click_entries[self.current_category]
        entries[self.current_index], entries[target_index] = entries[target_index], entries[
            self.current_index]
        # ボタンウィジェットの表示内容を更新
        buttons = self.button_widgets[self.current_category]
        buttons[self.current_index].config(text=entries[self.current_index]["title"])
        buttons[target_index].config(text=entries[target_index]["title"])

        # 選択中のインデックスを更新し、変更内容を保存
        self.current_index = target_index
        self.save_one_click_entries()

    def get_target_index(self, current, direction):
        """
        現在のインデックスから指定された方向への移動先インデックスを計算します。（2列グリッドを前提）
        
        引数:
          current (int): 現在のインデックス
          direction (str): "up"、"down"、"left"、"right"
        
        戻り値:
          int または None: 新しいインデックス。移動できない場合は None を返す
        """
        if direction == "up":
            new_index = current - 2 if current >= 2 else None
        elif direction == "down":
            new_index = current + 2 if current + 2 < DEFAULT_ENTRY_COUNT else None
        elif direction == "left":
            new_index = current - 1 if current % 2 == 1 else None
        elif direction == "right":
            new_index = current + 1 if current % 2 == 0 and current + 1 < DEFAULT_ENTRY_COUNT else None
        else:
            new_index = None
        return new_index
