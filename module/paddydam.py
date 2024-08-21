#######################################
# step1
#memo
# 更新日：2024-2-21
# 落水線を辿った場合の距離を求めるプログラム
#######################################

########################################
#ライブラリのインポート
#python = 3.9.17
#numpy = 1.23.5
#pandas = 2.1.0
#numba = 0.57.0
## インストール方法(例)バージョン指定
#conda install "python = 3.9.17"  ←"""の中をインストールしたいものに変える
#########################################
# #####################################step1###########################################
'''
筆ポリゴンのidを1~の整数に置き換えるプログラム
'''
import pandas as pd
from scipy.spatial import cKDTree
import pandas as pd

def mapping(csv_path, id_column):
    # CSVファイルの読み込み
    df = pd.read_csv(csv_path)
    # 欠損値を0で補完
    df = df.fillna(0)
    
    # ID列を文字列型に変換
    df[id_column] = df[id_column].astype(str)
    
    # 0以外のユニークなIDのリストを作成
    unique_ids = df[df[id_column] != '0'][id_column].unique()
    
    # 各IDに対応する整数をマッピング（0は除外してマッピング）
    id_mapping = {'0': 0}  # 0はマッピングで0のまま
    id_mapping.update({uuid: i + 1 for i, uuid in enumerate(unique_ids)})
    
    # 新しい番号をマッピングして新しい列に適用
    df['paddy_id'] = df[id_column].map(id_mapping)
    
    # 0以外のユニークなpaddy_idを取得し、ソート
    unique_paddy_ids = df[df['paddy_id'] != 0]['paddy_id'].unique()
    sorted_unique_paddy_ids = sorted(unique_paddy_ids)
    
    df.to_csv('log/paddyid.csv', index=False)
    
    return df, sorted_unique_paddy_ids

# #################################step2################################################
"""
田んぼからの流出量を割り当てる落水線を探索する（v3）
最小距離とそのメッシュ組み合わせのインデックスも取得
"""


# 各paddy_idに対して最も近いchannel_idを見つけるための関数
def find_closest_channel_optimized(df, paddy_ids, channel_rows):
    new_rows = []
    # channel_rowsの座標を抽出してk-d treeを構築
    channel_coords = channel_rows[['X', 'Y']].values
    tree = cKDTree(channel_coords)
    channel_indices = channel_rows.index.tolist()
    
    for paddy_id in paddy_ids:
        id_rows = df[df['paddy_id'] == paddy_id]
        #print('find_closet_channelmesh_id' ,paddy_id, '/', len(paddy_ids))
        min_distance = float('inf')
        min_index = None
        paddy_index = None
        
        for id_index, id_row in id_rows.iterrows():
            # k-d treeを使用して最も近いchannelのインデックスと距離を取得
            distance, index = tree.query([id_row['X'], id_row['Y']])
            if distance < min_distance:
                min_distance = distance
                min_index = channel_indices[index] + 1  # インデックスの調整
                paddy_index = id_index + 1
        
        if min_index is not None:
            new_row = {
                'paddy_id': paddy_id,
                'mesh_rakusui': min_index,
                'mesh_paddy': paddy_index,
                'dist': min_distance,
                'orifice': 1.000000000000000
            }
            new_rows.append(new_row)
    return new_rows







