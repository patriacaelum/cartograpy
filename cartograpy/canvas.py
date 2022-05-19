"""The canvas is where the layers are rendered and moved around."""


import wx


class Canvas(wx.Panel):
    """The canvas is where the layers are rendered and moved around.

    The canvas consists of these major elements:

    - The background colour.
    - The imported layers.

    Parameters
    ------------
    parent: wx.Frame
        The parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.render_order = list()

        # Maps layer data to a path
        self.paths = dict()

        # Maps a path to a bitmap
        self.bitmaps = dict()

        # Maps a layer data to a Rect
        self.destinations = dict()

        self.Bind(wx.EVT_PAINT, self.__on_paint)

    def __on_paint(self, event: wx.PaintEvent):
        """Repaints the canvas.

        Parameters
        ------------
        event: wx.PaintEvent
            a paint event is sent when a window's contents needs to be
            repainted.
        """
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        for key in self.render_order:
            gc.DrawBitmap(
                bmp=self.bitmaps[self.paths[key]],
                **self.destinations[key].to_dict(),
            )
