"""
one_click_manager.py
ワンクリック機能のデータ管理とロジックを担当するモジュールです。
JSONファイルの読み書きやエントリー操作などを処理します。
"""
import json
import os
from tkinter import messagebox

DEFAULT_ENTRY_COUNT = 20
DEFAULT_CATEGORIES = ["カテゴリ1", "カテゴリ2", "カテゴリ3"]
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
        self.one_click_entries = {}
        self.category_order = []  # カテゴリの表示順を保持するリスト
        self.load_one_click_entries()
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

        self.one_click_entries = {}
        self.category_order = []

        # ファイルが存在しない場合はデフォルト
        if not os.path.exists(json_path):
            self.category_order = DEFAULT_CATEGORIES[:MAX_CATEGORIES]
            for cat in self.category_order:
                self.one_click_entries[cat] = [{
                    "title": "",
                    "text": ""
                } for _ in range(DEFAULT_ENTRY_COUNT)]
            return self.one_click_entries

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

                is_format_converted = False  # フォーマット変換されたかどうか

                # 新形式（order属性を持つ）かどうか確認
                if isinstance(json_data, dict) and "order" in json_data and "entries" in json_data:
                    # 既に新形式: カテゴリ順序とエントリーが分離されている
                    self.category_order = json_data["order"]
                    entries_data = json_data["entries"]
                elif isinstance(json_data, dict):
                    # 中間形式: 辞書形式だがorder属性はない - 変換が必要
                    is_format_converted = True
                    self.category_order = list(json_data.keys())
                    entries_data = json_data
                    # バックアップ作成
                    self._backup_json_file(json_path)
                else:
                    # 旧形式: リスト形式 - 変換が必要
                    is_format_converted = True
                    self.category_order = [DEFAULT_CATEGORIES[0]]
                    entries_data = {DEFAULT_CATEGORIES[0]: json_data}
                    # 他のデフォルトカテゴリも追加
                    for cat in DEFAULT_CATEGORIES[1:]:
                        if cat not in self.category_order:
                            self.category_order.append(cat)
                            entries_data[cat] = []
                    # バックアップ作成
                    self._backup_json_file(json_path)

                # カテゴリ数が上限を超える場合は警告
                if len(self.category_order) > MAX_CATEGORIES:
                    messagebox.showwarning(
                        "警告", f"カテゴリタブは{MAX_CATEGORIES}つまでしか設定できません。先頭{MAX_CATEGORIES}個のみ読み込みます。")
                    self.category_order = self.category_order[:MAX_CATEGORIES]

                # カテゴリ順序に従ってエントリーを処理
                for cat in self.category_order:
                    entries = entries_data.get(cat, [])
                    # エントリーのバリデーションと正規化
                    for entry in entries:
                        if "title" not in entry:
                            entry["title"] = ""
                        if "text" not in entry:
                            entry["text"] = ""
                    # エントリー数を標準化
                    while len(entries) < DEFAULT_ENTRY_COUNT:
                        entries.append({"title": "", "text": ""})
                    self.one_click_entries[cat] = entries[:DEFAULT_ENTRY_COUNT]

                # データ形式が変換された場合、ユーザーに通知（初回のみ）
                if is_format_converted:
                    messagebox.showinfo(
                        "情報", "定型文データの形式を更新しました。\n"
                        "カテゴリの順序が保持されるようになります。\n"
                        "元のデータは「one_click.json.bak」にバックアップされています。")
                    # 新形式で保存
                    self.save_one_click_entries()

                # 少なくとも1つのカテゴリがあることを保証
                if not self.category_order:
                    self.category_order = DEFAULT_CATEGORIES[:MAX_CATEGORIES]
                    for cat in self.category_order:
                        self.one_click_entries[cat] = [{
                            "title": "",
                            "text": ""
                        } for _ in range(DEFAULT_ENTRY_COUNT)]

                return self.one_click_entries

        except Exception as e:
            print(f"one_click.json の読み込みに失敗しました: {e}")
            # エラー時はデフォルト値を使用
            self.category_order = DEFAULT_CATEGORIES[:MAX_CATEGORIES]
            for cat in self.category_order:
                self.one_click_entries[cat] = [{
                    "title": "",
                    "text": ""
                } for _ in range(DEFAULT_ENTRY_COUNT)]
            return self.one_click_entries

    def _backup_json_file(self, file_path):
        """
        JSONファイルのバックアップを作成します。
        
        引数:
          file_path (str): バックアップ対象のファイルパス
        
        戻り値:
          なし
        """
        try:
            backup_path = file_path + ".bak"
            # バックアップが既に存在する場合は上書きしない
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"バックアップ作成: {backup_path}")
        except Exception as e:
            print(f"バックアップ作成に失敗しました: {e}")

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
        if len(self.category_order) > MAX_CATEGORIES:
            messagebox.showwarning("警告", f"カテゴリタブは{MAX_CATEGORIES}つまでしか設定できません。")
            # 最大数に制限
            self.category_order = self.category_order[:MAX_CATEGORIES]
            limited_entries = {}
            for cat in self.category_order:
                if cat in self.one_click_entries:
                    limited_entries[cat] = self.one_click_entries[cat]
            self.one_click_entries = limited_entries

        # orderリストの順序に合わせてentriesを整理
        ordered_entries = {}
        for category in self.category_order:
            if category in self.one_click_entries:
                ordered_entries[category] = self.one_click_entries[category]

        # 新しいJSON構造（順序情報を含む）
        json_data = {"order": self.category_order, "entries": ordered_entries}

        # settingsフォルダのパスを取得し、そこにJSONを保存
        settings_dir = os.path.join(os.getcwd(), "settings")
        json_path = os.path.join(settings_dir, "one_click.json")

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
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

    def rename_category(self, old_name, new_name):
        """
        カテゴリ名を変更します。
        順序は維持されます。
        
        引数:
          old_name (str): 現在のカテゴリ名
          new_name (str): 新しいカテゴリ名
          
        戻り値:
          bool: 名前変更が成功したかどうか
        """
        if old_name not in self.one_click_entries:
            return False

        # 同じ名前のカテゴリが既に存在する場合はエラー
        if new_name in self.one_click_entries and old_name != new_name:
            messagebox.showerror("エラー", f"カテゴリ名「{new_name}」は既に存在します")
            return False

        # 空の名前はエラー
        if not new_name.strip():
            messagebox.showerror("エラー", "カテゴリ名を入力してください")
            return False

        # カテゴリ名を変更（順序を維持）
        self.one_click_entries[new_name] = self.one_click_entries.pop(old_name)

        # カテゴリ順序リストも更新（重要: 同じインデックス位置で名前のみ変更）
        for i, cat in enumerate(self.category_order):
            if cat == old_name:
                self.category_order[i] = new_name
                break

        # 現在選択中のカテゴリを更新
        if self.current_category == old_name:
            self.current_category = new_name

        # 変更を保存（JSONファイルの保存位置は変わりません）
        self.save_one_click_entries()
        return True
