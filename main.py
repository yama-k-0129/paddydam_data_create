import pandas as pd
from module.paddydam import mapping, find_closest_channel_optimized
from module.associate import association, process_nearest_ids
from module.rakusui import process_multiple_routes

csv_path = 'input/mesh_data.csv'
id_column = 'paddyid'
rakusui_df = pd.read_csv('input/等間隔落水線ポイント.csv')

# paddydam.py
format_df, sorted_unique_paddy_ids = mapping(csv_path, id_column)
print('mapping done')
# channel_idが1の行を抽出
channel_rows = format_df[format_df['rakusui'] == 1]
# 最も近いchannel_idを見つけ、新しい行をリストに追加
new_rows = find_closest_channel_optimized(format_df, sorted_unique_paddy_ids, channel_rows)
print('find_closest_channel_optimized done')
# 新しい行の情報を含むDataFrameを作成
pqout_df = pd.DataFrame(new_rows)



#associate.py
start_end_df, pqout_df = association(format_df, pqout_df)
print('association done')
rakusui_start_end_df = process_nearest_ids(rakusui_df, format_df, start_end_df)


# rakusui.py
opt_path_df = process_multiple_routes(rakusui_start_end_df, rakusui_df)
print('process_multiple_routes done')



# format_dfとopt_path_dfを結合
merged_df = pd.merge(pqout_df, opt_path_df, left_index=True, right_index=True)
# 指定された列のみ抜き出し
cols = ['paddy_id', 'mesh_rakusui', 'mesh_paddy', 'dist', 'orifice', 'drn_id', 'total_distance']
comp_df = merged_df[cols]
# comp_dfを保存
comp_df.to_csv('pqout.csv', index=False)


