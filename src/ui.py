#!/usr/bin env python3
from PySide6 import QtCore, QtWidgets
from __feature__ import snake_case
from __feature__ import true_property


class MainWindow(QtWidgets.QMainWindow):
    """App window instance."""
    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
