#######################################
# step2
#memo
# 更新日：2024-2-8
# 00_paddydamで作成したデータと、GISで作成した複数メッシュに対する排水ポイントで区分した領域データから
# メッシュid上の始点（直近落水線）と終点（落水線上の排水ポイント）を作成する
#######################################

import pandas as pd
import numpy as np

def association(format_df, pqout_df, error_log_path='log/error_log.csv'):

    # pqout_df と format_df を結合
    pqout_df = pd.merge(pqout_df, format_df, left_on='mesh_rakusui', right_on='fid', how='left')

    # format_dfのpaddy_idを使用するため、pqout_dfのpaddy_idは無視
    pqout_df.rename(columns={'paddy_id_x': 'paddy_id'}, inplace=True)

    # 不要になったfid列と重複するpaddy_id_x列を削除
    pqout_df.drop(columns=['fid', 'paddy_id_y'], inplace=True)

    # 必要な列を選択して新しいDataFrameを作成し、列名を変更
    start_end_df = pqout_df[['mesh_rakusui', 'drn_id']].rename(columns={'mesh_rakusui': 'start_id', 'drn_id': 'end_id'})

    # 0のend_idを持つ行のカウント
    zero_end_id = start_end_df[start_end_df['end_id'] == 0]
    zero_count = len(zero_end_id)
    
    if zero_count > 0:
        # エラーメッセージ出力とエラーログファイルへの保存
        print(f'error --end_id has {zero_count} values')
        zero_end_id[['start_id']].to_csv(error_log_path, index=False)
    else:
        # エラーがない場合のメッセージ
        print("complete --")
        
    


    return start_end_df, pqout_df


#######################################
#memo
# 更新日：2024-2-8
# メッシュ上のidと落水線だけで構成されたidを紐付け
#######################################

def calculate_euclidean_distance(x1, y1, x2, y2):
    """ユークリッド距離を計算する関数"""
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def find_nearest_point_id(x, y, df):
    """指定された座標に最も近い点のIDを探索する関数"""
    distances = df.apply(lambda row: calculate_euclidean_distance(x, y, row['X'], row['Y']), axis=1)
    return df.loc[distances.idxmin(), 'fid']


def process_nearest_ids(df, basedf, start_end_df):
    
    
    total_rows = len(start_end_df)
    new_start_end_ids = []

    for index, row in start_end_df.iterrows():
        # 現在の進捗状況を表示
        #print(f'Processing {index + 1}/{total_rows} rows...')
        start_x, start_y = basedf.loc[basedf['fid'] == row['start_id'], ['X', 'Y']].iloc[0]
        
        # end_idが0の場合はそのまま0を使用し、それ以外の場合に処理を実行
        if row['end_id'] == 0:
            end_x, end_y = 0, 0  # end_x, end_yを0とする
            end_id_nearest = 0  # end_id_nearestも0とする
        else:
            end_x, end_y = basedf.loc[basedf['fid'] == row['end_id'], ['X', 'Y']].iloc[0]
            end_id_nearest = find_nearest_point_id(end_x, end_y, df)

        start_id_nearest = find_nearest_point_id(start_x, start_y, df) if row['start_id'] != 0 else 0

        new_start_end_ids.append({'start_id': start_id_nearest, 'end_id': end_id_nearest})

    # 新しいIDの組み合わせをDataFrameに変換し、CSVファイルとして出力
    new_start_end_df = pd.DataFrame(new_start_end_ids)
    
    return new_start_end_df