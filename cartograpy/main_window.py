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
    EVT_SWAP_LAYER,
    EVT_UPDATE_VISIBILITY,
    LayerAddEvent,
    LayerDuplicateEvent,
    LayerRemoveEvent,
    SwapLayerEvent,
    UpdateVisibilityEvent,
    Rect,
    Rects,
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

        self.Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.__on_middle_down)
        self.Bind(wx.EVT_MOTION, self.__on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.__on_mousewheel)

        self.Bind(wx.EVT_TOOL, self.__on_tool_colourpicker, id=self.tool_colourpicker.GetId())

        self.Bind(EVT_LAYER_ADD, self.__on_layer_add)
        self.Bind(EVT_LAYER_DUPLICATE, self.__on_layer_duplicate)
        self.Bind(EVT_LAYER_REMOVE, self.__on_layer_remove)
        self.Bind(EVT_SWAP_LAYER, self.__on_swap_layer)
        self.Bind(EVT_UPDATE_VISIBILITY, self.__on_update_visibility)

        self.counter = 0
        self.paths = dict()
        self.bitmaps = dict()
        self.destinations = Rects()

        self.x_mouse = 0
        self.y_mouse = 0

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

        self.paths[self.counter] = temp_file
        self.bitmaps[temp_file] = bitmap
        self.destinations.append(rect=destination)

        # Update canvas
        self.canvas.order.append(self.counter)
        self.canvas.visibility.append(False)
        self.canvas.paths[self.counter] = temp_file
        self.canvas.bitmaps[temp_file] = self.__scale(bitmap, self.canvas.scale_factor)
        self.canvas.destinations.append(rect=destination.scale(self.canvas.scale_factor))
    
        # Update minimap
        self.inspector.minimap.order.append(self.counter)
        self.inspector.minimap.visibility.append(False)
        self.inspector.minimap.paths[self.counter] = temp_file
        self.inspector.minimap.destinations.append(rect=destination)
        self.__update_minimap(resize=True)

        # Update inspector
        self.inspector.layers.InsertItem(0, f"layer_{self.counter}")
        self.inspector.layers.SetItemData(0, self.counter)
        self.inspector.layers.CheckItem(0)
        self.inspector.layers.Select(0)

        self.counter += 1
        self.Refresh()

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
        index = -(selected + 1)

        self.paths[self.counter] = path
        self.destinations.insert(index=index, rect=destination)

        # Update canvas
        self.canvas.order.insert(index, self.counter)
        self.canvas.visibility.insert(index, False)
        self.canvas.paths[self.counter] = path
        self.canvas.destinations.insert(index=index, rect=destination)

        # Update minimap
        self.inspector.minimap.order.insert(index, self.counter)
        self.inspector.minimap.visibility.insert(index, False)
        self.inspector.minimap.paths[self.counter] = path
        self.inspector.minimap.destinations.insert(index=index, rect=destination)
        self.__update_minimap(resize=True)

        # Update inspector
        self.inspector.layers.InsertItem(selected, f"layer_{self.counter}")
        self.inspector.layers.SetItemData(selected, self.counter)
        self.inspector.layers.CheckItem(selected)
        self.inspector.layers.Select(selected)

        self.counter += 1
        self.Refresh()

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
        path = self.paths[item_data]
        index = -(selected + 1)

        del self.paths[item_data]
        self.destinations.delete(index)

        # Update inspector
        self.inspector.layers.DeleteItem(selected)
        self.inspector.layers.Select(selected)

        # Update canvas
        del self.canvas.order[index]
        del self.canvas.visibility[index]
        del self.canvas.paths[item_data]
        self.canvas.destinations.delete(index)

        # Update minimap
        del self.inspector.minimap.order[index]
        del self.inspector.minimap.visibility[index]
        del self.inspector.minimap.paths[item_data]
        self.inspector.minimap.delete(index)

        if path not in self.paths.values():
            del self.bitmaps[path]
            del self.inspector.minimap.bitmaps[path]
            del self.canvas.bitmaps[path]
            os.remove(path)

        self.__update_minimap(resize=True)
        self.Refresh()

    def __on_left_down(self, event: wx.MouseEvent):
        """Processes mouse left button down events.

        Parameters
        ------------
        event: wx.MouseEvent
            contains information about the events generated by the mouse.
        """
        self.x_mouse, self.y_mouse = event.GetPosition()

    def __on_middle_down(self, event: wx.MouseEvent):
        """Processes mouse middle button down events.

        Parameters
        ------------
        event: wx.MouseEvent
            contains information about the events generated by the mouse.
        """
        self.x_mouse, self.y_mouse = event.GetPosition()

    def __on_motion(self, event: wx.MouseEvent):
        """Processes mouse movement events.

        Parameters
        ------------
        event: wx.MouseEvent
            contains information about the events generated by the mouse.
        """
        # Move a single layer
        if event.LeftIsDown():
            x, y = event.GetPosition()

            dx = x - self.x_mouse
            dy = y - self.y_mouse

            self.x_mouse = x
            self.y_mouse = y

            selected = self.inspector.layers.GetFirstSelected()
            index = -(selected + 1)

            self.canvas.destinations.move(index=index, dx=dx, dy=dy)
            self.__update_minimap()

            self.Refresh()

        # Pan camera
        elif event.MiddleIsDown():
            x, y = event.GetPosition()

            dx = x - self.x_mouse
            dy = y - self.y_mouse

            self.x_mouse = x
            self.y_mouse = y

            for i in range(len(self.destinations)):
                self.canvas.destinations.move(index=i, dx=dx, dy=dy)

            self.__update_minimap()
            self.Refresh()

    def __on_mousewheel(self, event: wx.MouseEvent):
        """Zooms in and out.

        Parameters
        ------------
        event: wx.MouseEvent
            contains information about the events generated by the mouse.
        """
        x, y = event.GetPosition()
        rotation = event.GetWheelRotation()

        old_factor = self.canvas.scale_factor

        if rotation > 0:
            self.canvas.zoom(dz=1)
        
        elif rotation < 0:
            self.canvas.zoom(dz=-1)
        
        # Update destinations
        n_layers = len(self.canvas.destinations)

        self.canvas.destinations.rects[0] = np.full(n_layers, x) - (self.canvas.scale_factor / old_factor) * (np.full(n_layers, x) - self.canvas.destinations.x)
        self.canvas.destinations.rects[1] = np.full(n_layers, y) - (self.canvas.scale_factor / old_factor) * (np.full(n_layers, y) - self.canvas.destinations.y)
        self.canvas.destinations.rects[2] = self.destinations.w * self.canvas.scale_factor
        self.canvas.destinations.rects[3] = self.destinations.h * self.canvas.scale_factor

        for path, bitmap in self.bitmaps.items():
            self.canvas.bitmaps[path] = self.__scale(bitmap, self.canvas.scale_factor)

        self.__update_minimap(resize=True)
        self.Refresh()

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

    def __on_swap_layer(self, event: SwapLayerEvent):
        """Swaps the order of two layers in the canvas and minimap.

        Parameters
        ------------
        event: SwapLayerEvent
            the event is expected to have a tuple of size two as the `layers`
            property.
        """
        i, j = event.layers
        i = -(i + 1)
        j = -(j + 1)

        self.canvas.order[i], self.canvas.order[j] = self.canvas.order[j], self.canvas.order[i]
        self.canvas.visibility[i], self.canvas.visibility[j] = self.canvas.visibility[j], self.canvas.visibility[i]
        self.canvas.destinations.rects[:,[i,j]] = self.canvas.destinations.rects[:,[j,i]]

        self.inspector.minimap.order[i], self.inspector.minimap.order[j] = self.inspector.minimap.order[j], self.inspector.minimap.order[i]
        self.inspector.minimap.visibility[i], self.inspector.minimap.visibility[j] = self.inspector.minimap.visibility[j], self.inspector.minimap.visibility[i]
        self.inspector.minimap.destinations.rects[:,[i,j]] = self.inspector.minimap.destinations.rects[:,[j,i]]

        self.Refresh()

    def __on_update_visibility(self, event: UpdateVisibilityEvent):
        """Updates the visibility of the currently selected layer.

        Parameters
        ------------
        event: UpdateVisibilityEvent
            the event is expected to have a boolean `show` property.
        """
        selected = self.inspector.layers.GetFirstSelected()
        index = -(selected + 1)

        self.canvas.visibility[index] = not self.canvas.visibility[index]
        self.inspector.minimap.visibility[index] = not self.inspector.minimap.visibility[index]

        self.Refresh()

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

    def __update_minimap(self, resize: bool = False):
        """Updates the minimap from the canvas."""
        x_min = self.canvas.destinations.x.min()
        y_min = self.canvas.destinations.y.min()
        w_max = (self.canvas.destinations.x + self.canvas.destinations.w).max() - x_min
        h_max = (self.canvas.destinations.y + self.canvas.destinations.h).max() - y_min

        w_minimap, h_minimap = self.inspector.minimap.GetSize().Get()
        w_canvas, h_canvas = self.canvas.GetSize().Get()

        w_factor = w_minimap / w_max
        h_factor = h_minimap / h_max
        factor = min(w_factor, h_factor)

        # Update destinations
        n_layers = len(self.canvas.destinations)

        self.inspector.minimap.destinations.rects[0] = (self.canvas.destinations.x - np.full(n_layers, x_min)) * factor
        self.inspector.minimap.destinations.rects[1] = (self.canvas.destinations.y - np.full(n_layers, y_min)) * factor
        self.inspector.minimap.destinations.rects[2] = self.canvas.destinations.w * factor
        self.inspector.minimap.destinations.rects[3] = self.canvas.destinations.h * factor

        self.inspector.minimap.camera.x = int(-x_min * factor)
        self.inspector.minimap.camera.y = int(-y_min * factor)
        self.inspector.minimap.camera.w = int(w_canvas * factor)
        self.inspector.minimap.camera.h = int(h_canvas * factor)

        # Avoid resizing when possible
        if not resize or self.inspector.minimap.scale_factor == factor:
            return

        # Update resized bitmaps
        self.inspector.minimap.scale_factor = factor

        for path, bitmap in self.bitmaps.items():
            self.inspector.minimap.bitmaps[path] = self.__scale(bitmap, factor)

    @staticmethod
    def __scale(bitmap, scale):
        """Scales a bitmap."""
        return bitmap.ConvertToImage().Scale(
            width=int(bitmap.GetWidth() * scale), 
            height=int(bitmap.GetHeight() * scale)
        ).ConvertToBitmap()
