"""The layer properties widget displays the properties of the currently selected
layer in the inspector.
"""


import wx

from cartograpy import ALL_EXPAND, UpdateFilenameEvent


class LayerProperties(wx.Panel):
    """The layer properties component displays the properties of the currently
    selected layer in the inspector.

    Parameters
    ------------
    parent: wx.Frame
        the parent window of this component.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        self.__init_widgets()
        self.__size_widgets()

        self.Bind(wx.EVT_TEXT, self.__on_text_filename, id=self.filename.GetId())

    def __init_widgets(self):
        """Initializes the layer properties widgets."""
        self.header = wx.StaticText(parent=self, label="Layer Properties")
        self.header.SetFont(wx.Font(wx.FontInfo().Bold()))
        self.header_blank = wx.StaticText(parent=self, label="")

        self.x_label = wx.StaticText(parent=self, label="x")
        self.x = wx.TextCtrl(parent=self, size=(240, -1))

        self.y_label = wx.StaticText(parent=self, label="y")
        self.y = wx.TextCtrl(parent=self, size=(240, -1))

        self.z_label = wx.StaticText(parent=self, label="z")
        self.z = wx.TextCtrl(parent=self, size=(240, -1))

        self.w_label = wx.StaticText(parent=self, label="w")
        self.w = wx.TextCtrl(parent=self, size=(240, -1))

        self.h_label = wx.StaticText(parent=self, label="h")
        self.h = wx.TextCtrl(parent=self, size=(240, -1))

        self.filename_label = wx.StaticText(parent=self, label="Filename")
        self.filename = wx.TextCtrl(parent=self, size=(240, -1))

        self.zoom_label = wx.StaticText(parent=self, label="Zoom")
        self.zoom = wx.TextCtrl(parent=self, size=(240, -1))

        self.isolate_label = wx.StaticText(parent=self, label="Isolate z")
        self.isolate = wx.CheckBox(parent=self, label="Enable")

    def __on_text_filename(self, event: wx.CommandEvent):
        """When the filename property is changed.

        Parameters
        ------------
        event: wx.CommandEvent
        """
        wx.PostEvent(
            self.Parent, UpdateFilenameEvent(filename=self.filename.GetValue())
        )

    def __size_widgets(self):
        """Places all the initialized widgets in the panel."""
        sizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=5)

        sizer.Add(window=self.header, flag=ALL_EXPAND)
        sizer.Add(window=self.header_blank, flag=ALL_EXPAND)

        sizer.Add(window=self.x_label, flag=ALL_EXPAND)
        sizer.Add(window=self.x, flag=ALL_EXPAND)

        sizer.Add(window=self.y_label, flag=ALL_EXPAND)
        sizer.Add(window=self.y, flag=ALL_EXPAND)

        sizer.Add(window=self.z_label, flag=ALL_EXPAND)
        sizer.Add(window=self.z, flag=ALL_EXPAND)

        sizer.Add(window=self.w_label, flag=ALL_EXPAND)
        sizer.Add(window=self.w, flag=ALL_EXPAND)

        sizer.Add(window=self.h_label, flag=ALL_EXPAND)
        sizer.Add(window=self.h, flag=ALL_EXPAND)

        sizer.Add(window=self.filename_label, flag=ALL_EXPAND)
        sizer.Add(window=self.filename, flag=ALL_EXPAND)

        sizer.Add(window=self.zoom_label, flag=ALL_EXPAND)
        sizer.Add(window=self.zoom, flag=ALL_EXPAND)

        sizer.Add(window=self.isolate_label, flag=ALL_EXPAND)
        sizer.Add(window=self.isolate, flag=ALL_EXPAND)

        self.SetSizer(sizer)
        self.Layout()
