from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QToolButton, QFrame, \
    QLayout
from PySide6.QtGui import QIcon, QAction, QPainter, QColor, QIntValidator
from PySide6.QtCore import Signal, Qt, QSize
from globals import *

STYLESHEET_FILE_NAME = "schedule_item_stylesheet.qss"


class ScheduleItem(QWidget):
    """ Creates a schedule item """

    visibility_toggle_signal = Signal()  # Signal to monitor the session title visibility toggle

    def __init__(self, schedule_num):
        super().__init__()

        stylesheet = load_stylesheet(STYLESHEET_FILE_NAME)

        self.setMaximumHeight(300)
        self.setObjectName("myWidget")
        self.setStyleSheet(stylesheet)

        schedule_item_layout = QGridLayout()

        self.schedule_num = schedule_num # Create attribute to store the number ID of each schedule object

        self.schedule_row_num_label = QLabel()
        self.schedule_row_num_label.setObjectName("rowNum")
        self.schedule_row_num_label.setText(str(self.schedule_num))
        self.schedule_row_num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.schedule_row_num_label.setFixedWidth(20)

        # Create clock icons for schedule status indication
        self.clock_icon_white = QIcon(CLOCK_WHITE_ICON_DIR)
        self.clock_icon_green = QIcon(CLOCK_GREEN_ICON_DIR)
        self.clock_icon_red = QIcon(CLOCK_RED_ICON_DIR)

        self.schedule_status_button = QPushButton()
        self.schedule_status_button.setIcon(self.clock_icon_white)

        # Create validator for minutes and seconds input fields
        int_validator = QIntValidator()

        # Create minutes input field
        self.minutes_input = QLineEdit()
        self.minutes_input.setToolTip("Minutes")
        self.minutes_input.setPlaceholderText("Minutes")
        self.minutes_input.setFixedWidth(70)
        self.minutes_input.setValidator(int_validator)

        # Create seconds input field
        self.seconds_input = QLineEdit()
        self.seconds_input.setPlaceholderText("Seconds")
        self.seconds_input.setToolTip("Seconds")
        self.seconds_input.setToolTipDuration(0)
        self.seconds_input.setFixedWidth(70)
        self.seconds_input.setValidator(int_validator)

        # Layout to hold time inputs
        time_container = QHBoxLayout()

        time_container.addWidget(self.schedule_status_button)
        time_container.addWidget(self.minutes_input)
        time_container.addWidget(QLabel(":"))
        time_container.addWidget(self.seconds_input)
        time_container.addStretch(0)

        # Session title section
        # Create session title input field
        self.session_title_input = QLineEdit("")
        self.session_title_input.setPlaceholderText("Session")
        self.session_title_input.setObjectName("sessionTitle")

        # Create show and hide icons
        self.show_icon = QIcon(SHOW_ICON_DIR)
        self.hide_icon = QIcon(HIDE_ICON_DIR)

        # Create button to toggle session title's visibility
        self.set_visibility_button = QToolButton()
        self.set_visibility_button.setIcon(self.show_icon)
        self.set_visibility_button.setStyleSheet("background-color: transparent")
        self.set_visibility_button.clicked.connect(self.set_session_title_visibility)

        # Set session title's default state to visible
        self.session_title_is_visible = True

        # Layout to hold session title input field and visibility toggle button
        session_title_input_layout = QHBoxLayout()
        session_title_input_layout.setSpacing(0)
        session_title_input_layout.addWidget(self.session_title_input)
        session_title_input_layout.addWidget(self.set_visibility_button)

        # Reset button
        reset_button_icon = QIcon(RESET_ICON_DIR)
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("actionButtons")
        self.reset_button.setIcon(reset_button_icon)
        self.reset_button.setToolTip("Reset Timer")

        # Start button
        start_button_icon = QIcon(START_ICON_DIR)
        self.start_button = QPushButton()
        self.start_button.setIcon(start_button_icon)
        self.start_button.setToolTip("Start Timer")

        # Pause button
        pause_button_icon = QIcon(PAUSE_ICON_DIR)
        self.pause_button = QPushButton()
        self.pause_button.setIcon(pause_button_icon)
        self.pause_button.setToolTip("Pause Timer")

        # Resume button
        resume_button_icon = QIcon(RESUME_ICON_DIR)
        self.resume_button = QPushButton()
        self.resume_button.setIcon(resume_button_icon)
        self.resume_button.setToolTip("Resume Timer")
        self.resume_button.hide()

        # Set the default action of the pause button to "Pause"
        self.pause_button_action = "Pause"
        self.pause_button.hide()

        # Delete button
        delete_button_icon = QIcon(DELETE_ICON_DIR)
        self.delete_button = QPushButton()
        self.delete_button.setIcon(delete_button_icon)
        self.delete_button.setToolTip("Delete Schedule")

        # Add all widgets to row layout
        schedule_item_layout.addWidget(self.schedule_row_num_label, 0, 0)
        schedule_item_layout.addLayout(session_title_input_layout, 0, 1)
        schedule_item_layout.addLayout(time_container, 0, 2)
        schedule_item_layout.addWidget(self.reset_button, 0, 3)
        schedule_item_layout.addWidget(self.start_button, 0, 4)
        schedule_item_layout.addWidget(self.pause_button, 0, 4)
        schedule_item_layout.addWidget(self.resume_button, 0, 4)
        schedule_item_layout.addWidget(self.delete_button, 0, 5)

        # Set schedule as inactive by default
        self.schedule_is_active = False

        frame = QFrame()
        frame.setLayout(schedule_item_layout)
        frame.setObjectName("frame")

        layout = QHBoxLayout()
        layout.addWidget(frame)
        self.setLayout(schedule_item_layout)


    def get_session_title(self):
        """Returns the session title

        :returns: Session title
        :rtype: string

        """

        return self.session_title_input.text()

    def get_minutes(self) -> int:
        """Returns the number of minutes set

        :returns: Number of minutes set
        :rtype: int

        """

        if self.minutes_input.text() == "":
            minutes = 0
        else:
            minutes = int(self.minutes_input.text())

        return minutes

    def get_seconds(self) -> int:
        """Returns the number of seconds set

        :returns: Number of seconds set
        :rtype: int

        """

        if self.seconds_input.text() == "":
            seconds = 0
        else:
            seconds = int(self.seconds_input.text())

        return seconds


    def get_timer_value(self) -> int:
        """Retrieves the schedule's set time in hours and/or seconds, and converts to seconds

        :returns: Total number of seconds set
        :rtype: int

        """
        minutes = self.get_minutes()
        seconds = self.get_seconds()

        total_seconds = (minutes * 60) + seconds

        return total_seconds

    def set_timer_values(self):
        """Sets the minutes and seconds values of the schedule"""

    def start_timer(self):
        pass

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

    def update_schedule_row_num(self, new_row_num):
        """Updates the row number of the schedule item"""
        self.schedule_row_num_label.setText(str(new_row_num))

    def reset_start_pause_buttons(self):
        """Resets the start, pause, and resume timer buttons to their default state at startup"""

        self.pause_button.hide()  # Reset pause button to default pause state

        self.resume_button.hide()  # Reset resume button to default state

        # Show start button
        self.start_button.show()

        # Send
        # self.set_session_title_visibility()

    def set_session_title_visibility(self):
        """Switches the session title visibility button state whenever the button/icon is clicked

        The function is connected to the visibility icon's click signal

        It also emits a signal whenever it is called. This signal is received in the user interface and used
        to hide or show the session title in the timer window

        """

        if self.session_title_is_visible:
            self.session_title_is_visible = False
            self.set_visibility_button.setIcon(self.hide_icon)
        else:
            self.session_title_is_visible = True
            self.set_visibility_button.setIcon(self.show_icon)

        self.visibility_toggle_signal.emit()

    def reset_schedule_status(self):
        self.schedule_status_button.setIcon(self.clock_icon_white)
