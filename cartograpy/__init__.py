import dataclasses
import os

import numpy as np
import wx

from wx.lib.newevent import NewEvent


IMAGE_WILDCARD = "All files (*)|*|BMP files (*.bmp)|*.bmp|JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"


ROOT_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(ROOT_DIR, "assets")


ALL_EXPAND = wx.ALL | wx.EXPAND


LayerAddEvent, EVT_LAYER_ADD = NewEvent()
LayerBackwardEvent, EVT_LAYER_BACKWARD = NewEvent()
LayerDuplicateEvent, EVT_LAYER_DUPLICATE = NewEvent()
LayerForwardEvent, EVT_LAYER_FORWARD = NewEvent()
LayerRemoveEvent, EVT_LAYER_REMOVE = NewEvent()
SwapLayerEvent, EVT_SWAP_LAYER = NewEvent()
UpdateLayerEvent, EVT_UPDATE_LAYER = NewEvent()
UpdateVisibilityEvent, EVT_UPDATE_VISIBILITY = NewEvent()


@dataclasses.dataclass
class Rect:
    """Represents a rectangle."""
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
        }


class Rects:
    """Represents a group of rectangles.

    This class uses numpy arrays for faster calculations.
    """
    def __init__(self, rects: list = None):
        if rects is None:
            rects = list()

        x = list()
        y = list()
        w = list()
        h = list()

        for rect in rects:
            x.append(rect.x)
            y.append(rect.y)
            w.append(rect.w)
            h.append(rect.h)

        self.rects = np.array([x, y, w, h])

    def append(self, rect: Rect):
        self.rects = np.append(self.rects, [[rect.x], [rect.y], [rect.w], [rect.h]], axis=1)

    def delete(self, index: int):
        self.rects = np.delete(self.rects, index, axis=1)

    def get(self, index: int):
        return self[index]

    def insert(self, index: int, rect: Rect):
        self.rects = np.insert(
            self.rects, 
            index, 
            [rect.x, rect.y, rect.w, rect.h], 
            axis=1
        )

    def move(self, index: int, dx: int = 0, dy: int = 0):
        self.rects[0][index] += dx
        self.rects[1][index] += dy

    def set(self, index: int, rect: Rect):
        self[index] = rect

    def size(self):
        return len(self)

    @property
    def x(self):
        return self.rects[0]

    @property 
    def y(self):
        return self.rects[1]

    @property 
    def w(self):
        return self.rects[2]

    @property 
    def h(self):
        return self.rects[3]

    def __len__(self):
        return self.rects.shape[1]

    def __getitem__(self, key: int):
        return Rect(*self.rects[:,key])

    def __setitem__(self, key: int, value: Rect):
        self.rects[:,key] = [value.x, value.y, value.w, value.h]
