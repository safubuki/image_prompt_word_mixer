import json

class TemplateManager:
    def __init__(self, basic_prompt_file, element_prompt_file):
        self.basic_prompt_file = basic_prompt_file
        self.element_prompt_file = element_prompt_file
        self.basic_prompts = self.load_prompts(basic_prompt_file)
        self.element_prompts = self.load_prompts(element_prompt_file)

    def load_prompts(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_prompts(self, filename, prompts):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(prompts, file, ensure_ascii=False, indent=4)

    def get_basic_prompts(self):
        return self.basic_prompts

    def get_element_prompts(self):
        return self.element_prompts

    def update_basic_prompt(self, index, new_prompt):
        if 0 <= index < len(self.basic_prompts):
            self.basic_prompts[index] = new_prompt
            self.save_prompts(self.basic_prompt_file, self.basic_prompts)

    def update_element_prompt(self, category, index, new_prompt):
        for cat in self.element_prompts:
            if cat["category"] == category:
                if 0 <= index < len(cat["prompts"]):
                    cat["prompts"][index] = new_prompt
                    self.save_prompts(self.element_prompt_file, self.element_prompts)
                    break

    def replace_variables(self, text, variables):
        for var, value in variables.items():
            text = text.replace(f"{{{var}}}", value)
        return text

if __name__ == "__main__":
    manager = TemplateManager("basic_prompts.json", "element_prompts.json")
    print(manager.get_basic_prompts())
    print(manager.get_element_prompts())
