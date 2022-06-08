"""The layer menu controls the order and state of the layers in the inspector
panel
"""


import os

import wx

from cartograpy import IMAGE_WILDCARD, ASSET_DIR, ALL_EXPAND
from cartograpy import (
    LayerAddEvent,
    LayerBackwardEvent,
    LayerDuplicateEvent,
    LayerForwardEvent,
    LayerRemoveEvent,
)


class LayerMenu(wx.Panel):
    """The layer menu controls the order and state of the layers in the
    inspector panel.

    The layer menu consists of these major components:

    - Add another layer.
    - Duplicate the currently selected layer.
    - Move the currently selected layer forward.
    - Move the currently selected layer backward.
    - Remove the currently selected layer.

    Parameters
    ------------
    parent: wx.Frame
        the parent window of this component.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        self.__init_buttons()
        self.__size_widgets()

        self.Bind(
            event=wx.EVT_BUTTON,
            handler=self.__on_button_add,
            id=self.button_add.GetId(),
        )
        self.Bind(
            event=wx.EVT_BUTTON,
            handler=self.__on_button_backward,
            id=self.button_backward.GetId(),
        )
        self.Bind(
            event=wx.EVT_BUTTON,
            handler=self.__on_button_duplicate,
            id=self.button_duplicate.GetId(),
        )
        self.Bind(
            event=wx.EVT_BUTTON,
            handler=self.__on_button_forward,
            id=self.button_forward.GetId(),
        )
        self.Bind(
            event=wx.EVT_BUTTON,
            handler=self.__on_button_remove,
            id=self.button_remove.GetId(),
        )
    
    def reset(self):
        """Clears the current layer menu and resets all values."""
        pass

    def __on_button_add(self, event: wx.CommandEvent):
        """Adds an image file as a layer.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events, which originate from a
            variety of simple controls.
        """
        with wx.FileDialog(
            parent=self,
            message="Select and image file to import as a layer",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=IMAGE_WILDCARD,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            path = dialog.GetPath()

        wx.PostEvent(self.Parent, LayerAddEvent(path=path))

    def __on_button_backward(self, event: wx.CommandEvent):
        """Moves the currently selected layer backward.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events, which originate from a
            variety of simple controls.
        """
        wx.PostEvent(self.Parent, LayerBackwardEvent())

    def __on_button_duplicate(self, event: wx.CommandEvent):
        """Duplicates the currently selected layer.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events, which originate from a
            variety of simple controls.
        """
        wx.PostEvent(self.Parent, LayerDuplicateEvent())

    def __on_button_forward(self, event: wx.CommandEvent):
        """Moves the currently selected layer forward.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events, which originate from a
            variety of simple controls.
        """
        wx.PostEvent(self.Parent, LayerForwardEvent())

    def __on_button_remove(self, event: wx.CommandEvent):
        """Removes the currently selected layer.

        Parameters
        ------------
        event: wx.CommandEvent
            contains information about command events, which originate from a
            variety of simple controls.
        """
        wx.PostEvent(self.Parent, LayerRemoveEvent())

    def __init_buttons(self):
        """Initializes the buttons."""
        self.button_add = wx.Button(
            parent=self,
            id=wx.ID_ANY,
            label="Add",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BU_NOTEXT,
            validator=wx.DefaultValidator,
            name="Add",
        )
        self.button_duplicate = wx.Button(
            parent=self,
            id=wx.ID_ANY,
            label="Duplicate",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BU_NOTEXT,
            validator=wx.DefaultValidator,
            name="Duplicate",
        )
        self.button_forward = wx.Button(
            parent=self,
            id=wx.ID_ANY,
            label="Forward",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BU_NOTEXT,
            validator=wx.DefaultValidator,
            name="Forward",
        )
        self.button_backward = wx.Button(
            parent=self,
            id=wx.ID_ANY,
            label="Backward",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BU_NOTEXT,
            validator=wx.DefaultValidator,
            name="Backward",
        )
        self.button_remove = wx.Button(
            parent=self,
            id=wx.ID_ANY,
            label="Remove",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BU_NOTEXT,
            validator=wx.DefaultValidator,
            name="Remove",
        )

        add_bitmap = wx.Bitmap(name=os.path.join(ASSET_DIR, "button_add.png"))
        backward_bitmap = wx.Bitmap(name=os.path.join(ASSET_DIR, "button_backward.png"))
        duplicate_bitmap = wx.Bitmap(
            name=os.path.join(ASSET_DIR, "button_duplicate.png")
        )
        forward_bitmap = wx.Bitmap(name=os.path.join(ASSET_DIR, "button_forward.png"))
        remove_bitmap = wx.Bitmap(name=os.path.join(ASSET_DIR, "button_remove.png"))

        self.button_add.SetBitmap(bitmap=add_bitmap)
        self.button_backward.SetBitmap(bitmap=backward_bitmap)
        self.button_duplicate.SetBitmap(bitmap=duplicate_bitmap)
        self.button_forward.SetBitmap(bitmap=forward_bitmap)
        self.button_remove.SetBitmap(bitmap=remove_bitmap)

    def __size_widgets(self):
        """Generates the layout for the layer menu."""
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        sizer.Add(window=self.button_add, flag=ALL_EXPAND)
        sizer.Add(window=self.button_duplicate, flag=ALL_EXPAND)
        sizer.Add(window=self.button_forward, flag=ALL_EXPAND)
        sizer.Add(window=self.button_backward, flag=ALL_EXPAND)
        sizer.Add(window=self.button_remove, flag=ALL_EXPAND)

        self.SetSizer(sizer)
        self.Layout()
