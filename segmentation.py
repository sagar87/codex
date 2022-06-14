import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from skimage.io import imread
from stardist.plot import render_label

from codex.helper import CHANNEL_NUM, TMA
from codex.util import load_raw_tma

COLORS = [
    "#000000",
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#9a6324",
    "#fffac8",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#000075",
    "#808080",
    "#ffffff",
]


def load_tma(name, path="/g/huber/projects/CITEseq/CODEX/TIFs"):
    return load_raw_tma(
        TMA.assign(
            name=lambda tma: tma.apply(
                lambda df: f"{df['TMA']}_{df['Row']}{df['Col']}", 1
            )
        ).loc[lambda df: df["name"] == name],
        path,
    )


def load_segmentation(name, path="/g/huber/projects/CITEseq/CODEX/stardist/masks"):
    name_splitted = name.split("_")
    return imread(
        f'{path}/{name}labels.tif'
    )


def load_quantification(name, path="/g/huber/projects/CITEseq/CODEX/stardist/tables"):
    return pd.read_csv(
        f"{path}/{name}.csv",
        index_col=0,
    )


def label_segmentation_mask(segmentation, annotation, type_col="type", id_col="id"):
    """
    Relabels a segmentation according to the annotations df (contains the columns type, cell).
    """
    labeled_segmentation = segmentation.copy()
    cell_types = annotation.loc[:, type_col].values.astype(int)
    cell_ids = annotation.loc[:, id_col].values

    if 0 in cell_types:
        cell_types += 1

    for t in np.unique(cell_types):
        mask = np.isin(segmentation, cell_ids[cell_types == t])
        labeled_segmentation[mask] = t

    # remove cells that are not indexed
    neg_mask = ~np.isin(segmentation, cell_ids)
    labeled_segmentation[neg_mask] = 0

    return labeled_segmentation


def label_cells(raw_image, labeled_segmentation, cmap, **kwargs):
    return render_label(labeled_segmentation, img=raw_image, cmap=cmap, **kwargs)


def generate_cmap(num_cell_types, colors=COLORS, labels=None):
    cmap = ListedColormap(colors, N=num_cell_types)
    if labels is None:
        labels = ["BG"] + [f"Cell type {i}" for i in range(num_cell_types)]

    legend_elements = [
        Line2D(
            [0], [0], marker="o", color="w", label=t, markerfacecolor=c, markersize=15
        )
        for c, t in zip(colors, labels)
    ]
    return cmap, legend_elements

def draw_box(ax, xlim=[2800, 3200], ylim=[1500, 2000], linewidth=2):
    ax.hlines(xmin=xlim[0], xmax=xlim[1], y=ylim[0], color='w', linewidth=linewidth)
    ax.hlines(xmin=xlim[0], xmax=xlim[1], y=ylim[1], color='w', linewidth=linewidth)
    ax.vlines(ymin=ylim[0], ymax=ylim[1], x=xlim[0], color='w', linewidth=linewidth)
    ax.vlines(ymin=ylim[0], ymax=ylim[1], x=xlim[1], color='w', linewidth=linewidth)

class DataLoader:
    def __init__(self, name):
        self.name = name
        self.image = load_tma(name)[name]
        self.segmentation = load_segmentation(name)
        self.quantification = load_quantification(name)


class CodexVis:
    def __init__(
        self,
        data,
        annotation,
        id_col="id",
        type_col="leiden_0.5_z_normal",
        colors=COLORS,
        labels=None,
        alpha=0.8,
    ):
        self.data = data
        self.type_col = type_col
        self.id_col = id_col

        self.annotation = self.data.quantification.merge(
            annotation, left_on="id", right_on=self.id_col, how="right"
        )
        self.labeled_segmentation = label_segmentation_mask(
            self.data.segmentation, self.annotation, self.type_col, self.id_col
        )
        self.cmap, self.legend = generate_cmap(
            self.labeled_segmentation.max() + 1, colors=colors, labels=labels
        )
        self.labeled_image = label_cells(
            self.data.image[0, 0], self.labeled_segmentation, self.cmap, alpha=alpha
        )

    def show(
        self,
        name,
        type_segmentation=True,
        xlim=[1000, 1200],
        ylim=[1000, 1200],
        cell_filter=None,
        annotate=True,
        annotate_func=lambda row: int(row["id"]),
        origin="lower",
        highlight=[],
        axis_off=False,
        ax=None,
    ):
        if ax is None:
            fig = plt.figure(figsize=(24, 24))
            ax = plt.gca()

        cell_ids = []
        if cell_filter is not None:
            sub = self.annotation[cell_filter]

        else:
            sub = self.annotation

        sub = sub[
            (sub.x < xlim[1])
            & (sub.x > xlim[0])
            & (sub.y < ylim[1])
            & (sub.y > ylim[0])
        ]

        if annotate:
            for i, row in sub.iterrows():
                cell_id = int(row["id"])
                if cell_id in highlight:
                    ax.text(
                        row["x"],
                        row["y"],
                        s=f"{annotate_func(row)}",
                        color="w",
                        fontsize=16,
                        fontweight="bold",
                    )                    
                else:
                    ax.text(
                        row["x"],
                        row["y"],
                        s=f"{annotate_func(row)}",
                        color="w",
                        fontsize=12,
                    )

                cell_ids.append(cell_id)

        if type_segmentation:
            labeled = render_label(
                self.labeled_segmentation,
                img=self.data.image[CHANNEL_NUM[name], 0 if name == "Hoechst" else 1],
                cmap=self.cmap,
            )
        else:
            labeled = render_label(
                self.data.segmentation,
                img=self.data.image[CHANNEL_NUM[name], 0 if name == "Hoechst" else 1],
                cmap=self.cmap,
            ) 

        ax.imshow(labeled, origin=origin)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.legend(handles=self.legend, fontsize=16, framealpha=1)

        if axis_off:
            ax.axis("off")

        return fig, ax, labeled
