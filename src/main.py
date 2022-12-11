#!/usr/bin/env python3
import os
import sys
import threading
import time

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
        self.__set_custom_style()
        self.app_grid_columns_num = 6
        self.recent_apps = attachments.SavedApps(config_name='recent-apps')
        self.favorite_apps = attachments.SavedApps(config_name='favorite-apps')

        # Main container
        self.main_container = QtWidgets.QWidget()
        self.main_container.set_contents_margins(0, 0, 0, 0)
        self.set_central_widget(self.main_container)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_contents_margins(0, 0, 0, 0)
        self.layout_container.set_alignment(QtCore.Qt.AlignTop)
        self.layout_container.set_spacing(0)
        self.main_container.set_layout(self.layout_container)

        # App pagination layout
        self.app_pagination_layout = QtWidgets.QHBoxLayout()
        self.app_pagination_layout.set_contents_margins(0, 0, 0, 0)
        self.app_pagination_layout.set_spacing(0)
        self.app_pagination_layout.set_alignment(QtCore.Qt.AlignTop)
        self.layout_container.add_layout(self.app_pagination_layout)

        self.active_category_button = None
        self.category_buttons_layout = QtWidgets.QVBoxLayout()
        self.category_buttons_layout.set_contents_margins(0, 0, 0, 0)
        self.category_buttons_layout.set_spacing(0)
        self.category_buttons_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.app_pagination_layout.add_layout(self.category_buttons_layout)

        self.app_grid_stacked_layout = QtWidgets.QStackedLayout()
        self.app_grid_stacked_layout.set_contents_margins(0, 0, 0, 0)
        self.app_grid_stacked_layout.set_spacing(0)
        self.app_grid_stacked_layout.set_alignment(QtCore.Qt.AlignTop)
        self.app_pagination_layout.add_layout(self.app_grid_stacked_layout)

        self.__mount_recent_apps_grid()

        # Thread
        self.mount_app_grid_signal.connect(self.__mount_app_grid)
        self.mount_app_grid_thread = threading.Thread(
            target=self.__mount_app_grid_thread)
        self.mount_app_grid_thread.start()

    @QtCore.Slot()
    def __set_custom_style(self):
        # Adds CSS styling to the main window
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static/style.qss')
        with open(style_path, 'r') as f:
            _style = f.read()
            self.set_style_sheet(_style)

    @QtCore.Slot()
    def __mount_recent_apps_grid(self):
        # Mount recent app grid
        apps = self.recent_apps.apps

        if not apps:
            menu_schema = attachments.MenuSchema()
            menu_schema.schema['All'].sort()
            apps = menu_schema.schema['All'][:self.app_grid_columns_num]

        # Category buttons pagination
        category_button = widgets.CategoryButton(text='Recent')
        setattr(category_button, 'page_index', 0)
        category_button.set_check_state(state=True)
        self.active_category_button = category_button
        category_button.clicked.connect(self.__on_category_button)
        self.category_buttons_layout.add_widget(category_button)

        # Apps page
        page = QtWidgets.QWidget()
        page.set_contents_margins(0, 0, 0, 0)
        page.set_style_sheet('background: transparent;')
        self.app_grid_stacked_layout.add_widget(page)

        page_layout = QtWidgets.QVBoxLayout()
        page_layout.set_contents_margins(0, 0, 0, 0)
        page_layout.set_spacing(0)
        page.set_layout(page_layout)

        # Title
        title = QtWidgets.QLabel(f'Recent apps')
        title.set_contents_margins(0, 0, 0, 0)
        title.set_alignment(QtCore.Qt.AlignHCenter)
        title.set_style_sheet(
            'background: transparent; font-size: 24px;')
        page_layout.add_widget(title)

        # App grid
        app_grid = widgets.AppGrid(desktop_file_list=apps, columns_num=6)
        app_grid.clicked.connect(
            lambda widget: self.__on_app_launcher_was_clicked_signal(
                widget))
        app_grid.set_alignment(QtCore.Qt.AlignTop)
        page_layout.add_widget(app_grid)

    @QtCore.Slot()
    def __mount_app_grid_thread(self):
        # Wait for the main window to render to assemble the app grid
        time.sleep(0.05)
        self.mount_app_grid_signal.emit(0)

    @QtCore.Slot()
    def __mount_app_grid(self):
        # Mount app grid
        menu_schema = attachments.MenuSchema()
        page_index = 1
        for categ, apps in menu_schema.schema.items():
            if not apps:
                continue
            apps.sort()
            # Category buttons pagination
            category_button = widgets.CategoryButton(text=categ)
            setattr(category_button, 'page_index', page_index)
            category_button.clicked.connect(self.__on_category_button)
            self.category_buttons_layout.add_widget(category_button)

            # Apps page
            page = QtWidgets.QWidget()
            page.set_contents_margins(0, 0, 0, 0)
            page.set_style_sheet('background: transparent;')
            self.app_grid_stacked_layout.add_widget(page)

            page_layout = QtWidgets.QVBoxLayout()
            page_layout.set_contents_margins(0, 0, 0, 0)
            page_layout.set_spacing(0)
            page.set_layout(page_layout)

            # Title
            title = QtWidgets.QLabel(f'{categ} {len(apps)}')
            title.set_contents_margins(0, 0, 0, 0)
            title.set_alignment(QtCore.Qt.AlignHCenter)
            title.set_style_sheet(
                'background: transparent; font-size: 24px;')
            page_layout.add_widget(title)

            # App grid
            app_grid = widgets.AppGrid(
                desktop_file_list=apps, columns_num=self.app_grid_columns_num)
            app_grid.clicked.connect(
                lambda widget: self.__on_app_launcher_was_clicked_signal(
                    widget))
            app_grid.set_alignment(QtCore.Qt.AlignTop)
            page_layout.add_widget(app_grid)

            page_index += 1

    @QtCore.Slot()
    def __on_category_button(self):
        # Active category button state (highlight fixed)
        if self.active_category_button:
            self.active_category_button.set_check_state(state=False)
        self.sender().set_check_state(state=True)
        self.active_category_button = self.sender()

        self.app_grid_stacked_layout.set_current_index(
            self.sender().page_index)

    @QtCore.Slot()
    def __on_app_launcher_was_clicked_signal(self, widget):
        # When the app is clicked, this method is triggered
        print(widget)
        if str(widget) != '<GhostAppLauncher: Boo>':
            print(widget.desktop_file.url)
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

        # Show | show_maximized show_full_screen show
        self.application_window.show_maximized()
        sys.exit(self.application.exec())


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    app = Application(sys.argv)
    app.main()
