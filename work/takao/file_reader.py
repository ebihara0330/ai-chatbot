"""
title:
ファイル読み込み・クレンジング処理

contents:
- 元データファイルの読み込みとデータのクレンジング処理を行う。

実行方法:
- 右クリック > Run Python > Run Python File in Terminal 
"""
import os
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# キーの定義
libros = 'libros'
stef_csv = 'stef_csv'
stef_excel = 'stef_excel'
tps = 'tps'

# 取得項目の定義
libros_column = ['タイトル', 'タイトル(英)', '著者', '簡略概要', '補足検索キーワード']
stef_csv_column = ['メンバー', '出展テーマ名（英語）', '出展テーマ名（日本語）', '技術概要（英語）', '技術概要（日本語）', '想定応用事例と顧客価値（英語）', '想定応用事例と顧客価値（日本語）', '課題（英語）', '課題（日本語）']
stef_excel_column = ['label', 'author_id', 'タイトル', '概要', '本文']
tps_column = ['指図名称（日本語）', '指図名称（英語）', '指図リーダ呼称（日本語）', '指図リーダ呼称（英語）', '概要（日本語）', '概要（英語）', '実現機能の詳細', '解決すべき課題と実現方法']

# 辞書の作成
dict = {libros: libros_column, stef_csv: stef_csv_column, stef_excel: stef_excel_column, tps: tps_column}

vector_db_data_dir = '/data/vector_db_data/'

'''
指定ディレクトリの全ファイル読み込み処理
'''
def get_all_files(directory):
    file_list = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            d = directory
            file_list.append(os.path.join(root, filename))
    return file_list

'''
CSV→CSV作成処理
'''
def create_csv(file_path, selected_columns, data_source):
    original_data = pd.read_csv(file_path)
    selected_data = original_data[dict[selected_columns]]
    selected_data.to_csv(vector_db_data_dir + data_source + '.csv', index=False)

'''
CSV→CSV作成処理（日本語エンコード）
'''
def create_csv_japanese_encode(file_path, selected_columns, data_source):
    original_data = pd.read_csv(file_path, encoding='cp932')
    selected_data = original_data[dict[selected_columns]]
    selected_data.to_csv(vector_db_data_dir + data_source + '.csv', index=False)

'''
Excel→CSV作成処理
'''
def create_csv_from_excel(file_path, selected_columns, data_source):
    original_data = pd.read_excel(file_path)
    selected_data = original_data[dict[selected_columns]]
    selected_data.to_csv(vector_db_data_dir + data_source + '.csv', index=False)

'''
テキスト内のHTMLタグ除去
'''
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

'''
テキスト内のメールアドレス除去
'''
def remove_mail_address(data):
    return data.str.replace(r'[a-zA-Z0-9._+-]+@[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.+[a-zA-Z]{2,}', '', regex=True)

'''
ベクトルDB用のカラム結合データ作成
'''
def combine_columns(df, selected_columns, content_list):
    for col in df.columns:
        df[col] = df[col].fillna('')
        # 【カラム名】
        # 値
        # の形式にする
        df[col] = df[col].apply(lambda x: '【{}】\r\n{}'.format(col, str(x)))
    
    df = df[dict[selected_columns]]
    df['content'] = df.apply(lambda row: ' \r\n'.join(map(str, row)), axis=1)
    content_list.append(df['content'])

'''
ベクトルDB用のカラム結合データ作成
'''
def create_csv_for_vector_db():
    content_list = []
    current_directory = os.getcwd()

    # gitの管理外のディレクトリをデータ格納場所とする
    parent_directory = os.path.dirname(current_directory)
    directory_path = parent_directory + '/data/original_data'
    all_files = get_all_files(directory_path)

    # ベクトルDB用のCSV作成処理
    for file in all_files:
        data_source = file.split("\\")[-2]

        if data_source == "stef":
            extension = file.split("\\")[-1].split(".")[-1]
            # csvとExcelで項目が異なるため別々で処理
            if extension == "csv":
                selected_columns = stef_csv
                df = pd.read_csv(file)
                # メンバー（メールアドレスを除去）
                member = 'メンバー'
                df[member] = remove_mail_address(df[member])

                combine_columns(df, selected_columns, content_list)

            elif extension == "xlsx":
                selected_columns = stef_excel
                df = pd.read_excel(file)
                # 本文（HTMLタグ、不要な記載を除去）
                body = '本文'
                df[body] = df[body].apply(remove_html_tags)
                df[body] = df[body].str.replace('<Previous   /  Next>', '\r\n')

                combine_columns(df, selected_columns, content_list)

        elif data_source == "libros":
            selected_columns = data_source
            df = pd.read_csv(file)
            # 著者、簡略概要（メールアドレスを除去）
            author = '著者'
            short_description = '簡略概要'
            title_en = 'タイトル(英)'
            sub_search_keyword = '補足検索キーワード'
            df[author] = remove_mail_address(df[author])
            df[short_description] = remove_mail_address(df[short_description])
            combine_columns(df, selected_columns, content_list)

        elif data_source == "tps":
            selected_columns = data_source
            df = pd.read_csv(file, encoding='cp932')
            # 指図リーダ呼称・姓 + 指図リーダ呼称・名
            df['指図リーダ呼称（日本語）'] = df['指図リーダ呼称・姓（日本語）'] + ' ' + df['指図リーダ呼称・名（日本語）'] 
            df['指図リーダ呼称（英語）'] = df['指図リーダ呼称・名（英語）'] + ' ' + df['指図リーダ呼称・姓（英語）'] 
            df.drop(['指図リーダ呼称・姓（日本語）', '指図リーダ呼称・名（日本語）', '指図リーダ呼称・名（英語）', '指図リーダ呼称・姓（英語）'], axis=1)
            df['指図名称（日本語）'] = df['指図名称（日本語）'].str.replace(r'\d{4}_', '', regex=True)

            combine_columns(df, selected_columns, content_list)

    # クレンジング処理後のデータをCSVとして出力
    formatted_data_path = parent_directory + vector_db_data_dir

    # クレンジング処理後のデータをCSVとして出力
    df = pd.concat(content_list, ignore_index=True)
    new_csv_path = formatted_data_path + 'combined_data.csv'

    # 一旦100件でテスト
    # df = df.head(100)

    df.to_csv(new_csv_path, index=False)

    print('CSV load has been completed.')
    return new_csv_path

# 動作確認用
create_csv_for_vector_db()