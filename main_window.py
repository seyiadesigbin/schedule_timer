import webbrowser
import os
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QIcon, QAction, QPixmap, QScreen, QColor, QPainter, QBrush
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QWidget,
                               QGroupBox, QFormLayout, QPushButton, QScrollArea, QToolBar, QDialog, QMessageBox,
                               QSizePolicy, QStatusBar, QColorDialog, QFileDialog)
from timer_window import TimerWindow, DEFAULT_BACKGROUND_COLOR  # Import timer window module
from schedule_item_interface import ScheduleItem
from toolbar_interface import AboutDialog, CreditsDialog  # Import About and Credits windows
from globals import *
from export_schedule import ExportSchedule
from import_schedule import ImportSchedule
from ndi_output import NdiOutput, NDI_IS_AVAILABLE, NDI_SOURCE_NAME, NDI_FRAME_WIDTH, NDI_FRAME_HEIGHT

ADD_TIME = ["+15s", "+30s", "+1m", "+5m", "+15m", "+30m"]
MINUS_TIME = ["-15s", "-30s", "-1m", "-5m", "-15m", "-30m"]

MAIN_WINDOW_STYLESHEET_FILE_NAME = "main_window_stylesheet.qss"

TIMER_WINDOW_STYLESHEET_FILE_NAME = "timer_window_stylesheet.qss"

buttons_style = """padding: 5px 10px 5px 10px"""

# Timer window background options. Preset colors are applied directly, the others open a picker
BACKGROUND_PRESETS = {
    "Dark": DEFAULT_BACKGROUND_COLOR,
    "Black": "#000000",
    "Green Screen": "#00B140",
    "Blue Screen": "#0047BB",
}
BACKGROUND_CUSTOM_COLOR = "Custom Color..."
BACKGROUND_IMAGE = "Image..."
BACKGROUND_TRANSPARENT = "Transparent"

COLOR_DIALOG_STYLE = """
    QColorDialog { background-color: #2B2D30; }
    QSpinBox, QLineEdit { background-color: #1E1E1E; color: white; }
"""


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):

        super().__init__()

        self.app_instance = app  # Create attribute with app instance

        self.about_dialog = AboutDialog()  # Create About dialog object
        self.credits_dialog = CreditsDialog()  # create Credits dialog object

        # Load stylesheet from file
        self.stylesheet = load_stylesheet(MAIN_WINDOW_STYLESHEET_FILE_NAME)

        self.setStyleSheet(self.stylesheet)

        # Set up window basic settings
        self.setWindowTitle(APP_TITLE)
        self.setFixedSize(700, 780)
        self.setObjectName("mainWindow")
        self.setWindowIcon(QIcon(APP_ICON_DIR))

        # Add toolbar
        self.create_toolbar()

        # Create timer window object
        self.timer_window = TimerWindow()
        self.timer_window.window_update_signal.connect(self.update_timer_preview_window)
        self.timer_window.time_up_flash_signal.connect(self.update_timer_preview_window)
        self.timer_window.display_shortcut_signal.connect(self.activate_live_display_shortcut)
        self.timer_window.timer_window_destroyed_signal.connect(lambda: self.live_display_button.setChecked(False))

        # Create NDI output object, to broadcast the timer display over the network
        self.ndi_output = NdiOutput()
        self.ndi_output.connections_changed_signal.connect(self.update_ndi_button_text)

        self.available_monitors = app.screens()  # Get the list of available monitors

        # Window's parent layout, to hold all other layouts/containers
        self.main_layout = QVBoxLayout()

        # Layout to hold display settings box and timer preview
        top_layout = QHBoxLayout()

        # Create the QLabel to hold the timer values in the preview window
        self.timer_window_preview_label = QLabel()
        self.timer_window_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the display settings box and timer preview box to the top layout
        top_layout.addWidget(self.display_settings_group())
        top_layout.addWidget(self.create_timer_preview_group(self.timer_window_preview_label))

        # Create blank schedule items list
        self.schedule_items = []

        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(self.schedule_group())
        # self.main_layout.addLayout(self.app_settings())

        # Listen for monitors change and update the dropdown list when a screen is added or removed
        self.app_instance.screenAdded.connect(self.update_monitors_dropdown_list)
        self.app_instance.screenRemoved.connect(self.update_monitors_dropdown_list)

        # Set running seconds to 0
        self.running_seconds = 0

        # Create timer object
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        # Launch timer in secondary monitor
        self.launch_timer_in_secondary_monitor()

        self.widget = QWidget()
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

    def launch_timer_in_secondary_monitor(self):
        """Launches the timer window in the secondary monitor at startup"""
        # Startup the timer window in secondary monitor, if available
        if self.secondary_monitor_is_connected():
            self.timer_window.set_display_monitor(self.available_monitors[1])  # Set the timer window's display monitor
            # to the secondary monitor

            self.live_display_button.setChecked(True)

            self.displays_dropdown.setCurrentIndex(1)  # Set the selected monitor in the monitors dropdown
            # to the secondary monitor

    def get_monitor_names(self) -> list:
        """Gets the currently connected display monitors

        :return: List of all connected display monitors
        :rtype: list

        """

        self.available_monitors = self.app_instance.screens()  # Update the self.available_monitors attribute with
        # the list of currently connected display monitors

        display_monitors = []

        for monitor in self.available_monitors:
            display_monitors.append(monitor.name())

        return display_monitors

    def update_monitors_dropdown_list(self):
        """Updates the Output monitor dropdown list with the new list of available display monitors"""

        display_monitors = self.get_monitor_names()

        self.displays_dropdown.clear()  # Clear the values in the dropdown

        self.displays_dropdown.addItems(display_monitors)  # Add the updated list to the dropdown

    def secondary_monitor_is_connected(self) -> bool:
        """Checks if a secondary monitor is connected

        :returns: True if a secondary monitor is connected or False if otherwise
        :rtype: bool

        """

        if len(self.available_monitors) > 1:
            return True
        else:
            return False

    def display_settings_group(self):
        """Creates the section to change the display settings"""

        settings_group_box = QGroupBox("Display Settings")
        settings_group_box.setObjectName("displaySettingsBox")
        settings_group_box.setMaximumWidth(250)
        settings_group_box.setMinimumWidth(250)
        settings_group_box.setMinimumHeight(330)
        settings_group_box.setMaximumHeight(330)

        settings_layout = QFormLayout()

        # Output monitor row
        monitor_label = QLabel("Output Monitor")

        # Dropdown to change the display monitor
        self.displays_dropdown = QComboBox()
        display_monitors = self.get_monitor_names()  # Get list of all available displays
        self.displays_dropdown.addItems(display_monitors)
        self.displays_dropdown.currentTextChanged.connect(self.set_display_monitor)

        # Display timer live row
        timer_live_label = QLabel("Display Mode")
        self.live_display_button = QPushButton("Live")
        self.live_display_button.setCheckable(True)
        self.live_display_button.toggled.connect(self.display_timer_live)

        # Set the toggle to live and show timer preview, if a secondary monitor is connected
        # if self.secondary_monitor_is_connected():
        #     self.live_display_button.setChecked(True)
        #     # self.update_timer_preview_window()

        # NDI output row
        ndi_output_label = QLabel("NDI Output")
        self.ndi_button = QPushButton("NDI")
        self.ndi_button.setCheckable(True)
        self.ndi_button.setToolTip(f'Broadcast the timer display as the "{NDI_SOURCE_NAME}" NDI source')
        self.ndi_button.toggled.connect(self.ndi_button_toggled)

        # Disable the NDI button if the NDI library is not installed
        if not NDI_IS_AVAILABLE:
            self.ndi_button.setEnabled(False)
            self.ndi_button.setToolTip("Install ndi-python to enable NDI output")

        # Timer window background row
        background_label = QLabel("Background")
        self.background_dropdown = QComboBox()
        self.background_dropdown.addItems([*BACKGROUND_PRESETS, BACKGROUND_CUSTOM_COLOR, BACKGROUND_IMAGE,
                                           BACKGROUND_TRANSPARENT])
        self.background_dropdown.setToolTip("Transparent sends an alpha channel over NDI, for keying in OBS or vMix")
        self.background_dropdown.activated.connect(self.background_selected)  # Also fires when re-selecting an item
        self.current_background_index = 0

        # "Ministering Now" display row
        minister_label = QLabel("Minister")
        self.show_minister_button = QPushButton("Show")
        self.show_minister_button.setCheckable(True)
        self.show_minister_button.setChecked(True)
        self.show_minister_button.setToolTip("Show 'Ministering Now' and the minister's name under the timer")
        self.show_minister_button.toggled.connect(self.timer_window.set_minister_enabled)

        # Time up label display row
        display_time_up_label = QLabel("Time Up Alert")
        self.show_time_up_button = QPushButton("Show")
        self.show_time_up_button.setCheckable(True)
        self.show_time_up_button.toggled.connect(self.show_time_up_button_toggled)

        self.flash_time_up_button = QPushButton("Flash")
        self.flash_time_up_button.setCheckable(True)
        self.flash_time_up_button.toggled.connect(self.flash_time_up_button_toggled)

        time_up_display_options = QHBoxLayout()
        time_up_display_options.addWidget(self.show_time_up_button)
        time_up_display_options.addWidget(self.flash_time_up_button)

        # Add widgets to form layout
        settings_layout.addRow(monitor_label, self.displays_dropdown)
        settings_layout.addRow(timer_live_label, self.live_display_button)
        settings_layout.addRow(ndi_output_label, self.ndi_button)
        settings_layout.addRow(background_label, self.background_dropdown)
        settings_layout.addRow(minister_label, self.show_minister_button)
        settings_layout.addRow(display_time_up_label, time_up_display_options)
        settings_layout.setSpacing(10)

        settings_group_box.setLayout(settings_layout)

        return settings_group_box

    def create_timer_preview_group(self, widget):
        """Creates the timer preview box"""
        preview_group = QGroupBox("Output Preview")
        preview_group.setMaximumHeight(330)

        timer_window_style = load_stylesheet(TIMER_WINDOW_STYLESHEET_FILE_NAME)  # Load the timer window's stylesheet

        widget_background = QWidget()  # Widget to serve as the parent of the timer preview group
        widget_background.setObjectName("main")  # Set the object name to the same as timer_window's
        widget_background.setStyleSheet(timer_window_style)  # Set the widget's style to the timer window's

        timer_preview_layout = QVBoxLayout()
        timer_label = widget

        timer_preview_layout.addWidget(timer_label)

        widget_background.setLayout(timer_preview_layout)

        layout = QVBoxLayout()
        layout.addWidget(widget_background)

        preview_group.setLayout(layout)

        return preview_group

    def schedule_group(self):
        """Creates the section for the schedule list"""

        schedule_group_box = QGroupBox("Timer Schedule")
        schedule_group_box.setContentsMargins(5, 10, 5, 5)

        # Create button to add schedule item
        add_schedule_item_button = QPushButton("")
        add_schedule_item_button.setToolTip("Add Schedule")
        add_icon = QIcon(ADD_ICON_DIR)
        add_schedule_item_button.setIcon(add_icon)
        add_schedule_item_button.setMaximumWidth(50)
        add_schedule_item_button.setStyleSheet("padding: 4px;")
        add_schedule_item_button.clicked.connect(self.add_schedule_item)  # Add a new schedule item when
        # button is clicked

        # Create button to import schedule
        import_schedule_button = QPushButton("")
        import_schedule_button.setToolTip("Import Schedule")
        import_icon = QIcon(IMPORT_ICON_DIR)
        import_schedule_button.setIcon(import_icon)
        import_schedule_button.setMaximumWidth(50)
        import_schedule_button.setStyleSheet("padding: 4px;")
        import_schedule_button.clicked.connect(self.import_schedule)

        # Create button to export schedule
        export_schedule_button = QPushButton("")
        export_schedule_button.setToolTip("Export Schedule")
        export_icon = QIcon(EXPORT_ICON_DIR)
        export_schedule_button.setIcon(export_icon)
        export_schedule_button.setMaximumWidth(50)
        export_schedule_button.setStyleSheet("padding: 4px;")
        export_schedule_button.clicked.connect(self.export_schedule)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(export_schedule_button)
        button_layout.addWidget(import_schedule_button)
        button_layout.addWidget(add_schedule_item_button)

        # Create form layout to hold schedule items
        self.schedule_list_form = QFormLayout()
        self.schedule_list_form.setObjectName("scheduleForm")

        schedule_list_widget = QWidget()
        schedule_list_widget.setLayout(self.schedule_list_form)
        schedule_list_widget.setObjectName("scheduleWidget")

        # Create scroll area widget to hold the schedule form and make it scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(schedule_list_widget)
        # scroll_area.setStyleSheet(self.stylesheet)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(scroll_area)

        # Add one schedule by default
        self.add_schedule_item()

        starting_schedule_item = self.schedule_items[0]
        starting_schedule_item.schedule_status_button.setIcon(starting_schedule_item.clock_icon_green)

        # Set the timer window details to that of the default schedule
        self.set_timer_values(starting_schedule_item)

        # Set the default timer as active in the timer window
        self.timer_window.active_schedule = starting_schedule_item

        schedule_group_box.setLayout(layout)

        return schedule_group_box

    def create_toolbar(self):
        """"Create the menu toolbar"""
        toolbar = QToolBar("My main toolbar")
        toolbar.setObjectName("toolbar")
        toolbar.setStyleSheet(self.stylesheet)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(10, 10))
        toolbar.setMovable(False)

        help_button = QPushButton()
        help_button.setIcon(QIcon(HELP_ICON_DIR))
        help_button.setObjectName("toolbarButton")
        help_button.setText("Help")

        about_button = QPushButton()
        about_button.setIcon(QIcon(INFO_ICON_DIR))
        about_button.clicked.connect(self.about_button_is_clicked)
        about_button.setObjectName("toolbarButton")
        about_button.setText("About")

        credits_button = QPushButton()
        credits_button.setIcon(QIcon(CREDITS_ICON_DIR))
        credits_button.clicked.connect(self.credits_button_is_clicked)
        credits_button.setObjectName("toolbarButton")
        credits_button.setText("Credits")

        # toolbar.addWidget(help_button)
        toolbar.addWidget(about_button)
        toolbar.addWidget(credits_button)

        self.addToolBar(toolbar)

    def about_button_is_clicked(self):
        """Show the "About" window when the about button in the toolbar is clicked"""
        self.about_dialog.show()

    def credits_button_is_clicked(self):
        """Open the "Credits" webpage when the credits button in the toolbar is clicked"""
        url = 'file:///' + str(CREDITS_WEBPAGE_DIR)
        webbrowser.open(url)

    def add_schedule_item(self):
        """Adds a new schedule to the schedule list"""

        current_id = len(self.schedule_items)  # Get the length of the schedule_items list and set it as the id of the
        # object to be created. E.g, if length = 1, then means it last index = 0. Hence, the new object to be created
        # should have an id of 1

        new_schedule_item = ScheduleItem(current_id + 1)  # Creates a new ScheduleItem object

        # Set listener for start, pause, delete, and reset buttons
        new_schedule_item.start_button.clicked.connect(lambda: self.start_timer(new_schedule_item))
        new_schedule_item.delete_button.clicked.connect(lambda: self.delete_schedule_from_list(new_schedule_item))
        new_schedule_item.reset_button.clicked.connect(lambda: self.reset_timer(new_schedule_item))
        new_schedule_item.pause_button.clicked.connect(lambda: self.pause_resume_timer(new_schedule_item))
        new_schedule_item.resume_button.clicked.connect(lambda: self.resume_timer(new_schedule_item))
        new_schedule_item.session_title_input.textChanged.connect(lambda: self.update_session_title(new_schedule_item))
        new_schedule_item.minister_input.textChanged.connect(lambda: self.update_minister_name(new_schedule_item))

        new_schedule_item.visibility_toggle_signal.connect(lambda: self.toggle_button_is_clicked(new_schedule_item))

        # Add schedule item to the schedules list
        self.schedule_items.append(new_schedule_item)

        # Add schedule item to the form layout that displays the schedules
        self.schedule_list_form.addRow(new_schedule_item)

        # Set focus to the session title input field of the newly added schedule
        new_schedule_item.session_title_input.setFocus()

        # print(f"Added: Items list length: {len(self.schedule_items)} || Form row count: {self.schedule_list_form.rowCount()}")

    def export_schedule(self):
        """Exports the current schedule list to the file"""

        new_export = ExportSchedule(self.schedule_items)

        new_export.export_schedule_data()

    def import_schedule(self):
        """Imports a saved schedule from file"""

        import_schedule = ImportSchedule()

        try:
            schedule_to_import = import_schedule.get_schedule_data()
        except TypeError:
            print("Dialog box closed")
        else:
            # Authenticate the schedule file, to be sure it is a supported file type
            if import_schedule.is_valid_file():
                # Check if the schedule to be imported contains data. If no, terminate the import process
                if len(schedule_to_import) == 0:
                    QMessageBox.information(self, "Import Failed", "The selected schedule is empty.")
                else:
                    # Get user's confirmation to import schedule.
                    # Importing a new schedule will stop any running timer and clear the existing schedule.

                    # Set the prompt text.
                    text = ""
                    if self.timer_window.active_schedule.start_button.isHidden():
                        text = "Are you sure you want to import this schedule? The running timer will be stopped and current schedule will be cleared."
                    else:
                        text = "Are you sure you want to import this schedule? The current schedule will be cleared."

                        confirm_import_dialog = (
                            QMessageBox.question(self,
                                                 "Confirm Import",
                                                 text))

                        # If user confirms to import schedule
                        if confirm_import_dialog == QMessageBox.Yes:

                            # Proceed to clear the schedule item list.
                            self.timer_window.active_schedule = None  # disable the active schedule

                            # Delete all items in the schedule, starting from the last item in the list
                            for schedule_item in reversed(self.schedule_items):
                                self.delete_schedule_from_list(schedule_item)

                            # For each key in the data to be imported, create/add a new schedule item and update its title and time values accordingly
                            for schedule_item_id in schedule_to_import:
                                session_title = schedule_to_import[schedule_item_id]["Session Title"]
                                minister_name = schedule_to_import[schedule_item_id].get("Minister", "")
                                minutes = schedule_to_import[schedule_item_id]["Minutes"]
                                seconds = schedule_to_import[schedule_item_id]["Seconds"]

                                # Add new schedule
                                self.add_schedule_item()

                                index = int(schedule_item_id) - 1

                                self.schedule_items[index].session_title_input.setText(session_title)
                                self.schedule_items[index].minister_input.setText(minister_name)
                                self.schedule_items[index].minutes_input.setText(str(minutes))
                                self.schedule_items[index].seconds_input.setText(str(seconds))

                                # self.schedule_items[schedule_item_id - 1].in
                                # print(session_title, time_value)

                            # Set first item on the list as active schedule and set focus on its session title
                            self.reset_timer(self.schedule_items[0])
                            self.schedule_items[0].session_title_input.setFocus()
            else:
                QMessageBox.information(self, "Import Failed", "The selected file is not a valid schedule.")




        # # Remove all current schedule items
        # items_count = len(self.schedule_items)
        # print(items_count)
        #
        # for n in range(items_count):
        #     print(n)
        #
        # # for schedule_item in self.schedule_items:
        # #     if schedule_item.schedule_num > 1:
        # #         self.delete_schedule_from_list(schedule_item)

    def delete_schedule_from_list(self, schedule_item):

        """Deletes a schedule item from the list, if it is not currently active

        :param schedule_item: The schedule item to be deleted
        :type schedule_item: ScheduleItem

        """

        # Check if the schedule item to be deleted is not active and running
        if not self.timer_window.active_schedule == schedule_item:

            # Get the current id of the schedule item to be deleted
            schedule_id = self.schedule_items.index(schedule_item)

            # Remove the schedule item from the schedule form
            self.schedule_list_form.removeRow(schedule_id)

            # Remove the schedule item from the schedules list
            self.schedule_items.remove(self.schedule_items[schedule_id])

            # Update the row number of the remaining schedule items
            for item in self.schedule_items:
                # Get the current index of the schedule item and increment by 1
                new_row_num = self.schedule_items.index(item) + 1
                item.update_schedule_row_num(new_row_num)
        else:
            confirm_delete_message = QMessageBox.warning(self, "Error!",
                                                         "You cannot delete an active schedule.")

    def set_timer_values(self, schedule_item):
        """Sets the time values of the timer (hours,seconds) in the timer window

        :param schedule_item: The schedule with the timer values to be set
        :type schedule_item: ScheduleItem

        """

        self.running_seconds = schedule_item.get_timer_value()  # Get the total seconds inputted
        session_title = schedule_item.get_session_title()  # Get the session title
        minister_name = schedule_item.get_minister_name()  # Get the minister's name

        self.timer_window.set_timer_window_values(self.running_seconds,
                                                  session_title, minister_name)  # Update the timer window with the set
        # time values

        # Update the timer preview window to show the newly set timer values
        # self.update_timer_preview_window()

    def start_timer(self, schedule_item):
        """Starts the countdown timer

        This function overrides any running timer by stopping it, and starting a new one

        """

        # Check if the session title is set to visible
        # This ensures that any schedule with its session title set to hidden does not show, when the schedule's timer
        # is started for the first timer
        if schedule_item.session_title_is_visible:
            self.timer_window.session_title_label.show()
        elif not schedule_item.session_title_is_visible:
            self.timer_window.session_title_label.hide()

        # Set the schedule item as active
        self.timer_window.active_schedule = schedule_item

        # This function will initiate the timer mechanism
        self.set_timer_values(schedule_item)

        # Stop any running timer. This allows for overriding any running timer
        self.timer.stop()

        # Start the timer
        self.timer.start(1000)

        # Hide start button
        schedule_item.start_button.hide()

        # Show pause button
        schedule_item.pause_button.show()

        # Set schedule status button to green
        schedule_item.schedule_status_button.setIcon(schedule_item.clock_icon_green)

        # Loop through all schedule items to reset the state of all other schedule items apart from the active schedule
        # The code block is not enclosed in a function to make it clearer and easier to understand what it does, at a
        # glance
        for existing_schedule_item in self.schedule_items:
            if existing_schedule_item != schedule_item:

                # Set the start and play button for all other schedule items, to default state
                existing_schedule_item.reset_start_pause_buttons()

                # Set the schedule status button icon to default
                existing_schedule_item.reset_schedule_status()

    def reset_timer(self, schedule_item):
        """Stops the currently running timer and resets the timer to the time values of the schedule that was reset"""

        # Check if the session title is set to visible
        if schedule_item.session_title_is_visible:
            self.timer_window.session_title_label.show()
        elif not schedule_item.session_title_is_visible:
            self.timer_window.session_title_label.hide()

        # Stop the currently running timer if any and set running seconds to 0
        self.timer.stop()
        self.running_seconds = 0

        # Set the schedule item as active
        self.timer_window.active_schedule = schedule_item

        # This function will stop any running timer mechanism and set the timer window's values to that of the schedule
        # item whose reset button was clicked
        self.set_timer_values(schedule_item)

        # Reset start button, pause button, and resume button of currently active widget to default states
        schedule_item.reset_start_pause_buttons()

        # Set schedule status button icon to green
        schedule_item.schedule_status_button.setIcon(schedule_item.clock_icon_green)

        # Set the start and play button for all other schedule items, to default state
        # The code block is not enclosed in a function to make it clearer and easier to understand what it does, at a
        # glance
        for existing_schedule_item in self.schedule_items:
            if existing_schedule_item != schedule_item:
                existing_schedule_item.reset_start_pause_buttons()  # Reset start and pause buttons to default

                existing_schedule_item.reset_schedule_status()  # Reset schedule status button to default

    def pause_resume_timer(self, schedule_item):
        """Pauses or resumes the currently running timer"""

        self.timer.stop()  # Stop the timer
        schedule_item.pause_button.hide()  # Hide the pause button
        schedule_item.resume_button.show()  # Show the resume button

        # Set the schedule item as active
        self.timer_window.active_schedule = schedule_item

    def resume_timer(self, schedule_item):
        """Resumes the currently running timer"""
        self.timer.start(1000)

        schedule_item.resume_button.hide()  # Hide the resume button
        schedule_item.pause_button.show()  # Show the pause button

    def update_time(self):
        """Reduces the running seconds by 1 every 1sec and updates the timer window with the new running seconds value

        """
        self.running_seconds -= 1

        # print(self.running_seconds)

        self.timer_window.update_running_timer(self.running_seconds)
        # self.update_timer_preview_window()

    def update_session_title(self, schedule_item):
        """Updates the session title of the active schedule, in the timer window

        This function is called when the text in the session title input field of the active schedule is updated

        """
        if self.timer_window.active_schedule == schedule_item:
            session_title = schedule_item.session_title_input.text()
            self.timer_window.update_session_label(session_title)

    def update_minister_name(self, schedule_item):
        """Updates the minister's name of the active schedule, in the timer window

        This function is called when the text in the minister input field of a schedule is updated

        """
        if self.timer_window.active_schedule == schedule_item:
            self.timer_window.set_minister_name(schedule_item.get_minister_name())

    def update_timer_preview_window(self):
        """Updates the timer preview window with a live snapshot of the running timer

        This function is called everytime a change occurs in the timer window, to give a realtime preview of the running
        timer

        """

        snapshot = self.timer_window.snapshot()
        is_transparent = self.timer_window.background_is_transparent

        # Send the snapshot to NDI receivers
        if self.ndi_output.is_running():
            self.ndi_output.update_frame(snapshot, self.timer_window.background_color, is_transparent)

        # # pixmap = pixmap.scaledToWidth(200)
        # # pixmap = pixmap.scaledToHeight(200)
        pixmap = QPixmap.fromImage(snapshot).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Show a checkerboard behind a transparent background, so it is clear which parts are see-through
        if is_transparent:
            pixmap = self.add_checkerboard_background(pixmap)

        self.timer_window_preview_label.setPixmap(pixmap)

    @staticmethod
    def add_checkerboard_background(pixmap: QPixmap) -> QPixmap:
        """Draws a pixmap over a checkerboard pattern"""

        tile = QPixmap(16, 16)
        tile.fill(QColor("#3A3A3A"))
        tile_painter = QPainter(tile)
        tile_painter.fillRect(0, 0, 8, 8, QColor("#555555"))
        tile_painter.fillRect(8, 8, 8, 8, QColor("#555555"))
        tile_painter.end()

        result = QPixmap(pixmap.size())
        result.setDevicePixelRatio(pixmap.devicePixelRatio())
        painter = QPainter(result)
        painter.fillRect(result.rect(), QBrush(tile))
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result

    def background_selected(self, index):
        """Applies the background chosen in the background dropdown to the timer window

        For a custom color or an image, a picker is opened. If the picker is cancelled, the dropdown goes back to the
        previous selection

        """

        choice = self.background_dropdown.itemText(index)

        if choice in BACKGROUND_PRESETS:
            self.timer_window.set_background_color(QColor(BACKGROUND_PRESETS[choice]))

        elif choice == BACKGROUND_CUSTOM_COLOR:
            color_dialog = QColorDialog(self.timer_window.background_color, self)
            color_dialog.setWindowTitle("Select Background Color")
            color_dialog.setStyleSheet(COLOR_DIALOG_STYLE)  # The app stylesheet makes labels white, so darken it

            color = color_dialog.selectedColor() if color_dialog.exec() else QColor()
            if not color.isValid():
                self.background_dropdown.setCurrentIndex(self.current_background_index)
                return
            self.timer_window.set_background_color(color)

        elif choice == BACKGROUND_IMAGE:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", str(Path.home()),
                                                       "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
            image = QPixmap(file_path) if file_path else QPixmap()
            if image.isNull():
                if file_path:
                    QMessageBox.warning(self, "Image Error", "The selected image could not be opened.")
                self.background_dropdown.setCurrentIndex(self.current_background_index)
                return
            self.timer_window.set_background_image(image)

        elif choice == BACKGROUND_TRANSPARENT:
            self.timer_window.set_background_transparent()

        self.current_background_index = index

    def get_selected_monitor(self, selected_monitor) -> object:
        """Gets the currently selected monitor object, using its name attribute"""

        # Loop through all monitors in the available monitors list and identify the monitor whose name attribute is
        # same as the selected_monitor's
        for monitor in self.available_monitors:
            if monitor.name() == selected_monitor:
                return monitor

    def set_display_monitor(self, selected_monitor):
        """Sets the display monitor to the currently selected monitor

        This function is called when the selected monitor in the dropdown list changes or when the display mode button
        is toggled

        :param selected_monitor: The monitor selected in the monitors list dropdown
        :type selected_monitor: str

        """

        current_monitor = self.get_selected_monitor(selected_monitor)
        self.timer_window.set_display_monitor(current_monitor)

        if self.live_display_button.isChecked():
            # print(self.live_display_toggle.isChecked())
            # Ensures that the timer window display in full screen mode in the new monitor
            self.timer_window.show_timer()
            # pass

    def display_timer_live(self):
        """Sets the timer display to live or inactive

        If display_live is True, the timer window becomes active/visible in the currently selected monitor, else,
        the timer window is hidden

        This function is called whenever the "Live" display button is toggled

        """

        if self.live_display_button.isChecked():

            # Show timer in selected monitor
            self.timer_window.show_timer()
        else:
            self.timer_window.hide()

    def ndi_button_toggled(self):
        """Starts or stops broadcasting the timer display as an NDI source

        This function is called whenever the "NDI" button is toggled

        """

        if self.ndi_button.isChecked():

            # Give the timer window a full HD size while it is not shown on a monitor, so the NDI output is laid out
            # the same way as a full screen display
            if not self.timer_window.isVisible():
                self.timer_window.resize(NDI_FRAME_WIDTH, NDI_FRAME_HEIGHT)

            if self.ndi_output.start():
                self.update_timer_preview_window()  # Send the current display as the first frame
            else:
                self.ndi_button.setChecked(False)
                QMessageBox.warning(self, "NDI Error",
                                    "Could not start the NDI output. Make sure the NDI Runtime is installed.")
        else:
            self.ndi_output.stop()

    def update_ndi_button_text(self, connections):
        """Shows the number of receivers connected to the NDI source on the NDI button"""

        if connections > 0:
            self.ndi_button.setText(f"NDI ({connections})")
        else:
            self.ndi_button.setText("NDI")

    def toggle_button_is_clicked(self, schedule_item):
        """Shows or hides the session title label when the schedule's title display button is toggled"""
        if schedule_item == self.timer_window.active_schedule:
            if schedule_item.session_title_is_visible:
                self.timer_window.session_title_label.show()
                self.update_timer_preview_window()
            elif not schedule_item.session_title_is_visible:
                self.timer_window.session_title_label.hide()
                self.update_timer_preview_window()

    def activate_live_display_shortcut(self):
        """Toggles the display modde button when the live display shortcut key, Ctrl + L is pressed"""

        if self.live_display_button.isChecked():
            self.live_display_button.setChecked(False)
        else:
            self.live_display_button.setChecked(True)

    def show_time_up_button_toggled(self):
        """Shows or hides the time up label when the "Show" button is toggled

            The time up label is shown when the current time is negative, regardless of if the timer is running or not.
        I.e. the label will be displayed if the timer is reset to a negative value

            This function relies on the "set_timer_text" and "update_running_timer" methods in the timer_window object
        to update the display on the timer window whenever the "Show" button is toggled.

            The timer window object controls the visibility status of the time up label using a "show_time_up_label"
        attribute, defined as a Boolean data type. The value of this attribute is changed from this function; it is set
        to True when the "Show" time up alert is checked, and vice versa.

            This function also calls the "update_running_timer" method in the timer window object, which updates the
        labels in the window. This enables the time up label to become visible regardless of if the timer is active or
        not.

        """

        if not self.timer_window.first_negative_run:
            self.timer_window.first_negative_run = True

        if self.show_time_up_button.isChecked():

            # Set the show_time_up label attribute in the timer window to True
            self.timer_window.show_time_up_label = True

            # Call the "update_running_timer" function, which picks the new state of the "Show" time up label (visible)
            # and updates the content of the timer window
            if not self.timer.isActive():
                self.timer_window.update_running_timer(self.running_seconds)

        elif not self.show_time_up_button.isChecked():

            # Set the show_time_up label attribute in the timer window to False
            self.timer_window.show_time_up_label = False

            # Call the "update_running_timer" function, which picks the new state of the "Show" time up label (hidden)
            # and updates the content of the timer window
            self.timer_window.update_running_timer(self.running_seconds)

            # Uncheck the flash time up button (The button can only be checked if the time up label is set to visible)
            self.flash_time_up_button.setChecked(False)  # Uncheck the flash time up button

            self.timer_window.update()

        else:
            pass

    def flash_time_up_button_toggled(self):
        """Enables or disables the Time Up flash effect"""

        if self.flash_time_up_button.isChecked():

            # Activate the flash time up effect
            self.timer_window.enable_time_up_flash_effect()

            # If the "Show" time up alert feature is already turned on when the flash time up effect is activated,
            # update the timer window. This solves for cases when the flash effect is enabled, but the "Show" time up
            # alert is already checked
            if self.show_time_up_button.isChecked():
                self.timer_window.update_running_timer(self.running_seconds)

            # Else, check turn on the "Show" time up alert feature, which will update the timer window within the
            # show_time_up_button_toggled function.
            elif not self.show_time_up_button.isChecked():
                self.show_time_up_button.setChecked(True)

        elif not self.flash_time_up_button.isChecked():
            self.timer_window.disable_time_up_flash_effect()
            self.update_timer_preview_window()
        else:
            pass

    def keyPressEvent(self, event):
        """Handles keyboard keys press events"""

        # Ctrl + L shortcut to toggle timer window display mode
        if event.key() == Qt.Key_L and event.modifiers() == Qt.ControlModifier:
            self.activate_live_display_shortcut()

    def closeEvent(self, event):
        # Confirm app closure if an active timer is running
        # This checks if the start button of the active schedule is hidden, which indicates that its timer is currently running
        if self.timer_window.active_schedule.start_button.isHidden():
            confirm_exit_dialog = (
                QMessageBox.question(self,
                                     "Confirm exit",
                                     "There is an active timer running. Are you sure you want to exit the app?"))

            if confirm_exit_dialog == QMessageBox.Yes:
                event.accept()
                self.ndi_output.stop()  # Remove the NDI source from the network
                self.timer_window.close()  # Close active timer window
            elif confirm_exit_dialog == QMessageBox.No:
                event.ignore()
        else:
            self.ndi_output.stop()  # Remove the NDI source from the network
            self.timer_window.close()  # Close active timer window

