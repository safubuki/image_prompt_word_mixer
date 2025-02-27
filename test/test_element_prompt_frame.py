import os
import sys
import time
import tkinter as tk
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.element_prompt_frame import ElementPromptFrame


@pytest.fixture
def element_prompts():
    return [{
        "category": "Category 1",
        "prompt_lists": [{
            "title": "Prompt 1"
        }, {
            "title": "Prompt 2"
        }]
    }, {
        "category": "Category 2",
        "prompt_lists": [{
            "title": "Prompt 3"
        }, {
            "title": "Prompt 4"
        }]
    }]


@pytest.fixture
def on_element_select():
    return MagicMock()


@pytest.fixture
def on_text_change():
    return MagicMock()


@pytest.fixture
def root():
    time.sleep(1)  # Add a small delay before creating the root window
    root = tk.Tk()
    root.update_idletasks()
    return root


@pytest.fixture
def element_prompt_frame(root, element_prompts, on_element_select, on_text_change):
    return ElementPromptFrame(root, element_prompts, on_element_select, on_text_change)


def test_initialization(element_prompt_frame):
    """
    初期化テスト
    ElementPromptFrameが正しく初期化されることを確認します。
    """
    assert element_prompt_frame is not None
    assert element_prompt_frame.element_prompts is not None
    assert element_prompt_frame.on_element_select is not None
    assert element_prompt_frame.on_text_change is not None


def test_create_widgets(element_prompt_frame):
    """
    ウィジェット生成テスト
    create_widgetsメソッドが正しくウィジェットを生成することを確認します。
    """
    element_prompt_frame.create_widgets()
    assert hasattr(element_prompt_frame, 'subject_entry')
    assert hasattr(element_prompt_frame, 'tree')
    assert hasattr(element_prompt_frame, 'element_text')


def test_treeview_selection_updates_text(element_prompt_frame):
    """
    ツリービュー選択テスト
    ツリービューでプロンプトを選択した際に、テキストエリアが正しく更新されることを確認します。
    """
    element_prompt_frame.create_widgets()
    element_prompt_frame.tree.selection_set(element_prompt_frame.tree.get_children()[0])
    element_prompt_frame.tree.event_generate("<<TreeviewSelect>>")
    time.sleep(0.5)  # Add a small delay to ensure the event loop processes the event
    element_prompt_frame.on_element_select.assert_called_once()


def test_subject_entry(element_prompt_frame):
    """
    主語エントリテスト
    主語エントリフィールドに入力したテキストが正しく反映されることを確認します。
    """
    element_prompt_frame.create_widgets()
    element_prompt_frame.subject_entry.delete(0, tk.END)
    element_prompt_frame.subject_entry.insert(0, "新しい主語")
    assert element_prompt_frame.subject_entry.get() == "新しい主語"


def test_empty_element_prompts(root, on_element_select, on_text_change):
    """
    空のプロンプトリストテスト
    element_promptsリストが空の場合に正しく動作することを確認します。
    """
    element_prompt_frame = ElementPromptFrame(root, [], on_element_select, on_text_change)
    assert element_prompt_frame is not None


def test_missing_keys_in_element_prompts(root, on_element_select, on_text_change):
    """
    キー不足テスト
    element_promptsに必要なキーが不足している場合に正しく動作することを確認します。
    """
    incomplete_prompts = [{"category": "Category 1"}, {"prompt_lists": [{"title": "Prompt 1"}]}]
    element_prompt_frame = ElementPromptFrame(root, incomplete_prompts, on_element_select,
                                              on_text_change)
    assert element_prompt_frame is not None


def test_duplicate_prompt_titles(root, on_element_select, on_text_change):
    """
    重複タイトルテスト
    プロンプトのタイトルが重複している場合に正しく動作することを確認します。
    """
    duplicate_prompts = [{
        "category": "Category 1",
        "prompt_lists": [{
            "title": "Prompt 1"
        }, {
            "title": "Prompt 1"
        }]
    }]
    element_prompt_frame = ElementPromptFrame(root, duplicate_prompts, on_element_select,
                                              on_text_change)
    assert element_prompt_frame is not None


def test_clear_selection(element_prompt_frame):
    """
    選択解除ボタンの機能テスト:
    Treeview の選択が解除され、追加プロンプト表示欄がクリアされることを確認します。
    """
    # 必要なウィジェットを生成
    element_prompt_frame.create_widgets()

    # Treeview の先頭の項目を選択状態にする
    children = element_prompt_frame.tree.get_children()
    if children:
        element_prompt_frame.tree.selection_set(children[0])

    # Textウィジェットにサンプルテキストを設定
    element_prompt_frame.element_text.insert("1.0", "Sample prompt text")

    # clear_selection を呼び出す
    element_prompt_frame.clear_selection()

    # Treeview の選択が解除されていることを確認
    assert not element_prompt_frame.tree.selection(), "Treeview の選択が解除されていません。"

    # 追加プロンプト表示欄がクリアされていることを確認
    text_content = element_prompt_frame.element_text.get("1.0", tk.END).strip()
    assert text_content == "", "追加プロンプト表示欄がクリアされていません。"
