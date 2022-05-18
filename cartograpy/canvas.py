"""The canvas is where the layers are rendered and moved around."""


from wx import wx


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
