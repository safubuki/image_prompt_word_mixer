"""
template_manager.py
プロンプトデータの読み込み、保存、更新および変数の置換機能を提供するコンポーネントです。
"""
import json


class TemplateManager:
    """
    TemplateManager クラスは、プロンプトデータの読み込み、保存、更新および変数置換を提供するコンポーネントです。
    """

    def __init__(self, basic_prompt_file, element_prompt_file):
        """
        コンストラクタ
        
        引数:
            basic_prompt_file (str): 基本プロンプトJSONファイルのパス
            element_prompt_file (str): 要素プロンプトJSONファイルのパス
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
            list: 読み込んだプロンプトデータのリスト。ファイルが存在しない場合は空のリストを返します。
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_prompts(self, filename, prompts):
        """
        プロンプトデータを指定されたJSONファイルに保存します。
        
        引数:
            filename (str): 保存先のJSONファイルのパス
            prompts (list): 保存するプロンプトのリスト
        """
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(prompts, file, ensure_ascii=False, indent=4)

    def get_basic_prompts(self):
        """
        基本プロンプトのリストを返します。
        
        戻り値:
            list: 基本プロンプトのリスト
        """
        return self.basic_prompts

    def get_element_prompts(self):
        """
        要素プロンプトのリストを返します。
        
        戻り値:
            list: 要素プロンプトのリスト
        """
        return self.element_prompts

    def update_basic_prompt(self, index, new_prompt):
        """
        指定されたインデックスの基本プロンプトを更新し、JSONファイルに保存します。
        
        引数:
            index (int): 更新するプロンプトのインデックス
            new_prompt (dict): 新しいプロンプトデータ
        """
        if 0 <= index < len(self.basic_prompts):
            self.basic_prompts[index] = new_prompt
            self.save_prompts(self.basic_prompt_file, self.basic_prompts)

    def update_element_prompt(self, category, index, new_prompt):
        """
        指定されたカテゴリとインデックスの要素プロンプトを更新し、JSONファイルに保存します。
        
        引数:
            category (str): 要素プロンプトのカテゴリ名
            index (int): 更新するプロンプトのインデックス
            new_prompt (dict): 新しいプロンプトデータ
        """
        for cat in self.element_prompts:
            if cat["category"] == category:
                if 0 <= index < len(cat["prompts"]):
                    cat["prompts"][index] = new_prompt
                    self.save_prompts(self.element_prompt_file, self.element_prompts)
                    break

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


if __name__ == "__main__":
    manager = TemplateManager("basic_prompts.json", "element_prompts.json")
    print(manager.get_basic_prompts())
    print(manager.get_element_prompts())
