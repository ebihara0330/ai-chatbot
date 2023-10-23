## hive-pollinator-ai

### 概要
 * pollinator-aiの検証用アプリケーション


### 事前準備
 1. 仮想環境構築
 　 python -m venv ../venv
    ※pathは任意

 2. SWインストール
 　 ../venv/Scripts/activate
    python -m pip install -r ./requirements.txt

 3. パスワードファイルの設定
 　 root/.streamlit/secrets.tomlファイルを作成する
 　 password = 'xx'
 　 ※xxにはAzure App Service＞構成＞passwordの環境変数値を設定
  　※環境変数passwordに設定してもOK

 4. 作成したプロトタイプを設定ファイル（config.yaml）に追記する
 -----------------------
  prototype:
  Test1:　→セレクトボックスの表示名をセット
    title: Test1　→セレクトボックスの表示名をセット
    path: ./work/ebihara/prototype-test.py　→プロトタイプのプログラムパスを設定
    updatedate: 2023-10-16　→任意の更新日を設定（画面には降順で表示する）
 -----------------------


### ローカルの動作確認方法
 1. 以下のコマンドでstreamlitサーバを起動する
    ../venv/Scripts/activate
    streamlit run main.py
