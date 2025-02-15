"""
test_basic_prompt_frame.py
----------------------------
このモジュールは、ui/basic_prompt_frame.py 内の BasicPromptFrame クラスの機能をテストするためのテストケースを定義しています。
具体的には、ウィジェット生成、変数入力欄の更新、各イベントコールバック（基本プロンプト選択、テキスト変更）の動作を検証します。
"""

import os
import sys
import time
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.basic_prompt_frame import BasicPromptFrame


@pytest.fixture
def basic_prompts():
    """
    基本プロンプトのサンプルデータを返すフィクスチャです。
    各プロンプトは、名称、テンプレート、変数を含む辞書形式で定義しています。
    """
    return [{
        "name": "Prompt 1",
        "template": "Template 1",
        "variables": {
            "var1": "value1"
        }
    }, {
        "name": "Prompt 2",
        "template": "Template 2",
        "variables": {
            "var2": "value2"
        }
    }]


@pytest.fixture
def root():
    """
    Tkinter のルートウィジェットを返すフィクスチャです。
    GUI コンポーネントのテスト時に使用されます。
    """
    return tk.Tk()


@pytest.fixture
def frame(root, basic_prompts):
    """
    BasicPromptFrame のインスタンスを生成して返すフィクスチャです。
    テスト時に、ウィジェット生成や変数入力欄の更新、イベントの動作検証に使用します。
    """
    # MagicMock を利用してコールバックの呼び出しを検証できるようにする
    on_basic_select = MagicMock()
    on_text_change = MagicMock()
    return BasicPromptFrame(root, basic_prompts, on_basic_select, on_text_change)


def test_create_widgets(frame):
    """
    create_widgetsメソッドのテスト
    ウィジェットが正しく作成され、各ウィジェットに期待する属性が設定されていることを確認します。
    """
    # コンボボックス、テキストウィジェット、変数設定フレームが作成されているかどうか
    assert isinstance(frame.basic_combobox, ttk.Combobox)
    assert isinstance(frame.basic_text, tk.Text)
    assert isinstance(frame.variable_frame, ttk.LabelFrame)
    # コンボボックスの値リストが正しく設定されているか
    expected_names = ["Prompt 1", "Prompt 2"]
    assert list(frame.basic_combobox["values"]) == expected_names


def test_update_variable_entries(frame):
    """
    update_variable_entriesメソッドのテスト
    変数入力欄が正しく更新され、既存ウィジェットが削除されることを確認します。
    """
    variables = {"var1": "value1", "var2": "value2"}
    frame.update_variable_entries(variables)
    # 登録されたエントリーウィジェットの数が一致することを確認
    assert len(frame.variable_entries) == 2
    # 各エントリーに初期値が設定されているか
    assert frame.variable_entries["var1"].get() == "value1"
    assert frame.variable_entries["var2"].get() == "value2"


def test_on_basic_select_event(root, basic_prompts):
    """
    コンボボックス選択時のコールバックが呼ばれることをテストします。
    """
    on_basic_select = MagicMock()
    # on_text_change は不要なのでダミー関数
    on_text_change = lambda event: None
    frame = BasicPromptFrame(root, basic_prompts, on_basic_select, on_text_change)
    # コンボボックスの値を変更してイベントを発生させる
    frame.basic_combobox.current(1)
    frame.basic_combobox.event_generate("<<ComboboxSelected>>")
    # イベント処理を促すため update_idletasks を呼ぶ
    root.update_idletasks()
    # コールバックが呼ばれていることを確認
    assert on_basic_select.called


def test_on_text_change_event(root, basic_prompts):
    """
    on_text_change が呼び出されることをテストします。
    実際の KeyRelease イベントではなく、コールバックを直接呼び出して確認します。
    """
    on_basic_select = lambda event: None
    on_text_change = MagicMock()
    frame = BasicPromptFrame(root, basic_prompts, on_basic_select, on_text_change)

    # on_text_change を直接呼び出してテスト
    mock_event = MagicMock()
    frame.on_text_change(mock_event)

    assert on_text_change.called, "on_text_change が呼ばれていません。"
