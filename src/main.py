#!/usr/bin/env python3
import locale
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
    __mount_body_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.__set_style()

        # Main container
        self.__main_container = QtWidgets.QWidget()
        self.__main_container.set_contents_margins(0, 0, 0, 0)
        self.set_central_widget(self.__main_container)

        # Main layout
        self.__layout_container = QtWidgets.QVBoxLayout()
        self.__layout_container.set_contents_margins(0, 0, 0, 0)
        self.__layout_container.set_alignment(QtCore.Qt.AlignTop)
        self.__layout_container.set_spacing(0)
        self.__main_container.set_layout(self.__layout_container)

        # Search
        self.__search_input = widgets.SearchApps()
        self.__search_input.set_contents_margins(50, 0, 50, 0)
        self.__search_input.set_placeholder_text('Type to search')
        # self.search_input.set_read_only(True)
        self.__search_input.set_alignment(QtCore.Qt.AlignCenter)
        self.__layout_container.add_widget(self.__search_input)

        # App pagination layout
        self.__app_pagination_layout = QtWidgets.QHBoxLayout()
        self.__app_pagination_layout.set_contents_margins(0, 0, 0, 0)
        self.__app_pagination_layout.set_spacing(0)
        self.__app_pagination_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__layout_container.add_layout(self.__app_pagination_layout)

        # Category buttons layout
        self.__active_category_button = None
        self.__category_buttons_layout = QtWidgets.QVBoxLayout()
        self.__category_buttons_layout.set_contents_margins(0, 0, 0, 0)
        self.__category_buttons_layout.set_spacing(0)
        self.__category_buttons_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.__app_pagination_layout.add_layout(self.__category_buttons_layout)

        self.__app_grid_stacked_layout = QtWidgets.QStackedLayout()
        self.__app_grid_stacked_layout.set_contents_margins(0, 0, 0, 0)
        self.__app_grid_stacked_layout.set_spacing(0)
        self.__app_grid_stacked_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__app_pagination_layout.add_layout(self.__app_grid_stacked_layout)

        # Home grid page
        self.__app_grid_columns = 5

        self.__home_page_layout = QtWidgets.QVBoxLayout()
        self.__home_page_layout.set_contents_margins(0, 0, 0, 0)
        self.__home_page_layout.set_spacing(0)
        self.__home_page_layout.set_alignment(QtCore.Qt.AlignTop)

        self.__home_page_container = QtWidgets.QWidget()
        self.__home_page_container.set_contents_margins(0, 0, 0, 0)
        self.__home_page_container.set_style_sheet('background: transparent;')
        self.__app_grid_stacked_layout.add_widget(self.__home_page_container)
        self.__home_page_container.set_layout(self.__home_page_layout)

        self.__recent_apps = attachments.SavedApps(config_name='recent-apps')
        self.__mount_recent_apps_grid()

        self.__favorite_apps = attachments.SavedApps(
            config_name='favorite-apps')
        self.__mount_favorite_apps_grid()

        # Energy buttons layout
        self.__energy_buttons_layout = QtWidgets.QVBoxLayout()
        self.__energy_buttons_layout.set_contents_margins(10, 0, 10, 0)
        self.__energy_buttons_layout.set_spacing(10)
        self.__energy_buttons_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.__app_pagination_layout.add_layout(self.__energy_buttons_layout)

        # Grid pages thread
        self.__mount_body_signal.connect(self.__mount_body)
        self.__mount_body_thread = threading.Thread(
            target=self.__mount_body_thread)
        self.__mount_body_thread.start()

        # Status bar
        self.__status_bar = QtWidgets.QLabel(' ')
        self.__status_bar.set_word_wrap(True)
        self.__status_bar.set_fixed_height(50)
        self.__status_bar.set_contents_margins(250, 10, 250, 5)
        self.__status_bar.set_alignment(QtCore.Qt.AlignTop)
        self.__status_bar.set_style_sheet(
            'background: transparent; font-size: 13px;')
        self.__layout_container.add_widget(self.__status_bar)

    def __set_style(self):
        # Adds CSS styling to the main window
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static/style.qss')
        with open(style_path, 'r') as f:
            _style = f.read()
            self.set_style_sheet(_style)

    def __mount_recent_apps_grid(self):
        # ...

        # Category buttons pagination
        pagination_button = widgets.CategoryButton(
            text='Favorite',
            icon_name='preferences-desktop-default-applications')
        setattr(pagination_button, 'page_index', 0)
        pagination_button.set_check_state(state=True)
        self.__active_category_button = pagination_button
        pagination_button.clicked_signal().connect(self.__on_category_button)
        self.__category_buttons_layout.add_widget(pagination_button)

        # Title
        title = QtWidgets.QLabel('Recent')
        title.set_contents_margins(10, 10, 0, 10)
        title.set_alignment(QtCore.Qt.AlignLeft)
        title.set_style_sheet(
            'background: transparent; font-size: 20px;')
        self.__home_page_layout.add_widget(title)

        # App grid
        app_grid = widgets.AppGrid(
            desktop_file_list=self.__recent_apps.apps,
            columns_num=self.__app_grid_columns,
            empty_lines=1)
        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher_clicked_signal(
                widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event_signal(
                widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event_signal())
        app_grid.set_alignment(QtCore.Qt.AlignTop)
        self.__home_page_layout.add_widget(app_grid, 4)
        # self.home_page_layout.add_stretch(1)

    def __mount_favorite_apps_grid(self):
        # ...

        # Title
        title = QtWidgets.QLabel('Favorite')
        title.set_contents_margins(10, 10, 0, 10)
        title.set_alignment(QtCore.Qt.AlignLeft)
        title.set_style_sheet(
            'background: transparent; font-size: 20px;')
        self.__home_page_layout.add_widget(title)

        # App grid
        app_grid = widgets.AppGrid(
            desktop_file_list=self.__favorite_apps.apps,
            columns_num=self.__app_grid_columns,
            empty_lines=2)
        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher_clicked_signal(
                widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event_signal(
                widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event_signal())
        app_grid.set_alignment(QtCore.Qt.AlignTop)
        self.__home_page_layout.add_widget(app_grid, 6)

    def __mount_body_thread(self):
        # Wait for the main window to render to assemble the app grid
        time.sleep(0.05)
        self.__mount_body_signal.emit(0)

    def __mount_body(self):
        # Mount app grid
        menu_schema = attachments.MenuSchema()
        page_index = 1
        for categ, apps in menu_schema.schema.items():
            if not apps:
                continue
            apps.sort()
            # Category buttons pagination
            category_button = widgets.CategoryButton(
                text=categ, icon_name=menu_schema.icons_schema[categ])
            setattr(category_button, 'page_index', page_index)
            category_button.clicked_signal().connect(self.__on_category_button)
            self.__category_buttons_layout.add_widget(category_button)

            # Apps page
            page = QtWidgets.QWidget()
            page.set_contents_margins(0, 0, 0, 0)
            page.set_style_sheet('background: transparent;')
            self.__app_grid_stacked_layout.add_widget(page)

            page_layout = QtWidgets.QVBoxLayout()
            page_layout.set_contents_margins(0, 0, 0, 0)
            page_layout.set_spacing(0)
            page.set_layout(page_layout)

            # Title
            # title = QtWidgets.QLabel(categ)
            # title.set_contents_margins(10, 10, 0, 10)
            # title.set_alignment(QtCore.Qt.AlignLeft)
            # title.set_style_sheet(
            #     'background: transparent; font-size: 20px;')
            # page_layout.add_widget(title)

            # App grid
            app_grid = widgets.AppGrid(
                desktop_file_list=apps, columns_num=self.__app_grid_columns)
            app_grid.clicked_signal().connect(
                lambda widget: self.__on_app_launcher_clicked_signal(
                    widget))
            app_grid.enter_event_signal().connect(
                lambda widget: self.__on_app_launcher_enter_event_signal(
                    widget))
            app_grid.leave_event_signal().connect(
                lambda _: self.__on_app_launcher_leave_event_signal())
            app_grid.set_alignment(QtCore.Qt.AlignTop)
            page_layout.add_widget(app_grid)

            page_index += 1

        # Energy buttons
        lock_screen_button = widgets.EnergyButton('system-lock-screen')
        self.__energy_buttons_layout.add_widget(lock_screen_button)

        log_out_button = widgets.EnergyButton('system-log-out')
        self.__energy_buttons_layout.add_widget(log_out_button)

        system_suspend_button = widgets.EnergyButton('system-suspend')
        self.__energy_buttons_layout.add_widget(system_suspend_button)

        # switch_user_button = widgets.EnergyButton('system-switch-user')
        # self.energy_buttons_layout.add_widget(switch_user_button)

        reboot_button = widgets.EnergyButton('system-reboot')
        self.__energy_buttons_layout.add_widget(reboot_button)

        shutdown_button = widgets.EnergyButton('system-shutdown')
        self.__energy_buttons_layout.add_widget(shutdown_button)

    def __on_category_button(self):
        # Active category button state (highlight fixed)
        if self.__active_category_button:
            self.__active_category_button.set_check_state(state=False)
        self.sender().set_check_state(state=True)
        self.__active_category_button = self.sender()

        self.__app_grid_stacked_layout.set_current_index(
            self.sender().page_index)

    def __on_app_launcher_clicked_signal(self, widget):
        # When the app is clicked, this method is triggered
        if str(widget) != '<GhostAppLauncher: Boo>':
            # Save app in "Recents"
            if widget.desktop_file() in self.__recent_apps.apps:
                self.__recent_apps.apps.remove(widget.desktop_file())
            else:
                if self.__recent_apps.apps and (
                        len(self.__recent_apps.apps) >=
                        self.__app_grid_columns):
                    self.__recent_apps.apps.pop()
            self.__recent_apps.apps.insert(0, widget.desktop_file())
            self.__recent_apps.save_apps(
                url_list_apps=[x.url for x in self.__recent_apps.apps])
        self.close()

    def __on_app_launcher_enter_event_signal(self, widget):
        # Add status bar info
        local, escope = (locale.getdefaultlocale()[0], '[Desktop Entry]')

        # Name
        name = widget.desktop_file().content[escope]['Name']
        if f'Name[{local}]' in widget.desktop_file().content[escope]:
            name = widget.desktop_file().content[escope][f'Name[{local}]']

        # GenericName
        generic_name = ''
        if f'GenericName[{local}]' in widget.desktop_file().content[escope]:
            generic_name = widget.desktop_file().content[
                escope][f'GenericName[{local}]']
        elif 'GenericName' in widget.desktop_file().content[escope]:
            generic_name = widget.desktop_file().content[escope]['GenericName']

        # Coment
        coment = ''
        if f'Comment[{local}]' in widget.desktop_file().content[escope]:
            coment = widget.desktop_file().content[escope][f'Comment[{local}]']
        elif 'Comment' in widget.desktop_file().content[escope]:
            coment = widget.desktop_file().content[escope]['Comment']

        # Format text
        coment = (' | ' + coment if (
            coment and
            coment != name and
            coment != generic_name) else '')

        generic_name = (
            ': ' + generic_name
            if generic_name and generic_name != name else '')

        text = f'{name.strip(":").strip(".")}{generic_name}{coment}'
        self.__status_bar.set_text(text)

    def __on_app_launcher_leave_event_signal(self):
        self.__status_bar.set_text(' ')


class Application(object):
    """Desktop menu for Linux written in Python and Qt."""

    def __init__(self, args):
        """Class constructor."""
        self.__application = QtWidgets.QApplication(args)
        self.__application_icon = 'tuxmenu.png'
        self.__application_name = 'TuxMenu'
        self.__application_window = MainWindow()

    def main(self) -> None:
        """Start the app."""
        # Name
        self.__application_window.set_window_title(self.__application_name)

        # Icon
        app_icon = QtGui.QIcon(QtGui.QPixmap(self.__application_icon))
        self.__application_window.set_window_icon(app_icon)

        # Size
        self.__application_window.set_minimum_height(500)
        self.__application_window.set_minimum_width(500)

        # Blur
        self.__application_window.set_attribute(
            QtCore.Qt.WA_TranslucentBackground)
        GlobalBlur(self.__application_window.win_id(), Dark=True, QWidget=self)

        # Show | show_maximized show_full_screen show
        self.__application_window.show_maximized()
        sys.exit(self.__application.exec())


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    app = Application(sys.argv)
    app.main()
