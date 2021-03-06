"""The inspector panel displays information about the canvas."""


import wx

from cartograpy import (
    ALL_EXPAND,
    EVT_LAYER_ADD,
    EVT_LAYER_BACKWARD,
    EVT_LAYER_DUPLICATE,
    EVT_LAYER_FORWARD,
    EVT_LAYER_REMOVE,
    EVT_SWAP_LAYER,
    EVT_UPDATE_FILENAME,
    EVT_UPDATE_VISIBILITY,
    LayerAddEvent,
    LayerBackwardEvent,
    LayerDuplicateEvent,
    LayerForwardEvent,
    LayerRemoveEvent,
    LayerSelectedEvent,
    SwapLayerEvent,
    UpdateFilenameEvent,
    UpdateVisibilityEvent,
)
from cartograpy.layer_menu import LayerMenu
from cartograpy.layer_properties import LayerProperties
from cartograpy.minimap import Minimap


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

        self.minimap = Minimap(parent=self)
        self.layer_properties = LayerProperties(parent=self)
        self.layer_menu = LayerMenu(parent=self)
        self.__init_layers()
        self.__size_widgets()

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__on_list_item_activated)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__on_list_item_selected)
        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.__on_list_item_checked)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.__on_list_item_checked)

        self.Bind(EVT_LAYER_ADD, self.__on_layer_add)
        self.Bind(EVT_LAYER_BACKWARD, self.__on_layer_backward)
        self.Bind(EVT_LAYER_DUPLICATE, self.__on_layer_duplicate)
        self.Bind(EVT_LAYER_FORWARD, self.__on_layer_forward)
        self.Bind(EVT_LAYER_REMOVE, self.__on_layer_remove)
        self.Bind(EVT_UPDATE_FILENAME, self.__on_update_filename)

        self.reset()

    def to_dict(self):
        """Returns the state of the inspector as a JSON compatible dictionary.

        Returns
        ---------
        dict:
            the JSON compatible state of the inspector.
        """
        data = {
            "layers": [
                {
                    "text": self.layers.GetItemText(i),
                    "data": self.layers.GetItemData(i),
                    "checked": self.layers.IsItemChecked(i),
                }
                for i in range(self.layers.GetItemCount())
            ],
            "minimap": self.minimap.to_dict(),
        }

        return data

    def reset(self):
        """Clears the current inspector and resets all values."""
        self.minimap.reset()
        self.layer_menu.reset()
        self.layers.DeleteAllItems()

    def __init_layers(self):
        """Initializes the layer controller."""
        self.layers = wx.ListCtrl(
            parent=self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.LC_REPORT
            | wx.LC_ALIGN_LEFT
            | wx.LC_NO_HEADER
            | wx.LC_SINGLE_SEL
            | wx.LC_HRULES,
            validator=wx.DefaultValidator,
            name="Layers",
        )

        self.layers.EnableCheckBoxes()
        self.layers.InsertColumn(col=0, heading="Name", width=400)

    def __on_layer_add(self, event: LayerAddEvent):
        """Adds a layer from an image file.

        Parameters
        ------------
        event: LayerAddEvent
            the event is expected to have a `path` property.
        """
        wx.PostEvent(self.Parent, event)

    def __on_layer_backward(self, event: LayerBackwardEvent):
        """Moves a layer backward.

        Parameters
        ------------
        event: LayerBackwardEvent
        """
        selected = self.layers.GetFirstSelected()
        n_layers = self.layers.GetItemCount()

        if selected < n_layers:
            new_index = selected + 1

            item = self.layers.GetItem(selected)
            item.SetId(new_index)

            self.layers.DeleteItem(selected)
            self.layers.InsertItem(item)
            self.layers.CheckItem(new_index)
            self.layers.Select(new_index)

            wx.PostEvent(self.Parent, SwapLayerEvent(layers=(selected, new_index)))

    def __on_layer_duplicate(self, event: LayerDuplicateEvent):
        """Duplicates the currently selected layer.

        Parameters
        ------------
        event: LayerDuplicateEvent
        """
        wx.PostEvent(self.Parent, event)

    def __on_layer_forward(self, event: LayerForwardEvent):
        """Moves a layer forward.

        Parameters
        ------------
        event: LayerForwardEvent
        """
        selected = self.layers.GetFirstSelected()

        if selected > 0:
            new_index = selected - 1

            item = self.layers.GetItem(selected)
            item.SetId(new_index)

            self.layers.DeleteItem(selected)
            self.layers.InsertItem(item)
            self.layers.CheckItem(new_index)
            self.layers.Select(new_index)

            wx.PostEvent(self.Parent, SwapLayerEvent(layers=(selected, new_index)))

    def __on_layer_remove(self, event: LayerRemoveEvent):
        """Removes the currently selected layer.

        Parameters
        ------------
        event: LayerRemoveEvent
        """
        wx.PostEvent(self.Parent, event)

    def __on_list_item_activated(self, event: wx.ListEvent):
        """Renames the item when double clicked.

        Parameters
        ------------
        event: wx.ListEvent
        """
        index = event.GetIndex()
        self.layers.EditLabel(index)

    def __on_list_item_selected(self, event: wx.ListEvent):
        """Selects a new layer.

        Parameters
        ------------
        event: LayerSelectEvent
        """
        wx.PostEvent(self.Parent, LayerSelectedEvent())

    def __on_list_item_checked(self, event: wx.ListEvent):
        """Changes the visibility of the checked layer.

        Parameters
        ------------
        event: wx.ListEvent
        """
        wx.PostEvent(self.Parent, UpdateVisibilityEvent())

    def __on_update_filename(self, event: UpdateFilenameEvent):
        """When the filename property has been changed.

        Parameters
        ------------
        event: UpdateFilenameEvent
        """
        wx.PostEvent(
            self.Parent,
            UpdateFilenameEvent(
                filename=event.filename,
                index=self.layers.GetFirstSelected(),
            ),
        )

    def __size_widgets(self):
        """Generates the layout for the inspector panel."""
        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        sizer.Add(window=self.minimap, flag=ALL_EXPAND)
        sizer.Add(window=self.layer_properties, flag=ALL_EXPAND)
        sizer.Add(window=self.layers, flag=ALL_EXPAND)
        sizer.Add(window=self.layer_menu, flag=ALL_EXPAND)

        self.SetSizer(sizer)
        self.Layout()
