#### ライブラリのインポート ####
import openpyxl as px
import pandas as pd
from pathlib import Path
import numpy as np
import re
import matplotlib.pyplot as plt
import japanize_matplotlib


#### 定数の定義 ####
# フォルダのパス (フォルダの場所)
# NOTE: Excelファイルの名前には`_CSR0.40_`と`_e0.750_`という形で
#       CSRやeの値が含まれるようにしてください。
#       この値は箱ひげ図を作成する際に使用します。
#       この文字列が含まれていればある程度他の文字が含まれいてもOKです。
#       例) Test01_CSR0.40_e0.750_(1).xlsx
folder_path = r"data"
folder_path = r"data_simple"

# 情報を取り出したい列名
# NOTE: この列名はExcelファイルの内容に合わせて変更してください。
columns = ["DA", "s12(kPa)", "plastDissip(Nm)", "過剰間隙水圧比"]

# 摩擦損失エネルギーとDAの列名
# NOTE: この列名はExcelファイルの内容に合わせて変更してください。
col_friction_energy = "plastDissip(Nm)"
col_DA = "DA"

# 抽出したい条件
DA_list = [1, 2, 3, 5, 7, 7.5, 8, 10, 15, 25, 50]             # DAの値 (%)
ru_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

# 条件値の単位の変更
DA_list = [DA / 100 for DA in DA_list]                        # DAの値 (% -> 1)


# ファイル名からCSRと間隙比を取得する関数
def extract_CSR_e(file_name):

    # CSRの値を取得
    CSR = float(re.search(r"_CSR([0-9.]+[0-9]{1})", file_name).group(1))

    # 間隙比の値を取得
    e = float(re.search(r"_e([0-9.]+[0-9]{1})", file_name).group(1))

    return CSR, e



#### 前処理 ####
# フォルダのパスを扱いやすい形に変更
folder_path = Path(folder_path).resolve()

print("処理を開始します。")
print(f"フォルダのパス: {folder_path}")

# 結果を格納するためのフォルダを作成
result_folder = folder_path / "result"
result_folder.mkdir(exist_ok=True)

print(f"結果を格納するフォルダ: {result_folder}")

# フォルダ内のファイルを取得して並べ替えを行う
xlsx_files = list(folder_path.glob("*.xlsx"))
xlsx_files.sort()

print("Excelファイルの数: ", len(xlsx_files))


#### ファイルの読み込み ####
# 結果を格納するリスト
result = []

# xlsxファイルに対しての処理
print("Excelファイルの読み込みを開始します。")

for xlsx_file in xlsx_files:

    print(f"  {xlsx_file.name}の処理を開始...", end="")

    # ファイルの読み込み
    wb = px.load_workbook(xlsx_file, data_only=True)

    # シートの取得
    ws = wb.active

    # データの取得
    data = ws.values

    # データをDataFrameに変換
    df = pd.DataFrame(data, columns=next(data))

    # CSRと間隙比の取得
    CSR, e = extract_CSR_e(xlsx_file.name)

    # DAに対しての処理
    for DA in DA_list:

        # DAの値が最大値を超えている場合
        if DA > df["DA"].max():
            res = df[columns].iloc[-1]
            continue

        # 値の抽出
        res = df.loc[df["DA"] >= DA, columns].iloc[0]

        # 結果をリストに追加
        result.append(np.append([xlsx_file.name, CSR, e, DA, -1], res))
    
    # ruに対しての処理
    for ru in ru_list:

        # 値の抽出
        res = df.loc[df["過剰間隙水圧比"] >= ru, columns].iloc[0]

        # 結果をリストに追加
        result.append(np.append([xlsx_file.name, CSR, e, -1, ru], res))

    # メモリの解放
    del wb, ws, df

    print("  終了しました。")

# 結果をDataFrameに変換
result = pd.DataFrame(result, 
                      columns=["file_name", "CSR", "e", 
                               "target_DA", "target_ru"] + columns)

# file_name以外の列のdtypeを変更
columns = result.columns[1:]
result[columns] = result[columns].astype(float)


#### データの保存 ####
# 結果をcsvファイルに保存
result.to_csv(result_folder / "result.csv", index=False)

print("データを", result_folder / "result.csv", "に保存しました。")


#### 箱ひげ図の作成 1 ####
# 以下のコードは、あるCSR、あるDA基準での、箱ひげ図 (横軸: e, 縦軸: 摩擦損失エネルギー)
# を作成するコードです。CSR=0.100, DA=0.01 (1%)の場合のコードです。
# 以下のコードをコピーしたり、変更して、他の条件に対しても箱ひげ図を作成することができます。

## 取り出したいCSR, DAの値の設定
# CSR_ex: CSRの値の例 (example)
# DA_ex: DAの値の例 (example)
CSR_ex = 0.100
DA_ex = 0.01

# 条件に合致するデータを抽出
data = result.loc[(result["CSR"] == CSR_ex) & (result["target_DA"] == DA_ex)]

# データの形を変更
data_e = data["e"].unique()
data_fric = []

for e in data_e:

    data_fric.append(data.loc[data["e"] == e, col_friction_energy].values)

data_fric = np.array(data_fric).reshape(-1, len(data_e))

# 箱ひげ図の作成
fig, ax = plt.subplots()

ax.boxplot(data_fric, vert=True, patch_artist=True)

# 細かい図のデザインの変更
# タイトルとラベルの設定
ax.set_title(f"CSR={CSR_ex}, DA={DA_ex}の場合の摩擦損失エネルギー")
ax.set_xticklabels(data_e)
ax.set_xlabel("e")
ax.set_ylabel("摩擦損失エネルギー")

# 目盛線の設定
ax.xaxis.grid(True)
ax.yaxis.grid(True)

# 縦軸の範囲の設定
ax.set_ylim(0, 0.05)

# グラフの保存
plt.savefig(result_folder / f"CSR_{CSR_ex}_DA_{DA_ex}.png", dpi=300)


#### 箱ひげ図の作成 2 ####
# 以下のコードは、あるe、あるru基準での、箱ひげ図 (横軸: DA, 縦軸: 摩擦損失エネルギー)
# を作成するコードです。e=0.750, ru=0.1の場合のコードです。
# 以下のコードをコピーしたり、変更して、他の条件に対しても箱ひげ図を作成することができます。

## 取り出したいe, ruの値の設定
# e_ex: eの値の例 (example)
# ru_ex: ruの値の例 (example)
e_ex = 0.750
ru_ex = 0.1

# 条件に合致するデータを抽出
data = result.loc[(result["e"] == e_ex) & (result["target_ru"] == ru_ex)]

# データの形を変更
data_DA = data["target_DA"].unique()

data_fric = []

for DA in data_DA:
    data_fric.append(data.loc[data["target_DA"] == DA, col_friction_energy].values)

data_fric = np.array(data_fric).reshape(-1, len(data_DA))

# 箱ひげ図の作成
fig, ax = plt.subplots()

ax.boxplot(data_fric, vert=True, patch_artist=True)

# 細かい図のデザインの変更
# タイトルとラベルの設定
ax.set_title(f"e={e_ex}, ru={ru_ex}の場合の摩擦損失エネルギー")
ax.set_xticklabels(data_DA)
ax.set_xlabel("DA")
ax.set_ylabel("摩擦損失エネルギー")

# 目盛線の設定
ax.xaxis.grid(True)
ax.yaxis.grid(True)

# 縦軸の範囲の設定
ax.set_ylim(0, 0.05)

# グラフの保存
plt.savefig(result_folder / f"e_{e_ex}_ru_{ru_ex}.png", dpi=300)