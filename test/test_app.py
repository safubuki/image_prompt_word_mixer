import os
import sys
import time
import tkinter as tk
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import PromptGeneratorApp


@pytest.fixture
def root():
    """
    Tkinter のルートウィジェットを返すフィクスチャです。
    GUI コンポーネントのテスト時に使用されます。
    """
    time.sleep(0.5)  # 少し待機して安定化
    root = tk.Tk()
    time.sleep(0.5)
    root.update_idletasks()
    return root


@pytest.fixture
def app(root):
    """
    PromptGeneratorApp のインスタンスを生成して返すフィクスチャです。
    """
    return PromptGeneratorApp(root)


def test_initial_prompt(app):
    """
    初期プロンプトの設定をテストします。
    """
    assert app.basic_frame.basic_combobox.current() == 0
    assert app.basic_frame.basic_text.get(1.0, tk.END).strip() == app.basic_prompts[0]["prompt"]


def test_basic_prompt_selection(app):
    """
    基本プロンプトの選択をテストします。
    """
    app.basic_frame.basic_combobox.current(1)
    app.on_basic_select(None)
    app.master.update()  # イベント処理を完了させる
    time.sleep(0.5)
    assert app.basic_frame.basic_text.get(1.0, tk.END).strip() == app.basic_prompts[1]["prompt"]


def test_element_prompt_selection(app):
    """
    追加プロンプトの選択をテストします。
    カテゴリの子要素（実際の追加プロンプト項目）を選択し、
    element_text にプロンプトが反映されることを確認します。
    """
    # カテゴリノードの取得
    categories = app.element_frame.tree.get_children()
    assert categories, "カテゴリが存在しません。"
    # 最初のカテゴリ内の子要素（追加プロンプト項目）を取得
    children = app.element_frame.tree.get_children(categories[0])
    assert children, "カテゴリ内に追加プロンプトが存在しません。"
    target_item = children[0]

    # 追加プロンプト項目を選択
    app.element_frame.tree.selection_set(target_item)
    app.element_frame.tree.event_generate("<<TreeviewSelect>>")
    app.master.update()  # イベントキューを処理
    time.sleep(0.5)  # 少し待機

    # 選択後に element_text に反映されたテキストを取得
    element_text = app.element_frame.element_text.get(1.0, tk.END).strip()
    print(f"Element text: '{element_text}'")  # Debug print
    selected_item_text = app.element_frame.tree.item(target_item, "text")
    print(f"Selected item: {selected_item_text}")  # Debug print
    print(f"Element prompts: {app.element_prompts}")  # Debug print

    # element_text が空でないことを確認
    assert element_text != "", "選択された追加プロンプトのテキストが反映されていません。"


def test_final_prompt_generation(app):
    """
    最終プロンプトの生成をテストします。
    """
    # 基本プロンプトを設定
    app.basic_frame.basic_combobox.current(0)
    app.on_basic_select(None)
    app.master.update()
    time.sleep(0.5)

    # 追加プロンプトの選択（最初のカテゴリの子要素を選択）
    categories = app.element_frame.tree.get_children()
    assert categories, "カテゴリが存在しません。"
    children = app.element_frame.tree.get_children(categories[0])
    assert children, "カテゴリ内に追加プロンプトが存在しません。"
    app.element_frame.tree.selection_set(children[0])
    app.element_frame.tree.event_generate("<<TreeviewSelect>>")
    app.master.update()
    time.sleep(0.5)

    # 完成プロンプトの生成
    app.generate_final_prompt()
    app.master.update()
    time.sleep(0.5)
    final_text = app.final_frame.final_text.get(1.0, tk.END).strip()
    assert final_text != "", "完成プロンプトが生成されていません。"
