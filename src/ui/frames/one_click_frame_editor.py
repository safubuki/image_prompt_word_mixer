import tkinter as tk
from tkinter import messagebox, ttk


class OneClickFrameEditor:

    def __init__(self, owner):
        """
        owner には OneClickFrame のインスタンスが渡されます。
        """
        self.owner = owner

    def create_editor_area(self):
        owner = self.owner
        edit_frame = ttk.Frame(owner)
        edit_frame.pack(padx=10, pady=10, fill="x", expand=False)
        title_label = ttk.Label(edit_frame, text="ボタンタイトル:")
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        owner.title_edit = tk.Text(edit_frame, height=1)
        owner.title_edit.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        owner.title_edit.bind("<Tab>", self.move_focus_to_edit)
        owner.title_edit.bind("<FocusIn>", owner.on_text_focus_in)
        owner.title_edit.bind("<FocusOut>", owner.on_text_focus_out)

        text_label = ttk.Label(edit_frame, text="定型文:")
        text_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        owner.edit_text = tk.Text(edit_frame, height=5)
        owner.edit_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        owner.edit_text.bind("<FocusIn>", owner.on_text_focus_in)
        owner.edit_text.bind("<FocusOut>", owner.on_text_focus_out)

        button_panel = ttk.Frame(edit_frame)
        button_panel.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="ns")
        save_btn = ttk.Button(button_panel, text="更新・保存", command=self.save_current_entry)
        save_btn.pack(side="top", fill="x")
        clear_btn = ttk.Button(button_panel, text="クリア", command=self.clear_current_entry)
        clear_btn.pack(side="top", fill="x", pady=(5, 0))
        disable_copy_cb = ttk.Checkbutton(button_panel, text="コピー無効", variable=owner.disable_copy)
        disable_copy_cb.pack(side="top", fill="x", pady=(5, 0))

        edit_frame.columnconfigure(1, weight=1)
        hint_label = ttk.Label(edit_frame,
                               text="※矢印キーでボタン位置を移動できます",
                               font=("Arial", 8),
                               foreground="gray")
        hint_label.grid(row=2, column=1, sticky="e", padx=5, pady=(2, 0))

    def move_focus_to_edit(self, _):
        self.owner.edit_text.focus_set()
        return "break"

    def on_button_click(self, category, index):
        owner = self.owner
        entry = owner.manager.get_entry(category, index)
        text_to_copy = entry["text"]
        title_to_copy = entry["title"]

        if not owner.disable_copy.get():
            owner.clipboard_clear()
            owner.clipboard_append(text_to_copy)

        owner.title_edit.delete("1.0", tk.END)
        owner.title_edit.insert(tk.END, title_to_copy)
        owner.edit_text.delete("1.0", tk.END)
        owner.edit_text.insert(tk.END, text_to_copy)

    def save_current_entry(self):
        owner = self.owner
        if owner.manager.current_category is not None and owner.manager.current_index is not None:
            new_title = owner.title_edit.get("1.0", tk.END).strip()
            new_text = owner.edit_text.get("1.0", tk.END).strip()

            category = owner.manager.current_category
            index = owner.manager.current_index

            owner.manager.update_entry(category, index, new_title, new_text)

            if category in owner.button_widgets and index < len(owner.button_widgets[category]):
                owner.button_widgets[category][index].config(text=new_title)

    def clear_current_entry(self):
        owner = self.owner
        if owner.manager.current_category is not None and owner.manager.current_index is not None:
            if messagebox.askokcancel("確認", "登録内容をクリアします"):
                category = owner.manager.current_category
                index = owner.manager.current_index

                new_title = "（空き）"
                new_text = ""

                owner.manager.update_entry(category, index, new_title, new_text)

                owner.title_edit.delete("1.0", tk.END)
                owner.title_edit.insert(tk.END, new_title)
                owner.edit_text.delete("1.0", tk.END)

                if category in owner.button_widgets and index < len(owner.button_widgets[category]):
                    owner.button_widgets[category][index].config(text=new_title)
