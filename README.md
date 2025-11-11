# RPMT_reader

<a href="README_EN.md">English README</a>

RPMTをneunetで利用した場合に得られるedrファイルを位置と時間を持つイベントデータに変換し、CSVに出力します。
また、出力されたCSVに位置のROIや時間のROIを掛けることができます。

本コードはpythonライブラリとして利用することができ、
pythonコード内に組み込むことが可能です。

Tips: 
`.edr` ファイルには以下の情報が含まれています。
- 検出器電気信号の波高データ  
- 縦検出器または横検出器の識別情報  
- キッカーパルスからの経過時間


## インストール法、始め方
0. python と git をインストールする。
1. RPMT_reader のプログラムを置きたい任意のフォルダに移動。
`cd {任意のフォルダ名}`
2. `git clone https://github.com/carbon12-ryu/RPMT_reader.git`
3. `pip install -e ./RPMT_reader`

`pip install ./RPMT_reader` としても利用できますが、モジュールの中身をローカルで内容を変更しても反映されません。

## 使い方
1. インストール後にpythonファイル内で`import RPMTreader`を宣言する。
2. `RPMTreader.EDRread()`の様に呼び出して利用する。

サンプルコード https://github.com/carbon12-ryu/RPMT_reader_sampleCode

## 各関数の説明
# EDRread
```
EDRread(filePath, mapGraphPath, tofGraphPath, eventCsvPath, tofCsvPath, xSwap, ySwap, tofBinTime)
```
`.edr`ファイルを読み込む。`.edr`は波高データであるためこれを中性子イベントデータに解釈しなおす。解釈したデータを二次元マップ、TOFスペクトルとしての出力も行う。

### Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `filePath` | `str` | — | 読み込む `.edr` ファイルのフルパス |
| `mapGraphPath` | `str`, optional | `None` | 中性子イベントの2D分布を出力するグラフのファイルパス。拡張子は matplotlib の `savefig` が対応する形式（`.png`, `.pdf`, `.jpeg` など）に限る。空欄の場合、描画されない。 |
| `tofGraphPath` | `str`, optional | `None` | TOFスペクトルグラフのファイルパス。拡張子と空欄時は`mapGraphPath`同様。|
| `eventCsvPath` | `str`, optional | `None` | 各イベントの詳細を CSV に出力するパス。拡張子は`.csv`のみ。空欄時は保存されない。 |
| `tofCsvPath` | `str`, optional | `None` | 時間と中性子数を CSV に出力するパス。拡張子は`.csv`のみ。空欄時は保存されない。|
| `xSwap` | `bool`, optional | `False` | X軸を反転して表示する場合に `True` に設定。 |
| `ySwap` | `bool`, optional | `False` | Y軸を反転して表示する場合に `True` に設定。 |
| `xySwap` | `bool`, optional | `False` | X軸とY軸を交換して表示する場合に `True` に設定。 |
| `tofBinTime` | `float`, optional | `1e-5` | TOFスペクトルのビン幅 [秒]（デフォルトは 10 µs）。 |

### Returns
| Name | Type | Description |
|------|------|-------------|
| `t0_pulse` | `int` | `.edr`に含まれるキッカーパルス数 |
| `neutrons` | `numpy.ndarray` | 中性子イベントの配列。各行 `[x, y, t]` で、位置 x, y と到着時間が格納される。形状は `(N, 3)`。 |
| `tof_data` | `numpy.ndarray` | TOFの配列。各行`[time, count]`で、時間と中性子数が格納される。形状は `(N, 2)`。 `tofBinTime` に基づくビン幅で集計。 |
| `total_count` | `int` | 全体の中性子数 |

### eventCsvの形式
2行目にキッカーパルス数、4行目から`[x, y, t]`のイベントデータが格納される。
```
total KP 
5116
x,y,time[s]
0.506711,0.450617,0.044244
```

### tofCsvの形式
2行目にキッカーパルス数、4行目にbin幅、6行目から`[time, count]`のイベントデータが格納される。
```
total KP 
5116
bin time[s]
0.0001
time[s],counts
0.000060,12.000000
```

### より高度な設定
`.edr`ファイルには波高データが格納されており、それを中性子数として変換しています。
そのための変換パラメータは`./RPMTreader/settings/EDRsettings.json`に格納されています。通常使用では変更の必要はありません。変更してもリモートにはpushしないでください。
| Name | default | Description |
|------|------|-------------|
| `clockFreq` | 40e6 | neunetのクロック周波数 |
| `effectiveTime` | 400e-9 | 中性子計数として認識される縦軸検出器と横軸検出器の出力時間差。縦軸検出器と横軸検出器がこの時間以内に同時に作動した場合のみ中性子計数としてカウントされる。 |
| `PL_min` | 128 | 左側波高の最小値。これより小さいものはノイズとして処理。 |
| `PL_max` | 1024 | 左側波高の最大値。これより大きいものはノイズとして処理。 |
| `PR_min` | 128 | 右側波高の最小値。これより小さいものはノイズとして処理。 |
| `PR_max` | 1024 | 右側波高の最大値。これより大きいものはノイズとして処理。 |

# rectROI
```
rectROI(eventCsvPath, xmin, xmax, ymin, ymax, mapGraphPath, tofGraphPath, tofCsvPath, timeROImin, timeROImax, tofBinTime)
```
位置に関して四角形のROIを掛ける関数。同時に、中性子到達時間のROIを掛けることも可能。`EDRread`で出力されたCSVを読み込む。
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `eventCsvPath` | `str` | — | 読み込むイベント CSV ファイルのfull path。EDRread の出力CSV。 |
| `xmin` | `float` | — | ROIのx最小値。 |
| `xmax` | `float` | — | ROIのx最大値。 |
| `ymin` | `float` | — | ROIのy最小値。 |
| `ymax` | `float` | — | ROIのy最大値。 |
| `mapGraphPath` | `str`, optional | `None` | 2D マップを出力するグラフのファイルパス。抽出範囲も同時に表示される。拡張子は matplotlib が対応する形式 (`.png`, `.pdf`, `.jpeg` 等)。空欄の場合、描画されない。 |
| `tofGraphPath` | `str`, optional | `None`  | 抽出イベントの TOFスペクトルを出力するグラフのファイルパス。拡張子・空欄時は mapGraphPath 同様。                          |
| `tofCsvPath`   | `str`, optional | `None`  | 抽出 TOF データを CSV に保存するパス。空欄の場合は保存されません。 |
| `timeROImin`   | `float`, optional | `None`  | TOFの下限（秒）。指定した場合、範囲時間内の中性子のみが出力される。 |
| `timeROImax`   | `float`, optional | `None`  | TOFの上限（秒）。指定した場合、範囲時間内の中性子のみが出力される。 `timeROImin`が指定されている場合、必須。|
| `tofBinTime`   | `float`, optional | `10e-6` | TOFスペクトルのビン幅 [秒]（デフォルトは 10 µs）。 |

### Returns
| Name | Type | Description |
|------|------|-------------|
| `t0_pulse` | `int` | イベントCSVに入力されているキッカーパルス数 |
| `neutrons` | `numpy.ndarray` | 抽出された中性子イベントの配列。|
| `tof_data` | `numpy.ndarray` | 抽出されたTOFの配列。|
| `total_count` | `int` | 抽出された中性子数 |

# circleROI
```
circleROI(eventCsvPath, xcenter, ycenter, radius, mapGraphPath, tofGraphPath, tofCsvPath, timeROImin, timeROImax, tofBinTime)
```
位置に関して円形のROIを掛ける関数。同時に、中性子到達時間のROIを掛けることも可能。`EDRread`で出力されたCSVを読み込む。
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `eventCsvPath` | `str` | — | 読み込むイベント CSV ファイルのfull path。EDRread の出力CSV。 |
| `xcenter` | `float` | — | ROI円のx中心。 |
| `ycenter` | `float` | — | ROI円のy中心。 |
| `radius` | `float` | — | ROI円の半径。 |
| `mapGraphPath` | `str`, optional | `None` | 2D マップを出力するグラフのファイルパス。抽出範囲も同時に表示される。拡張子は matplotlib が対応する形式 (`.png`, `.pdf`, `.jpeg` 等)。空欄の場合、描画されない。 |
| `tofGraphPath` | `str`, optional | `None`  | 抽出イベントの TOF（Time-of-Flight）スペクトルを出力するグラフのファイルパス。拡張子・空欄時は mapGraphPath 同様。                          |
| `tofCsvPath`   | `str`, optional | `None`  | 抽出 TOF データを CSV に保存するパス。空欄の場合は保存されません。 |
| `timeROImin`   | `float`, optional | `None`  | TOFの下限（秒）。指定した場合、範囲時間内の中性子のみが出力される。 |
| `timeROImax`   | `float`, optional | `None`  | TOFの上限（秒）。指定した場合、範囲時間内の中性子のみが出力される。 `timeROImin`が指定されている場合、必須。|
| `tofBinTime`   | `float`, optional | `10e-6` | TOFスペクトルのビン幅 [秒]（デフォルトは 10 µs）。 |

### Returns
| Name | Type | Description |
|------|------|-------------|
| `t0_pulse` | `int` | イベントCSVに入力されているキッカーパルス数 |
| `neutrons` | `numpy.ndarray` | 抽出された中性子イベントの配列。|
| `tof_data` | `numpy.ndarray` | 抽出されたTOFの配列。|
| `total_count` | `int` | 抽出された中性子数 |


## 開発者
Ryuto Fujitani

## 開発方法
リポジトリをforkして、mainブランチへpull requestを作成して下さい。
バグ報告、機能追加要望等はissueへ
