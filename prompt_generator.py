import tkinter as tk
from tkinter import ttk, messagebox
import re
from template_manager import TemplateManager
import threading


class PromptGeneratorApp:
    """Gemini Prompt Generatorアプリケーションを表すクラスです。
    
    基本プロンプトと要素プロンプトを組み合わせ、最終プロンプトを生成します。
    """

    def __init__(self, master):
        """PromptGeneratorAppクラスのコンストラクタです。
        
        引数:
            master (tk.Tk): メインウィンドウのTkオブジェクト
        """
        self.master = master
        self.master.title("Gemini Prompt Generator")
        self.master.geometry("800x800")  # ウィンドウサイズの調整

        self.template_manager = TemplateManager("basic_prompts.json",
                                                "element_prompts.json")
        self.basic_prompts = self.template_manager.get_basic_prompts()
        self.element_prompts = self.template_manager.get_element_prompts()

        self.update_timer = None  # update_timerの初期化

        self.create_widgets()
        self.set_default_prompt()

    def create_widgets(self):
        """ウィジェットを作成し、レイアウトを設定します。"""
        # Basic Prompt Section
        basic_frame = ttk.LabelFrame(self.master, text="基本プロンプト")
        basic_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 基本プロンプト選択部分（LabelFrameで囲む）
        basic_select_frame = ttk.LabelFrame(basic_frame, text="基本プロンプトを選択")
        basic_select_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.basic_combobox = ttk.Combobox(
            basic_select_frame,
            values=[prompt["name"] for prompt in self.basic_prompts],
            width=48)  # 枠内に収めるためwidthを調整
        self.basic_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.basic_combobox.bind("<<ComboboxSelected>>", self.on_basic_select)

        # 基本プロンプト テンプレート表示部分（LabelFrameで囲む）
        template_frame = ttk.LabelFrame(basic_frame, text="基本プロンプト テンプレート表示")
        template_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.basic_text = tk.Text(template_frame, height=10, width=50)  # サイズ調整
        self.basic_text.grid(row=0, column=0, padx=5, pady=5)
        self.basic_text.bind("<KeyRelease>", self.on_text_change)

        self.variable_frame = ttk.LabelFrame(basic_frame, text="変数設定")
        self.variable_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.variable_entries = {}

        # Element Prompt Section
        element_frame = ttk.LabelFrame(self.master, text="追加プロンプト")
        element_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 追加プロンプト選択部分（LabelFrameで囲む）
        select_element_frame = ttk.LabelFrame(element_frame, text="追加プロンプトを選択（複数可）")
        select_element_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")

        # Subject入力欄はselect_element_frame内に配置
        subject_frame = ttk.Frame(select_element_frame)
        subject_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        subject_label = ttk.Label(subject_frame, text="主語:")
        subject_label.pack(side=tk.LEFT, padx=(0, 30))
        self.element_subject_entry = ttk.Entry(subject_frame, width=30)
        self.element_subject_entry.pack(side=tk.LEFT)
        self.element_subject_entry.insert(0, "被写体")  # 初期値を設定

        # 追加プロンプト選択用Treeviewをselect_element_frame内に配置
        self.element_tree = ttk.Treeview(select_element_frame, selectmode="extended")
        self.element_tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.element_tree.bind("<<TreeviewSelect>>", self.on_element_select)
        for category in self.element_prompts:
            parent = self.element_tree.insert("", tk.END, text=category["category"])
            for prompt in category["prompts"]:
                self.element_tree.insert(parent, tk.END, text=prompt["name"])

        # 追加プロンプト表示部分（LabelFrameで囲む）
        display_frame = ttk.LabelFrame(element_frame, text="追加プロンプトを表示")
        display_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.element_text = tk.Text(display_frame, height=7, width=50)  # サイズ調整
        self.element_text.grid(row=0, column=0, padx=5, pady=5)
        self.element_text.bind("<KeyRelease>", self.on_text_change)

        # Final Prompt Section
        final_frame = ttk.LabelFrame(self.master, text="完成プロンプト（基本＋追加）")
        final_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.final_text = tk.Text(final_frame, height=15, width=100, state="disabled")
        self.final_text.grid(row=0, column=0, padx=5, pady=5)
        copy_button = ttk.Button(final_frame, text="クリップボードにコピー", command=self.copy_to_clipboard)
        copy_button.grid(row=1, column=0, padx=5, pady=5)

    def set_default_prompt(self):
        """初期の基本プロンプトを設定します。"""
        self.basic_combobox.current(0)
        self.on_basic_select(None)

    def on_basic_select(self, _):
        """基本プロンプト選択時の処理を行います。
        
        選択された基本プロンプトのテキストや変数入力欄を更新します。
        """
        selection = self.basic_combobox.current()
        if selection >= 0:
            prompt = self.basic_prompts[selection]
            self.basic_text.delete(1.0, tk.END)
            self.basic_text.insert(tk.END, prompt["text"])
            self.update_variable_entries(prompt["variables"])
            self.schedule_update()

    def update_variable_entries(self, variables):
        """変数入力欄を更新します。
        
        引数:
            variables (dict): プロンプト内の変数とその初期値の辞書
        """
        for widget in self.variable_frame.winfo_children():
            widget.destroy()
        self.variable_entries.clear()
        
        # 列設定を変更：3列を用意し、中央列をスペーサーとする
        self.variable_frame.columnconfigure(0, weight=1)
        self.variable_frame.columnconfigure(1, minsize=20)  # スペーサー列（20ピクセル固定幅）
        self.variable_frame.columnconfigure(2, weight=1)
        
        for i, (var, default_value) in enumerate(variables.items()):
            row, col = divmod(i, 2)
            # 使用する実際の列は、colが0なら左側（0）、1なら右側（2）になります
            use_col = 0 if col == 0 else 2
            label = ttk.Label(self.variable_frame, text=var)
            label.grid(row=row * 2, column=use_col, padx=5, pady=0, sticky="w")
            entry = ttk.Entry(self.variable_frame)
            entry.grid(row=row * 2 + 1,
                       column=use_col,
                       padx=5,
                       pady=5,
                       sticky="ew")
            entry.insert(0, default_value)
            entry.bind("<KeyRelease>", self.on_text_change)
            self.variable_entries[var] = entry

    def on_element_select(self, event):
        """Element PromptのTreeviewで項目が選択された際の処理を行います。
        
        選択されたプロンプトのテキストを取得し、改行区切りで表示します。
        また、Subject入力欄の値で{subject}を置換します。
        """
        selection = event.widget.selection()
        selected_texts = []
        for item in selection:
            item_text = self.element_tree.item(item, "text")
            parent = self.element_tree.parent(item)
            if parent:
                for category in self.element_prompts:
                    if category["category"] == self.element_tree.item(
                            parent)["text"]:
                        for prompt in category["prompts"]:
                            if prompt["name"] == item_text:
                                selected_texts.append(prompt["text"])
                                break
        element_prompt_raw = "\n".join(selected_texts)
        subject_val = self.element_subject_entry.get().strip()
        element_prompt_final = self.template_manager.replace_variables(
            element_prompt_raw, {"subject": subject_val})
        self.element_text.delete(1.0, tk.END)
        self.element_text.insert(tk.END, element_prompt_final)
        self.schedule_update()

    def on_text_change(self, _):
        """テキストが変更された際に最終プロンプトを再生成します。"""
        self.schedule_update()

    def schedule_update(self):
        """一定の遅延後に最終プロンプトを生成するようタイマーを設定します。"""
        if self.update_timer:
            self.master.after_cancel(self.update_timer)
        self.update_timer = self.master.after(
            1000, self.generate_final_prompt)  # 1秒のディレイ

    def generate_final_prompt(self):
        """基本プロンプトとElement Promptを結合し、最終プロンプトを生成します。"""
        basic_text = self.basic_text.get(1.0, tk.END).strip()
        variables = {
            var: entry.get()
            for var, entry in self.variable_entries.items()
        }
        final_prompt = self.template_manager.replace_variables(
            basic_text, variables)
        element_text = self.element_text.get(1.0, tk.END).strip()
        final_prompt += "\n" + element_text
        self.final_text.config(state=tk.NORMAL)
        self.final_text.delete(1.0, tk.END)
        self.final_text.insert(tk.END, final_prompt)
        self.final_text.config(state=tk.DISABLED)

    def copy_to_clipboard(self):
        """最終プロンプトをクリップボードにコピーし、メッセージを表示します。"""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.final_text.get(1.0, tk.END))
        messagebox.showinfo("Copied", "Final prompt copied to clipboard.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
