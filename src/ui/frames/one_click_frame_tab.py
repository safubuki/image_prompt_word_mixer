import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


class OneClickFrameTab:

    def __init__(self, owner):
        """
        owner には OneClickFrame のインスタンスが渡されます。
        """
        self.owner = owner
        self.last_click_x = 0
        self.last_click_y = 0

    def create_tab_notebook(self):
        owner = self.owner
        # タブの幅を固定するためのスタイル設定
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[2, 1], width=14)

        owner.tab_notebook = ttk.Notebook(owner)
        owner.tab_notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # タブ用コンテキストメニューの拡張
        owner.tab_context_menu = tk.Menu(owner, tearoff=0)
        owner.tab_context_menu.add_command(label="タブ名変更", command=self.rename_selected_tab)
        owner.tab_context_menu.add_separator()
        owner.tab_context_menu.add_command(label="新規タブ追加", command=self.add_new_tab)
        owner.tab_context_menu.add_command(label="タブ削除", command=self.delete_current_tab)
        # 新規追加：タブ移動機能
        owner.tab_context_menu.add_separator()
        owner.tab_context_menu.add_command(label="タブを左に移動", command=self.move_tab_left)
        owner.tab_context_menu.add_command(label="タブを右に移動", command=self.move_tab_right)

        # 複数のイベントを削除し、1つだけにシンプル化
        owner.tab_notebook.bind("<ButtonPress-3>", self.show_tab_context_menu)

        # 管理クラスからカテゴリ一覧を取得しタブを作成
        categories = owner.manager.category_order
        for category in categories:
            self.create_tab_for_category(category)

    def create_tab_for_category(self, category):
        """新しいタブを作成"""
        owner = self.owner
        frame = ttk.Frame(owner.tab_notebook)
        frame.bind("<Button-3>", self.on_tab_right_click)

        owner.tab_notebook.add(frame, text=category)
        owner.button_widgets[category] = []

        # 2列グリッド用の設定
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # エントリーを取得してボタンを配置
        entries = owner.manager.one_click_entries.get(category, [])
        for idx, entry in enumerate(entries):
            row = idx // 2
            col = idx % 2
            btn = ttk.Button(frame,
                             text=entry["title"],
                             width=20,
                             command=owner.create_button_command(category, idx))
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            owner.button_widgets[category].append(btn)
            frame.rowconfigure(row, weight=1)

        return frame

    def on_tab_right_click(self, event):
        """右クリック位置を記録"""
        self.last_click_x = event.x
        self.last_click_y = event.y
        self.last_click_x_root = event.x_root
        self.last_click_y_root = event.y_root
        # タブの特定を試みる（詳細なデバッグ情報をコンソールに出力）
        try:
            element = self.owner.tab_notebook.identify(event.x, event.y)
            print(f"右クリック検出: 要素={element}, 座標=({event.x}, {event.y})")
        except Exception as e:
            print(f"タブ特定中にエラー: {e}")

    def show_tab_context_menu(self, event):
        """タブを右クリックした際にコンテキストメニューを表示"""
        owner = self.owner  # 明示的に宣言

        # シンプルなアプローチ - 座標に関わらず右クリックでメニューを表示
        try:
            # タブが右クリックされたと仮定し、現在位置にコンテキストメニューを表示
            owner.tab_context_menu.post(event.x_root, event.y_root)
            print(f"コンテキストメニューを表示: 座標=({event.x_root}, {event.y_root})")
            return "break"  # イベント伝播を停止
        except Exception as e:
            print(f"メニュー表示エラー: {e}")
            import traceback
            traceback.print_exc()

    def rename_selected_tab(self):
        """選択中のタブ名を変更"""
        owner = self.owner
        current_tab_index = owner.tab_notebook.index("current")
        if current_tab_index < 0:
            return

        old_name = owner.tab_notebook.tab(current_tab_index, "text")
        new_name = simpledialog.askstring("タブ名変更",
                                          "新しいタブ名を入力してください:",
                                          initialvalue=old_name,
                                          parent=owner)

        if not new_name or new_name == old_name:
            return

        # OneClickManager でカテゴリ名を変更
        if owner.manager.rename_category(old_name, new_name):
            owner.tab_notebook.tab(current_tab_index, text=new_name)
            # button_widgets のキーを更新
            if old_name in owner.button_widgets:
                owner.button_widgets[new_name] = owner.button_widgets.pop(old_name)
            print(f"タブ名を '{old_name}' から '{new_name}' に変更しました")

    def add_new_tab(self):
        """新しいタブ（カテゴリ）を追加"""
        owner = self.owner
        new_name = simpledialog.askstring("新規タブ追加", "新しいタブ名を入力してください:", parent=owner)
        if not new_name:
            return

        # 既存のカテゴリ名と重複チェック
        if new_name in owner.manager.category_order:
            messagebox.showerror("エラー", f"'{new_name}' は既に存在します。別の名前を指定してください。")
            return

        # カテゴリを追加
        owner.manager.add_category(new_name)
        # 新しいタブを作成
        self.create_tab_for_category(new_name)
        print(f"新しいタブ '{new_name}' を追加しました")

    def delete_current_tab(self):
        """選択中のタブを削除"""
        owner = self.owner
        current_tab_index = owner.tab_notebook.index("current")
        if current_tab_index < 0:
            return

        category = owner.tab_notebook.tab(current_tab_index, "text")
        if len(owner.manager.category_order) <= 1:
            messagebox.showwarning("警告", "最後のタブは削除できません。")
            return

        if messagebox.askyesno("確認", f"タブ '{category}' とその中の全てのボタンを削除しますか？"):
            try:
                # カテゴリを削除
                result = owner.manager.remove_category(category)
                print(f"カテゴリ削除結果: {result}")

                # タブを削除
                owner.tab_notebook.forget(current_tab_index)

                # button_widgets から削除
                if category in owner.button_widgets:
                    del owner.button_widgets[category]

                # 画面を更新（必要に応じて）
                owner.update()

                print(f"タブ '{category}' を削除しました")
            except Exception as e:
                print(f"タブ削除中にエラーが発生しました: {e}")
                import traceback
                traceback.print_exc()

    def move_tab_left(self):
        """タブを左に移動"""
        owner = self.owner
        current_index = owner.tab_notebook.index("current")
        if current_index <= 0:
            messagebox.showinfo("情報", "これ以上左には移動できません。")
            return
        # swap managerの順序リスト内のカテゴリ
        order = owner.manager.category_order
        order[current_index - 1], order[current_index] = order[current_index], order[current_index -
                                                                                     1]
        owner.manager.save_one_click_entries()
        self.update_tabs_order()
        print(f"タブを左に移動: インデックス {current_index} -> {current_index - 1}")

    def move_tab_right(self):
        """タブを右に移動"""
        owner = self.owner
        current_index = owner.tab_notebook.index("current")
        if current_index >= len(owner.manager.category_order) - 1:
            messagebox.showinfo("情報", "これ以上右には移動できません。")
            return
        order = owner.manager.category_order
        order[current_index], order[current_index + 1] = order[current_index +
                                                               1], order[current_index]
        owner.manager.save_one_click_entries()
        self.update_tabs_order()
        print(f"タブを右に移動: インデックス {current_index} -> {current_index + 1}")

    def update_tabs_order(self):
        """
        manager.category_order の順序に従い、タブのUIを再構築します。
        既存のタブを全て削除し、再生成します。
        """
        owner = self.owner
        # 現在の選択タブのカテゴリ名（再選択用）
        try:
            current_category = owner.tab_notebook.tab("current", "text")
        except Exception:
            current_category = None
        # 全タブ削除
        for tab_id in owner.tab_notebook.tabs():
            owner.tab_notebook.forget(tab_id)
        owner.button_widgets = {}
        # manager.category_orderの順にタブ作成
        for cat in owner.manager.category_order:
            self.create_tab_for_category(cat)
        # 可能なら再選択
        if current_category and current_category in owner.manager.category_order:
            new_index = owner.manager.category_order.index(current_category)
            owner.tab_notebook.select(new_index)
