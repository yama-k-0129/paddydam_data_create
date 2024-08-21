import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

def find_path_with_kdtree(df, start_fid, end_fid, max_distance=30):
    # start_fid と end_fid の順序を保証
    min_fid, max_fid = min(start_fid, end_fid), max(start_fid, end_fid)
    path_df = df[(df['fid'] >= min_fid) & (df['fid'] <= max_fid)].sort_values(by='fid').reset_index(drop=True)
    
    if path_df.empty:
        return None, "No valid path found (check FID range)"

    coords = path_df[['X', 'Y']].values
    tree = cKDTree(coords)

    # start_fid および end_fid が存在するか確認
    if start_fid not in path_df['fid'].values or end_fid not in path_df['fid'].values:
        return None, "Start or end FID not found in the data"

    current_idx = path_df[path_df['fid'] == start_fid].index[0]
    end_idx = path_df[path_df['fid'] == end_fid].index[0]
    path_indices = [current_idx]
    total_distance = 0

    while current_idx != end_idx:
        current_point = coords[current_idx]
        distances, indices = tree.query(current_point, k=len(path_df), distance_upper_bound=max_distance)

        filtered_indices = [i for i, d in zip(indices, distances) if d != np.inf and i not in path_indices]
        if not filtered_indices:
            max_distance += 5
            continue

        next_idx = filtered_indices[0]
        next_distance = distances[np.where(indices == next_idx)[0][0]]

        path_indices.append(next_idx)
        total_distance += next_distance
        current_idx = next_idx

    # path_indices を使用して正確な fid を参照
    formatted_ids = ' or '.join(f'"fid" = {float(path_df.loc[path_df.index[idx], "fid"])}' for idx in path_indices)
    return total_distance, formatted_ids

def process_multiple_routes(df_routes, df_points):
    results = []

    for _, row in df_routes.iterrows():
        #print(f'Processing {_ + 1}/{len(df_routes)} rows...')
        start_id, end_id = row['start_id'], row['end_id']
        total_distance, route = find_path_with_kdtree(df_points, start_id, end_id)
        if total_distance is None:
            print(f"Route from {start_id} to {end_id} could not be computed: {route}")
            continue
        results.append([start_id, end_id, total_distance, route])

    df_results = pd.DataFrame(results, columns=['start_id', 'end_id', 'total_distance', 'route'])
    return df_results

