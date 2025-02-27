"""
app.py
Gemini Prompt Generatorアプリケーションの起動およびUI統合機能を提供するコンポーネントです。
"""
import json
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

from template_manager import TemplateManager
from ui.basic_prompt_frame import BasicPromptFrame
from ui.element_prompt_frame import ElementPromptFrame
from ui.final_prompt_frame import FinalPromptFrame
from ui.one_click_frame import OneClickFrame


class PromptGeneratorApp:
    """
    PromptGeneratorApp クラスは、各UIコンポーネントの統合とプロンプト生成処理を管理します。
    
    引数:
      master (tk.Widget): メインウィジェット
       
    戻り値:
      なし
    """

    def __init__(self, master):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): メインウィジェット
          
        戻り値:
          なし
        """
        self.master = master
        self.master.title("Image Prompt Word-Mixer ")
        self.set_icon()
        self.master.resizable(False, False)
        self.create_menu()
        self.create_notebook()
        self.load_prompts()
        self.create_ui_components()
        self.basic_frame.set_basic_prompt(0)

    def set_icon(self):
        """
        アプリのアイコンを設定します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        icon_path = os.path.join("image", "turtle.ico")
        try:
            self.master.iconbitmap(icon_path)
        except tk.TclError:
            print(f"アイコンファイルが見つかりませんでした: {icon_path}")

    def create_menu(self):
        """
        メニューバーを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="基本プロンプト編集",
                              command=lambda: self.open_json_editor("basic_prompts.json"))
        file_menu.add_command(label="追加プロンプト編集",
                              command=lambda: self.open_json_editor("element_prompts.json"))
        file_menu.add_command(label="定型文編集",
                              command=lambda: self.open_json_editor("one_click.json"))
        # 定型文ファイルの後、区切り線を追加
        file_menu.add_separator()
        # 編集結果反映機能を統合して全設定ファイルを反映
        file_menu.add_command(label="編集内容を反映", command=self.reload_json)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label="APIキー設定", command=self.open_api_key_dialog)
        menubar.add_cascade(label="設定", menu=setting_menu)
        self.master.config(menu=menubar)

    def create_notebook(self):
        """
        Notebook タブを作成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=1, fill="both")
        self.prompt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.prompt_tab, text="プロンプト作成")
        self.one_click_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.one_click_tab, text="定型文簡単コピー")

    def load_prompts(self):
        """
        JSONファイルからプロンプトデータを読み込みます。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.template_manager = TemplateManager("basic_prompts.json", "element_prompts.json")
        self.basic_prompts = self.template_manager.get_basic_prompts()
        self.element_prompts = self.template_manager.get_element_prompts()
        self.update_timer = None

    def create_ui_components(self):
        """
        UIコンポーネントを生成・配置します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
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
        self.variable_entries = self.basic_frame.variable_entries
        self.one_click_frame = OneClickFrame(self.one_click_tab)
        self.one_click_frame.pack(expand=1, fill="both", padx=10, pady=10)

    def open_json_editor(self, file_path):
        """
        指定されたJSONファイルをエディタで開きます。
        
        引数:
          file_path (str): ファイルパス
          
        戻り値:
          なし
        """
        try:
            subprocess.Popen(["notepad", file_path])
        except Exception as e:
            messagebox.showerror("エラー", f"{file_path} の起動に失敗しました: {e}")

    def open_api_key_dialog(self):
        """
        APIキー設定ダイアログを表示します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        dialog = tk.Toplevel(self.master)
        dialog.title("APIキー設定")
        tk.Label(dialog, text="DeepLのAPIキーを設定してください。\n保存ボタンを押すとapi_key.jsonに保存します。").pack(padx=10,
                                                                                          pady=5)
        entry = tk.Entry(dialog, width=50)
        entry.pack(padx=10, pady=5)
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
                self.reload_api_key()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")

        tk.Button(button_frame, text="保存", command=save_api_key).pack(side="left", padx=5)
        tk.Button(button_frame, text="キャンセル", command=dialog.destroy).pack(side="left", padx=5)

    def reload_api_key(self):
        """
        APIキーを再読み込みします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        try:
            with open("api_key.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            self.deepl_api_key = data.get("api_key", "")
            print("APIキーを設定しました。")
        except Exception as e:
            print(f"APIキーの設定に失敗しました: {e}")

    def reload_json(self):
        """
        JSONファイルを再読み込みし、UIを更新します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        try:
            # 既存の基本プロンプト、追加プロンプトの反映
            self.template_manager.basic_prompts = self.template_manager.load_prompts(
                self.template_manager.basic_prompt_file)
            self.template_manager.element_prompts = self.template_manager.load_prompts(
                self.template_manager.element_prompt_file)
            self.basic_prompts = self.template_manager.get_basic_prompts()
            self.element_prompts = self.template_manager.get_element_prompts()

            # BasicPromptFrameとElementPromptFrameの更新用メソッドを呼び出す
            self.basic_frame.update_basic_prompts(self.basic_prompts)
            self.basic_frame.set_basic_prompt(0)
            self.element_frame.update_element_prompts(self.element_prompts)

            # one_click_frame のエントリーも反映
            self.one_click_frame.refresh_entries()
            messagebox.showinfo("情報", "全ての編集結果が反映されました。")
        except Exception as e:
            messagebox.showerror("エラー", f"編集結果の反映に失敗しました: {e}")

    def on_basic_select(self, _):
        """
        基本プロンプト選択時の処理を行います。
        
        引数:
          _ : イベント引数（なしの場合は「なし」）
          
        戻り値:
          なし
        """
        self.schedule_update()

    def on_element_select(self, _):
        """
        追加プロンプト選択時の処理を行います。
        
        引数:
          _ : イベント引数
          
        戻り値:
          なし
        """
        self.schedule_update()

    def on_text_change(self, _):
        """
        テキスト変更時の処理を実行します。
        
        引数:
          _ : イベント引数（なしの場合は「なし」）
          
        戻り値:
          なし
        """
        self.schedule_update()

    def schedule_update(self):
        """
        最終プロンプト生成を一定遅延後にスケジュールします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        if self.update_timer:
            self.master.after_cancel(self.update_timer)
        self.update_timer = self.master.after(1000, self.generate_final_prompt)

    def generate_final_prompt(self):
        """
        基本プロンプトと追加プロンプトを結合し、最終プロンプトを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        # BasicPromptFrameから現在の基本プロンプトテキストと変数値を取得
        basic_text, variables = self.basic_frame.get_current_prompt()
        final_prompt = self.template_manager.replace_variables(basic_text, variables)

        # ElementPromptFrameから現在の追加プロンプト内容と主語を取得
        element_prompt_raw, subject_val = self.element_frame.get_prompt_content()
        if element_prompt_raw:
            element_text = self.template_manager.replace_variables(element_prompt_raw,
                                                                   {"character": subject_val})
            final_prompt += "\n" + element_text

        self.final_frame.final_text.delete(1.0, tk.END)
        self.final_frame.final_text.insert(tk.END, final_prompt)


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
