"""The main loop of the application.

CartograPy is a simple 2D map editor used to move images around a canvas and
exports to JSON.
"""


import wx

from cartograpy.main_window import MainWindow


def main():
    """The main loop of the application."""
    app = wx.App()

    main_window = MainWindow()
    main_window.show()

    app.MainLoop()


if __name__ == "__main__":
    main()
