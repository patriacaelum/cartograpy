"""The inspector panel displays information about the canvas."""


from wx import wx


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
        The parent window of the application.
    """

    def __init__(self, parent: wx.Frame):
        super().__init__(parent=parent)

        self.SetMaxSize(wx.Size(300, -1))
