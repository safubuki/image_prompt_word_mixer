# Image Prompt Word-Mixer 
**Image Prompt Word-Mixer** は、画像生成に使用するプロンプトのワードを自由に組み替えることで、さまざまなパターンの画像作成を支援するデスクトップアプリケーションです。
 
<div align="center">
  <img src="./image/winter_tool.png" alt="Winter Tool" width="650"/>
  <p>Image Prompt Word-Mixer の画面</p>
  <p>▼</p>
  <img src="./image/winter_gemini.png" alt="Winter Gemini" height="200"/>
  <img src="./image/winter_imagefx.png" alt="Winter ImageFX" height="200"/>
  <p>さまざまな生成 AI ツールで利用可能です！</p>
</div>

## 使い方

1. **環境設定**  
   - Python 3.x がインストールされていることを確認してください。  
   - 依存パッケージとして [requests](https://pypi.org/project/requests/) を利用しているため、以下のコマンドでインストールしてください。  
   ※なお、ホスト環境にインストールすることが気になる方は、適宜venv(Python仮想環境など)を利用してください。

     ```sh
     pip install requests
     ```  

2. **起動方法**  
   - プロジェクトルートディレクトリに移動し、以下のコマンドでアプリケーションを起動してください。  
     ```sh
     python app.py
     ```  
   - [app.py](app.py) をエントリーポイントとして、GUI ウィンドウが表示されます。

3. **GUI の操作**  
   - **基本プロンプト**  
     画面左側では、ドロップダウンリストから基本プロンプトを選択すると、テンプレートと変数入力欄が表示されます。  
     - 例: 「人物がものを持っている」を選択すると、`{character}`、`{goods}`、`{state}` の各変数の初期値が入力欄に表示され、これらを編集するとプロンプトが更新されます。

   - **追加プロンプト**  
     画面右側では、まず`主語`に「男性」や「女性」など入力し、Treeview から追加プロンプト（感情表現やアクションなど）を選択することで、プロンプトを作成できます。このとき`Ctrlキー`を押しながら複数選択することもできます。
     - 例: 「笑顔」や「走っている」を選択すると、各プロンプトが選択され、内部でプレースホルダー `{character}` が「主語」で指定した文字列に置換されます。

   - **完成プロンプト**  
     基本プロンプトと追加プロンプトが結合され、下部のテキストエリアに完成プロンプトとして表示されます。  

   - **プロンプト英語翻訳（任意）**  
     生成完了した日本語のプロンプトを `DeePL API` を利用して英訳することもできます。  
     英語翻訳機能を利用しない場合は、この項目はスキップしてください。

      - **API キーの取得**  
        `DeePL API` を利用するためには API キーが必要です。API キーは DeePL の公式サイト  
        [https://www.deepl.com/ja/pro-api](https://www.deepl.com/ja/pro-api)  
        で取得してください。なお、API 利用には、ユーザー登録、住所登録、クレジットカード登録が必要です。

      - **API キーの設定 ([api_key.json](api_key.json))**  
        DeePL の API キーを取得したら、`api_key.json` に保存してください。  
        以下の JSON フォーマットの `your_api_key_here` の部分を、実際の API キーに置き換えてください。

        ```json
        {
            "api_key": "your_api_key_here"
        }
        ```
      - **英語に翻訳ボタン**  
        日本語プロンプトが完成している状態で `▼ プロンプトを英語に翻訳 ▼` ボタンをクリックすると、日本語の完成プロンプトが `DeePL API` を利用して英訳され、その結果が下部のテキスト領域に表示されます。  
        なお、日本語プロンプト欄が空欄の場合、または API キーが設定されていない場合は、エラーメッセージが表示されます。

    - **プロンプトのコピー**  
      完成したプロンプトは「コピーボタン」を押すことで、クリップボードにコピーすることができます。確認ダイアログは表示されませんので、すぐに利用可能です。

4. **JSON ファイルの作成方法**  

   このソフトウェアでは、プロンプトのテンプレートは JSON 形式で管理されています。利用するテンプレート用 JSON ファイルは以下の 2 種類です。

   - **基本プロンプト (basic_prompts.json)**

     基本プロンプトは生成する画像のベースとなるテンプレート情報を含み、テンプレートと変数の初期値が定義されています。  
     
     ファイル例:
     ```json
     [
         {
             "name": "人物がものを持っている",
             "prompt": "{character}が{goods}を持っている写真を生成してください。\n{goods}は、{state}です。",
             "default_variables": {
                 "character": "中年男性",
                 "goods": "マグカップ",
                 "state": "ユニーク"
             }
         },
         {
             "name": "背景をバックにポーズを取る",
             "prompt": "{character}が{background}を背景にポーズをとっている写真を生成してください。",
             "default_variables": {
                 "character": "アメリカ人女性",
                 "background": "美しい夕焼け"
             }
         }
     ]
     ```

     各オブジェクトは以下のキーを持ちます:

     - **name**  
       プロンプトの名称です。GUI 上ではこの名前が表示され、ユーザーがテンプレートを識別するために利用されます。

     - **prompt**  
       画像生成に用いられる説明テンプレートです。中に含まれる `{character}` などのプレースホルダーは、実行時に `default_variables` の値やユーザーの入力で置換されます。

     - **default_variables**  
       テンプレート内に含まれる各プレースホルダーの初期値を定義します。ユーザーはこの初期値を編集して、最終的なプロンプトを生成できます。

   - **追加プロンプト (element_prompts.json)**

     追加プロンプトは基本プロンプトに追加するオプション文章を管理します。  
     
     ファイル例:
     ```json
     [
         {
             "category": "感情表現",
             "prompt_lists": [
                 {"title": "笑顔", "prompt": "その{character}は、笑顔です。"},
                 {"title": "悲しい", "prompt": "その{character}は、悲しそうです。"}
             ]
         },
         {
             "category": "アクション",
             "prompt_lists": [
                 {"title": "走っている", "prompt": "その{character}は、素早く走っている。"},
                 {"title": "ジャンプしている", "prompt": "その{character}は、ジャンプしています。"},
                 {"title": "クライミング", "prompt": "その{character}は、壁を登っています。"}
             ]
         }
     ]
     ```

     各カテゴリおよびプロンプトオブジェクトは以下のキーを持ちます：

     - **category**  
       追加プロンプトを分類するためのカテゴリ名です。GUI 上でグループ分けに利用されます。

     - **prompt_lists**  
       各カテゴリ内で定義された追加プロンプトのリストです。  

       各要素は以下のキーを持ちます:
     
       - **title**  
         プロンプトの名称です。GUI 上ではツリービューの各項目として表示され、ユーザーが内容を識別する際に利用されます。

       - **prompt**  
         実際に画像生成に用いられる説明テンプレートです。テンプレート内に含まれる `{character}` のプレースホルダーは、実行時に「主語」テキストボックスに指定された文字列に置換されます。

## exeファイルの作成

Python のスクリプトを単体の exe ファイルとして利用する場合は、[PyInstaller](https://pypi.org/project/pyinstaller/) を利用します。  
事前に以下のコマンドで pyinstaller をインストールしてください:

```bash
pip install pyinstaller
```

インストール後、以下のコマンドで exeファイルを作成します:

```bash
pyinstaller --onefile --windowed app.py
```

上記コマンドを実行すると「dist」フォルダに exeファイルが生成されます。  
作成されたexeファイルと同階層に
- basic_prompts.json
- element_prompts.json
- api_key.json  

を配置してください。

## ライセンス
ライセンスファイルを参照してください  
[LICENSE ファイルへ](LICENSE)

## 最後に
もし問題やご要望がありましたら、issue でご連絡ください。






