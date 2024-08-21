# コードの使用方法

## 事前に用意するデータ
- 落水線データ（rasterデータを想定）
- メッシュデータ（*.shp, *.gpkg）
- 集水域を特定するポリゴンデータ（集水域を認識する一意のid, 集水域に対応する排水メッシュid）
![集水域](https://github.com/user-attachments/assets/53476a6a-b013-46f1-9618-62de09d02de3)


## 作成手順

### QGIS作業
1. メッシュの重心を算出
2. 落水線のラスタとメッシュの重心データのCRSを統一する
3. ポイントサンプリングツールで、落水線(rakusui: 0/1)および水田ポリゴン(paddyid: 筆ポリゴンのuuid属性をコピー)と重なるメッシュの重心に属性を付与(mesh_data.csv)
4. 落水線のラスタを等間隔のポイントデータにした*.csvファイル（等間隔落水線ポイント.csv）
5. mesh_data.csvに集水域を特定するポリゴンデータと重なる部分の排水メッシュidを結合する

### Python
1. QGIS作業で用意した「mesh_data.csv」と、「等間隔落水線ポイント.csv」をinputフォルダに格納

2. main.pyがあるディレクトリに移動し、以下のコマンドを実行:
```
python main.py
```
落水線を辿った排水ポイントまでの距離をそれぞれの田んぼから算出
![イメージ](https://github.com/user-attachments/assets/dc9346ea-9cde-4d1c-8f05-ca555f6bd2d7)

3. 出力されるファイル:
- pqout.csv
- log/paddyid.csv

これらを加工してUNSTのinputデータとして使用
