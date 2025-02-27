"""
template_manager.py
プロンプトデータの読み込み、保存、更新および変数の置換機能を提供するコンポーネントです。
"""
import json
import sys
import tkinter as tk
from tkinter import messagebox

# 定数（出力メッセージなど）の定義
FILE_NOT_FOUND_MSG = "jsonファイルをexeファイルと同じフォルダに用意してください。"


class TemplateManager:
    """
    TemplateManager クラスは、プロンプトデータの読み込み、保存、更新および変数置換を提供するコンポーネントです。
    
    引数:
      basic_prompt_file (str): 基本プロンプトJSONファイルのパス
      element_prompt_file (str): 要素プロンプトJSONファイルのパス
      
    戻り値:
      なし
    """

    def __init__(self, basic_prompt_file, element_prompt_file):
        """
        コンストラクタ
        
        引数:
          basic_prompt_file (str): 基本プロンプトJSONファイルのパス
          element_prompt_file (str): 要素プロンプトJSONファイルのパス
          
        戻り値:
          なし
        """
        self.basic_prompt_file = basic_prompt_file
        self.element_prompt_file = element_prompt_file
        self.basic_prompts = self.load_prompts(basic_prompt_file)
        self.element_prompts = self.load_prompts(element_prompt_file)

    def load_prompts(self, filename):
        """
        指定されたJSONファイルからプロンプトを読み込みます。
        
        引数:
          filename (str): JSONファイルのパス
          
        戻り値:
          list: 読み込んだプロンプトデータのリスト
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            self._handle_file_not_found()

    def _handle_file_not_found(self):
        """
        ファイルが見つからなかった場合のエラー処理を行います。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを表示しない
        messagebox.showerror("Error", FILE_NOT_FOUND_MSG)
        sys.exit()

    def get_basic_prompts(self):
        """
        基本プロンプトのリストを返します。
        
        引数:
          なし
          
        戻り値:
          list: 基本プロンプトのリスト
        """
        return self.basic_prompts

    def get_element_prompts(self):
        """
        要素プロンプトのリストを返します。
        
        引数:
          なし
          
        戻り値:
          list: 要素プロンプトのリスト
        """
        return self.element_prompts

    def replace_variables(self, text, variables):
        """
        テキスト中のプレースホルダ（例: {subject}）を、変数辞書の値に置換します。
        
        引数:
          text (str): 置換対象のテキスト
          variables (dict): 変数名と置換値の辞書
          
        戻り値:
          str: 変数が置換されたテキスト
        """
        for var, value in variables.items():
            text = text.replace(f"{{{var}}}", value)
        return text

    def reload_templates(self):
        """
        基本プロンプトと要素プロンプトの両方を再読み込みします。
        
        引数:
          なし
          
        戻り値:
          なし
        """
        self.basic_prompts = self.load_prompts(self.basic_prompt_file)
        self.element_prompts = self.load_prompts(self.element_prompt_file)


if __name__ == "__main__":
    manager = TemplateManager("basic_prompts.json", "element_prompts.json")
    print(manager.get_basic_prompts())
    print(manager.get_element_prompts())
