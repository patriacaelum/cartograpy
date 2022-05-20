import dataclasses
import os

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
UpdateCanvasEvent, EVT_UPDATE_CANVAS = NewEvent()


@dataclasses.dataclass
class Rect:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def set(self, x: int = None, y: int = None, w: int = None, h: int = None):
        if x is not None:
            self.x = int(x)

        if y is not None:
            self.y = int(y)

        if w is not None:
            self.w = int(w)

        if h is not None:
            self.h = int(h)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
        }
