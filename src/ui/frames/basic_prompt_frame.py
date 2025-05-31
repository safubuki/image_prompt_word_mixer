"""
basic_prompt_frame.py
基本プロンプトの選択、テンプレート表示および変数入力機能を提供するコンポーネントです。
"""

import tkinter as tk
from tkinter import ttk


class BasicPromptFrame(ttk.LabelFrame):
    """
    BasicPromptFrame クラスは、基本プロンプトの選択、テンプレート表示および変数入力を提供するコンポーネントです。
    
    引数:
      master (tk.Widget): 親ウィジェット
      basic_prompts (list): 基本プロンプトのデータリスト
      on_basic_select (function): コンボボックス選択時のコールバック関数
      on_text_change (function): テキスト変更時のコールバック関数
      *args, **kwargs: その他
     
    戻り値:
      なし
    """

    def __init__(self, master, basic_prompts, on_basic_select, on_text_change, *args, **kwargs):
        """
        コンストラクタ
        
        引数:
          master (tk.Widget): 親ウィジェット
          basic_prompts (list): 基本プロンプトのデータリスト
          on_basic_select (function): コンボボックス選択時のコールバック関数
          on_text_change (function): テキスト変更時のコールバック関数
          *args, **kwargs: その他
          
        戻り値:
          なし
        """
        super().__init__(master, text="基本プロンプト", *args, **kwargs)
        self.basic_prompts = basic_prompts
        self.on_select_callback = on_basic_select
        self.on_text_change_callback = on_text_change
        self.variable_entries = {}
        self.create_widgets()

    def create_widgets(self):
        """
        UIウィジェットを生成し、レイアウトを設定します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.create_basic_select_frame()
        self.create_template_frame()
        self.create_variable_frame()

    def create_basic_select_frame(self):
        """
        基本プロンプト選択部分のウィジェットを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        basic_select_frame = ttk.LabelFrame(self, text="基本プロンプトを選択")
        basic_select_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.basic_combobox = ttk.Combobox(basic_select_frame,
                                           values=[prompt["name"] for prompt in self.basic_prompts],
                                           width=48)
        self.basic_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.basic_combobox.bind("<<ComboboxSelected>>", self.on_basic_select)

    def create_template_frame(self):
        """
        基本プロンプトテンプレート表示部分のウィジェットを生成します。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        template_frame = ttk.LabelFrame(self, text="基本プロンプト テンプレート表示")
        template_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.basic_text = tk.Text(template_frame, height=10, width=50)
        self.basic_text.grid(row=0, column=0, padx=5, pady=5)
        self.basic_text.bind("<KeyRelease>", self.on_text_change)

    def create_variable_frame(self):
        """
        変数設定部分のウィジェットを生成します。
        """
        self.variable_frame = ttk.LabelFrame(self, text="変数設定")
        # 幅をさらに広げる（例: width=520）
        self.variable_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.variable_frame.config(width=520)  # 幅を大きめに設定
        self._variable_canvas = None
        self._variable_inner_frame = None
        self._variable_scrollbar = None

    def update_variable_entries(self, variables):
        """
        変数入力欄を更新します。
        Args:
            variables (dict): プロンプトに含まれる変数とその初期値の辞書
        Returns:
            なし
        """
        # 既存ウィジェットの削除
        for widget in self.variable_frame.winfo_children():
            widget.destroy()
        self.variable_entries.clear()

        # 常にスクロールバー＋Canvas＋Frame構成で表示
        canvas = tk.Canvas(self.variable_frame, height=180, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.variable_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.variable_frame.grid_rowconfigure(0, weight=1)
        self.variable_frame.grid_columnconfigure(0, weight=1)

        def _on_frame_configure(_):
            # scrollregionの更新
            canvas.configure(scrollregion=canvas.bbox("all"))
            # scrollable_frameの幅をcanvasに合わせる
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(window_id, width=canvas_width)

        scrollable_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_frame_configure)

        for col in range(3):
            scrollable_frame.columnconfigure(col,
                                             weight=1 if col != 1 else 0,
                                             minsize=20 if col == 1 else 0)
        for i, (var, default_value) in enumerate(variables.items()):
            row, col = divmod(i, 2)
            use_col = 0 if col == 0 else 2
            label = ttk.Label(scrollable_frame, text=var)
            label.grid(row=row * 2, column=use_col, padx=3, pady=(2, 0), sticky="w")
            entry = ttk.Entry(scrollable_frame)
            entry.grid(row=row * 2 + 1, column=use_col, padx=3, pady=(0, 4), sticky="ew")
            entry.insert(0, default_value)
            entry.bind("<KeyRelease>", self.on_text_change)
            self.variable_entries[var] = entry
        self._variable_canvas = canvas
        self._variable_inner_frame = scrollable_frame
        self._variable_scrollbar = scrollbar

    def on_basic_select(self, event):
        """
        基本プロンプト選択時の処理を行います。
        
        引数:
          event: イベントオブジェクト
          
        戻り値:
          なし
        """
        selection = self.basic_combobox.current()
        if selection >= 0:
            prompt_obj = self.basic_prompts[selection]
            self.basic_text.delete(1.0, tk.END)
            self.basic_text.insert(tk.END, prompt_obj["prompt"])
            self.update_variable_entries(prompt_obj["default_variables"])
            if self.on_select_callback:
                self.on_select_callback(event)

    def on_text_change(self, event):
        """
        テキスト変更時の処理を実行します。
        
        引数:
          event: イベントオブジェクト
          
        戻り値:
          なし
        """
        if self.on_text_change_callback:
            self.on_text_change_callback(event)

    def set_basic_prompt(self, index=0):
        """
        初期プロンプトを設定します。
        
        引数:
          index (int): 選択するプロンプトのインデックス
          
        戻り値:
          なし
        """
        if 0 <= index < len(self.basic_combobox['values']):
            self.basic_combobox.current(index)
            self.on_basic_select(None)

    def update_basic_prompts(self, prompts):
        """
        基本プロンプトの一覧を更新します。
        
        引数:
          prompts (list): 更新する基本プロンプトのリスト
          
        戻り値:
          なし
        """
        self.basic_prompts = prompts
        self.basic_combobox['values'] = [p["name"] for p in prompts]

    def get_current_prompt(self):
        """
        現在選択されている基本プロンプトのテキストと変数値を取得します。
        
        引数:
          なし
          
        戻り値:
          tuple: (基本プロンプトテキスト, 変数値の辞書)
        """
        basic_text = self.basic_text.get(1.0, tk.END).strip()
        variables = {var: entry.get() for var, entry in self.variable_entries.items()}
        return basic_text, variables
