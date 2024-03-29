from typing import Union

import matplotlib.pyplot as plt
from stardist.plot import render_label

from codex.experiment import Codex
from codex.helper import DEFAULT_CHANNEL, DEFAULT_SEGMENTATION


def plot_labeled_slide(
    experiment,
    df,
    cell_filter=None,
    xlim=[1000, 1200],
    ylim=[1000, 1200],
    preprocess=lambda x: x,
    annotate=True,
    ax=None,
):
    full_slide = preprocess(experiment.get_slide()).copy()
    segmentation = experiment.get_slide(DEFAULT_SEGMENTATION).copy()
    if ax is None:
        fig = plt.figure(figsize=(24, 24))
        ax = plt.gca()

    cell_ids = []
    if cell_filter is not None:
        sub = df[cell_filter]
        sub_border = df[~cell_filter]
    else:
        sub = df
        sub_border = df

    sub = sub[
        (sub.x < xlim[1]) & (sub.x > xlim[0]) & (sub.y < ylim[1]) & (sub.y > ylim[0])
    ]
    sub_border = sub_border[
        (sub_border.x < xlim[1])
        & (sub_border.x > xlim[0])
        & (sub_border.y < ylim[1])
        & (sub_border.y > ylim[0])
    ]

    if annotate:
        for i, row in sub.iterrows():
            ax.text(row["x"], row["y"], s=f"{int(row['id'])}", color="w")
            cell_ids.append(int(row["id"]))
        # segmentation[segmentation==row['id']] = 0

    sub_pic = segmentation[xlim[0] : xlim[1], ylim[0] : ylim[1]]

    # print(sub_pic[sub_pic>0].min(), sub_pic.max())
    if cell_filter is not None:
        for i, row in sub_border.iterrows():
            # print(row['id'])
            segmentation[segmentation == row["id"]] = 0

    labeled = render_label(segmentation, full_slide)
    ax.imshow(labeled)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    return ax


# def show_slide(
#     experiment: Codex,
#     name: Union[None, str] = None,
#     ax: Union[None, plt.Axes] = None,
# ) -> plt.Axes:
#     """
#     Plots a slide.
#     """
#     slide = experiment.get_slide(name)

#     if ax is None:
#         fig, ax = plt.subplots()

#     ax.imshow(slide)
#     return ax


# def show_tile(
#     experiment: Codex,
#     x: int,
#     y: int,
#     name: Union[None, str] = None,
#     ax: plt.Axes = None,
# ) -> plt.Axes:
#     """
#     Plots a tile.
#     """
#     tile = experiment.get_tile(
#         x, y, name
#     )  # cv2.imread(self[name][(i, j) if name is None else (j, i)], -1)
#     if ax is None:
#         fig, ax = plt.subplots()
#     ax.imshow(tile)
#     ax.set_title(name if name is not None else "original")
#     return ax


# def show_labeled_tile(
#     experiment: Codex,
#     x: int,
#     y: int,
#     name: Union[None, str] = "lgbm_test_sub2",
#     original: Union[None, np.ndarray] = None,
#     ax: plt.Axes = None,
# ):
#     """
#     Plots a tile and overlays cell predictions.
#     """
#     im = experiment.get_tile_overlay(x, y, original, name)

#     if ax is None:
#         fig, ax = plt.subplots()

#     ax.imshow(im)
#     return ax


def plot_tiles_on_slide(
    experiment: Codex, name: Union[None, str] = DEFAULT_CHANNEL, ax: plt.Axes = None,
) -> plt.Axes:
    """
    Plots the full slide with all slides.
    """
    slide = experiment.get_slide(name)
    tile_loc = [k for k in experiment[name].keys()]

    if ax is None:
        fig, ax = plt.subplots()

    ax.imshow(slide)
    for i, j in tile_loc:
        tile = experiment.get_tile(
            i, j, name
        )  # cv2.imread(self[name][(i, j) if name is None else (j, i)], -1)
        x = i * tile.shape[0], (i + 1) * tile.shape[0]
        y = j * tile.shape[1], (j + 1) * tile.shape[1]
        # print(x, y)
        # ax.axvline(y[0], color='w')
        ax.vlines(x, y[0], y[1], color="w")
        ax.hlines(y, x[0], x[1], color="w")
        ax.text(
            (2 * i + 1) * (x[1] - x[0]) / 2,
            (2 * j + 1) * (y[1] - y[0]) / 2,
            s=f"{i},{j}",
            color="w",
            ha="center",
            va="center",
        )

    ax.set_xlim([0, slide.shape[1]])
    ax.set_ylim([slide.shape[0], 0])

    return ax


def plot_tile_location(
    experiment: Codex,
    x: int,
    y: int,
    name: Union[None, str] = DEFAULT_CHANNEL,
    ax: plt.Axes = None,
) -> plt.Axes:
    """
    Plots the full slide highlighting the slide at (x, y).
    """
    slide = experiment.get_slide(name)
    tile = experiment.get_tile(x, y, name)
    xx = x * tile.shape[0], (x + 1) * tile.shape[0]
    yy = y * tile.shape[1], (y + 1) * tile.shape[1]

    if ax is None:
        fig, ax = plt.subplots()

    ax.imshow(slide)
    ax.vlines(xx, yy[0], yy[1], color="w")
    ax.hlines(yy, xx[0], xx[1], color="w")
    ax.set_xlim(
        [0, slide.shape[1],]
    )
    ax.set_ylim([slide.shape[0], 0])

    return ax
