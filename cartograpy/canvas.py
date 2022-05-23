"""The canvas is where the layers are rendered and moved around."""


import wx

from cartograpy import UpdateLayerEvent


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

        self.render_order = list()
        self.paths = dict()
        self.bitmaps = dict()
        self.destinations = dict()

        self.x_mouse = None
        self.y_mouse = None

        self.Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)
        self.Bind(wx.EVT_MOTION, self.__on_motion)

        self.Bind(wx.EVT_PAINT, self.__on_paint)

    def __on_left_down(self, event: wx.MouseEvent):
        """Processes mouse left button down events.

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
        if event.LeftIsDown():
            x, y = event.GetPosition()

            dx = x - self.x_mouse
            dy = y - self.y_mouse

            self.x_mouse = x
            self.y_mouse = y

            wx.PostEvent(self.Parent, UpdateLayerEvent(dx=dx, dy=dy))

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
