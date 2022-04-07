import bebi103
import bokeh
import bokeh.io
import bokeh.plotting as bk
import numpy as np
from bokeh.models import Label

from codex.experiment import Codex
from codex.helper import DEFAULT_CHANNEL
from codex.quantify import quantify_segmentation


def interactive_tile(
    experiment: Codex,
    x: int,
    y: int,
    names: list = [DEFAULT_CHANNEL, "CD4", "CD8"],
    frame_height: int = 200,
    frame_width: int = 200,
    colorbar: bool = False,
    interpixel_distances: float = 0.377442,
    length_units: str = "μm",
    color_mapper=None,
    max_intensity: int = None,
    ncols: int = 4,
    raw_plots: bool = False,
):
    """Convenient function for showing two images side by side."""
    plots = []

    for i, name in enumerate(names):
        im = experiment.get_tile(x, y, name=name)

        p = bebi103.image.imshow(
            im,
            frame_height=im.shape[0] if frame_height is None else frame_height,
            frame_width=im.shape[1] if frame_width is None else frame_width,
            colorbar=colorbar,
            title=name if name is not None else "Hoechst",
            cmap=color_mapper,
            interpixel_distance=interpixel_distances
            if interpixel_distances is not None
            else 1.0,
            length_units=length_units,
            max_intensity=max_intensity[i]
            if max_intensity is not None
            else np.quantile(im, 0.99),
        )
        plots.append(p)

    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if raw_plots:
        return p

    return bokeh.io.show(bokeh.layouts.gridplot(plots, ncols=ncols))


def interactive_labeled_tile(
    experiment: Codex,
    x: int,
    y: int,
    names: list = [DEFAULT_CHANNEL, "BCL6", "Myc"],
    frame_height: int = 200,
    frame_width: int = 200,
    colorbar: bool = False,
    interpixel_distances: float = 1.0,
    length_units: str = "pixel",
    color_mapper=None,
    max_intensity: int = None,
    ncols: int = 4,
    quantify: bool = True,
    raw_plots: bool = False,
):
    """Convenient function for showing two images side by side."""
    plots = []
    if quantify:
        df = quantify_segmentation(experiment, x, y).reset_index()

    for i, name in enumerate(names):
        im = experiment.get_tile_overlay(x, y, name=name)

        p = bebi103.image.imshow(
            im,
            frame_height=im.shape[0] if frame_height is None else frame_height,
            frame_width=im.shape[1] if frame_width is None else frame_width,
            colorbar=colorbar,
            title=name if name is not None else "Hoechst",
            cmap=color_mapper,
            interpixel_distance=interpixel_distances
            if interpixel_distances is not None
            else 1.0,
            length_units=length_units,
            # max_intensity=max_intensity[i]
            # if max_intensity is not None
            # else np.quantile(im, 0.99),
        )
        if quantify:
            for i, row in df.iterrows():
                label = Label(
                    x=row["x"],
                    y=im.shape[1] - row["y"],
                    x_offset=-5,
                    y_offset=0,
                    text=f"{int(row['id'])}",
                    text_color="white",
                )
                p.add_layout(label)
        plots.append(p)

    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if raw_plots:
        return p

    return bokeh.io.show(bokeh.layouts.gridplot(plots, ncols=ncols))


def interactive_slide(
    experiment: Codex,
    xmin: int = 1000,
    xmax: int = 1200,
    ymin: int = 1000,
    ymax: int = 1200,
    names: list = [DEFAULT_CHANNEL],
    frame_height: int = 600,
    frame_width: int = 600,
    colorbar: bool = False,
    interpixel_distances: float = 0.377442,
    length_units: str = "μm",
    color_mapper=None,
    max_intensity: int = None,
    ncols: int = 4,
    raw_plots: bool = False,
):
    """Convenient function for showing two images side by side."""
    plots = []

    for i, name in enumerate(names):
        im_full = experiment.get_slide(name=name)
        im = im_full[xmin:xmax, ymin:ymax]

        p = bebi103.image.imshow(
            im,
            frame_height=im.shape[0] if frame_height is None else frame_height,
            frame_width=im.shape[1] if frame_width is None else frame_width,
            colorbar=colorbar,
            title=name if name is not None else "Hoechst",
            cmap=color_mapper,
            interpixel_distance=interpixel_distances
            if interpixel_distances is not None
            else 1.0,
            length_units=length_units,
            max_intensity=max_intensity[i]
            if max_intensity is not None
            else np.quantile(im, 0.99),
        )
        plots.append(p)

    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if raw_plots:
        return p

    return bokeh.io.show(bokeh.layouts.gridplot(plots, ncols=ncols))


def plot_hist(
    hist_bin, title, y_axis_type="linear", x_axis_type="linear", width=300, height=150
):
    """Make plot of image histogram."""
    p = bk.figure(
        plot_height=height,
        plot_width=width,
        x_axis_type=x_axis_type,
        y_axis_type=y_axis_type,
        x_axis_label="intensity",
        y_axis_label="count",
        title=title,
    )
    hist, bins = hist_bin
    p.line(bins, hist, line_width=2)
    return p


def interactive_labeled_slide(
    experiment: Codex,
    df,
    xmin: int = 1000,
    xmax: int = 1200,
    ymin: int = 1000,
    ymax: int = 1200,
    names: list = [DEFAULT_CHANNEL, "BCL6", "Myc"],
    frame_height: int = 200,
    frame_width: int = 200,
    colorbar: bool = False,
    interpixel_distances: float = 1.0,
    length_units: str = "pixel",
    color_mapper=None,
    max_intensity: int = None,
    ncols: int = 4,
    quantify: bool = True,
    raw_plots: bool = False,
):
    """Convenient function for showing two images side by side."""
    plots = []

    sub = df[(df.x > xmin) & (df.x < xmax) & (df.y > ymin) & (df.y < ymax)]

    for i, name in enumerate(names):
        im = experiment.get_slide(name=name)

        p = bebi103.image.imshow(
            im,
            frame_height=im.shape[0] if frame_height is None else frame_height,
            frame_width=im.shape[1] if frame_width is None else frame_width,
            colorbar=colorbar,
            title=name if name is not None else "Hoechst",
            cmap=color_mapper,
            interpixel_distance=interpixel_distances
            if interpixel_distances is not None
            else 1.0,
            length_units=length_units,
            # max_intensity=max_intensity[i]
            # if max_intensity is not None
            # else np.quantile(im, 0.99),
        )
        if quantify:
            for i, row in sub.iterrows():
                label = Label(
                    x=row["x"],
                    y=im.shape[1] - row["y"],
                    x_offset=-5,
                    y_offset=0,
                    text=f"{int(row['id'])}",
                    text_color="white",
                )
                p.add_layout(label)
        plots.append(p)

    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if raw_plots:
        return p

    return bokeh.io.show(bokeh.layouts.gridplot(plots, ncols=ncols))


def show_multiple_channels(
    im,
    channels=["BCL6", "Myc"],
    frame_height=200,
    frame_width=200,
    titles=None,
    interpixel_distances=None,
    color_mapper=None,
    max_intensity=None,
    subset=8,
    ncols=4,
    show_hoechst=True,
):
    """Convenient function for showing two images side by side."""
    if subset > 0:
        sub_r, sub_c = im.shape[-2] // subset, im.shape[-1] // subset
        im = im[..., :sub_r, :sub_c]

    plots = []

    if show_hoechst:
        p = bebi103.image.imshow(
            im[0, 0],
            frame_height=frame_height,
            frame_width=frame_width,
            colorbar=True,
            title="Hoechst",
            cmap=color_mapper,
            interpixel_distance=interpixel_distances[i]
            if interpixel_distances is not None
            else 1.0,
            length_units="pixels",
            max_intensity=max_intensity[i]
            if max_intensity is not None
            else np.quantile(im[0, 0], 0.99),
        )
        plots.append(p)

    for i, channel in enumerate(channels):
        p = bebi103.image.imshow(
            im[CHANNEL_NUM[channel], 1],
            frame_height=frame_height,
            frame_width=frame_width,
            colorbar=True,
            title=titles[i] if titles is not None else channel,
            cmap=color_mapper,
            interpixel_distance=interpixel_distances[i]
            if interpixel_distances is not None
            else 1.0,
            length_units="pixels",
            max_intensity=max_intensity[i]
            if max_intensity is not None
            else np.quantile(im[CHANNEL_NUM[channel], 1], 0.99),
        )
        plots.append(p)

    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    return bokeh.layouts.gridplot(plots, ncols=ncols)


def show_mult_ims(
    ims,
    cbar=True,
    titles=None,
    frame_height=100,
    frame_width=100,
    interpixel_distances=[1.0, 1.0],
    color_mapper=None,
    max_intensity=[None, None],
    ncols=4,
):
    """Convenient function for showing two images side by side."""

    plots = []
    for i, im in enumerate(ims):
        p_1 = bebi103.image.imshow(
            im,
            frame_height=frame_height,
            frame_width=frame_width,
            colorbar=False,
            title=titles[i] if titles is not None else f"Im {i}",
            cmap=color_mapper,
            interpixel_distance=1,
            length_units="pixels",
        )
        plots.append(p_1)

    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    return bokeh.layouts.gridplot(plots, ncols=ncols)
