import json
import bcrypt

def create_user(salt, username, password):
    # ユーザー情報を格納する辞書を作成
    user_data = {}
    salt_bytes = "$2b$12$CjgL/abaAHtNb5cpZVa3G.".encode('utf-8')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt_bytes)

    # ユーザー情報を辞書に格納
    user_data['username'] = username
    user_data['hashed_password'] = hashed_password.decode('utf-8')  # ハッシュ値を文字列として保存

    # accounts.jsonファイルを読み込み
    with open('accounts.json', 'r') as file:
        data = json.load(file)
    
    # usersキーの配列にユーザー情報を追加
    data['users'].append(user_data)

    # accounts.jsonファイルを上書き保存
    with open('accounts.json', 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    salt = input("ハッシュ化のキー情報を入力してください: ")
    username = input("ユーザー名を入力してください: ")
    password = input("パスワードを入力してください: ")

    create_user(salt, username, password)
    print("ユーザー情報を保存しました。")
