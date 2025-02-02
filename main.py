# main.py
import pandas as pd
from config.handler import ConfigHandler
from module.preprocessing import process_input_data
from module.paddydam import mapping, find_closest_channel_optimized
from module.associate import association, process_nearest_ids
from module.rakusui import process_multiple_routes
def main():
    # 設定の読み込み（config.ymlのパスを指定）
    try:
        config = ConfigHandler("config/config.yml")
    except FileNotFoundError as e:
        print(f"Error loading configuration: {e}")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return
    
    # 前処理の実行
    print('Starting preprocessing...')
    try:
        _, _ = process_input_data(config)
        print('Preprocessing done')
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return
    
    try:
        # メインの処理フロー
        format_df, sorted_unique_paddy_ids = mapping(
            config.get_path('mesh_data'),
            'paddyid'
        )
        print('Mapping done')
        
        # 落水線ポイントの読み込み
        rakusui_df = pd.read_csv(config.get_path('rakusui_points'))
        
        # channel_idが1の行を抽出
        channel_rows = format_df[format_df['rakusui'] == 1]
        
        # 最も近いchannel_idを見つける
        new_rows = find_closest_channel_optimized(
            format_df,
            sorted_unique_paddy_ids,
            channel_rows
        )
        print('Find closest channel optimized done')
        
        # 新しい行の情報を含むDataFrameを作成
        pqout_df = pd.DataFrame(new_rows)
        
        # 関連付け処理
        start_end_df, pqout_df = association(format_df, pqout_df)
        print('Association done')
        
        rakusui_start_end_df = process_nearest_ids(
            rakusui_df,
            format_df,
            start_end_df
        )
        
        # 落水処理
        opt_path_df = process_multiple_routes(
            rakusui_start_end_df,
            rakusui_df
        )
        print('Process multiple routes done')
        
        # 結果の結合と出力
        merged_df = pd.merge(
            pqout_df,
            opt_path_df,
            left_index=True,
            right_index=True
        )
        cols = [
            'paddy_id',
            'mesh_rakusui',
            'mesh_paddy',
            'dist',
            'orifice',
            'drn_id',
            'total_distance'
        ]
        comp_df = merged_df[cols]
        
        # 結果の保存
        final_output_path = config.get_path('final_output')
        comp_df.to_csv(final_output_path, index=False)
        print(f'Results saved to {final_output_path}')
        
    except Exception as e:
        print(f"Error during processing: {e}")
        return

if __name__ == "__main__":
    main()