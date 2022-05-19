"""The main window that houses the application."""


import os
import shutil

from dataclasses import dataclass

import wx

from cartograpy import ROOT_DIR, ASSET_DIR, ALL_EXPAND
from cartograpy import (
    EVT_LAYER_ADD,
    EVT_LAYER_DUPLICATE,
    EVT_LAYER_REMOVE,
    EVT_UPDATE_CANVAS,
)
from cartograpy import (
    LayerAddEvent,
    LayerDuplicateEvent,
    LayerRemoveEvent,
    UpdateCanvasEvent,
)
from cartograpy.canvas import Canvas
from cartograpy.inspector import Inspector


@dataclass
class Rect:
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


class MainWindow(wx.Frame):
    """The main window that houses the application.

    The application consists of these major components:

    - The menu bar at the top of the window.
    - The toolbar on the left of the window.
      - A move tool that moves the currently selected layer.
      - A colourpicker tool that shows the border of the currently selected
        layer.
    - The inspector panel on the right side of the window.
      - A mini map showing the entire canvas.
      - The properties of the currently selected layer.
      - A list of layers corresponding to the graphics shown on the canvas.
    - The canvas where the graphics are rendered in the centre of the window.

    """

    def __init__(self):
        super().__init__(
            parent=None,
            title="cartograpy",
            size=wx.Size(640, 480),
            style=wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN,
        )

        self.Centre(wx.BOTH)
        self.Maximize()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.canvas = Canvas(parent=self)
        self.inspector = Inspector(parent=self)

        self.__init_toolbar()
        self.__size_widgets()

        self.Bind(EVT_LAYER_ADD, self.__on_layer_add)
        self.Bind(EVT_LAYER_DUPLICATE, self.__on_layer_duplicate)
        self.Bind(EVT_LAYER_REMOVE, self.__on_layer_remove)
        self.Bind(EVT_UPDATE_CANVAS, self.__on_update_canvas)

        self.counter = 0
        self.images = dict()
        self.filenames = dict()

        self.temp_dir = os.path.join(ROOT_DIR, "temp")
        shutil.rmtree(self.temp_dir)
        os.mkdir(self.temp_dir)

    def __init_toolbar(self):
        """Initializes the toolbar.

        The toolbar icons are expected to be the the `assets` directory relative
        to `main.py`.

        The toolbar consists of theses items:

        - Move
        - Colourpicker

        """
        move_bitmap = wx.Bitmap(name=os.path.join(ASSET_DIR, "tool_move.png"))
        colourpicker_bitmap = wx.Bitmap(
            name=os.path.join(ASSET_DIR, "tool_colourpicker.png")
        )

        self.toolbar = self.CreateToolBar(
            style=wx.TB_VERTICAL,
            id=wx.ID_ANY,
        )

        self.tool_move = self.toolbar.AddTool(
            toolId=wx.ID_ANY,
            label="Move",
            bitmap=move_bitmap,
            kind=wx.ITEM_CHECK,
        )

        self.toolbar.AddSeparator()

        self.tool_colourpicker = self.toolbar.AddTool(
            toolId=wx.ID_ANY,
            label="Colourpicker",
            bitmap=colourpicker_bitmap,
            kind=wx.ITEM_NORMAL,
        )

        self.toolbar.Realize()

    def __on_layer_add(self, event: LayerAddEvent):
        """Adds a layer from an image file.

        Parameters
        ------------
        event: LayerAddEvent
            the event is expected to have a `path` property.
        """
        layer_name = str(self.counter)

        # Copy image to temporary directory
        temp_file = os.path.join(self.temp_dir, layer_name)
        shutil.copyfile(event.path, temp_file)

        # Load image file
        bitmap = wx.Bitmap(name=temp_file)
        destination = Rect(w=bitmap.GetWidth(), h=bitmap.GetHeight())

        # Update inspector
        self.inspector.layers.InsertItem(0, f"layer_{self.counter}")
        self.inspector.layers.SetItemData(0, self.counter)
        self.inspector.layers.CheckItem(0)
        self.inspector.layers.Select(0)

        # Update canvas
        self.canvas.paths[self.counter] = temp_file
        self.canvas.bitmaps[temp_file] = bitmap
        self.canvas.destinations[self.counter] = destination

        self.counter += 1
        self.__update_render_order()

    def __on_layer_duplicate(self, event: LayerDuplicateEvent):
        """Duplicates the currently selected layer.

        Parameters
        ------------
        event: LayerDuplicateEvent
        """
        selected = self.inspector.layers.GetFirstSelected()

        # Get original
        selected_data = self.inspector.layers.GetItemData(selected)
        path = self.canvas.paths[selected_data]
        destination = self.canvas.destinations[selected_data]

        # Update inspector
        self.inspector.layers.InsertItem(selected, f"layer_{self.counter}")
        self.inspector.layers.SetItemData(selected, self.counter)
        self.inspector.layers.CheckItem(selected)
        self.inspector.layers.Select(selected)

        # Update canvas
        self.canvas.paths[self.counter] = path
        self.canvas.destinations[self.counter] = destination

        self.counter += 1
        self.__update_render_order()

    def __on_layer_remove(self, event: LayerRemoveEvent):
        """Removes the currently selected layer.

        If there are no more references to the image layer, the image file is
        removed from the temporary directory.

        Parameters
        ------------
        event: LayerRemoveEvent
        """
        selected = self.inspector.layers.GetFirstSelected()
        item_data = self.inspector.layers.GetItemData(selected)

        # Update inspector
        self.inspector.layers.DeleteItem(selected)
        self.inspector.layers.Select(selected)

        # Update canvas
        path = self.canvas.paths[item_data]

        del self.canvas.paths[item_data]
        del self.canvas.destinations[item_data]

        if path not in self.canvas.paths.values():
            del self.canvas.bitmaps[path]
            os.remove(path)

        self.__update_render_order()

    def __on_update_canvas(self, event: UpdateCanvasEvent):
        """Updates the canvas.

        Parameters
        ------------
        event: UpdateCanvasEvent
        """
        self.__update_render_order()

    def __size_widgets(self):
        """Generates the layout for the canvas and inspector."""
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        sizer.Add(
            window=self.canvas,
            proportion=1,
            flag=ALL_EXPAND,
            border=5,
        )
        sizer.Add(
            window=self.inspector,
            proportion=1,
            flag=ALL_EXPAND,
            border=5,
        )

        self.SetSizer(sizer)
        self.Layout()

    def __update_render_order(self):
        """Updates the render order in the canvas from the inspector."""
        render_order = [
            self.inspector.layers.GetItemData(i)
            for i in range(self.inspector.layers.GetItemCount())
            if self.inspector.layers.IsItemChecked(i)
        ]

        self.canvas.render_order = list(reversed(render_order))
        self.Refresh()
