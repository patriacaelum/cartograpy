"""The canvas is where the layers are rendered and moved around."""


import wx

from cartograpy import Rects


class Canvas(wx.Panel):
    """The canvas is where the layers are rendered and moved around.

    The canvas consists of these major elements:

    - The background colour.
    - The imported layers.

    The internal parameters are:

    - `render_order` is a list of layer data indicating the order to render the
      layers.
    - `paths` maps layer data to the path of the image.
    - `bitmaps` maps the path of the image to a `wx.Bitmap` object.
    - `destinations` maps layer data to a `Rect` defining where on the canvas
      the corresponding bitmap will be rendered.

    Parameters
    ------------
    parent: wx.Frame
        The parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.order = list()
        self.visibility = list()
        self.paths = dict()
        self.bitmaps = dict()
        self.destinations = Rects()

        self.zoom_level = 0
        self.scale_factor = 1

        self.Bind(wx.EVT_LEFT_DOWN, self.__to_parent)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.__to_parent)
        self.Bind(wx.EVT_MOTION, self.__to_parent)

        self.Bind(wx.EVT_PAINT, self.__on_paint)

    def zoom(self, dz: int = 0):
        """Increases or decreases the zoom level and computes the scale factor.

        The equation for calculating the scale factor is::

            (|x| + 1)^{\\frac{x}{|x|}}

        Parameters
        ------------
        dz: int
            the change in zoom level. This should be either `1` or `-1`.
        """
        self.zoom_level += dz

        if self.zoom_level == 0:
            self.scale_factor = 1

        else:
            self.scale_factor = (abs(self.zoom_level) + 1)**(self.zoom_level / abs(self.zoom_level))

    def __to_parent(self, event: wx.Event):
        """Passes the event to the parent object."""
        wx.PostEvent(self.Parent, event)

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

        for n, key in enumerate(self.order):
            if not self.visibility[n]:
                continue

            gc.DrawBitmap(
                bmp=self.bitmaps[self.paths[key]],
                **self.destinations[n].to_dict(),
            )
