import os
import sys
import time
import tkinter as tk
from unittest.mock import MagicMock, patch

import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.frames.final_prompt_frame import FinalPromptFrame


@pytest.fixture
def root():
    return tk.Tk()


@pytest.fixture
def frame(root):
    return FinalPromptFrame(root)


@patch('ui.final_prompt_frame.requests.post')
def test_translate_to_english(mock_post, frame):
    """
    DeePL APIを利用して日本語プロンプトを英訳する機能のテスト
    """
    # モックの設定
    mock_response = MagicMock()
    mock_response.json.return_value = {'translations': [{'text': 'This is a test translation.'}]}
    mock_post.return_value = mock_response

    # テスト用の日本語プロンプトを設定
    frame.final_text.config(state='normal')
    frame.final_text.insert('1.0', 'これはテストです。')
    frame.final_text.config(state='disabled')

    # APIキーのモック
    frame.get_api_key = MagicMock(return_value='test_api_key')

    # 翻訳実行
    frame.translate_to_english()

    # 結果確認
    time.sleep(1)  # 確認のタイミングを遅らせる
    frame.english_text.config(state='normal')
    translated_text = frame.english_text.get('1.0', 'end-1c')
    frame.english_text.config(state='disabled')
    assert translated_text == 'This is a test translation.'


@patch('ui.final_prompt_frame.messagebox.showerror')
def test_translate_to_english_no_api_key(mock_showerror, frame):
    """
    APIキーが設定されていない場合のエラーメッセージ表示のテスト
    """
    frame.get_api_key = MagicMock(return_value=None)
    frame.translate_to_english()
    time.sleep(1)  # 確認のタイミングを遅らせる
    mock_showerror.assert_called_once_with('エラー', 'DeePLのAPIが設定されていません')


@patch('ui.final_prompt_frame.messagebox.showwarning')
def test_translate_to_english_no_text(mock_showwarning, frame):
    """
    翻訳するプロンプトがない場合の警告メッセージ表示のテスト
    """
    frame.get_api_key = MagicMock(return_value='test_api_key')
    frame.translate_to_english()
    time.sleep(1)  # 確認のタイミングを遅らせる
    mock_showwarning.assert_called_once_with('警告', '翻訳するプロンプトがありません。')


@patch('ui.final_prompt_frame.requests.post')
@patch('ui.final_prompt_frame.messagebox.showerror')
def test_translate_to_english_request_exception(mock_showerror, mock_post, frame):
    """
    翻訳リクエストが失敗した場合のエラーメッセージ表示のテスト
    """
    mock_post.side_effect = requests.exceptions.RequestException('Test exception')
    frame.get_api_key = MagicMock(return_value='test_api_key')
    frame.final_text.config(state='normal')
    frame.final_text.insert('1.0', 'これはテストです。')
    frame.final_text.config(state='disabled')
    frame.translate_to_english()
    time.sleep(1)  # 確認のタイミングを遅らせる
    mock_showerror.assert_called_once_with('エラー', '翻訳リクエストに失敗しました: Test exception')
