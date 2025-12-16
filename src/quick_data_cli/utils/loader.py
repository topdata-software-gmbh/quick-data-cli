import pandas as pd
import csv
from pathlib import Path
from typing import Union, Optional


def _detect_csv_separator(p: Path) -> Optional[str]:
    with p.open("r", encoding="utf-8", errors="replace") as f:
        sample = f.read(65536)
    lines = [ln for ln in sample.splitlines() if ln.strip()]
    if lines:
        header = lines[0]
        candidates = [";", ",", "\t", "|"]
        counts = {c: header.count(c) for c in candidates}
        best = max(counts, key=counts.get)
        if counts[best] > 0:
            return best
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t,|")
        return dialect.delimiter
    except Exception:
        return None


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    suffix = p.suffix.lower()
    if suffix == ".csv":
        sep = _detect_csv_separator(p)
        if sep is None:
            df = pd.read_csv(p)
        else:
            df = pd.read_csv(p, sep=sep)
    elif suffix == ".json":
        df = pd.read_json(p)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    return df
