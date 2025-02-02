# module/preprocessing.py
import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import Point
import pandas as pd

def process_input_data(config):
    """
    入力データの処理を行う関数（旧MK_input.pyの機能）
    """
    # データ読み込み
    mesh_gdf = gpd.read_file(config.get_path('mesh'))
    paddy_gdf = gpd.read_file(config.get_path('paddy'), encoding='utf-8')
    catchment_gdf = gpd.read_file(config.get_path('catchment'))
    raster = rasterio.open(config.get_path('raster'))
    
    # ラスタデータから重心を計算
    centroids = _calculate_centroids(raster)
    centroids_gdf = gpd.GeoDataFrame(centroids, crs=raster.crs)
    
    # 既存の index_left や index_right 列を削除
    for df in [centroids_gdf, mesh_gdf, paddy_gdf, catchment_gdf]:
        if 'index_left' in df.columns:
            df.drop(columns=['index_left'], inplace=True)
        if 'index_right' in df.columns:
            df.drop(columns=['index_right'], inplace=True)
    
    # 空間結合処理
    result_df, centroids_with_drn = _perform_spatial_joins(
        centroids_gdf, mesh_gdf, paddy_gdf, catchment_gdf, raster
    )
    
    # 'no'列を'fid'列に変更
    result_df = result_df.rename(columns={'no': 'fid'})
    centroids_with_drn = centroids_with_drn.rename(columns={'no': 'fid'})
    
    # 結果をCSVに出力
    result_df[['fid', 'X', 'Y', 'paddyid', 'rakusui', 'drn_id']].to_csv(
        config.get_path('mesh_data'), index=False, na_rep=''
    )
    centroids_with_drn[['fid', 'X', 'Y', 'drn_id', 'value']].to_csv(
        config.get_path('rakusui_points'), index=False
    )
    
    return result_df, centroids_with_drn

def _calculate_centroids(raster):
    """ラスタデータから重心を計算する補助関数"""
    mask = raster.read(1)
    transform = raster.transform
    centroids = []
    
    for row, col_data in enumerate(mask):
        for col, value in enumerate(col_data):
            if value != raster.nodata:
                x, y = transform * (col + 0.5, row + 0.5)
                centroids.append({
                    'geometry': Point(x, y),
                    'X': x,
                    'Y': y,
                    'value': value,
                    'no': len(centroids) + 1  # このままnoとして追加
                })
    
    return centroids

def _perform_spatial_joins(centroids_gdf, mesh_gdf, paddy_gdf, catchment_gdf, raster):
    """空間結合処理を行う補助関数"""
    # メッシュの重心計算
    mesh_gdf['centroid'] = mesh_gdf.geometry.centroid
    mesh_gdf['X'] = mesh_gdf.centroid.x
    mesh_gdf['Y'] = mesh_gdf.centroid.y
    
    # 空間結合処理
    centroids_with_drn = gpd.sjoin(
        centroids_gdf,
        catchment_gdf[['geometry', 'drn_id']],
        how="left",
        predicate='intersects'
    )
    
    # index_left と index_right を削除
    if 'index_right' in centroids_with_drn.columns:
        centroids_with_drn.drop(columns=['index_right'], inplace=True)
    
    mesh_with_centroid = mesh_gdf.set_geometry('centroid')
    centroids_with_paddy = gpd.sjoin(
        mesh_with_centroid,
        paddy_gdf[['geometry', 'polygon_uu']],
        how="left",
        predicate='intersects'
    )
    
    # index_left と index_right を削除
    if 'index_right' in centroids_with_paddy.columns:
        centroids_with_paddy.drop(columns=['index_right'], inplace=True)
    
    centroids_with_paddy['paddyid'] = centroids_with_paddy['polygon_uu']
    
    # 最終的な空間結合
    result_df = gpd.sjoin(
        centroids_with_paddy,
        catchment_gdf[['geometry', 'drn_id']],
        how="left",
        predicate='intersects'
    )
    
    # index_left と index_right を削除
    if 'index_right' in result_df.columns:
        result_df.drop(columns=['index_right'], inplace=True)
    
    # ラスタ値の抽出
    coords = [(x, y) for x, y in zip(result_df['X'], result_df['Y'])]
    raster_values = np.array([x[0] for x in raster.sample(coords)])
    result_df['rakusui'] = np.where(raster_values == raster.nodata, np.nan, raster_values)
    
    return result_df, centroids_with_drn