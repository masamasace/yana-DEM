#### ライブラリのインポート ####
import openpyxl as px
import pandas as pd
from pathlib import Path
import numpy as np
import re
import matplotlib.pyplot as plt
import japanize_matplotlib
import gc


#### 定数の定義 ####
# フォルダのパス (フォルダの場所)
# NOTE: Excelファイルの名前には`_CSR0.40_`と`_e0.750_`という形で
#       CSRやeの値が含まれるようにしてください。
#       この値は箱ひげ図を作成する際に使用します。
#       この文字列が含まれていればある程度他の文字が含まれいてもOKです。
#       例) Test01_CSR0.40_e0.750_(1).xlsx
folder_path = r"C:\Users\EEL06\Documents\研究\2024DEM解析データ\Test_DEM"

# 情報を取り出したい列名
# NOTE: この列名はExcelファイルの内容に合わせて変更してください。
columns = ["DA", "s12(kPa)", "摩擦損失エネルギー", "過剰間隙水圧比ru"]

# 抽出したい条件
DA_list = [1, 2, 3, 5, 7, 7.5, 8, 10, 15, 25, 50]
ru_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]


#### 関数の定義 ####
# 特定の条件における値を抽出する関数
def extract_value(path, col, DA=None, ru=None):

    # 引数のチェック
    if DA is None and ru is None:
        raise ValueError("DAとruのどちらかは指定してください。")
    elif DA is not None:
        cond_col = "過剰間隙水圧比ru"
    elif ru is not None:
        cond_col = "DA"

    # Excelファイルを開く
    wb = px.load_workbook(path)

    # シートを取得
    ws = wb.active

    # データを取得
    data = ws.values

    # データをDataFrameに変換
    df = pd.DataFrame(data)

    # 値の抽出
    # DAの値が指定されている場合
    if cond_col == "DA":

        # ruがある一定以上の値の行を取得
        extract_value = df.loc[df[cond_col] >= ru, col]
        # その中でも一番最初の行を取得
        extract_value = extract_value.iloc[0]
    # ruの値が指定されている場合
    elif cond_col == "ru":

        # DAがある一定以上の値の行を取得
        extract_value = df.loc[df[cond_col] >= DA, col]
        # その中でも一番最初の行を取得
        extract_value = extract_value.iloc[0]
    
    return extract_value.values


# ファイル名からCSRと間隙比を取得する関数
def extract_CSR_e(file_name):

    # CSRの値を取得
    CSR = float(re.search(r"_CSR([0-9.]+)_", file_name).group(1))

    # 間隙比の値を取得
    e = float(re.search(r"_e([0-9.]+)_", file_name).group(1))

    return CSR, e

# 箱ひげ図を作成する関数
def draw_boxplot(data_x, data_y, x_label, y_label, title, save_path):
    
    # 箱ひげ図の作成
    fig, ax = plt.subplots()

    # 箱ひげ図の作成
    ax.boxplot(data_y, labels=data_x)
    
    # x軸、y軸、タイトルの設定 
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    fig.savefig(save_path, dpi=300)

    plt.clf()
    plt.cla()
    gc.collect()


#### 前処理 ####
# フォルダのパスを扱いやすい形に変更
folder_path = Path(folder_path).resolve()

# 結果を格納するためのフォルダを作成
result_folder = folder_path / "result"
result_folder.mkdir(exist_ok=True)

# フォルダ内のファイルを取得して並べ替えを行う
xlsx_files = list(folder_path.glob("*.xlsx")).sort()


#### メイン処理 ####
# 結果を格納するリスト
result = []

# DAに対しての処理
for DA in DA_list:

    for xlsx_file in xlsx_files:
        # 値の抽出
        res = extract_value(xlsx_file, columns, DA=DA)
        CSR, e = extract_CSR_e(xlsx_file.name)
        # 結果をリストに追加
        result.append(np.append(xlsx_file.name, CSR, e, DA, -1, res))

# ruに対しての処理
for ru in ru_list:

    for xlsx_file in xlsx_files:
        # 値の抽出
        res = extract_value(xlsx_file, columns, ru=ru)
        CSR, e = extract_CSR_e(xlsx_file.name)
        # 結果をリストに追加
        result.append(np.append(xlsx_file.name, CSR, e, -1, ru, res))

# 結果をDataFrameに変換
result = pd.DataFrame(result, 
                      columns=["file_name", "CSR", "e", 
                               "target_DA", "target_ru"] + columns)

#### 後処理 ####
# 結果をcsvファイルに保存
result.to_csv(result_folder / "result.csv", index=False)

# 箱ヒゲ図の作成
# あるCSR、あるDA or あるru基準での、箱ひげ図 (横軸: e, 縦軸: 摩擦損失エネルギー)の作成
for CSR in result["CSR"].unique():

    for DA in DA_list:

        # 条件に合致するデータを抽出
        data = result.loc[(result["CSR"] == CSR) 
                          & (result["target_DA"] == DA)]

        # 箱ひげ図の作成
        draw_boxplot(data["e"], data["摩擦損失エネルギー"],
                        "e", "摩擦損失エネルギー", f"CSR={CSR}, DA={DA}",
                        result_folder / f"CSR_{CSR}_DA_{DA}.png")

    for ru in ru_list:

        # 条件に合致するデータを抽出
        data = result.loc[(result["CSR"] == CSR) 
                          & (result["target_ru"] == ru)]
        
        # 箱ひげ図の作成
        draw_boxplot(data["e"], data["摩擦損失エネルギー"],
                        "e", "摩擦損失エネルギー", f"CSR={CSR}, ru={ru}",
                        result_folder / f"CSR_{CSR}_ru_{ru}.png")

# ある間隙比、あるDA or あるru基準での、箱ひげ図 (横軸: CSR, 縦軸: 摩擦損失エネルギー)の作成
for e in result["e"].unique():

    for DA in DA_list:

        # 条件に合致するデータを抽出
        data = result.loc[(result["e"] == e) 
                          & (result["target_DA"] == DA)]

        # 箱ひげ図の作成
        draw_boxplot(data["CSR"], data["摩擦損失エネルギー"],
                        "CSR", "摩擦損失エネルギー", f"e={e}, DA={DA}",
                        result_folder / f"e_{e}_DA_{DA}.png")

    for ru in ru_list:

        # 条件に合致するデータを抽出
        data = result.loc[(result["e"] == e) 
                          & (result["target_ru"] == ru)]
        
        # 箱ひげ図の作成
        draw_boxplot(data["CSR"], data["摩擦損失エネルギー"],
                        "CSR", "摩擦損失エネルギー", f"e={e}, ru={ru}",
                        result_folder / f"e_{e}_ru_{ru}.png")

