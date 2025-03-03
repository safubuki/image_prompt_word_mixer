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
from tkinter import messagebox, simpledialog, ttk

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
        self.disable_copy = tk.BooleanVar(value=False)  # コピー無効フラグを追加
        self.create_widgets()

        # キーバインディングを修正して、テキストボックスにフォーカスがない時のみ動作するよう変更
        self.bind_all("<Up>", self.handle_up_key)
        self.bind_all("<Down>", self.handle_down_key)
        self.bind_all("<Left>", self.handle_left_key)
        self.bind_all("<Right>", self.handle_right_key)

    def handle_up_key(self, event):
        """
        上矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          event: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("up")

    def handle_down_key(self, event):
        """
        下矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          event: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("down")

    def handle_left_key(self, event):
        """
        左矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          event: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("left")

    def handle_right_key(self, event):
        """
        右矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          event: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("right")

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
        # TNotebook.Tabに固定幅と余白を設定（タブ幅を小さく設定）
        style.configure("TNotebook.Tab", padding=[2, 1], width=14)

        self.tab_notebook = ttk.Notebook(self)
        self.tab_notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # タブコンテキストメニュー設定
        self.tab_context_menu = tk.Menu(self, tearoff=0)
        self.tab_context_menu.add_command(label="タブ名変更", command=self.rename_selected_tab)

        # タブ右クリックイベントを設定
        self.tab_notebook.bind("<ButtonPress-3>", self.show_tab_context_menu)

        # 管理クラスからカテゴリ一覧を取得（順序を保持）
        categories = self.manager.category_order

        # この順序どおりにタブを作成するので、タブの位置は維持されます
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

    def show_tab_context_menu(self, event):
        """
        タブを右クリックした際にコンテキストメニューを表示します。
        
        引数:
          event: マウスイベント
        
        戻り値:
          なし
        """
        try:
            # クリックされた位置からタブインデックスを取得
            clicked_tab = self.tab_notebook.tk.call(self.tab_notebook._w, "identify", "tab",
                                                    event.x, event.y)

            # タブが有効な場合のみメニューを表示
            if clicked_tab >= 0:
                self.tab_notebook.select(clicked_tab)  # クリックされたタブを選択状態にする
                self.tab_context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"タブメニュー表示中にエラーが発生しました: {e}")

    def rename_selected_tab(self):
        """
        選択中のタブの名前を変更するダイアログを表示します。
        
        引数:
          なし
        
        戻り値:
          なし
        """
        current_tab_index = self.tab_notebook.index("current")
        if current_tab_index < 0:
            return

        old_name = self.tab_notebook.tab(current_tab_index, "text")

        # 新しいタブ名を入力するダイアログを表示
        new_name = simpledialog.askstring("タブ名変更", "新しいタブ名を入力してください:", initialvalue=old_name)

        # キャンセルされた場合や空の入力の場合は何もしない
        if not new_name:
            return

        # OneClickManagerでカテゴリ名を変更（内部で順序は維持されます）
        if self.manager.rename_category(old_name, new_name):
            # タブのテキストを更新（位置はそのまま）
            self.tab_notebook.tab(current_tab_index, text=new_name)

            # button_widgetsのキーも更新
            if old_name in self.button_widgets:
                self.button_widgets[new_name] = self.button_widgets.pop(old_name)

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

        # テキストボックスにフォーカス状態変更コールバックを追加
        self.title_edit.bind("<FocusIn>", self.on_text_focus_in)
        self.title_edit.bind("<FocusOut>", self.on_text_focus_out)

        text_label = ttk.Label(edit_frame, text="定型文:")
        text_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.edit_text = tk.Text(edit_frame, height=5)
        self.edit_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # テキストボックスにフォーカス状態変更コールバックを追加
        self.edit_text.bind("<FocusIn>", self.on_text_focus_in)
        self.edit_text.bind("<FocusOut>", self.on_text_focus_out)

        # ボタンパネルの作成
        button_panel = ttk.Frame(edit_frame)
        button_panel.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="ns")
        save_btn = ttk.Button(button_panel, text="更新・保存", command=self.save_current_entry)
        save_btn.pack(side="top", fill="x")

        # クリアボタンを追加
        clear_btn = ttk.Button(button_panel, text="クリア", command=self.clear_current_entry)
        clear_btn.pack(side="top", fill="x", pady=(5, 0))

        # コピー無効チェックボックスを追加
        disable_copy_cb = ttk.Checkbutton(button_panel, text="コピー無効", variable=self.disable_copy)
        disable_copy_cb.pack(side="top", fill="x", pady=(5, 0))

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

        # コピー無効チェックボックスがオフの場合のみクリップボードにコピー
        if not self.disable_copy.get():
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
        # コピー無効フラグの値を保持
        disable_copy_value = self.disable_copy.get()

        # すべてのウィジェットを破棄
        for widget in self.winfo_children():
            widget.destroy()

        # ボタンウィジェット辞書をクリア
        self.button_widgets.clear()

        # エントリーを再読み込み
        self.manager = OneClickManager()

        # コピー無効フラグを再初期化（以前の値を保持）
        self.disable_copy = tk.BooleanVar(value=disable_copy_value)

        # UIを再構築
        self.create_widgets()

        # キーバインドを再設定
        self.bind_all("<Up>", self.handle_up_key)
        self.bind_all("<Down>", self.handle_down_key)
        self.bind_all("<Left>", self.handle_left_key)
        self.bind_all("<Right>", self.handle_right_key)

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

    def on_text_focus_in(self, event):
        """
        テキストボックスがフォーカスを得た時の処理。
        
        引数:
          event: フォーカスイベント
          
        戻り値:
          なし
        """
        # デバッグ用のコンソール出力（必要に応じて）
        # print("テキスト入力モード：ボタン移動は無効")
        pass

    def on_text_focus_out(self, event):
        """
        テキストボックスがフォーカスを失った時の処理。
        
        引数:
          event: フォーカスイベント
          
        戻り値:
          なし
        """
        # デバッグ用のコンソール出力（必要に応じて）
        # print("テキスト入力モード終了：ボタン移動有効")
        pass

    def clear_current_entry(self):
        """
        確認ダイアログを表示し、OKが押された場合は
        現在選択中のエントリーの内容をクリアします。
        タイトルを「（空き）」に設定し、定型文を空にします。
        
        引数:
          なし
        
        戻り値:
          なし
        """
        if self.manager.current_category is not None and self.manager.current_index is not None:
            # 確認ダイアログを表示
            if messagebox.askokcancel("確認", "登録内容をクリアします"):
                category = self.manager.current_category
                index = self.manager.current_index

                # タイトルを「（空き）」に、テキストを空文字に設定
                new_title = "（空き）"
                new_text = ""

                # 管理クラスを通じてエントリーを更新
                self.manager.update_entry(category, index, new_title, new_text)

                # 編集領域の表示を更新
                self.title_edit.delete("1.0", tk.END)
                self.title_edit.insert(tk.END, new_title)
                self.edit_text.delete("1.0", tk.END)

                # ボタンの表示を更新
                if category in self.button_widgets and index < len(self.button_widgets[category]):
                    self.button_widgets[category][index].config(text=new_title)
