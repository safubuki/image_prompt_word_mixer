import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.template_manager import TemplateManager


def test_load_prompts():
    """
    load_promptsメソッドのテスト。
    JSONファイルからプロンプトを正しく読み込むことを確認します。
    """
    manager = TemplateManager("basic_prompts.json", "element_prompts.json")
    assert isinstance(manager.get_basic_prompts(), list)
    assert isinstance(manager.get_element_prompts(), list)


def test_replace_variables():
    """
    replace_variablesメソッドのテスト。
    テキスト中のプレースホルダが正しく置換されることを確認します。
    """
    manager = TemplateManager("basic_prompts.json", "element_prompts.json")
    text = "Hello, {name}!"
    variables = {"name": "World"}
    result = manager.replace_variables(text, variables)
    assert result == "Hello, World!"


def test_file_not_found(monkeypatch):
    """
    ファイルが見つからない場合のload_promptsメソッドのテスト。
    エラーメッセージが表示され、システムが終了することを確認します。
    """

    def mock_showerror(title, message):
        pass

    monkeypatch.setattr("tkinter.messagebox.showerror", mock_showerror)
    with pytest.raises(SystemExit):
        manager = TemplateManager("non_existent_file.json", "element_prompts.json")
