#!/usr/bin/env python3
import locale
import logging
import os
import shutil
import subprocess
import sys
import threading
import time

from BlurWindow.blurWindow import GlobalBlur
from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

import attachments
import widgets


class MainWindow(QtWidgets.QMainWindow):
    """App window instance"""
    __mount_category_buttons_signal = QtCore.Signal(object)
    __mount_recent_apps_signal = QtCore.Signal(object)
    __mount_pin_apps_signal = QtCore.Signal(object)
    __mount_energy_buttons_signal = QtCore.Signal(object)
    __app_launcher_focus_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.
        """
        super().__init__(*args, **kwargs)
        self.__set_style()

        self.__menu_schema = None
        self.__status_bar_default_text = None
        self.__energy_buttons_schema = None
        self.__active_context_menu_app_launcher = None

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

        # Header
        self.__header_layout = QtWidgets.QHBoxLayout()
        self.__header_layout.set_contents_margins(10, 0, 10, 0)
        self.__header_layout.set_spacing(5)
        self.__header_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__layout_container.add_layout(self.__header_layout)

        # Settings
        self.__settings_button = widgets.ActionButton(
            icon_name='configure', text='Menu settings')
        self.__settings_button.set_contents_margins(0, 0, 0, 0)
        # self.__settings_button.clicked_signal().connect(
        #     lambda widget: self.__on_full_screen_button(widget))
        self.__settings_button.enter_event_signal().connect(
            lambda widget: self.__on_action_button_enter_event(widget))
        self.__settings_button.leave_event_signal().connect(
            lambda _: self.__on_action_button_leave_event())
        self.__header_layout.add_widget(self.__settings_button)

        # Search input
        self.__search_input = widgets.SearchApps()
        self.__search_input.set_placeholder_text('Type to search')
        self.__search_input.set_alignment(QtCore.Qt.AlignHCenter)
        self.__search_input.text_changed_signal().connect(
            self.__on_search_input)
        self.__header_layout.add_widget(self.__search_input)

        self.__app_launcher_focus_signal.connect(
            lambda sender_id: self.__apps_launcher_focus(sender_id))

        # Fullscreen
        self.__full_screen_button = widgets.ActionButton(
            icon_name='view-restore', text='Exit full screen')
        self.__full_screen_button.set_contents_margins(0, 0, 0, 0)
        self.__full_screen_button.clicked_signal().connect(
            lambda widget: self.__on_full_screen_button(widget))
        self.__full_screen_button.enter_event_signal().connect(
            lambda widget: self.__on_action_button_enter_event(widget))
        self.__full_screen_button.leave_event_signal().connect(
            lambda _: self.__on_action_button_leave_event())
        self.__header_layout.add_widget(self.__full_screen_button)

        # Close
        self.__close_window_button = widgets.ActionButton(
            icon_name='edit-delete-remove', text='Close this menu')
        self.__close_window_button.set_contents_margins(0, 0, 0, 0)
        self.__close_window_button.clicked_signal().connect(
            lambda _: self.close())
        self.__close_window_button.enter_event_signal().connect(
            lambda widget: self.__on_action_button_enter_event(widget))
        self.__close_window_button.leave_event_signal().connect(
            lambda _: self.__on_action_button_leave_event())
        # self.__header_layout.add_widget(self.__close_window_button)

        # Body layout
        self.__body_layout = QtWidgets.QHBoxLayout()
        self.__body_layout.set_contents_margins(0, 0, 0, 0)
        self.__body_layout.set_spacing(0)
        self.__body_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__layout_container.add_layout(self.__body_layout)

        # Category buttons layout
        self.__active_category_button = None
        self.__category_buttons_layout = QtWidgets.QVBoxLayout()
        self.__category_buttons_layout.set_contents_margins(0, 0, 0, 0)
        self.__category_buttons_layout.set_spacing(0)
        self.__category_buttons_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.__body_layout.add_layout(self.__category_buttons_layout)

        self.__mount_category_buttons_signal.connect(
            self.__mount_category_buttons)

        category_buttons_thread = threading.Thread(
            target=self.__mount_category_buttons_bg)
        category_buttons_thread.start()

        # Apps layout
        self.__stack_grids = {}
        self.__app_grid_stacked_layout = QtWidgets.QStackedLayout()
        self.__app_grid_stacked_layout.set_contents_margins(0, 0, 0, 0)
        self.__app_grid_stacked_layout.set_spacing(0)
        self.__app_grid_stacked_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__body_layout.add_layout(self.__app_grid_stacked_layout)

        # Searched apps page (temp 0 index)
        self.__app_grid_stacked_layout.add_widget(QtWidgets.QWidget())

        # Home page: Recents and Pin's
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

        # Home page: Recent
        self.__recent_apps = attachments.SavedApps(config_name='recent-apps')

        self.__mount_recent_apps_signal.connect(self.__mount_recent_apps)

        self.__mount_recent_apps_thread = threading.Thread(
            target=self.__mount_recent_apps_bg)

        # Home page: Pin's
        self.__pin_update_index = 0
        self.__pin_apps = attachments.SavedApps(config_name='pin-apps')

        self.__mount_pin_apps_signal.connect(self.__mount_pin_apps)

        self.__mount_pin_apps_thread = threading.Thread(  # start() on 'recent'
            target=self.__mount_pin_apps_bg)

        # App pages
        self.__app_page_created = []

        # Energy buttons layout
        self.__energy_buttons_pages_have_been_created = False
        self.__energy_buttons_layout = QtWidgets.QVBoxLayout()
        self.__energy_buttons_layout.set_contents_margins(20, 0, 20, 0)
        self.__energy_buttons_layout.set_spacing(5)
        self.__energy_buttons_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.__body_layout.add_layout(self.__energy_buttons_layout)

        self.__mount_energy_buttons_signal.connect(self.__mount_energy_buttons)

        self.__energy_buttons_thread = threading.Thread(  # start() on
            target=self.__mount_energy_buttons_bg)    # 'pin' thread

        # Status bar
        self.__status_bar_temp_text = None
        self.__status_bar = QtWidgets.QLabel(self.__status_bar_temp_text)
        self.__status_bar.set_word_wrap(True)
        self.__status_bar.set_fixed_height(50)
        self.__status_bar.set_alignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.__status_bar.set_style_sheet(
            'background-color: rgba(0, 0, 0, 0.1);'
            'font-size: 13px;'
            'border-top: 1px solid rgba(255, 255, 255, 0.03);'
            'padding-left: 10px;')
        self.__layout_container.add_widget(self.__status_bar)
        self.set_focus()
        self.install_event_filter(self)

    def __set_style(self) -> None:
        # Adds CSS styling to the main window
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static/style.qss')

        with open(style_path, 'r') as style_qss_file:
            style_qss = style_qss_file.read()
            self.set_style_sheet(style_qss)

    def __mount_category_buttons_bg(self) -> None:
        # Wait for pin apps to render and mount category buttons
        time.sleep(0.15)
        self.__mount_category_buttons_signal.emit(0)

    def __mount_category_buttons(self) -> None:
        # Mount category buttons

        # Menu schema
        self.__menu_schema = attachments.MenuSchema()
        menu_schema = self.__menu_schema.schema

        # Update number_of_apps
        self.__status_bar_default_text = str(
            len(self.__menu_schema.schema['All'])) + " app's"
        self.__status_bar.set_text(self.__status_bar_default_text)

        # Buttons
        page_index = 1
        for categ, apps in menu_schema.items():
            if not apps and categ != 'Home' or categ == 'All':
                continue
            category_button = widgets.CategoryButton(
                text=categ, icon_name=self.__menu_schema.icons_schema[categ])
            setattr(category_button, 'page_index', page_index)
            setattr(category_button, 'category', categ)
            category_button.set_contents_margins(0, 0, 10, 0)
            category_button.clicked_signal().connect(self.__on_category_button)
            self.__category_buttons_layout.add_widget(category_button)

            self.__app_grid_stacked_layout.add_widget(QtWidgets.QWidget())
            page_index += 1

        # First item focus (Category button: Home)
        first_button = self.__category_buttons_layout.item_at(0).widget()
        first_button.set_check_state(state=True)
        self.__active_category_button = first_button

        self.__mount_recent_apps_thread.start()

    def __mount_recent_apps_bg(self) -> None:
        # Wait for window to render and mount recent app launchers
        time.sleep(0.03)
        self.__mount_recent_apps_signal.emit(0)

    def __mount_recent_apps(self) -> None:
        # Mount recent app launchers
        self.__mount_home_page_apps(
            desktop_file_list=self.__recent_apps.apps,
            home_page_type='recent',
            title='Recents')

        # Pin apps
        self.__app_grid_stacked_layout.set_current_index(1)
        self.__mount_pin_apps_thread.start()

    def __mount_pin_apps_bg(self) -> None:
        # Wait for recent apps to render and mount pin app launchers
        time.sleep(0.03)
        self.__mount_pin_apps_signal.emit(0)

    def __mount_pin_apps(self) -> None:
        # Mount pin app launchers

        self.__mount_home_page_apps(
            desktop_file_list=self.__pin_apps.apps,
            home_page_type='pin',
            title="Pin's")

        # Category buttons
        if not self.__energy_buttons_pages_have_been_created:
            self.__energy_buttons_thread.start()
            self.__energy_buttons_pages_have_been_created = True

        self.__app_page_created.append('Home')

    def __mount_home_page_apps(
            self,
            desktop_file_list: list,
            home_page_type: str = 'pin',
            title: str = None,
            ) -> widgets.AppGrid:

        page_layout = self.__home_page_layout
        empty_lines = 1 if home_page_type == 'pin' else 2
        page_layout_stretch = 6 if home_page_type == 'pin' else 4

        title_label = QtWidgets.QLabel(title)
        title_label.set_contents_margins(10, 10, 0, 10)
        title_label.set_alignment(QtCore.Qt.AlignLeft)
        title_label.set_style_sheet(
            'background: transparent; font-size: 20px;')
        page_layout.add_widget(title_label)

        # App grid
        app_grid = widgets.AppGrid(
            desktop_file_list=desktop_file_list,
            pin_desktop_file_list=self.__pin_apps.apps,
            columns_num=self.__app_grid_columns,
            empty_lines=empty_lines)

        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher(widget))
        app_grid.right_clicked_signal().connect(
            lambda widget: self.__on_app_launcher_right_click(widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event(widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event())

        app_grid.set_alignment(QtCore.Qt.AlignTop)
        page_layout.add_widget(app_grid, page_layout_stretch)
        return app_grid

    def __mount_energy_buttons_bg(self) -> None:
        # Wait for category buttons to render and mount energy buttons
        time.sleep(0.03)
        self.__mount_energy_buttons_signal.emit(0)

    def __mount_energy_buttons(self) -> None:
        # Mount energy buttons

        self.__energy_buttons_schema = attachments.EnergyButtonsSchema()
        for name_id, values in self.__energy_buttons_schema.schema.items():
            energy_button = widgets.EnergyButton(
                icon_name=values['icon-name'],
                text=values['text'],
                name_id=name_id)
            energy_button.clicked_signal().connect(
                lambda widget: self.__on_energy_buttons(widget))
            energy_button.enter_event_signal().connect(
                lambda widget: self.__on_energy_buttons_enter_event(widget))
            energy_button.leave_event_signal().connect(
                lambda _: self.__on_energy_buttons_leave_event())
            self.__energy_buttons_layout.add_widget(energy_button)

    def __mount_app_category_pages(
            self, desktop_file_list: list, index: int) -> widgets.AppGrid:
        page = QtWidgets.QWidget()
        page.set_contents_margins(0, 0, 0, 0)
        page.set_style_sheet('background: transparent;')
        # self.__app_grid_stacked_layout.add_widget(page)
        self.__app_grid_stacked_layout.insert_widget(index, page)

        page_layout = QtWidgets.QVBoxLayout()
        page_layout.set_contents_margins(0, 0, 0, 0)
        page_layout.set_spacing(0)
        page.set_layout(page_layout)

        # App grid
        app_grid = widgets.AppGrid(
            desktop_file_list=desktop_file_list,
            pin_desktop_file_list=self.__pin_apps.apps,
            columns_num=self.__app_grid_columns,
            empty_lines=0)

        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher(widget))
        app_grid.right_clicked_signal().connect(
            lambda widget: self.__on_app_launcher_right_click(widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event(widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event())

        app_grid.set_alignment(QtCore.Qt.AlignTop)
        page_layout.add_widget(app_grid, -1)
        return app_grid

    def __on_search_input(self, text: str) -> None:
        # Triggered when text is entered into the search box
        if text:
            if self.__category_buttons_layout.item_at(0).widget().is_enabled():
                self.__show_searched_apps_page(show=True)

            desktop_file_list = self.__searched_apps(text=text)
            if desktop_file_list:
                grid = self.__mount_searched_apps_grid(
                    desktop_file_list=desktop_file_list)
                self.__stack_grids['search'] = grid

                app_launcher_focus_thread = threading.Thread(
                    target=self.__app_launcher_focus_bg, args=['search'])
                app_launcher_focus_thread.start()
            else:
                self.__mount_empty_searched_apps_grid()

        else:  # Restore default menu layout
            self.__show_searched_apps_page(show=False)

    def __app_launcher_focus_bg(self, sender_id: str) -> None:
        time.sleep(0.7)
        self.__app_launcher_focus_signal.emit(sender_id)

    def __apps_launcher_focus(self, sender_id: str) -> None:
        if self.__stack_grids[sender_id].widgets_list():
            self.__stack_grids[sender_id].widgets_list()[0].set_focus()

    def __searched_apps(self, text: str) -> list:
        # Searched app list [DesktopFile, DesktopFile]
        desktop_files = []
        local = locale.getdefaultlocale()[0]
        escope = '[Desktop Entry]'
        for desk_app in self.__menu_schema.schema['All']:

            # Name[<local>]
            if (f'Name[{local}]' in desk_app.content[escope]
                    and text in desk_app.content[escope][
                        f'Name[{local}]'].lower()):
                desktop_files.append(desk_app)

            # Name: Always exists
            elif text in desk_app.content[escope]['Name'].lower():
                desktop_files.append(desk_app)

            # GenericName[<local>]
            elif (f'GenericName[{local}]' in desk_app.content[escope]
                  and text in desk_app.content[escope][
                      f'GenericName[{local}]'].lower()):
                desktop_files.append(desk_app)

            # GenericName
            elif ('GenericName' in desk_app.content[escope]
                  and text in desk_app.content[escope][
                      'GenericName'].lower()):
                desktop_files.append(desk_app)

            # Coment[<local>]
            elif (f'Comment[{local}]' in desk_app.content[escope]
                  and text in desk_app.content[escope][
                      f'Comment[{local}]'].lower()):
                desktop_files.append(desk_app)

            # Coment
            elif ('Comment' in desk_app.content[escope]
                  and text in desk_app.content[escope]['Comment'].lower()):
                desktop_files.append(desk_app)

            # Exec: Always exists
            elif text in desk_app.content[escope]['Exec'].lower():
                desktop_files.append(desk_app)

        return desktop_files

    def __mount_searched_apps_grid(
            self, desktop_file_list: list) -> widgets.AppGrid:
        # Searched app grid

        # Total apps per search
        total_apps_per_search = self.__app_grid_columns * 4
        if len(desktop_file_list) > total_apps_per_search:
            desktop_file_list = (
                desktop_file_list[:total_apps_per_search])

        # Clear old apps page
        self.__app_grid_stacked_layout.set_current_index(0)
        self.__app_grid_stacked_layout.remove_widget(
            self.__app_grid_stacked_layout.current_widget())

        # Create new apps page
        app_grid = widgets.AppGrid(
            desktop_file_list=desktop_file_list,
            pin_desktop_file_list=self.__pin_apps.apps,
            columns_num=self.__app_grid_columns)
        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher(widget))
        app_grid.right_clicked_signal().connect(
            lambda widget: self.__on_app_launcher_right_click(widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event(widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event())
        app_grid.set_alignment(QtCore.Qt.AlignTop)

        # Insert new apps page
        self.__app_grid_stacked_layout.insert_widget(0, app_grid)
        self.__app_grid_stacked_layout.set_current_index(0)

        return app_grid

    def __mount_empty_searched_apps_grid(self) -> None:
        # Clear old apps page
        self.__app_grid_stacked_layout.set_current_index(0)
        self.__app_grid_stacked_layout.remove_widget(
            self.__app_grid_stacked_layout.current_widget())

        # Message
        no_apps_message = QtWidgets.QLabel('No apps found!')
        no_apps_message.set_alignment(QtCore.Qt.AlignCenter)
        no_apps_message.set_style_sheet(
            'background: transparent; font-size: 30px;')

        # Insert message
        self.__app_grid_stacked_layout.insert_widget(
            0, no_apps_message)
        self.__app_grid_stacked_layout.set_current_index(0)

    def __show_searched_apps_page(self, show: bool) -> None:
        # Back to home category (Recents and Pin's)
        first_button = self.__category_buttons_layout.item_at(0).widget()
        if not first_button.check_state():
            first_button.clicked_signal().emit(0)

        # Show 'Searched apps' page
        self.__app_grid_stacked_layout.set_current_index(
            0 if show else 1)

        # Block Category buttons and Energy buttons
        enabled_status = False if show else True
        for index in range(self.__category_buttons_layout.count()):
            item = self.__category_buttons_layout.item_at(index)
            item.widget().set_enabled(enabled_status)
            item.widget().set_enter_event_enabled(enabled_status)

        for index in range(self.__energy_buttons_layout.count()):
            item = self.__energy_buttons_layout.item_at(index)
            item.widget().set_enabled(enabled_status)
            item.widget().set_enter_event_enabled(enabled_status)

    def __on_full_screen_button(self, widget: widgets.ActionButton) -> None:
        # Fullscreen
        if widget.icon_name() == 'view-fullscreen':
            widget.set_icon_name('view-restore')
            widget.set_text('Exit full screen')
            self.show_full_screen()
        else:
            widget.set_icon_name('view-fullscreen')
            widget.set_text('Enter full screen')
            self.show_maximized()

    def __on_action_button_enter_event(
            self, widget: widgets.ActionButton) -> None:
        # Add status bar information about this button
        self.__status_bar.set_text(widget.text())

    def __on_action_button_leave_event(self) -> None:
        # Clear status bar
        self.__status_bar.set_text(self.__status_bar_default_text)

    def __close_active_context_menus(self):
        # Close context menus
        if self.__active_context_menu_app_launcher:
            (self.__active_context_menu_app_launcher
                .set_context_menu_to_visible(visible=False))

    def __on_category_button(self) -> None:
        # When mouse cursor hovers over category button
        self.__close_active_context_menus()

        # Active category button state (highlight fixed)
        if self.__active_category_button:
            self.__active_category_button.set_check_state(state=False)
        self.__active_category_button = self.sender()
        self.__active_category_button.set_check_state(state=True)

        category = self.__active_category_button.category
        index = self.__active_category_button.page_index
        if category not in self.__app_page_created:
            # Clear old apps page
            self.__app_grid_stacked_layout.set_current_index(index)
            self.__app_grid_stacked_layout.remove_widget(
                self.__app_grid_stacked_layout.current_widget())

            # Creat new apps page
            grid = self.__mount_app_category_pages(
                desktop_file_list=self.__menu_schema.schema[category],
                index=index)

            # Update grid list
            self.__stack_grids[category] = grid
            # Update page list
            self.__app_page_created.append(category)

            self.__active_category_button.clicked_signal().emit(0)

        # Show page
        self.__app_grid_stacked_layout.set_current_index(index)

    def __on_app_launcher(
            self,
            widget:
            widgets.AppLauncher |
            widgets.GhostAppLauncher |
            widgets.AppLauncherContextMenuButton) -> None:
        # When the app is clicked, this method is triggered

        # AppLauncher
        if isinstance(widget, widgets.AppLauncher):
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

            # Exec
            exe = widget.desktop_file().content['[Desktop Entry]']['Exec']
            exec_command = exe.split(' %', 1)[0] if ' %' in exe else exe
            subprocess.Popen(exec_command.strip().strip('"').strip().split())
            print(widget)

        # Ghost AppLauncher
        elif isinstance(widget, widgets.GhostAppLauncher):
            print(widget)

        # Context menu button
        elif isinstance(widget, widgets.AppLauncherContextMenuButton):
            self.__on_app_launcher_context_menu_buttons(widget=widget)
            print(widget)
            return

        print('<QtWidgets.QMainWindow: close>')
        self.close()

    def __on_app_launcher_context_menu_buttons(
            self, widget: widgets.AppLauncherContextMenuButton) -> None:
        # Context menu buttons management
        if widget.button_id() == 'go-back':
            self.__on_app_launcher_go_back_context_menu_button()

        elif widget.button_id() == 'pin':
            self.__on_app_launcher_pin_context_menu_button()

        elif widget.button_id() == 'unpin':
            self.__on_app_launcher_unpin_context_menu_button()

        elif widget.button_id() == 'shortcut':
            self.__on_app_launcher_shortcut_context_menu_button()

    def __on_app_launcher_go_back_context_menu_button(self) -> None:
        # Go back

        # Reset status bar text
        self.__status_bar.set_text(self.__status_bar_temp_text)
        # Close active context menu
        self.__close_active_context_menus()

    def __on_app_launcher_pin_context_menu_button(self) -> None:
        # Pin's

        # Toggle pin button
        self.__active_context_menu_app_launcher.toggle_pin_button()

        # Insert fav app on app list
        if (self.__active_context_menu_app_launcher.desktop_file()
                not in self.__pin_apps.apps):
            self.__pin_apps.apps.insert(
                0, self.__active_context_menu_app_launcher.desktop_file())

            # Save configs
            self.__pin_apps.save_apps(url_list_apps=[
                x.url for x in self.__pin_apps.apps])

        # Hide old pin apps
        self.__pin_update_index += 2
        self.__home_page_layout.item_at(
            self.__pin_update_index).widget().set_visible(False)
        self.__home_page_layout.item_at(
            self.__pin_update_index + 1).widget().set_visible(False)

        # Render new app list
        self.__mount_pin_apps()

        self.__close_active_context_menus()

    def __on_app_launcher_unpin_context_menu_button(self) -> None:
        # Unpin

        # Toggle pin button
        self.__active_context_menu_app_launcher.toggle_pin_button()

        # Remove pin app on app list
        if (self.__active_context_menu_app_launcher.desktop_file()
                in self.__pin_apps.apps):
            self.__pin_apps.apps.remove(
                self.__active_context_menu_app_launcher.desktop_file())

            # Save configs
            self.__pin_apps.save_apps(url_list_apps=[
                x.url for x in self.__pin_apps.apps])

        # Hide old pin apps
        self.__pin_update_index += 2
        self.__home_page_layout.item_at(
            self.__pin_update_index).widget().set_visible(False)
        self.__home_page_layout.item_at(
            self.__pin_update_index + 1).widget().set_visible(False)

        # Render new app list
        self.__mount_pin_apps()

        self.__close_active_context_menus()

    def __on_app_launcher_shortcut_context_menu_button(self) -> None:
        # Desktop: default
        desktop_path = os.path.join(os.environ['HOME'], 'Desktop')

        # Desktop: XDG_DESKTOP_DIR
        user_dirs_file = os.path.join(
            os.environ['HOME'], '.config', 'user-dirs.dirs')
        if os.path.isfile(user_dirs_file):
            with open(user_dirs_file, 'r') as dirs_file:
                dirs_file_lines = dirs_file.readlines()

            for line in dirs_file_lines:
                if 'XDG_DESKTOP_DIR=' in line:
                    desktop_path = line.split('=')[1].strip().strip('"')

        # Source and destination
        source = self.__active_context_menu_app_launcher.desktop_file().url
        destination = os.path.join(
            desktop_path.replace('$HOME', os.environ['HOME']),
            os.path.basename(source))

        # Copy shortcut to desktop
        if not os.path.isfile(destination):
            shutil.copyfile(source, destination)

            # Make shortcut executable
            executable_command = subprocess.Popen(
                ['chmod', '+x', destination],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _stdout, _stderr = executable_command.communicate()

        self.__close_active_context_menus()

    def __on_app_launcher_right_click(
            self, widget: widgets.AppLauncher) -> None:
        # App launcher right click

        # Save status bar text
        self.__status_bar_temp_text = self.__status_bar.text()

        # Show context menu
        if not widget.context_menu_is_visible():
            self.__close_active_context_menus()

            widget.set_context_menu_to_visible(True)

            widget.app_launcher_context_menu().enter_event_signal().connect(
                self.__on_app_launcher_context_menu_enter_event)

            # Save widget
            self.__active_context_menu_app_launcher = widget

            # Toggle pin button
            if widget.desktop_file() not in self.__pin_apps.apps:
                # If widget is not a pin app and 'unpin' is showed...
                if not widget.app_launcher_context_menu(
                        ).pin_button_is_visible():
                    # ... else show the 'pin' button
                    self.__active_context_menu_app_launcher.toggle_pin_button()

        print(widget, '<QtCore.Qt.RightButton>')

    def __on_app_launcher_context_menu_enter_event(
            self, widget: widgets.AppLauncherContextMenuButton) -> None:
        # Add status bar context menu info

        # Show in the status bar more information about the context menu ...
        # ...button that the mouse hovers over
        if widget.button_id() == 'go-back':
            self.__status_bar.set_text(
                'Closes the context menu and returns to application view')
        elif widget.button_id() == 'pin':
            self.__status_bar.set_text(
                "Pin application on menu home page, in the Pin's section")
        elif widget.button_id() == 'unpin':
            self.__status_bar.set_text(
                "Unpin the application from the menu home page under the "
                "Pin's section")
        elif widget.button_id() == 'shortcut':
            self.__status_bar.set_text('Create an app shortcut on the desktop')
        elif widget.button_id() == 'hide':
            self.__status_bar.set_text('Hide app from menu')

    def __on_app_launcher_enter_event(
            self, widget: widgets.AppLauncher) -> None:
        # Add status bar information about the app

        # Language code
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

    def __on_app_launcher_leave_event(self) -> None:
        # Clear status bar
        self.__status_bar.set_text(self.__status_bar_default_text)

    def __on_energy_buttons(self, widget: widgets.EnergyButton) -> None:
        # When one energy button is clicked
        for name_id, values in self.__energy_buttons_schema.schema.items():
            if widget.name_id() == name_id:
                if values['command']:
                    command = subprocess.Popen(
                        values['command'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _stdout, _stderr = command.communicate()

                print(widget)
                break

        print('<QtWidgets.QMainWindow: close>')
        self.close()

    def __on_energy_buttons_enter_event(
            self, widget: widgets.EnergyButton) -> None:
        # Add status bar information about this energy button
        self.__status_bar.set_text(widget.text())

    def __on_energy_buttons_leave_event(self) -> None:
        # Clear status bar
        self.__status_bar.set_text(self.__status_bar_default_text)

    def event_filter(
            self, widget: QtWidgets.QMainWindow, event: QtCore.QEvent) -> None:
        """Traces the keys

        Used to manipulate keys and shortcuts.

        :param widget: QMainWindow that receives the event
        :param event: QEvent that captures keyboard keys
        """
        if event.type() == QtCore.QEvent.KeyPress and widget is self:
            key = event.key()
            text = event.text()

            if key == QtCore.Qt.Key_Escape:
                self.__search_input.clear()
                # text = ''  # Fix espace

            elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
                focus_widget = QtWidgets.QApplication.focus_widget()
                if isinstance(focus_widget, widgets.AppLauncher):
                    self.__on_app_launcher(widget=focus_widget)

            elif key == QtCore.Qt.Key_Backspace:
                self.__search_input.set_text(self.__search_input.text()[:-1])

            elif key != QtCore.Qt.Key_Tab:
                self.__search_input.set_text(self.__search_input.text() + text)
            self.__search_input.deselect()

        return QtWidgets.QWidget.event_filter(self, widget, event)

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget

        Emits a signal that the widget has been clicked.

        :param event: QEvent that captures keyboard keys
        """
        if event.button() == QtCore.Qt.LeftButton:
            print('<QtWidgets.QMainWindow: close>')
            self.close()


class Application(object):
    """Desktop menu for Linux written in Python and Qt"""
    def __init__(self, args: list) -> None:
        """Class constructor

        Initialize class attributes.

        :param args: List of command line arguments
        """
        self.__application = QtWidgets.QApplication(args)
        self.__application_name = 'Menu'
        self.__application_icon = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static', 'grid.svg')
        self.__application_window = MainWindow()

    def main(self) -> None:
        """Start the app

        Sets basic window details and starts the application.
        """
        # Name
        self.__application_window.set_window_title(self.__application_name)

        # Icon
        app_icon = QtGui.QIcon(QtGui.QPixmap(self.__application_icon))
        self.__application_window.set_window_icon(app_icon)

        # Size
        self.__application_window.set_minimum_height(650)
        self.__application_window.set_minimum_width(1100)

        # Blur
        self.__application_window.set_attribute(
            QtCore.Qt.WA_TranslucentBackground)
        GlobalBlur(self.__application_window.win_id(), Dark=True, QWidget=self)

        # Show | show_maximized show_full_screen show
        self.__application_window.show_full_screen()
        sys.exit(self.__application.exec())


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    app = Application(sys.argv)
    app.main()
