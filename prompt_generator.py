class PromptGenerator:
    def __init__(self, template_manager):
        self.template_manager = template_manager

    def generate_basic_prompt(self, var_values):
        basic_template = self.template_manager.get_basic_template()
        prompt = self.template_manager.replace_variables(basic_template, var_values)
        return prompt

    def generate_final_prompt(self, basic_prompt, additional_elements):
        """
        additional_elements: dict with keys as category names and values as the text.
        決められた順序で追加要素を連結します。
        """
        parts = [basic_prompt]
        for key in ["衣装特徴", "人物特徴", "外的要因"]:
            if key in additional_elements and additional_elements[key]:
                parts.append(additional_elements[key])
        return " ".join(parts)