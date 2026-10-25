"""Собирает разметку 300W из .pts в один CSV.

Запуск из корня репозитория:
    python src/facekp/data/make_csv.py
"""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import pandas as pd
from PIL import Image

N_POINTS = 68


def read_pts(path: Path) -> list[float]:
    # формат .pts: шапка, потом 68 строк "x y" между { и }
    lines = path.read_text().splitlines()
    start = lines.index("{") + 1
    end = lines.index("}")
    coords = [tuple(map(float, l.split())) for l in lines[start:end]]
    if len(coords) != N_POINTS:
        raise ValueError(f"{path.name}: {len(coords)} точек вместо {N_POINTS}")
    return [c for xy in coords for c in xy]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="data/raw/300w", help="папка с 01_Indoor и 02_Outdoor")
    ap.add_argument("--out", default="data/raw/landmarks_300w.csv")
    args = ap.parse_args()

    src = Path(args.src)
    rows = []
    for pts in sorted(src.rglob("*.pts")):
        img = pts.with_suffix(".png")
        if not img.exists():
            print(f"нет картинки для {pts.name}, пропускаю")
            continue
        with Image.open(img) as im:  # читает только заголовок, быстро
            w, h = im.size
        rows.append(
            [img.relative_to(src).as_posix(), pts.parent.name.split("_")[-1].lower(), w, h]
            + read_pts(pts)
        )

    cols = ["image", "subset", "width", "height"]
    for i in range(1, N_POINTS + 1):  # нумерация с 1, как в описании 300W
        cols += [f"x{i}", f"y{i}"]
    df = pd.DataFrame(rows, columns=cols)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    # файл-описание для версионного контроля
    manifest = {
        "file": out.name,
        "rows": len(df),
        "sha256": sha256(out),
        "source": "https://ibug.doc.ic.ac.uk/resources/300-W/",
        "created": date.today().isoformat(),
    }
    out.with_suffix(".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

    print(f"готово: {len(df)} строк -> {out}")
    print(df["subset"].value_counts().to_string())


if __name__ == "__main__":
    main()
