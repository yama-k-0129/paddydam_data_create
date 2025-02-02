# config_handler.py
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigHandler:
    def __init__(self, config_path: str = "config.yml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # ベースディレクトリのPath objectを作成
        self.input_base = Path(self.config['paths']['input']['base_dir'])
        self.output_base = Path(self.config['paths']['output']['base_dir'])
        
        # 完全なパスを構築
        self.paths = self._build_paths()
        
        # パスの検証
        self.validate_paths()

    def _build_paths(self) -> Dict[str, Path]:
        """完全なファイルパスを構築"""
        return {
            'mesh': self.input_base / self.config['paths']['input']['mesh'],
            'paddy': self.input_base / self.config['paths']['input']['paddy'],
            'catchment': self.input_base / self.config['paths']['input']['catchment'],
            'raster': self.input_base / self.config['paths']['input']['raster'],
            'mesh_data': self.output_base / self.config['paths']['output']['mesh_data'],
            'rakusui_points': self.output_base / self.config['paths']['output']['rakusui_points'],
            'final_output': self.output_base / self.config['paths']['output']['final_output']
        }

    def validate_paths(self) -> None:
        """入力ファイルの存在確認とoutputディレクトリの作成"""
        # 入力ファイルの確認
        input_files = [
            self.paths['mesh'],
            self.paths['paddy'],
            self.paths['catchment'],
            self.paths['raster']
        ]
        
        missing_files = [str(path) for path in input_files if not path.exists()]
        if missing_files:
            raise FileNotFoundError(f"Required input files not found: {', '.join(missing_files)}")
        
        # 出力ディレクトリの作成
        self.output_base.mkdir(parents=True, exist_ok=True)

    def get_path(self, key: str) -> Path:
        """パスを取得"""
        return self.paths[key]

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """設定パラメータを取得"""
        return self.config.get('parameters', {}).get(key, default)