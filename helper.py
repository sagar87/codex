import os
from glob import glob

import pandas as pd
from skimage.io import imread

CODEX_FOLDER = "/home/voehring/voehring/projects/2022-02-18_codex"
IMG_PATH_FULL = "/g/huber/projects/CITEseq/CODEX/TIFs/"
IMG_PATH_DOWN = "/g/huber/projects/CITEseq/CODEX/TIFs_downsized"
RESOLUTION = 0.377442  # micron
# downsized paths
IMG_FULL = {
    p.split("/")[-1].split(".")[0]: p
    for p in glob(os.path.join(IMG_PATH_FULL, "*.tif"))
}
IMG_DOWN = {
    p.split("/")[-1].split(".")[0]: p
    for p in glob(os.path.join(IMG_PATH_DOWN, "*.tif"))
}

channels_full = (
    pd.read_csv(os.path.join(CODEX_FOLDER, "channelnames.txt"), header=None)
    .assign(dim0=lambda df: [i for i in range(int(df.shape[0] / 2))] * 2)
    .assign(dim1=lambda df: [0, 1] * int(df.shape[0] / 2))
    .rename(columns={0: "marker"})
)

CHANNELS = pd.read_csv(
    os.path.join(CODEX_FOLDER, "channelnames_ch2.txt"), header=None
).rename(columns={0: "marker"})

ANNOTATIONS = pd.read_csv(
    os.path.join(CODEX_FOLDER, "CODEX_panel_TMA_191.csv"), sep=";", skiprows=2
).drop(columns="Unnamed: 15")

META = (
    pd.read_csv(
        os.path.join(CODEX_FOLDER, "Daten 191_191_1-5-Table 1.csv"), sep=";", header=1
    )
    .rename(
        columns={
            "TMA-Nr/\nAnzahl": "tma_n",
            "TMA-Position": "tma_dim0",
            "Unnamed: 2": "tma_dim1",
            "Unnamed: 3": "patient_id",
            "Histo-Nr ": "histo",
            "Eingangs-\ndatum": "date",
            "Lokalisation": "loc",
            "Diagnose": "entity",
            "Diagnose_lang": "diagnosis",
            "Geschlecht": "sex",
            "Alter": "age",
        }
    )
    .assign(tma_n=lambda df: df["tma_n"].fillna(method="ffill"))
    .assign(date=lambda df: df["date"].fillna(method="ffill"))
    .assign(loc=lambda df: df["loc"].fillna(method="ffill"))
    .assign(entity=lambda df: df["entity"].fillna(method="ffill"))
    .assign(diagnosis=lambda df: df["diagnosis"].fillna(method="ffill"))
    .assign(sex=lambda df: df["sex"].fillna(method="ffill"))
    .assign(age=lambda df: df["age"].fillna(method="ffill"))
    .dropna()
)

TMA = pd.read_csv(
    "/home/voehring/voehring/projects/2022-02-18_codex/Montage_key-Table 1.csv", sep=";"
).iloc[:, :11]


DEFAULT_CHANNEL = "Hoechst"
NUM_CHANNEL = {i: marker for i, marker in enumerate(CHANNELS.marker.tolist())}
CHANNEL_NUM = {marker: i for i, marker in enumerate(CHANNELS.marker.tolist())}
CHANNEL_NUM[DEFAULT_CHANNEL] = 0


def crop_tma(img, row=0, col=0, nrows=3, ncols=2):
    v_size, h_size = int(img.shape[-2] / nrows), int(img.shape[-1] / ncols)
    return img[
        ..., row * v_size : (row + 1) * v_size, col * h_size : (col + 1) * h_size
    ]


def load_tma(tma):
    path = IMG_FULL[TMA.iloc[tma].loc["TMA"]]
    img = imread(path)
    return crop_tma(
        img,
        TMA.iloc[tma].loc["Row"],
        TMA.iloc[tma].loc["Col"],
        nrows=TMA.iloc[tma].loc["Nrows"],
        ncols=TMA.iloc[tma].loc["Ncols"],
    )
