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
    """App window instance"""
    __mount_category_buttons_signal = QtCore.Signal(object)
    __mount_recent_apps_signal = QtCore.Signal(object)
    __mount_pin_apps_signal = QtCore.Signal(object)
    __mount_apps_signal = QtCore.Signal(object)
    __mount_energy_buttons_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.
        """
        super().__init__(*args, **kwargs)
        self.__set_style()
        self.__menu_schema = None
        self.__active_context_app_launcher = None

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

        # Search input
        self.__search_input = widgets.SearchApps()
        self.__search_input.set_contents_margins(200, 0, 200, 0)
        self.__search_input.set_placeholder_text('Type to search')
        self.__search_input.set_alignment(QtCore.Qt.AlignHCenter)
        self.__search_input.text_changed_signal().connect(
            self.__on_search_input)
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

        self.__mount_category_buttons_signal.connect(
            self.__mount_category_buttons)

        self.__category_buttons_thread = threading.Thread(  # start() on
            target=self.__mount_category_buttons_thread)    # 'pin' thread

        # Apps layout
        self.__app_grid_stacked_layout = QtWidgets.QStackedLayout()
        self.__app_grid_stacked_layout.set_contents_margins(0, 0, 0, 0)
        self.__app_grid_stacked_layout.set_spacing(0)
        self.__app_grid_stacked_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__app_pagination_layout.add_layout(self.__app_grid_stacked_layout)

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
        self.__recent_apps_thread = threading.Thread(
            target=self.__mount_recent_apps_thread)
        self.__recent_apps_thread.start()

        # Home page: Pin's
        self.__pin_update_index = 0
        self.__pin_apps = attachments.SavedApps(config_name='pin-apps')
        self.__mount_pin_apps_signal.connect(self.__mount_pin_apps)
        self.__pin_apps_thread = threading.Thread(  # start() on 'recent'
            target=self.__mount_pin_apps_thread)    # thread

        # App pages
        self.__app_pages_created = False
        self.__mount_apps_signal.connect(self.__mount_apps)
        self.__apps_thread = threading.Thread(  # start() on category button
            target=self.__mount_apps_thread)

        # Energy buttons layout
        self.__energy_buttons_layout = QtWidgets.QVBoxLayout()
        self.__energy_buttons_layout.set_contents_margins(10, 0, 10, 0)
        self.__energy_buttons_layout.set_spacing(10)
        self.__energy_buttons_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.__app_pagination_layout.add_layout(self.__energy_buttons_layout)

        self.__mount_energy_buttons_signal.connect(self.__mount_energy_buttons)

        self.__energy_buttons_thread = threading.Thread(  # start() on
            target=self.__mount_energy_buttons_thread)    # 'pin' thread

        # Status bar
        self.__status_bar_temp_text = ' '
        self.__status_bar = QtWidgets.QLabel(self.__status_bar_temp_text)
        self.__status_bar.set_word_wrap(True)
        self.__status_bar.set_fixed_height(50)
        self.__status_bar.set_contents_margins(250, 10, 250, 5)
        self.__status_bar.set_alignment(QtCore.Qt.AlignTop)
        self.__status_bar.set_style_sheet(
            'background: transparent; font-size: 13px;')
        self.__layout_container.add_widget(self.__status_bar)
        self.set_focus()
        self.install_event_filter(self)

    def __set_style(self) -> None:
        # Adds CSS styling to the main window
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static/style.qss')
        with open(style_path, 'r') as f:
            _style = f.read()
            self.set_style_sheet(_style)

    def __mount_recent_apps_thread(self) -> None:
        # Wait for window to render and mount recent app launchers
        time.sleep(0.05)
        self.__mount_recent_apps_signal.emit(0)

    def __mount_recent_apps(self) -> None:
        # Mount recent app launchers

        # Category buttons pagination
        category_button = widgets.CategoryButton(
            text='Home',
            icon_name='applications-all')
        setattr(category_button, 'page_index', 1)
        setattr(category_button, 'category', 'home')
        category_button.set_check_state(state=True)
        self.__active_category_button = category_button
        category_button.clicked_signal().connect(self.__on_category_button)
        self.__category_buttons_layout.add_widget(category_button)

        # Title
        title = QtWidgets.QLabel('Recents')
        title.set_contents_margins(10, 10, 0, 10)
        title.set_alignment(QtCore.Qt.AlignLeft)
        title.set_style_sheet(
            'background: transparent; font-size: 20px;')
        self.__home_page_layout.add_widget(title)

        # App grid
        app_grid = widgets.AppGrid(
            desktop_file_list=self.__recent_apps.apps,
            pin_desktop_file_list=self.__pin_apps.apps,
            columns_num=self.__app_grid_columns,
            empty_lines=1)
        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher(widget))
        app_grid.right_clicked_signal().connect(
            lambda widget: self.__on_app_launcher_right_click(widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event(widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event())
        app_grid.set_alignment(QtCore.Qt.AlignTop)
        self.__home_page_layout.add_widget(app_grid, 4)
        # self.home_page_layout.add_stretch(1)

        # Pin apps
        self.__app_grid_stacked_layout.set_current_index(1)
        self.__pin_apps_thread.start()

    def __mount_pin_apps_thread(self) -> None:
        # Wait for recent apps to render and mount pin app launchers
        time.sleep(0.05)
        self.__mount_pin_apps_signal.emit(0)

    def __mount_pin_apps(self) -> None:
        # Mount pin app launchers

        # Title
        title = QtWidgets.QLabel("Pin's")
        title.set_contents_margins(10, 10, 0, 10)
        title.set_alignment(QtCore.Qt.AlignLeft)
        title.set_style_sheet(
            'background: transparent; font-size: 20px;')
        self.__home_page_layout.add_widget(title)

        # App grid
        app_grid = widgets.AppGrid(
            desktop_file_list=self.__pin_apps.apps,
            pin_desktop_file_list=self.__pin_apps.apps,
            columns_num=self.__app_grid_columns,
            empty_lines=2)
        app_grid.clicked_signal().connect(
            lambda widget: self.__on_app_launcher(widget))
        app_grid.right_clicked_signal().connect(
            lambda widget: self.__on_app_launcher_right_click(widget))
        app_grid.enter_event_signal().connect(
            lambda widget: self.__on_app_launcher_enter_event(widget))
        app_grid.leave_event_signal().connect(
            lambda _: self.__on_app_launcher_leave_event())
        app_grid.set_alignment(QtCore.Qt.AlignTop)
        self.__home_page_layout.add_widget(app_grid, 6)

        # Category buttons
        try:
            self.__category_buttons_thread.start()
        except Exception as err:
            print(type(err))

    def __mount_category_buttons_thread(self) -> None:
        # Wait for pin apps to render and mount category buttons
        time.sleep(0.05)
        self.__mount_category_buttons_signal.emit(0)

    def __mount_category_buttons(self) -> None:
        # Mount category buttons
        self.__menu_schema = attachments.MenuSchema()

        page_index = 2
        for categ, apps in self.__menu_schema.schema.items():
            if not apps or categ == 'All':
                continue

            # Category buttons pagination
            category_button = widgets.CategoryButton(
                text=categ, icon_name=self.__menu_schema.icons_schema[categ])
            setattr(category_button, 'page_index', page_index)
            setattr(category_button, 'category', categ)
            category_button.clicked_signal().connect(self.__on_category_button)
            self.__category_buttons_layout.add_widget(category_button)

            page_index += 1

        self.__energy_buttons_thread.start()

    def __mount_energy_buttons_thread(self) -> None:
        # Wait for category buttons to render and mount energy buttons
        time.sleep(0.05)
        self.__mount_energy_buttons_signal.emit(0)

    def __mount_energy_buttons(self) -> None:
        # Mount energy buttons

        # Energy buttons
        lock_screen_button = widgets.EnergyButton('system-lock-screen')
        lock_screen_button.clicked_signal().connect(
            lambda widget: self.__on_energy_buttons(widget))
        self.__energy_buttons_layout.add_widget(lock_screen_button)

        log_out_button = widgets.EnergyButton('system-log-out')
        log_out_button.clicked_signal().connect(
            lambda widget: self.__on_energy_buttons(widget))
        self.__energy_buttons_layout.add_widget(log_out_button)

        system_suspend_button = widgets.EnergyButton('system-suspend')
        system_suspend_button.clicked_signal().connect(
            lambda widget: self.__on_energy_buttons(widget))
        self.__energy_buttons_layout.add_widget(system_suspend_button)

        # switch_user_button = widgets.EnergyButton('system-switch-user')
        # switch_user_button.clicked_signal().connect(
        #     lambda widget: self.__on_energy_buttons(widget))
        # self.energy_buttons_layout.add_widget(switch_user_button)

        reboot_button = widgets.EnergyButton('system-reboot')
        reboot_button.clicked_signal().connect(
            lambda widget: self.__on_energy_buttons(widget))
        self.__energy_buttons_layout.add_widget(reboot_button)

        shutdown_button = widgets.EnergyButton('system-shutdown')
        shutdown_button.clicked_signal().connect(
            lambda widget: self.__on_energy_buttons(widget))
        self.__energy_buttons_layout.add_widget(shutdown_button)

    def __mount_apps_thread(self) -> None:
        # Wait for render and mount app launchers
        time.sleep(0.05)
        self.__mount_apps_signal.emit(0)

    def __mount_apps(self) -> None:
        # Mount app launchers
        for categ, apps in self.__menu_schema.schema.items():
            if not apps or categ == 'All':
                continue

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
                desktop_file_list=apps,
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
            page_layout.add_widget(app_grid)

        self.__active_category_button.clicked_signal().emit(0)

    def __on_search_input(self, text: str) -> None:
        # Triggered when text is entered into the search box
        if text:
            if self.__category_buttons_layout.item_at(0).widget().is_enabled():
                self.__show_searched_apps_page(show=True)

            desktop_apps = []
            local = locale.getdefaultlocale()[0]
            escope = '[Desktop Entry]'
            for desk_app in self.__menu_schema.schema['All']:

                # Name[<local>]
                if (f'Name[{local}]' in desk_app.content[escope]
                        and text in desk_app.content[escope][
                            f'Name[{local}]'].lower()):
                    desktop_apps.append(desk_app)

                # Name: Always exists
                elif text in desk_app.content[escope]['Name'].lower():
                    desktop_apps.append(desk_app)

                # GenericName[<local>]
                elif (f'GenericName[{local}]' in desk_app.content[escope]
                      and text in desk_app.content[escope][
                            f'GenericName[{local}]'].lower()):
                    desktop_apps.append(desk_app)

                # GenericName
                elif ('GenericName' in desk_app.content[escope]
                        and text in desk_app.content[escope][
                          'GenericName'].lower()):
                    desktop_apps.append(desk_app)

                # Coment[<local>]
                elif (f'Comment[{local}]' in desk_app.content[escope]
                        and text in desk_app.content[escope][
                            f'Comment[{local}]'].lower()):
                    desktop_apps.append(desk_app)

                # Coment
                elif ('Comment' in desk_app.content[escope]
                        and text in desk_app.content[escope]['Comment']
                        .lower()):
                    desktop_apps.append(desk_app)

                # Exec: Always exists
                elif text in desk_app.content[escope]['Exec'].lower():
                    desktop_apps.append(desk_app)

            if desktop_apps:
                # Total apps per search
                total_apps_per_search = self.__app_grid_columns * 4
                if len(desktop_apps) > total_apps_per_search:
                    desktop_apps = desktop_apps[:total_apps_per_search]

                # Clear old apps page
                self.__app_grid_stacked_layout.set_current_index(0)
                self.__app_grid_stacked_layout.remove_widget(
                    self.__app_grid_stacked_layout.current_widget())

                # Create new apps page
                app_grid = widgets.AppGrid(
                    desktop_file_list=desktop_apps,
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

            else:
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

        else:  # Restore default menu layout
            self.__show_searched_apps_page(show=False)

    def __show_searched_apps_page(self, show: bool) -> None:
        # Back to home category (Recents and Pin's)
        first_button = self.__category_buttons_layout.item_at(
            0).widget()
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

    def __on_category_button(self) -> None:
        # When mouse cursor hovers over category button

        # Close context menus
        if self.__context_app_launcher:
            self.__context_app_launcher.set_context_menu_to_visible(False)

        # Active category button state (highlight fixed)
        if self.__active_category_button:
            self.__active_category_button.set_check_state(state=False)
        self.sender().set_check_state(state=True)
        self.__active_category_button = self.sender()

        # Create page
        if not self.__app_pages_created:
            self.__app_pages_created = True
            self.__apps_thread.start()

        # Show page
        self.__app_grid_stacked_layout.set_current_index(
            self.sender().page_index)

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
            print(f'Run "AppLauncher: {widget.desktop_file()}" and close')

        # Ghost AppLauncher
        elif isinstance(widget, widgets.GhostAppLauncher):
            print(f'Run "GhostAppLauncher" and close')

        # Context menu button
        elif isinstance(widget, widgets.AppLauncherContextMenuButton):

            # Go back
            if widget.button_id() == 'go-back':
                # Reset status bar text
                self.__status_bar.set_text(self.__status_bar_temp_text)
                # Close active context menu
                self.__active_context_app_launcher.set_context_menu_to_visible(
                    False)
                return

            # Pin's
            elif widget.button_id() == 'pin':
                # Toggle pin button
                self.__context_app_launcher.toggle_pin_button()

                # Insert fav app on app list
                if (self.__context_app_launcher.desktop_file()
                        not in self.__pin_apps.apps):
                    self.__pin_apps.apps.insert(
                        0, self.__context_app_launcher.desktop_file())

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

                # Close active context menu
                self.__context_app_launcher.set_context_menu_to_visible(False)

                print('Context menu: Pin')
                return

            # !Pin's
            elif widget.button_id() == 'unpin':
                # Toggle pin button
                self.__context_app_launcher.toggle_pin_button()

                # Remove pin app on app list
                if (self.__context_app_launcher.desktop_file()
                        in self.__pin_apps.apps):
                    self.__pin_apps.apps.remove(
                        self.__context_app_launcher.desktop_file())

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

                # Close active context menu
                self.__context_app_launcher.set_context_menu_to_visible(False)

                print('Context menu: Unpin')
                return

            elif widget.button_id() == 'shortcut':
                print('Context menu: Shortcut')

            elif widget.button_id() == 'hide':
                print('Context menu: Hide')

        self.close()

    def __on_app_launcher_right_click(
            self, widget: widgets.AppLauncher) -> None:
        # When the app is clicked, this method is triggered
        print(f'Right click on "AppLauncher: {widget.desktop_file()}"')

        # Save status bar text
        self.__status_bar_temp_text = self.__status_bar.text()

        # Show context menu
        if not widget.context_menu_is_visible():
            if self.__active_context_app_launcher:  # Close other context menus
                self.__active_context_app_launcher.set_context_menu_to_visible(
                    False)

            widget.set_context_menu_to_visible(True)
            self.__active_context_app_launcher = widget

            widget.app_launcher_context_menu().enter_event_signal().connect(
                self.__on_app_launcher_context_menu_enter_event)

            # Save widget
            self.__context_app_launcher = widget

            # Toggle pin button
            if widget.desktop_file() not in self.__pin_apps.apps:
                # If widget is not a pin app and 'unpin' is showed...
                if not widget.app_launcher_context_menu(
                        ).pin_button_is_visible():
                    # ... else show the 'pin' button
                    self.__context_app_launcher.toggle_pin_button()

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
        # Add status bar app launcher info

        # Show more information about the app in the status bar when the ...
        # ...mouse hovers over the app launcher

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
        self.__status_bar.set_text(' ')

    def __on_energy_buttons(self, widget: widgets.EnergyButton) -> None:
        # When one energy button is clicked
        if widget.name_id() == 'system-lock-screen':
            print('Run "system-lock-screen" and close')
        elif widget.name_id() == 'system-log-out':
            print('Run "system-log-out" and close')
        elif widget.name_id() == 'system-suspend':
            print('Run "system-suspend" and close')
        elif widget.name_id() == 'system-switch-user':
            print('Run "system-switch-user" and close')
        elif widget.name_id() == 'system-reboot':
            print('Run "system-reboot" and close')
        elif widget.name_id() == 'system-shutdown':
            print('Run "system-shutdown" and close')
        self.close()

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
                print("Enter key pressed")
                # focus_widget = QtWidgets.QApplication.focus_widget()
                # if isinstance(focus_widget, widgets.AppLauncher):
                #     print(focus_widget)
                #     self.close()

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
            print('MainWindow close')
            self.close()


class Application(object):
    """Desktop menu for Linux written in Python and Qt"""
    def __init__(self, args: list) -> None:
        """Class constructor

        Initialize class attributes.

        :param args: List of command line arguments
        """
        self.__application = QtWidgets.QApplication(args)
        self.__application_icon = 'tuxmenu.png'
        self.__application_name = 'TuxMenu'
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
