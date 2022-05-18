"""The main window that houses the application."""


import os

from wx import wx

from canvas import Canvas
from inspector import Inspector


ROOT_DIR = os.path.dirname(__file__)

ALL_EXPAND = wx.ALL | wx.EXPAND


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
            style=wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDRREN,
        )

        self.Centre(wx.BOTH)
        self.Maximize()
        self.SetDoubleBuffered(True)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.canvas = Canvas(parent=self)
        self.inspector = Inspector(parent=self)

        self.__size_widgets()
        self.__init_toolbar()

    def __init_toolbar(self):
        """Initializes the toolbar.

        The toolbar icons are expected to be the the `assets` directory relative
        to `main.py`.

        The toolbar consists of theses items:

        - Move
        - Colourpicker

        """
        tool_move_asset = os.path.join(ROOT_DIR, "assets/tool_move.png")
        tool_colourpicker_asset = os.path.join(ROOT_DIR, "assets/tool_colourpicker.png")

        self.toolbar = self.CreateToolBar(
            style=wx.TB_VERTICAL,
            id=wx.ID_ANY,
        )

        self.tool_move = self.toolbar.AddTool(
            toolId=wx.ID_ANY,
            label="Move",
            bitmap=wx.Bitmap(name=tool_colourpicker_asset),
            kind=wx.ITEM_CHECK,
        )

        self.toolbar.AddSeparator()

        self.tool_colourpicker = self.toolbar.AddTool(
            toolId=wx.ID_ANY,
            label="Colourpicker",
            bitmap=wx.Bitmap(name=tool_move_asset),
            kind=wx.ITEM_NORMAL,
        )

        self.toolbar.Realize()

    def __size_widgets(self):
        """Creates the layout for the canvas and inspector."""
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
