import os
from typing import Callable, List, Union

import cv2
import numpy as np
import pandas as pd
import scipy.ndimage
from tqdm import tqdm

from codex.experiment import Codex
from codex.helper import CHANNEL_NUM, DEFAULT_CHANNEL


def get_x_and_y(name):
    x, y = os.path.splitext(name)[0].split("_")[-2:]
    return int(x), int(y)


def position(img: np.ndarray, **kwargs):
    y, x = scipy.ndimage.measurements.center_of_mass(img)
    return {"x": x, "y": y}


def size(img: np.ndarray, **kwargs):
    return {"size": img.sum()}


def intensity(img: np.ndarray, **kwargs):
    orig = kwargs["original"]
    channel = kwargs.get("channel", "")
    cell_pixels = orig[img]
    return {
        f"{channel} mean".lstrip(): cell_pixels.mean(),
        f"{channel} std".lstrip(): cell_pixels.std(),
        f"{channel} sum".lstrip(): cell_pixels.sum(),
    }


def ellipse(img, **kwargs):
    contours, hierarchy = cv2.findContours(
        img.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    has_ellipse = len(contours) > 0 and contours[0].shape[0] >= 5
    if has_ellipse:
        cnt = contours[0]
        ellipse_center, axles, angle = cv2.fitEllipse(cnt)
        return {
            "ellipse": 1,
            "cx": ellipse_center[0],
            "cy": ellipse_center[1],
            "major": axles[0],
            "minor": axles[1],
            "angle": angle,
        }
    return {"ellipse": 0, "cx": 0, "cy": 0, "major": 0, "minor": 0, "angle": 0}


def border(img, **kwargs):
    top = (np.any(img[0])).astype(int)
    bottom = (np.any(img[-1])).astype(int)
    left = (np.any(img[:, 0])).astype(int)
    right = (np.any(img[:, -1])).astype(int)
    border = np.any(np.array([top, bottom, left, right]) == 1).astype(int)
    return {
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right,
        "border": border,
    }


def quantify_segmentation(
    experiment: Codex,
    x: Union[None, int] = None,
    y: Union[None, int] = None,
    name: Union[None, str] = DEFAULT_CHANNEL,
    funcs: List[Callable] = [position, size, ellipse, border],
    segmentation: str = "lgbm_test_sub2",
    channels: bool = False,
):
    if x is None and y is None:
        segmentation = experiment.get_slide(segmentation)
        original = experiment.get_slide()
    else:
        segmentation = experiment.get_tile(x, y, segmentation)
        original = experiment.get_tile(x, y)

    data = []

    for i in tqdm(range(1, segmentation.max() + 1)):
        img = segmentation == i
        data_dict = {"id": int(i)}

        for func in funcs:
            out = func(img, original=original)
            data_dict.update(out)
        if channels:
            channel_dict = {}
            for channel in CHANNEL_NUM.keys():
                if x is None and y is None:
                    channel_img = experiment.get_slide(name=channel)
                else:
                    channel_img = experiment.get_tile(x, y, name=channel)
                channel_out = intensity(img, original=channel_img, channel=channel)
                channel_dict.update(channel_out)
            data_dict.update(channel_dict)

        data.append(data_dict)

    data = pd.DataFrame(data)

    return data
