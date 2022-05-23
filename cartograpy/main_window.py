"""The main window that houses the application.

Optimizations that can be done:

- Store rectangles as numpy arrays instead of individual objects
- When the layer operations are performed, instead of rebuilding everything
  from scratch, switch the two columns in the array or extend the array
- Only recreate the minimap images when the scaling factor from canvas to
  minimap is changed

"""


import os
import shutil

import numpy as np
import wx

from cartograpy import (
    ROOT_DIR, 
    ASSET_DIR, 
    ALL_EXPAND,
    EVT_LAYER_ADD,
    EVT_LAYER_DUPLICATE,
    EVT_LAYER_REMOVE,
    EVT_UPDATE_CANVAS,
    EVT_UPDATE_LAYER,
    LayerAddEvent,
    LayerDuplicateEvent,
    LayerRemoveEvent,
    UpdateCanvasEvent,
    UpdateLayerEvent,
    Rect
)
from cartograpy.canvas import Canvas
from cartograpy.inspector import Inspector


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

        self.Bind(wx.EVT_TOOL, self.__on_tool_colourpicker, id=self.tool_colourpicker.GetId())

        self.Bind(EVT_LAYER_ADD, self.__on_layer_add)
        self.Bind(EVT_LAYER_DUPLICATE, self.__on_layer_duplicate)
        self.Bind(EVT_LAYER_REMOVE, self.__on_layer_remove)
        self.Bind(EVT_UPDATE_CANVAS, self.__on_update_canvas)
        self.Bind(EVT_UPDATE_LAYER, self.__on_update_layer)

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
        colourpicker_bitmap = wx.Bitmap(
            name=os.path.join(ASSET_DIR, "tool_colourpicker.png")
        )

        self.toolbar = self.CreateToolBar(
            style=wx.TB_VERTICAL,
            id=wx.ID_ANY,
        )

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

        # Update minimap
        self.inspector.minimap.paths[self.counter] = temp_file
        self.__update_minimap()

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

        # Update minimap
        self.inspector.minimap.paths[self.counter] = path
        self.__update_minimap()

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

    def __on_tool_colourpicker(self, event: wx.CommandEvent):
        """Opens the colour dialog and sets the draw colour.

        Parameters
        ------------
        event: wx.CommandEvent
            Contains information about command events from controls.
        """
        with wx.ColourDialog(parent=self) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            colour = dialog.GetColourData().GetColour()
        self.Refresh()

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

    def __on_update_layer(self, event: UpdateLayerEvent):
        """Updates the currently selected layer in the inspector.

        Parameters
        ------------
        event: UpdateLayerEvent
            the event is expected to have `dx` and `dy` properties.
        """
        selected = self.inspector.layers.GetFirstSelected()
        key = self.inspector.layers.GetItemData(selected)

        self.canvas.destinations[key].move(dx=event.dx, dy=event.dy)
        self.__update_minimap()

        self.Refresh()

    def __update_minimap(self):
        """Updates the minimap from the canvas."""
        n_layers = len(self.canvas.destinations)
        x = np.zeros(n_layers)
        y = np.zeros(n_layers)
        w = np.zeros(n_layers)
        h = np.zeros(n_layers)

        for n, destination in enumerate(self.canvas.destinations.values()):
            x[n] = destination.x
            y[n] = destination.y
            w[n] = destination.x + destination.w
            h[n] = destination.y + destination.h

        x_min = np.min(x)
        y_min = np.min(y)
        w_max = np.max(w) - x_min
        h_max = np.max(h) - y_min

        w_new, h_new = self.inspector.minimap.GetSize().Get()

        w_factor = w_new / w_max
        h_factor = h_new / h_max
        factor = min(w_factor, h_factor)

        for path, bitmap in self.canvas.bitmaps.items():
            image = bitmap.ConvertToImage().Scale(
                width=int(bitmap.GetWidth() * factor), 
                height=int(bitmap.GetHeight() * factor),
            )

            self.inspector.minimap.bitmaps[path] = image.ConvertToBitmap()

        for key, destination in self.canvas.destinations.items():
            self.inspector.minimap.destinations[key] = Rect(
                x=(destination.x - x_min) * factor,
                y=(destination.y - y_min) * factor,
                w=destination.w * factor,
                h=destination.h * factor,
            )

    def __update_render_order(self):
        """Updates the render order in the canvas and minimap from the
        inspector.
        """
        render_order = [
            self.inspector.layers.GetItemData(i)
            for i in range(self.inspector.layers.GetItemCount())
            if self.inspector.layers.IsItemChecked(i)
        ]

        render_order = list(reversed(render_order))

        self.canvas.render_order = render_order
        self.inspector.minimap.render_order = render_order

        self.Refresh()
