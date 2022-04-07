import os

import cv2
from skimage.io import imread

from codex.experiment import Codex
from codex.helper import IMG_FULL, crop_tma


def clahe(img):
    # print('Applying clahe')
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(12, 12))
    return clahe.apply(img)


def load_all_tma(tma):
    current_tma = ""
    codex_slides = {}

    for i, row in tma.iterrows():
        # print(f"{row['TMA']}_{row['Row']}{row['Col']}")
        if row["TMA"] != current_tma:
            # print(f"Loading {cd.IMG_FULL[row['TMA']]}.")
            img = imread(IMG_FULL[row["TMA"]])
            current_tma = row["TMA"]

        codex_slides[f"{row['TMA']}_{row['Row']}{row['Col']}"] = crop_tma(
            img, row["Row"], row["Col"], nrows=row["Nrows"], ncols=row["Ncols"]
        )

    segmentation = {}

    for i, row in tma.iterrows():
        # print(f"{row['TMA']}_{row['Row']}{row['Col']}")
        seg_path = os.path.join(
            f"/home/voehring/voehring/conda/segmentation/{row['TMA']}_{row['Row']}{row['Col']}_128"
        )
        segmentation[f"{row['TMA']}_{row['Row']}{row['Col']}"] = Codex(
            seg_path, codex_slides[f"{row['TMA']}_{row['Row']}{row['Col']}"]
        )

    return codex_slides, segmentation
