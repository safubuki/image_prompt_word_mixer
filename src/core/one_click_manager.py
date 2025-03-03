"""
one_click_manager.py
ワンクリック機能のデータ管理とロジックを担当するモジュールです。
JSONファイルの読み書きやエントリー操作などを処理します。
"""
import json
import os
from tkinter import messagebox

DEFAULT_ENTRY_COUNT = 20
DEFAULT_CATEGORIES = ["よく使う", "表情", "品質向上", "品質向上1", "品質向上2", "品質向上3", "品質向上4", "品質向上5"]
MAX_CATEGORIES = 8  # カテゴリタブの最大数（7から8に変更）


class OneClickManager:
    """
    ワンクリック機能のデータ管理とロジックを担当するクラスです。
    JSONファイルの読み書き、エントリーの操作などを処理します。
    """

    def __init__(self):
        """
        コンストラクタ。
        データの初期化を行います。
        """
        self.one_click_entries = self.load_one_click_entries()
        self.current_category = None
        self.current_index = None

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
        # settingsフォルダのパスを取得
        settings_dir = os.path.join(os.getcwd(), "settings")
        json_path = os.path.join(settings_dir, "one_click.json")

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

        # settingsフォルダのパスを取得し、そこにJSONを保存
        settings_dir = os.path.join(os.getcwd(), "settings")
        json_path = os.path.join(settings_dir, "one_click.json")

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.one_click_entries, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"one_click.json の保存に失敗しました: {e}")

    def update_entry(self, category, index, title, text):
        """
        指定されたカテゴリとインデックスのエントリーを更新します。
        
        引数:
          category (str): カテゴリ名
          index (int): エントリーのインデックス
          title (str): 新しいタイトル
          text (str): 新しいテキスト
        
        戻り値:
          bool: 更新が成功したかどうか
        """
        if category in self.one_click_entries and 0 <= index < len(
                self.one_click_entries[category]):
            self.one_click_entries[category][index]["title"] = title
            self.one_click_entries[category][index]["text"] = text
            self.current_category = category
            self.current_index = index
            self.save_one_click_entries()
            return True
        return False

    def get_entry(self, category, index):
        """
        指定されたカテゴリとインデックスのエントリーを取得します。
        
        引数:
          category (str): カテゴリ名
          index (int): エントリーのインデックス
        
        戻り値:
          dict: エントリー情報（title, textのキーを持つ辞書）
        """
        if category in self.one_click_entries and 0 <= index < len(
                self.one_click_entries[category]):
            self.current_category = category
            self.current_index = index
            return self.one_click_entries[category][index]
        return {"title": "", "text": ""}

    def swap_entries(self, category, index1, index2):
        """
        同じカテゴリ内の2つのエントリーを入れ替えます。
        
        引数:
          category (str): カテゴリ名
          index1 (int): 1つ目のエントリーインデックス
          index2 (int): 2つ目のエントリーインデックス
        
        戻り値:
          bool: 入れ替えが成功したかどうか
        """
        if (category in self.one_click_entries and
                0 <= index1 < len(self.one_click_entries[category]) and
                0 <= index2 < len(self.one_click_entries[category])):

            # エントリーを入れ替え
            entries = self.one_click_entries[category]
            entries[index1], entries[index2] = entries[index2], entries[index1]

            # 現在選択中のインデックスを更新
            if self.current_index == index1:
                self.current_index = index2
            elif self.current_index == index2:
                self.current_index = index1

            self.save_one_click_entries()
            return True
        return False

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
