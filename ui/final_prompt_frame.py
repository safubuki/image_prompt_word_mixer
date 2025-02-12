"""
final_prompt_frame.py
完成プロンプト（基本＋追加）の表示およびクリップボードへのコピー機能を提供するコンポーネントです。
"""

import tkinter as tk
from tkinter import ttk


class FinalPromptFrame(ttk.LabelFrame):
    """
    FinalPromptFrame クラスは、完成プロンプトの表示とクリップボードへのコピー機能を提供するコンポーネントです。
    """

    def __init__(self, master, copy_command, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
            master (tk.Widget): 親ウィジェット
            copy_command (function): コピー時に実行するコールバック関数
            *args, **kwargs: その他の引数
        """
        super().__init__(master, text="初回画像生成用プロンプト（基本＋追加）", *args, **kwargs)
        self.copy_command = copy_command
        self.create_widgets()

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        """
        self.final_text = tk.Text(self, height=10, width=109, state="disabled")
        self.final_text.grid(row=0, column=0, padx=5, pady=5)
        copy_button = ttk.Button(self, text="クリップボードにコピー", command=self.copy_command)
        copy_button.grid(row=1, column=0, padx=5, pady=5)
