import tkinter as tk
from tkinter import ttk, messagebox
import re
from template_manager import TemplateManager

class PromptGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gemini Prompt Generator")
        self.master.geometry("800x600")  # Set fixed window size

        self.template_manager = TemplateManager("basic_prompts.json", "element_prompts.json")
        self.basic_prompts = self.template_manager.get_basic_prompts()
        self.element_prompts = self.template_manager.get_element_prompts()

        self.create_widgets()
        self.set_default_prompt()

    def create_widgets(self):
        # Basic Prompt Section
        basic_frame = ttk.LabelFrame(self.master, text="Basic Prompts")
        basic_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.basic_combobox = ttk.Combobox(basic_frame, values=[prompt["name"] for prompt in self.basic_prompts], width=40)
        self.basic_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.basic_combobox.bind("<<ComboboxSelected>>", self.on_basic_select)

        self.basic_text = tk.Text(basic_frame, height=10, width=33)  # Set width to 2/3 of the original
        self.basic_text.grid(row=1, column=0, padx=5, pady=5)

        self.variable_frame = ttk.LabelFrame(basic_frame, text="Variables")
        self.variable_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.variable_entries = {}

        # Element Prompt Section
        element_frame = ttk.LabelFrame(self.master, text="Element Prompts")
        element_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.element_tree = ttk.Treeview(element_frame)
        self.element_tree.grid(row=0, column=0, padx=5, pady=5)
        self.element_tree.bind("<<TreeviewSelect>>", self.on_element_select)

        for category in self.element_prompts:
            parent = self.element_tree.insert("", tk.END, text=category["category"])
            for prompt in category["prompts"]:
                self.element_tree.insert(parent, tk.END, text=prompt["name"])

        self.element_text = tk.Text(element_frame, height=10, width=50)
        self.element_text.grid(row=1, column=0, padx=5, pady=5)

        # Final Prompt Section
        final_frame = ttk.LabelFrame(self.master, text="Final Prompt")
        final_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.final_text = tk.Text(final_frame, height=10, width=100, state="disabled")
        self.final_text.grid(row=0, column=0, padx=5, pady=5)

        copy_button = ttk.Button(final_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.grid(row=1, column=0, padx=5, pady=5)

        generate_button = ttk.Button(final_frame, text="Generate Final Prompt", command=self.generate_final_prompt)
        generate_button.grid(row=1, column=1, padx=5, pady=5)

    def set_default_prompt(self):
        self.basic_combobox.current(0)
        self.on_basic_select(None)

    def on_basic_select(self, _):
        selection = self.basic_combobox.current()
        if selection >= 0:
            prompt = self.basic_prompts[selection]
            self.basic_text.delete(1.0, tk.END)
            self.basic_text.insert(tk.END, prompt["text"])
            self.update_variable_entries(prompt["variables"])

    def update_variable_entries(self, variables):
        for widget in self.variable_frame.winfo_children():
            widget.destroy()
        self.variable_entries.clear()

        for i, (var, default_value) in enumerate(variables.items()):
            row, col = divmod(i, 2)
            label = ttk.Label(self.variable_frame, text=var)
            label.grid(row=row*2, column=col, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(self.variable_frame)
            entry.grid(row=row*2+1, column=col, padx=5, pady=5, sticky="ew")
            entry.insert(0, default_value)
            self.variable_entries[var] = entry

    def on_element_select(self, event):
        selection = event.widget.selection()
        if selection:
            item = self.element_tree.item(selection[0])
            self.element_text.delete(1.0, tk.END)
            self.element_text.insert(tk.END, item["text"])

    def generate_final_prompt(self):
        basic_text = self.basic_text.get(1.0, tk.END).strip()
        variables = {var: entry.get() for var, entry in self.variable_entries.items()}
        final_prompt = self.template_manager.replace_variables(basic_text, variables)
        self.final_text.config(state=tk.NORMAL)
        self.final_text.delete(1.0, tk.END)
        self.final_text.insert(tk.END, final_prompt)
        self.final_text.config(state=tk.DISABLED)

    def copy_to_clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.final_text.get(1.0, tk.END))
        messagebox.showinfo("Copied", "Final prompt copied to clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()
