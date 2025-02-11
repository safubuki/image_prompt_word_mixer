from template_manager import TemplateManager
from prompt_generator import PromptGenerator

def main():
    # JSONファイルのパス設定
    basic_template_path = "basic_template.json"
    categories_path = "categories.json"

    # TemplateManager の初期化
    tm = TemplateManager(basic_template_path, categories_path)
    pg = PromptGenerator(tm)
    
    # 変数の初期値取得とユーザー入力（CLIでの入力例）
    variables = tm.get_variables()
    print("基本プロンプトの変数を入力してください。（Enterを押すと既定値が使用されます）")
    var_values = {}
    for var, info in variables.items():
        default_value = info.get("default", "")
        prompt_text = f"{info.get('description')} [{default_value}]: "
        user_value = input(prompt_text)
        var_values[var] = user_value.strip() if user_value.strip() else default_value

    basic_prompt = pg.generate_basic_prompt(var_values)
    print("\n【基本プロンプト】")
    print(basic_prompt)
    
    # カテゴリ別追加要素の入力
    categories = tm.get_categories()
    additional_elements = {}
    print("\nカテゴリ別の追加要素を入力してください。（Enterで既定値を使用またはスキップ）")
    for cat, info in categories.items():
        default_value = info.get("default", "")
        prompt_text = f"{cat} - {info.get('description')} [{default_value}]: "
        user_value = input(prompt_text)
        additional_elements[cat] = user_value.strip() if user_value.strip() else default_value

    # 最終プロンプト生成
    final_prompt = pg.generate_final_prompt(basic_prompt, additional_elements)
    print("\n【最終プロンプト】")
    print(final_prompt)
    
    # プロンプトをファイルに保存
    with open("final_prompt.txt", "w", encoding="utf-8") as f:
        f.write(final_prompt)
    print("\n最終プロンプトを final_prompt.txt に保存しました。")

if __name__ == "__main__":
    main()