import os

import wx

from wx.lib.newevent import NewEvent


IMAGE_WILDCARD = "All files (*)|*|BMP files (*.bmp)|*.bmp|JPG files (*.jpg)|*.jpg|PNG files (*.png)|*.png"


ROOT_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(ROOT_DIR, "assets")


ALL_EXPAND = wx.ALL | wx.EXPAND


AddLayerEvent, EVT_ADD_LAYER = NewEvent()
BackwardLayerEvent, EVT_BACKWARD_LAYER = NewEvent()
DuplicateLayerEvent, EVT_DUPLICATE_LAYER = NewEvent()
ForwardLayerEvent, EVT_FORWARD_LAYER = NewEvent()
RemoveLayerEvent, EVT_REMOVE_LAYER = NewEvent()
UpdateCanvasEvent, EVT_UPDATE_CANVAS = NewEvent()
