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

# キーの定義
libros = 'LIBROS'
stef_csv = 'STEF_csv'
stef_excel = 'STEF_excel'
tps = 'TPS'

# 取得項目の定義
libros_column = ['タイトル', 'タイトル(英)', '著者', '簡略概要', '補足検索キーワード']
stef_csv_column = ['メンバー', '出展テーマ名（英語）', '出展テーマ名（日本語）', '技術概要（英語）', '技術概要（日本語）', '課題（英語）', '課題（日本語）']
stef_excel_column = ['label', 'author_id', 'タイトル', '概要', '本文']
tps_column = ['指図名称（日本語）', '指図名称（英語）', '指図リーダ呼称（日本語）', '指図リーダ呼称（英語）', '概要（日本語）', '概要（英語）', '実現機能の詳細', '解決すべき課題と実現方法']

# 辞書の作成
dict = {libros: libros_column, stef_csv: stef_csv_column, stef_excel: stef_excel_column, tps: tps_column}

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
    selected_data.to_csv('data/Formatted_file/' + data_source + '.csv', index=False)

'''
CSV→CSV作成処理（日本語エンコード）
'''
def create_csv_japanese_encode(file_path, selected_columns, data_source):
    original_data = pd.read_csv(file_path, encoding='cp932')
    selected_data = original_data[dict[selected_columns]]
    selected_data.to_csv('data/Formatted_file/' + data_source + '.csv', index=False)

'''
Excel→CSV作成処理
'''
def create_csv_from_excel(file_path, selected_columns, data_source):
    original_data = pd.read_excel(file_path)
    selected_data = original_data[dict[selected_columns]]
    selected_data.to_csv('data/Formatted_file/' + data_source + '.csv', index=False)

'''
テキスト内のHTMLタグ除去
'''
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

# TODO ファイルの場所によって適宜修正
current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
directory_path = parent_directory + '\\data\\original_data'
all_files = get_all_files(directory_path)

# ベクトルDB用のCSV作成処理
original_data = ""
selected_columns = ""
libros_list = []
stef_list = []
stef_csv_list = []
stef_excel_list = []
tps_list = []
for file in all_files:
    data_source = file.split("\\")[-2]
    original_file_name = file.split("\\")[-1].split(".")[0]

    if data_source == "STEF":
        extension = file.split("\\")[-1].split(".")[-1]
        # csvとExcelで項目が異なるため別々で処理
        if extension == "csv":
            selected_columns = stef_csv
            original_data = pd.read_csv(file)
            selected_data = original_data[dict[selected_columns]]
            stef_csv_list.append(selected_data)
            stef_len = len(stef_csv_list)
        elif extension == "xlsx":
            selected_columns = stef_excel
            df = pd.read_excel(file)
            # 本文（HTMLタグ、不要な記載を除去）
            df['本文'] = df['本文'].apply(remove_html_tags)
            df['本文'] = df['本文'].str.replace('<Previous   /  Next>', '\r\n')
            selected_data = df[dict[selected_columns]]
            stef_excel_list.append(selected_data)
            stef_len = len(stef_excel_list)

    elif data_source == "LIBROS":
        selected_columns = data_source
        df = pd.read_csv(file)
        # 著者（メールアドレスを除去）
        df['著者'] = df['著者'].str.replace(r'[a-zA-Z0-9._+-]+@[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.+[a-zA-Z]{2,}', '', regex=True)
        selected_data = df[dict[selected_columns]]
        libros_list.append(selected_data)

    elif data_source == "TPS":
        selected_columns = data_source
        df = pd.read_csv(file, encoding='cp932')
        # 指図リーダ呼称・姓 + 指図リーダ呼称・名
        df['指図リーダ呼称（日本語）'] = df['指図リーダ呼称・姓（日本語）'] + ' ' + df['指図リーダ呼称・名（日本語）'] 
        df['指図リーダ呼称（英語）'] = df['指図リーダ呼称・名（英語）'] + ' ' + df['指図リーダ呼称・姓（英語）'] 
        df.drop(['指図リーダ呼称・姓（日本語）', '指図リーダ呼称・名（日本語）', '指図リーダ呼称・名（英語）', '指図リーダ呼称・姓（英語）'], axis=1)
        df['指図名称（日本語）'] = df['指図名称（日本語）'].str.replace(r'\d{4}_', '', regex=True)
        selected_data = df[dict[selected_columns]]
        tps_list.append(selected_data)

# クレンジング処理後のデータをCSVとして出力
formatted_data_path = parent_directory + '/data/formatted_data/'

# クレンジング処理後のデータをCSVとして出力
combined_stef_csv_df = pd.concat(stef_csv_list, ignore_index=True)
combined_stef_csv_df.to_csv(formatted_data_path + 'combined_stef_csv_data.csv', index=False)
combined_stef_excel_df = pd.concat(stef_excel_list, ignore_index=True)
combined_stef_excel_df.to_csv(formatted_data_path + 'combined_stef_excel_data.csv', index=False)
combined_libros_df = pd.concat(libros_list, ignore_index=True)
combined_libros_df.to_csv(formatted_data_path + 'combined_libros_data.csv', index=False)
combined_tps_df = pd.concat(tps_list, ignore_index=True)
combined_tps_df.to_csv(formatted_data_path + 'combined_tps_data.csv', index=False)

# TOOD 各カラムデータの結合

print('CSV load has been completed.')
