#### ライブラリのインポート ####
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

#### csvファイルの読み込み ####
result_csv_path = r"data_simple/result/result.csv"

result = pd.read_csv(result_csv_path)

print(result)

raise NotImplementedError("このコードは未完成です。")


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