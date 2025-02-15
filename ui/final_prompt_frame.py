"""
final_prompt_frame.py
完成プロンプト（基本＋追加）の表示、クリップボードへのコピー、およびDeePL APIを利用した英訳機能を提供するコンポーネントです。
"""

import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

import requests  # DeePL APIへのアクセスに利用


class FinalPromptFrame(ttk.LabelFrame):
    """
    FinalPromptFrame クラスは、完成プロンプトの表示、コピー、及び英訳を提供するコンポーネントです。
    """

    def __init__(self, master, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
            master (tk.Widget): 親ウィジェット
        """
        super().__init__(master, text="完成プロンプト（基本＋追加）", *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        """
        # 完成プロンプト表示用テキスト領域
        self.final_text = tk.Text(self, height=7, width=109, state="disabled")
        self.final_text.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # プロンプトを英語に翻訳するボタン
        translate_button = ttk.Button(self,
                                      text="▼ プロンプトを英語に翻訳 ▼",
                                      command=self.translate_to_english)
        translate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # 英訳結果を表示するテキスト領域
        self.english_text = tk.Text(self, height=7, width=109, state="disabled")
        self.english_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # 日本語プロンプトをコピーするボタンと、英語プロンプトをコピーするボタンを
        # 英訳結果テキスト領域の下に、同じ行に中央寄せで横並びに配置する
        copy_jp_button = ttk.Button(self, text="日本語プロンプトをコピー", command=self.copy_japanese_prompt)
        copy_eng_button = ttk.Button(self, text="英語プロンプトをコピー", command=self.copy_english_prompt)
        copy_jp_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        copy_eng_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        # 各列の重みを設定して中央寄せを実現
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def copy_japanese_prompt(self):
        """
        日本語プロンプトをクリップボードにコピーします。
        """
        jp_text = self.final_text.get(1.0, tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(jp_text)

    def copy_english_prompt(self):
        """
        英語プロンプトをクリップボードにコピーします。
        """
        en_text = self.english_text.get(1.0, tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(en_text)

    def get_api_key(self):
        """
        api_key.json からAPIキーを取得します。
        """
        api_key_path = "api_key.json"
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
        DeePL APIを利用して、完成プロンプトを英訳し、英訳結果を英語用テキスト領域に表示します。
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
                self.english_text.delete(1.0, tk.END)
                self.english_text.insert(tk.END, en_text)
                self.english_text.config(state="disabled")
            else:
                messagebox.showerror("エラー", "翻訳結果が取得できませんでした。")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("エラー", f"翻訳リクエストに失敗しました: {e}")
