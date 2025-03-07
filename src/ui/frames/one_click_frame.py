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
from tkinter import messagebox, ttk
from typing import Optional  # 追加

from src.core.one_click_manager import OneClickManager
from src.ui.frames.one_click_frame_editor import OneClickFrameEditor
from src.ui.frames.one_click_frame_tab import OneClickFrameTab


class OneClickFrame(ttk.Frame):
    """
    OneClickFrameクラス

    このクラスは、ワンクリックで定型文コピーを実行するUIコンポーネントです。
    タブでカテゴリを分け、各ボタンをクリックすると、該当の定型文がエディタに
    反映され、クリップボードへコピーされます。

    属性:
      manager: 定型文エントリーを管理するクラスインスタンス
      button_widgets: カテゴリごとのボタンウィジェット群
      disable_copy: コピー機能の有効/無効を管理するフラグ
      title_edit: タイトル編集用のテキストウィジェット（エディタ領域）
      edit_text: 定型文編集用のテキストウィジェット（エディタ領域）

    引数:
      master (tk.Widget): 親ウィジェット

    戻り値:
      なし
    """

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

        # 下記属性は後でOneClickFrameEditor.create_editor_area内で生成されるが、
        # mypy対応のために初期値をNoneで宣言しておく
        self.title_edit: Optional[tk.Text] = None
        self.edit_text: Optional[tk.Text] = None

        # ヘルパーオブジェクトの生成
        self._tab_helper = OneClickFrameTab(self)
        self._editor_helper = OneClickFrameEditor(self)
        self.create_widgets()

        # キーバインディングを修正して、テキストボックスにフォーカスがない時のみ動作するよう変更
        self.bind_all("<Up>", self.handle_up_key)
        self.bind_all("<Down>", self.handle_down_key)
        self.bind_all("<Left>", self.handle_left_key)
        self.bind_all("<Right>", self.handle_right_key)

    def handle_up_key(self, _):
        """
        上矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          _: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("up")

    def handle_down_key(self, _):
        """
        下矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          _: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("down")

    def handle_left_key(self, _):
        """
        左矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          _: キーイベント
          
        戻り値:
          なし
        """
        # フォーカスがテキストボックスにあるか確認
        focused = self.master.focus_get()
        if isinstance(focused, tk.Text):
            return  # テキストボックスにフォーカスがある場合は何もしない
        self.move_selected_button("left")

    def handle_right_key(self, _):
        """
        右矢印キーのイベントハンドラ。テキストボックスにフォーカスがない時のみ処理する。
        
        引数:
          _: キーイベント
          
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
        self._tab_helper.create_tab_notebook()  # タブ作成
        self._editor_helper.create_editor_area()  # 編集領域作成

    def create_button_command(self, category, index):
        """
        指定されたカテゴリとインデックスのボタン用コールバック関数を生成します。
        
        引数:
          category (str): カテゴリ名
          index (int): エントリーのインデックス
        
        戻り値:
          function: 生成されたコールバック関数
        """
        return lambda: self._editor_helper.on_button_click(category, index)

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
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, UnicodeDecodeError) as e:
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

                # エディタ領域のウィジェットが生成されていることを保証する
                assert self.title_edit is not None, "タイトル編集ウィジェットが生成されていません。"
                assert self.edit_text is not None, "テキスト編集ウィジェットが生成されていません。"

                # 編集領域の表示を更新
                self.title_edit.delete("1.0", tk.END)
                self.title_edit.insert(tk.END, new_title)
                self.edit_text.delete("1.0", tk.END)

                # ボタンの表示を更新
                if category in self.button_widgets and index < len(self.button_widgets[category]):
                    self.button_widgets[category][index].config(text=new_title)
