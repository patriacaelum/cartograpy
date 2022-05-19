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
