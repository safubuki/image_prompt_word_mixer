"""
app.py
Gemini Prompt Generatorアプリケーションの起動およびUI統合機能を提供するコンポーネントです。
"""
import os  # osモジュールを追加
import tkinter as tk

from template_manager import TemplateManager
from ui.basic_prompt_frame import BasicPromptFrame
from ui.element_prompt_frame import ElementPromptFrame
from ui.final_prompt_frame import FinalPromptFrame


class PromptGeneratorApp:
    """
    PromptGeneratorApp クラスは、各コンポーネントを統合しプロンプト生成のロジックを提供するコンポーネントです。
    """

    def __init__(self, master):
        """
        コンストラクタ
        
        引数:
            master (tk.Widget): ルートウィジェット
        """
        self.master = master
        self.master.title("Image Prompt Word-Mixer ")

        # アイコン設定
        icon_path = os.path.join("image", "turtle.ico")  # imageフォルダのアイコン
        try:
            self.master.iconbitmap(icon_path)
        except tk.TclError:
            print(f"アイコンファイルが見つかりませんでした: {icon_path}")

        self.master.resizable(True, True)

        self.template_manager = TemplateManager("basic_prompts.json", "element_prompts.json")
        self.basic_prompts = self.template_manager.get_basic_prompts()
        self.element_prompts = self.template_manager.get_element_prompts()

        self.update_timer = None  # タイマー初期化

        # 各UIコンポーネント（セクション）をインスタンス化
        self.basic_frame = BasicPromptFrame(master, self.basic_prompts, self.on_basic_select,
                                            self.on_text_change)
        self.basic_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.element_frame = ElementPromptFrame(master, self.element_prompts,
                                                self.on_element_select, self.on_text_change)
        self.element_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.final_frame = FinalPromptFrame(master)
        self.final_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # 変数設定はBasicPromptFrame内のvariable_frameを利用
        self.variable_entries = self.basic_frame.variable_entries

        self.set_default_prompt()

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
        追加プロンプト選択時の処理を行い、重複しない内容を表示します。
        """
        selection = event.widget.selection()
        selected_texts = []
        seen_keys = set()
        # ルートレベル（カテゴリ）のIDリスト（JSON順と仮定）
        parent_ids = list(self.element_frame.tree.get_children(""))

        for item in selection:
            parent = self.element_frame.tree.parent(item)
            if parent:
                try:
                    category_index = parent_ids.index(parent)
                except ValueError:
                    continue
                category_data = self.element_prompts[category_index]
                item_text = self.element_frame.tree.item(item, "text")
                # キー "prompts" -> "prompt_lists"、"name" -> "title"、"text" -> "prompt"
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
        self.update_timer = self.master.after(1000, self.generate_final_prompt)  # 1秒後に生成

    def generate_final_prompt(self):
        """
        基本プロンプトと追加プロンプトを結合して完成プロンプトを生成します。
        """
        basic_text = self.basic_frame.basic_text.get(1.0, tk.END).strip()
        variables = {var: entry.get() for var, entry in self.basic_frame.variable_entries.items()}
        final_prompt = self.template_manager.replace_variables(basic_text, variables)
        # ElementPromptFrame からは element_text が得られないので、保持している element_prompt_content を利用
        element_text = getattr(self, 'element_prompt_content', '')
        final_prompt += "\n" + element_text

        self.final_frame.final_text.config(state=tk.NORMAL)
        self.final_frame.final_text.delete(1.0, tk.END)
        self.final_frame.final_text.insert(tk.END, final_prompt)
        self.final_frame.final_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
