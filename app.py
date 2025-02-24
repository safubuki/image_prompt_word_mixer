"""
app.py
Gemini Prompt Generatorアプリケーションの起動およびUI統合機能を提供するコンポーネントです。
"""
import json  # 追加
import os
import subprocess  # 追加
import tkinter as tk
from tkinter import messagebox  # 追加
from tkinter import ttk  # Notebook用に追加

from template_manager import TemplateManager
from ui.basic_prompt_frame import BasicPromptFrame
from ui.element_prompt_frame import ElementPromptFrame
from ui.final_prompt_frame import FinalPromptFrame
from ui.one_click_frame import OneClickFrame  # 新規作成するファイル


class PromptGeneratorApp:
    """
    PromptGeneratorApp クラスは、各UIコンポーネントを統合し、ユーザーがプロンプトを効率的に生成できるようにするための機能を提供します。
    各メソッドは、目的に沿った処理内容（メニュー生成、JSON再読み込み、プロンプト結合など）を実装しています。
    """

    def __init__(self, master):
        """
        コンストラクタ:
          - アプリウィンドウの初期設定（タイトル、アイコン、ウィンドウサイズ固定）
          - メニューバーとNotebookタブの生成
          - 基本、追加、最終プロンプトおよびワンクリック定型UIの配置と初期化
          - jsonファイルからプロンプトデータをロードして各コンポーネントを更新
        
        引数:
            master (tk.Widget): アプリのメインウィジェット（ルートウィンドウ）
        """
        self.master = master
        self.master.title("Image Prompt Word-Mixer ")

        # アイコン設定
        icon_path = os.path.join("image", "turtle.ico")
        try:
            self.master.iconbitmap(icon_path)
        except tk.TclError:
            print(f"アイコンファイルが見つかりませんでした: {icon_path}")

        # Fix: ウィンドウサイズを固定
        self.master.resizable(False, False)

        # メニューバーの作成
        self.create_menu()

        # Notebook（タブ）作成: 異なるプロンプト生成機能を分割して表示
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=1, fill="both")

        # 「プロンプト作成」タブ用フレームを作成
        self.prompt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.prompt_tab, text="プロンプト作成")

        # 「ワンクリック定型」タブ用フレームを作成 ← タイトルを変更
        self.one_click_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.one_click_tab, text="定型文簡単コピー")

        self.template_manager = TemplateManager("basic_prompts.json", "element_prompts.json")
        self.basic_prompts = self.template_manager.get_basic_prompts()
        self.element_prompts = self.template_manager.get_element_prompts()

        self.update_timer = None  # タイマー初期化

        # 各UIコンポーネントを「プロンプト作成」タブ内に配置
        self.basic_frame = BasicPromptFrame(self.prompt_tab, self.basic_prompts,
                                            self.on_basic_select, self.on_text_change)
        self.basic_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.prompt_tab.columnconfigure(0, weight=1)

        self.element_frame = ElementPromptFrame(self.prompt_tab, self.element_prompts,
                                                self.on_element_select, self.on_text_change)
        self.element_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.prompt_tab.columnconfigure(1, weight=1)

        self.final_frame = FinalPromptFrame(self.prompt_tab)
        self.final_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.prompt_tab.rowconfigure(1, weight=1)

        # 変数設定はBasicPromptFrame内のvariable_frameを利用
        self.variable_entries = self.basic_frame.variable_entries

        # 「ワンクリック」タブにワンクリック用のUIコンポーネントを配置
        self.one_click_frame = OneClickFrame(self.one_click_tab)
        self.one_click_frame.pack(expand=1, fill="both", padx=10, pady=10)

        self.set_default_prompt()

    # 新規メソッド: メニューバー作成
    def create_menu(self):
        """
        メニューバー生成:
          - ファイルメニュー: 基本・追加プロンプトの編集やJSONリロード機能を提供
          - 設定メニュー: APIキー設定ダイアログを表示し、ユーザーのAPIキー管理を支援
        
        ユーザーが必要な操作を迅速に実施できるよう、直感的なメニュー構成にしています。
        """
        menubar = tk.Menu(self.master)
        # ファイルメニュー：基本・追加プロンプトの編集
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="基本プロンプト(basic_prompts.json)を開く", command=lambda: self.open_json_editor("basic_prompts.json"))
        file_menu.add_command(label="追加プロンプト(element_prompts.json)を開く", command=lambda: self.open_json_editor("element_prompts.json"))
        file_menu.add_command(label="基本・追加プロンプトJsonをリロード", command=self.reload_json)  # 追加
        menubar.add_cascade(label="ファイル", menu=file_menu)
        # 設定メニュー：APIキー設定
        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label="APIキー設定", command=self.open_api_key_dialog)
        menubar.add_cascade(label="設定", menu=setting_menu)
        self.master.config(menu=menubar)

    # 修正済み: JSONファイル編集用エディター → Windows標準のNotepadで開く
    def open_json_editor(self, file_path):
        try:
            subprocess.Popen(["notepad", file_path])
        except Exception as e:
            messagebox.showerror("エラー", f"{file_path} の起動に失敗しました: {e}")

    # 新規メソッド: APIキー設定用ダイアログ
    def open_api_key_dialog(self):
        """
        APIキー設定ダイアログ:
          - APIキー情報をapi_key.jsonから読み込み、表示します
          - ユーザーが新たなAPIキーを入力後、json形式で保存し、設定を即時反映します
          
          設定内容は、外部API利用時に必要な認証情報として活用されます。
        """
        dialog = tk.Toplevel(self.master)
        dialog.title("APIキー設定")
        tk.Label(dialog, text="DeepLのAPIキーを設定してください。\n保存ボタンを押すとapi_key.jsonに保存します。").pack(padx=10, pady=5)
        entry = tk.Entry(dialog, width=50)
        entry.pack(padx=10, pady=5)
        # api_key.jsonから現在のAPIキーを読み込み
        try:
            with open("api_key.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            current_key = data.get("api_key", "")
        except Exception:
            current_key = ""
        entry.insert(0, current_key)
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=5)
        def save_api_key():
            new_key = entry.get()
            try:
                with open("api_key.json", "w", encoding="utf-8") as f:
                    json.dump({"api_key": new_key}, f, ensure_ascii=False, indent=4)
                # 追加: api_key.jsonを再読み込みして設定を反映
                self.reload_api_key()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")
        tk.Button(button_frame, text="保存", command=save_api_key).pack(side="left", padx=5)
        tk.Button(button_frame, text="キャンセル", command=dialog.destroy).pack(side="left", padx=5)

    def reload_api_key(self):
        """
        APIキーの再読み込み:
          - api_key.jsonから最新のAPIキーを取得し、内部プロパティに反映させます
          - これにより、保存直後からDeeplへのアクセスが可能となります
        """
        try:
            with open("api_key.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            self.deepl_api_key = data.get("api_key", "")
            # オプション: APIキー再設定時の通知やログ出力を実施
            print("APIキーがリロードされました。")
        except Exception as e:
            print(f"APIキーのリロードに失敗しました: {e}")

    def reload_json(self):
        """
        JSONファイルの再読み込み:
          - 基本および追加プロンプトのJSONファイルを再読み込みし、最新データに更新
          - UI（例: コンボボックス）の内容も即時反映
        
        動的なプロンプト更新を可能にし、ファイル編集後の内容変更を即座に利用できるようにします。
        """
        try:
            self.template_manager.basic_prompts = self.template_manager.load_prompts(self.template_manager.basic_prompt_file)
            self.template_manager.element_prompts = self.template_manager.load_prompts(self.template_manager.element_prompt_file)
            self.basic_prompts = self.template_manager.get_basic_prompts()
            self.element_prompts = self.template_manager.get_element_prompts()
            # 基本プロンプトのコンボボックスを更新
            self.basic_frame.basic_combobox['values'] = [p["name"] for p in self.basic_prompts]
            self.basic_frame.basic_combobox.current(0)
            self.on_basic_select(None)
            messagebox.showinfo("情報", "Jsonファイルがリロードされました。")
        except Exception as e:
            messagebox.showerror("エラー", f"Jsonのリロードに失敗しました: {e}")

    def set_default_prompt(self):
        """
        初期の基本プロンプトを設定します。
        """
        self.basic_frame.basic_combobox.current(0)
        self.on_basic_select(None)

    def on_basic_select(self, _):
        """
        基本プロンプト選択時の処理を行います。
        """
        selection = self.basic_frame.basic_combobox.current()
        if selection >= 0:
            prompt_obj = self.basic_prompts[selection]
            self.basic_frame.basic_text.delete(1.0, tk.END)
            self.basic_frame.basic_text.insert(tk.END, prompt_obj["prompt"])
            self.basic_frame.update_variable_entries(prompt_obj["default_variables"])
            self.schedule_update()

    def on_element_select(self, event):
        """
        追加プロンプト選択時の処理:
          - ユーザーが選択した追加プロンプトの内容から、重複のないプロンプトテキストを抽出
          - JSON構造に沿って正確なカテゴリー・プロンプト情報を取得
        
        複数選択された情報を統合し、最終プロンプト生成用に処理内容を保持します。
        """
        selection = event.widget.selection()
        selected_texts = []
        seen_keys = set()
        parent_ids = list(self.element_frame.tree.get_children(""))

        for item in selection:
            parent = self.element_frame.tree.parent(item)
            if parent:
                try:
                    category_index = parent_ids.index(parent)
                except ValueError:
                    continue
                # JSON構造が dict になったため、"categories" キーを追加して取得
                category_data = self.element_prompts["categories"][category_index]
                item_text = self.element_frame.tree.item(item, "text")
                for prompt in category_data["prompt_lists"]:
                    if prompt["title"] == item_text:
                        key = (category_data["category"], prompt["title"], prompt["prompt"])
                        if key not in seen_keys:
                            seen_keys.add(key)
                            selected_texts.append(prompt["prompt"])
                        break

        element_prompt_raw = "\n".join(selected_texts)
        subject_val = self.element_frame.subject_entry.get().strip()
        element_prompt_final = self.template_manager.replace_variables(
            element_prompt_raw, {"character": subject_val})
        # element_textウィジェットではなく、取得したテキストを保持
        self.element_prompt_content = element_prompt_final
        self.schedule_update()

    def on_text_change(self, _):
        """
        テキスト変更時に最終プロンプト更新をスケジュールします。
        """
        self.schedule_update()

    def schedule_update(self):
        """
        一定遅延後に最終プロンプトを生成するタイマーを設定します。
        """
        if self.update_timer:
            self.master.after_cancel(self.update_timer)
        self.update_timer = self.master.after(1000, self.generate_final_prompt)

    def generate_final_prompt(self):
        """
        最終プロンプト生成:
          - 基本プロンプトにユーザー指定の変数を置換して動的に内容を更新
          - 追加プロンプト（重複を除外したユーザー選択内容）を結合して最終プロンプトを構築
          - 完成したプロンプトをUIのテキストウィジェットに反映
        
        この処理により、ユーザーの入力・選択内容を統合した完成度の高いプロンプトが得られます。
        """
        # 基本プロンプトテキスト取得: ユーザーが選択または入力した内容を取得
        basic_text = self.basic_frame.basic_text.get(1.0, tk.END).strip()
        # 変数置換: テキスト内のプレースホルダをUIで入力された値に変換
        variables = {var: entry.get() for var, entry in self.basic_frame.variable_entries.items()}
        final_prompt = self.template_manager.replace_variables(basic_text, variables)
        # 追加プロンプト: ユーザーの選択に基づいたテキストを結合
        element_text = getattr(self, 'element_prompt_content', '')
        final_prompt += "\n" + element_text

        self.final_frame.final_text.delete(1.0, tk.END)
        self.final_frame.final_text.insert(tk.END, final_prompt)


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
