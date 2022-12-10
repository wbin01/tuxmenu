#!/usr/bin/env python3
import os
import sys
import time
import threading

from BlurWindow.blurWindow import GlobalBlur
from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

import attachments
import widgets


class MainWindow(QtWidgets.QMainWindow):
    """App window instance."""
    mount_app_grid_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        # CSS
        self.set_custom_style()

        # Main container
        self.main_container = QtWidgets.QWidget()
        self.main_container.set_contents_margins(0, 0, 0, 0)
        self.set_central_widget(self.main_container)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_alignment(QtCore.Qt.AlignTop)
        self.layout_container.set_spacing(0)
        self.main_container.set_layout(self.layout_container)

        # App launcher
        self.app_grid_layout = QtWidgets.QVBoxLayout()
        self.app_grid_layout.set_spacing(0)
        self.app_grid_layout.set_alignment(QtCore.Qt.AlignTop)
        self.layout_container.add_layout(self.app_grid_layout)

        self.mount_app_grid_signal.connect(self.mount_app_grid_fg_thread)
        self.mount_app_grid_thread = threading.Thread(
            target=self.mount_app_grid_bg_thread)
        self.mount_app_grid_thread.start()

    @QtCore.Slot()
    def set_custom_style(self):
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static/style.qss')
        with open(style_path, 'r') as f:
            _style = f.read()
            self.set_style_sheet(_style)

    @QtCore.Slot()
    def mount_app_grid_bg_thread(self):
        time.sleep(0.03)
        self.mount_app_grid_signal.emit(0)

    @QtCore.Slot()
    def mount_app_grid_fg_thread(self):
        menu_schema = attachments.MenuSchema()
        all_menu_desktop_files = menu_schema.schema['All']
        all_menu_desktop_files.sort()

        app_grid = widgets.AppGrid(
            desktop_file_list=all_menu_desktop_files, columns_num=6)
        app_grid.set_alignment(QtCore.Qt.AlignTop)
        app_grid.clicked.connect(self.app_launcher_was_clicked)
        self.app_grid_layout.add_widget(app_grid)

    @QtCore.Slot()
    def app_launcher_was_clicked(self, widget):
        print(widget)
        if str(widget) != '<GhostAppLauncher: Boo>':
            print(widget.desktop_file.content['[Desktop Entry]']['Name'])
        self.close()


class Application(object):
    """Desktop menu for Linux written in Python and Qt."""
    control_signal = QtCore.Signal(str)

    def __init__(self, args):
        """Class constructor."""
        self.application = QtWidgets.QApplication(args)
        self.application_icon = 'tuxmenu.png'
        self.application_name = 'TuxMenu'
        self.application_window = MainWindow()

    def main(self) -> None:
        """Start the app."""
        # Name
        self.application_window.set_window_title(self.application_name)

        # Icon
        app_icon = QtGui.QIcon(QtGui.QPixmap(self.application_icon))
        self.application_window.set_window_icon(app_icon)

        # Size
        self.application_window.set_minimum_height(500)
        self.application_window.set_minimum_width(500)

        # Blur
        self.application_window.set_attribute(
            QtCore.Qt.WA_TranslucentBackground)
        GlobalBlur(self.application_window.win_id(), Dark=True, QWidget=self)

        # Show
        self.application_window.show_maximized()  # .show_full_screen() .show()
        sys.exit(self.application.exec())


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    app = Application(sys.argv)
    app.main()
