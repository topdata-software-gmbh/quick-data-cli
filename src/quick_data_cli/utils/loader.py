import pandas as pd
from pathlib import Path
from typing import Union


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    suffix = p.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(p)
    elif suffix == ".json":
        df = pd.read_json(p)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    return df
