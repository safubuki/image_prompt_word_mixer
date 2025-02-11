import json

class TemplateManager:
    def __init__(self, basic_template_path, categories_path):
        self.basic_template = self.load_json(basic_template_path)
        self.categories = self.load_json(categories_path)

    def load_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_basic_template(self):
        return self.basic_template["template"]

    def get_variables(self):
        return self.basic_template.get("variables", {})

    def get_categories(self):
        return self.categories.get("categories", {})

    def replace_variables(self, template_str, var_values):
        result = template_str
        for key, value in var_values.items():
            result = result.replace("{" + key + "}", value)
        return result