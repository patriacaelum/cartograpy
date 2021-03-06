"""The minimap shows where viewpoint of the camera in relation to all of the
images.
"""


import wx

from cartograpy import Rect, Rects


class Minimap(wx.Panel):
    """The minimap shows the viewpoint of the camera in relation to all of
    the images.

    The minimap consists of these major elements:

    - The background colour.
    - The imported layers.
    - The viewpoint of the canvas.

    The internal parameters are:

    - `render_order` is a list of layer data indicating the order to render the
      layers.
    - `path` maps layer data to the path of the image.
    - `bitmaps` maps the path of the image to a `wx.Bitmap` object.
    - `destinations` maps layer data to a `Rect` defining where on the minimap
      the corresponding bitmap will be rendered.

    Parameters
    ------------
    parent: wx.Frame
        The parent window of this component.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent, size=wx.Size(400, 400))

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_PAINT, self.__on_paint)

        self.reset()

    def to_dict(self):
        """Returns the state of the minimap as a JSON compatible dictionary.

        Returns
        ---------
        dict:
            the JSON compatible state of the minimap.
        """
        data = {
            "order": self.order,
            "visibility": self.visibility,
            "paths": self.paths,
            "destinations": self.destinations.tolist(),
            "scale_factor": self.scale_factor,
            "camera": self.camera.to_dict(),
        }

        return data

    def reset(self):
        """Clears the current minimap and resets all values."""
        self.order = list()
        self.visibility = list()
        self.paths = dict()
        self.bitmaps = dict()
        self.destinations = Rects()

        self.scale_factor = 1

        self.camera = Rect(w=400, h=400)
        self.camera_view = wx.Bitmap.FromRGBA(400, 400, 255, 255, 255, 128)

    def __on_paint(self, event: wx.PaintEvent):
        """Repaints the minimap.

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

        gc.DrawBitmap(
            bmp=self.camera_view,
            **self.camera.to_dict(),
        )
