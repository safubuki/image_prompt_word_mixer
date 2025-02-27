"""
final_prompt_frame.py
完成プロンプト（基本＋追加）の表示、クリップボードへのコピー、およびDeePL APIを利用した英訳機能を提供するコンポーネントです。
"""

import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

import requests  # DeePL APIへのアクセスに利用
from src.template_manager import TemplateManager


class FinalPromptFrame(ttk.LabelFrame):
    """
    FinalPromptFrame クラスは、完成プロンプトの表示、コピー、及び英訳の機能を提供するコンポーネントです。
    
    引数:
      master (tk.Widget): 親ウィジェット
      template_manager (object): テンプレート管理オブジェクト
      *args, **kwargs: その他
      
    戻り値:
      なし
    """

    def __init__(self, master, template_manager=None, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): 親ウィジェット
          template_manager (object): テンプレート管理オブジェクト
          *args, **kwargs: その他
          
        戻り値:
          なし
        """
        super().__init__(master, text="完成プロンプト（基本＋追加）", *args, **kwargs)
        self.template_manager = template_manager
        self.update_timer = None
        self.basic_frame = None
        self.element_frame = None
        self.create_widgets()

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.create_final_text_area()
        self.create_translate_button()
        self.create_english_text_area()
        self.create_copy_buttons()

    def create_final_text_area(self):
        """
        完成プロンプト表示用テキスト領域（編集可能）を生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.final_text = tk.Text(self, height=7, width=109)
        self.final_text.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    def create_translate_button(self):
        """
        プロンプトを英語に翻訳するボタンを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        translate_button = ttk.Button(self,
                                      text="▼ プロンプトを英語に翻訳 ▼",
                                      command=self.translate_to_english)
        translate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def create_english_text_area(self):
        """
        英訳結果表示用テキスト領域（読み取り専用）を生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.english_text = tk.Text(self, height=7, width=109, state="disabled")
        self.english_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def create_copy_buttons(self):
        """
        日本語プロンプト・英語プロンプトのコピー用ボタンを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        copy_jp_button = ttk.Button(self, text="日本語プロンプトをコピー", command=self.copy_japanese_prompt)
        copy_eng_button = ttk.Button(self, text="英語プロンプトをコピー", command=self.copy_english_prompt)
        copy_jp_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        copy_eng_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def copy_japanese_prompt(self):
        """
        日本語プロンプトをクリップボードにコピーします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        jp_text = self.final_text.get(1.0, tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(jp_text)

    def copy_english_prompt(self):
        """
        英語プロンプトをクリップボードにコピーします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        en_text = self.english_text.get(1.0, tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(en_text)

    def get_api_key(self):
        """
        api_key.json からAPIキーを取得します。
        
        引数:
          なし
          
        戻り値:
          str または None
        """
        config_dir = os.path.join(os.getcwd(), "config")
        api_key_path = os.path.join(config_dir, "api_key.json")
        if os.path.exists(api_key_path):
            try:
                with open(api_key_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    key = data.get("api_key", "").strip()
                    if key:
                        return key
            except Exception as e:
                messagebox.showerror("エラー", f"APIキーの読み込みに失敗しました: {e}")
        return None

    def translate_to_english(self):
        """
        DeePL API を利用して、完成プロンプトを英訳し、表示します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        api_key = self.get_api_key()
        if not api_key:
            messagebox.showerror("エラー", "DeePLのAPIが設定されていません")
            return

        jp_text = self.final_text.get(1.0, tk.END).strip()

        if not jp_text:
            messagebox.showwarning("警告", "翻訳するプロンプトがありません。")
            return

        url = "https://api-free.deepl.com/v2/translate"
        params = {"auth_key": api_key, "text": jp_text, "target_lang": "EN"}
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()  # HTTPエラーがあれば例外を送出
            result = response.json()
            translations = result.get("translations", [])
            if translations:
                en_text = translations[0].get("text", "")
                self.english_text.config(state="normal")
                self.english_text.insert(tk.END, en_text)
                self.english_text.config(state="disabled")
            else:
                messagebox.showerror("エラー", "翻訳結果が取得できませんでした。")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("エラー", f"翻訳リクエストに失敗しました: {e}")

    def set_input_sources(self, basic_frame, element_frame, template_manager):
        """
        入力ソースとなるフレームとテンプレートマネージャーを設定します。
        
        引数:
          basic_frame (BasicPromptFrame): 基本プロンプトフレーム
          element_frame (ElementPromptFrame): 追加プロンプトフレーム
          template_manager (object): テンプレート管理オブジェクト
          
        戻り値:
          なし
        """
        self.basic_frame = basic_frame
        self.element_frame = element_frame
        self.template_manager = template_manager

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
        if not self.basic_frame or not self.element_frame or not self.template_manager:
            return

        # BasicPromptFrameから現在の基本プロンプトテキストと変数値を取得
        basic_text, variables = self.basic_frame.get_current_prompt()
        final_prompt = self.template_manager.replace_variables(basic_text, variables)

        # ElementPromptFrameから現在の追加プロンプト内容と主語を取得
        element_prompt_raw, subject_val = self.element_frame.get_prompt_content()
        if element_prompt_raw:
            element_text = self.template_manager.replace_variables(element_prompt_raw,
                                                                   {"character": subject_val})
            final_prompt += "\n" + element_text

        self.final_text.delete(1.0, tk.END)
        self.final_text.insert(tk.END, final_prompt)

    def clear(self):
        """
        テキストエリアをクリアします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.final_text.delete(1.0, tk.END)
        self.english_text.config(state="normal")
        self.english_text.delete(1.0, tk.END)
        self.english_text.config(state="disabled")
