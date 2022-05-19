"""The inspector panel displays information about the canvas."""


import wx

from cartograpy import ALL_EXPAND
from cartograpy import EVT_ADD_LAYER, EVT_BACKWARD_LAYER, EVT_DUPLICATE_LAYER, EVT_FORWARD_LAYER, EVT_REMOVE_LAYER, EVT_UPDATE_CANVAS
from cartograpy import AddLayerEvent, BackwardLayerEvent, DuplicateLayerEvent, ForwardLayerEvent, RemoveLayerEvent, UpdateCanvasEvent
from cartograpy.layer_menu import LayerMenu


class Inspector(wx.Panel):
    """The inspector panel displays information about the canvas.

    The inspector panel consists of these major components:

    - The minimap that shows the entire canvas.
    - The properties of the currently selected layer.
      - The x-coordinate of the top left corner of the currently selected layer.
      - The y-coordinate of the top left corner of the currently selected layer.
      - The z-coordinate of the currently selected layer.
      - The width (in pixels) of the currently selected layer.
      - The height (in pixels) of the currently selected layer.
    - The control options for the currently selected layer.
      - Add another layer.
      - Duplicate the currently selected layer.
      - Move the currently selected layer foward.
      - Move the currently selected layer backward.
      - Hide the currently selected layer.
      - Remove the currently selected layer.
    - The list of imported images as layers.

    Parameters
    ------------
    parent: wx.Frame
        the parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        self.SetMaxSize(wx.Size(400, -1))

        self.layer_menu = LayerMenu(parent=self)
        self.__init_layers()
        self.__size_widgets()

        self.Bind(EVT_ADD_LAYER, self.__on_add_layer)
        self.Bind(EVT_BACKWARD_LAYER, self.__on_backward_layer)
        self.Bind(EVT_DUPLICATE_LAYER, self.__on_duplicate_layer)
        self.Bind(EVT_FORWARD_LAYER, self.__on_forward_layer)
        self.Bind(EVT_REMOVE_LAYER, self.__on_remove_layer)

    def __init_layers(self):
        """Initializes the layer controller."""
        self.layers = wx.ListCtrl(
            parent=self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.LC_REPORT | wx.LC_ALIGN_LEFT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_HRULES,
            validator=wx.DefaultValidator,
            name="Layers",
        )

        self.layers.EnableCheckBoxes()
        self.layers.InsertColumn(col=0, heading="Name", width=400)

    def __on_add_layer(self, event: AddLayerEvent):
        """Adds a layer from an image file.

        Parameters
        ------------
        event: AddLayerEvent
            the event is expected to have a `path` property.
        """
        wx.PostEvent(self.Parent, event)

    def __on_backward_layer(self, event: BackwardLayerEvent):
        """Moves a layer backward.

        Parameters
        ------------
        event: BackwardLayerEvent
        """
        selected = self.layers.GetFirstSelected()
        n_layers = self.layers.GetItemCount()

        if selected < n_layers:
            new_index = selected + 1

            item = self.layers.GetItem(selected)
            item.SetId(new_index)

            self.layers.DeleteItem(selected)
            self.layers.InsertItem(item)
            self.layers.Select(new_index)

            wx.PostEvent(self.Parent, UpdateCanvasEvent())

    def __on_duplicate_layer(self, event: DuplicateLayerEvent):
        """Duplicates the currently selected layer.

        Parameters
        ------------
        event: DuplicateLayerEvent
        """
        wx.PostEvent(self.Parent, event)

    def __on_forward_layer(self, event: ForwardLayerEvent):
        """Moves a layer forward.

        Parameters
        ------------
        event: ForwardLayerEvent
        """
        selected = self.layers.GetFirstSelected()

        if selected > 0:
            new_index = selected - 1

            item = self.layers.GetItem(selected)
            item.SetId(new_index)

            self.layers.DeleteItem(selected)
            self.layers.InsertItem(item)
            self.layers.Select(new_index)

            wx.PostEvent(self.Parent, UpdateCanvasEvent())

    def __on_remove_layer(self, event: RemoveLayerEvent):
        """Removes the currently selected layer.

        Parameters
        ------------
        event: RemoveLayerEvent
        """
        wx.PostEvent(self.Parent, event)

    def __size_widgets(self):
        """Generates the layout for the inspector panel."""
        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        sizer.Add(window=self.layers, flag=ALL_EXPAND)
        sizer.Add(window=self.layer_menu, flag=ALL_EXPAND)

        self.SetSizer(sizer)
        self.Layout()
