from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QHBoxLayout, QSizePolicy)
from PySide6.QtGui import Qt, QColor, QFont, QIcon, QImage, QPainter, QPixmap, QRegion
from PySide6.QtCore import Signal, QTimer, QPoint
from globals import APP_TITLE, APP_ICON_DIR, APP_FONT_FAMILY

DEFAULT_BACKGROUND_COLOR = "#1E1E1E"
TIMER_CENTRE_HEIGHT_RATIO = 0.45  # The timer is centred at this fraction of the window height, a little above the middle

TIMER_TEXT_DEFAULT_STYLE = """
    font-size:  300pt;
    color: white;
    qproperty-alignment: AlignCenter;
    font-family: Barlow;
    font-weight: 600;
"""

TIMER_TEXT_DEFAULT_STYLE_HOUR = """
    font-size:  250pt;
    color: white;
    qproperty-alignment: AlignCenter;
    font-family: Barlow;
    font-weight: 600;
"""

TIMER_TEXT_TIME_UP_STYLE_WITH_TIME_UP_LABEL = """
    font-size:  200pt;
    color: #F44336;
    qproperty-alignment: AlignCenter;
    font-family: Barlow;
    font-weight: 600;
"""

TIMER_TEXT_TIME_UP_STYLE = """
    font-size:  300pt;
    color: #F44336;
    qproperty-alignment: AlignCenter;
    font-family: Barlow;
    font-weight: 600;
"""

TIMER_TEXT_TIME_UP_STYLE_HOUR = """
    font-size:  230pt;
    color: #F44336;
    qproperty-alignment: AlignCenter;
    font-family: Barlow;
    font-weight: 600;
"""

SESSION_LABEL_STYLE = f"""
    font-size: 100px;
    qproperty-alignment: AlignCenter;
    margin-top: 30px;
    color: #7CCBFF;
    font-family: Barlow;
    font-weight: 700;
"""

MINISTER_CAPTION_STYLE = """
    font-size: 40px;
    qproperty-alignment: AlignCenter;
    color: #FFC857;
    font-family: Barlow;
    font-weight: 700;
"""

MINISTER_NAME_STYLE = """
    font-size: 80px;
    qproperty-alignment: AlignCenter;
    color: white;
    font-family: Barlow;
    font-weight: 600;
"""

TIME_UP_LABEL_STYLE = """
    font-size: 200pt;
    qproperty-alignment: AlignCenter;
    margin-bottom: 40px;
    color: white;
    font-family: Barlow;
    font-weight: 700;
"""

class TimerWindow(QWidget):

    window_update_signal = Signal()  # Signal to monitor when the window is updated
    time_up_flash_signal = Signal()  # Signal to monitor when the time up label flashes
    display_shortcut_signal = Signal()  # Signal to monitor when Ctrl + L is pressed in the timer window
    timer_window_destroyed_signal = Signal()  # Signal to monitor when the timer window is destroyed/closed

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(APP_ICON_DIR))
        self.setObjectName("main")

        # The background is painted in paintEvent, so it can be a solid color, an image, or transparent
        self.background_color = QColor(DEFAULT_BACKGROUND_COLOR)
        self.background_image = None  # QPixmap, when an image background is selected
        self.background_is_transparent = False
        self.text_shadows = []  # Drop shadows on the text, used with image and transparent backgrounds

        self.time_up_flash_timer = QTimer()
        self.time_up_flash_timer.timeout.connect(self.toggle_time_up_flash_effect)
        self.time_up_flash_is_on = False
        self.flash_time_up_alert_is_enabled = False  # This attribute

        self.display_monitor = None
        self.minutes = 0
        self.seconds = 0

        self.window_is_active = True

        # Textbox to hold session title for default layout
        self.session_title_label = QLabel(self)
        # self.session_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.session_title_label.setStyleSheet(SESSION_LABEL_STYLE)
        self.session_title_label.setWordWrap(True)  # Wrap long titles instead of cutting them off

        # Textbox to hold timer values for default layout
        # self.timer_label = QLabel(f"0{self.minutes}:0{self.seconds}")
        self.timer_label = QLabel(self)
        self.timer_label.setStyleSheet(TIMER_TEXT_DEFAULT_STYLE)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Barlow's digits have different widths by default, which makes the countdown shift sideways as it runs.
        # Tabular figures give every digit the same width
        timer_font = QFont(APP_FONT_FAMILY)
        timer_font.setFeature(QFont.Tag("tnum"), 1)
        self.timer_label.setFont(timer_font)

        # Font settings for timer label
        # timer_font = QFont()
        # timer_font.setPointSize(200)

        # "Ministering Now" panel, shown under the timer with the name of the minister responsible for the session.
        # It is shown when enabled in the display settings and the active schedule has a minister's name
        self.minister_caption_label = QLabel("MINISTERING NOW")
        self.minister_caption_label.setStyleSheet(MINISTER_CAPTION_STYLE)

        self.minister_name_label = QLabel()
        self.minister_name_label.setStyleSheet(MINISTER_NAME_STYLE)
        self.minister_name_label.setWordWrap(True)

        minister_layout = QVBoxLayout()
        minister_layout.setContentsMargins(0, 0, 0, 0)
        minister_layout.setSpacing(0)
        minister_layout.addWidget(self.minister_caption_label)
        minister_layout.addWidget(self.minister_name_label)

        self.minister_panel = QWidget(self)
        self.minister_panel.setLayout(minister_layout)
        self.minister_panel.hide()

        self.minister_is_enabled = True
        self.minister_name = ""

        # Textbox to hold "Time Up" text
        self.time_up_label = QLabel("Time Up", self)
        self.time_up_label.setStyleSheet(TIME_UP_LABEL_STYLE)
        self.time_up_label.hide()
        self.show_time_up_label = False

        self.active_schedule = None

        self.first_negative_run = True

        # Emit signal
        self.window_is_updated()

    def set_timer_window_values(self, total_seconds: int, session_title: str = "", minister_name: str = ""):
        """Set the timer values (hours, minutes, and seconds) and session title in the timer window

        This function is called when the reset or start button is clicked

        :param total_seconds: Total number of seconds for countdown
        :type total_seconds: int

        :param session_title: Title of current session
        :type session_title: str

        :param minister_name: Name of the minister responsible for the current session
        :type minister_name: str

        """

        self.first_negative_run = True

        self.update_timer_window_labels(total_seconds)

        self.session_title_label.setText(session_title.upper())
        self.set_minister_name(minister_name)

        # Emit signal
        self.window_is_updated()

    def update_timer_window_labels(self, total_seconds):
        """Updates the timer window's labels/displays with the appropriate values

        - Updates the time label with the corresponding (HH:MM:SS) format
        - Adds the "-" sign to the time label as required
        - Updates the stylesheet of the time, time_up, and session labels as required
        - Shows/Hides the Time Up label

        :param total_seconds: Total number of seconds for countdown
        :type total_seconds: int

        """

        # Used as a means of telling the program that the timer is negative.
        time_is_negative = False

        # This variable holds the display to be shown on the timer, i.e. 00:00:00
        timer_text = ""

        # Serves as a means of setting the visibility state of the hour (00) section in the timer.
        # This variable is used later in this function to set the stylesheet of the time label
        hour_is_visible = False

        if total_seconds < 0:
            time_is_negative = True

        # Convert total seconds to positive value
        total_seconds = abs(total_seconds)

        minutes = int(total_seconds / 60)  # Get minutes value
        seconds = int(total_seconds % 60)  # Get seconds value
        hours = 0

        # Get hour value from minutes if total minutes is greater than or equal to 60
        if minutes >= 60:
            hours = int(minutes / 60)
            minutes = int(minutes % 60)

        # Add leading zero if any time unit is less than 10 e.g. 5 becomes 05
        if minutes < 10:
            minutes = f"0{minutes}"
        if seconds < 10:
            seconds = f"0{seconds}"
        if hours < 10:
            hours = f"0{hours}"

        # Add the "hour" digits to the time label, if the current time has an hour value
        if int(hours) > 0:
            timer_text = f"{hours}:{minutes}:{seconds}"
            hour_is_visible = True
        else:
            timer_text = f"{minutes}:{seconds}"

        # Add minus to timer text if the running seconds is negative
        if time_is_negative:
            timer_text = "-" + timer_text + " "  # Add a minus sign to the timer text

            # Show or hide the time up label
            # Show the label if the "Time Up Alert" toggle in the main interface is set to show, else hide the label
            # The "show_time_up_label" attribute is a boolean type, which is used to determine the toggle stage of the
            # "Time Up Alert" button. It is set to True whenever the button is checked and is set to False whenever the
            # button is unchecked

            if self.show_time_up_label:  # If the "Show" time up alert button is enabled

                # Update the style of the timer label
                self.timer_label.setStyleSheet(TIMER_TEXT_TIME_UP_STYLE_WITH_TIME_UP_LABEL)

                # Show the time up label
                self.time_up_label.show()

                # Start the flash time up timer if the flash effect is turned on and the timer is not currently active and the
                # total seconds is negative. This enables the flash effect to be visible if it is enabled when the timer is not
                # running (reset, paused, etc.)
                if self.flash_time_up_alert_is_enabled and not self.time_up_flash_timer.isActive():
                    self.time_up_flash_timer.start(500)

                if self.first_negative_run and self.isVisible():
                    self.show_timer()
                    self.first_negative_run = False

            elif not self.show_time_up_label:
                self.time_up_label.hide()

                if hour_is_visible:
                    self.timer_label.setStyleSheet(TIMER_TEXT_TIME_UP_STYLE_HOUR)
                else:
                    self.timer_label.setStyleSheet(TIMER_TEXT_TIME_UP_STYLE)

        else:
            # Hide the time up label
            self.time_up_label.hide()

            # Stop the timer that controls the Time Up flash effect
            self.time_up_flash_timer.stop()

            # Update the font style of the timer text
            if hour_is_visible:
                self.timer_label.setStyleSheet(TIMER_TEXT_DEFAULT_STYLE_HOUR)
            else:
                self.timer_label.setStyleSheet(TIMER_TEXT_DEFAULT_STYLE)

        self.timer_label.setText(timer_text)

        self.refresh_minister_panel_visibility()  # The minister panel gives way to the Time Up label

    def update_running_timer(self, total_seconds):
        """Updates the timer window with the most recent time value

        This function is called when the timer object in the main_window emits a timeout signal (every 1 sec),
        which usually happens when a countdown timer is running. It is also called within the "Show" button toggled
        method in the main_window object, to update the window when the time up alert is set to show or hide and the
        timer is not currently running.

        The difference between this function and the "set_timer_text function" is that this only updates the time
        value, while the latter updates both the time value and the session label.

        """

        self.update_timer_window_labels(total_seconds)

        # Emit signal
        self.window_is_updated()

    def update_session_label(self, session_title):
        self.session_title_label.setText(session_title.upper())

        # Emit signal
        self.window_is_updated()

    def set_minister_name(self, minister_name: str):
        """Sets the name shown under "Ministering Now" """

        self.minister_name = minister_name.strip()
        self.minister_name_label.setText(self.minister_name.upper())
        self.update_minister_panel()

    def set_minister_enabled(self, enabled: bool):
        """Turns the "Ministering Now" panel on or off. Called when the minister toggle in the display settings changes"""

        self.minister_is_enabled = enabled
        self.update_minister_panel()

    def update_minister_panel(self):
        """Shows the "Ministering Now" panel if it is enabled and there is a name to show, and hides it otherwise

        The panel is also hidden while the Time Up alert is showing, since the alert takes the space under the timer

        """

        self.refresh_minister_panel_visibility()
        self.window_is_updated()

    def refresh_minister_panel_visibility(self):
        self.minister_panel.setVisible(self.minister_is_enabled and self.minister_name != ""
                                       and self.time_up_label.isHidden())

    def position_labels(self):
        """Places the labels in the window

        The labels are positioned directly rather than with a layout, so the timer always sits at the same height
        (TIMER_CENTRE_HEIGHT_RATIO) no matter how tall the title is or whether the minister panel is shown. The title
        is at the top, the minister panel just under the timer, and the Time Up label at the bottom

        """

        width = self.width()
        height = self.height()

        def label_height(widget):
            return widget.heightForWidth(width) if widget.hasHeightForWidth() else widget.sizeHint().height()

        self.session_title_label.setGeometry(0, 0, width, label_height(self.session_title_label))

        timer_height = label_height(self.timer_label)
        timer_top = round(height * TIMER_CENTRE_HEIGHT_RATIO - timer_height / 2)
        self.timer_label.setGeometry(0, timer_top, width, timer_height)

        self.minister_panel.setGeometry(0, timer_top + timer_height, width, label_height(self.minister_panel))

        time_up_height = label_height(self.time_up_label)
        self.time_up_label.setGeometry(0, height - time_up_height, width, time_up_height)

    def resizeEvent(self, event):
        self.position_labels()

    def set_background_color(self, color: QColor):
        """Sets a solid color as the timer window's background"""

        self.background_color = QColor(color)
        self.background_image = None
        self.set_window_transparency(False)
        self.update_background()

    def set_background_image(self, image: QPixmap):
        """Sets an image as the timer window's background. The image is scaled to cover the whole window"""

        self.background_image = image
        self.set_window_transparency(False)
        self.update_background()

    def set_background_transparent(self):
        """Removes the timer window's background, so only the text is shown

        On a monitor, whatever is behind the window shows through. Over NDI, the frames are sent with an alpha
        channel, so receivers such as OBS and vMix can key the timer over other video

        """

        self.background_image = None
        self.set_window_transparency(True)
        self.update_background()

    def update_background(self):
        """Repaints the window after a background change, and adds a shadow to the text when the background is an
        image or transparent, to keep it readable over busy or bright content"""

        text_needs_shadow = self.background_image is not None or self.background_is_transparent

        # References are kept, since PySide deletes an effect once nothing in Python refers to it
        self.text_shadows = []

        for label in (self.session_title_label, self.timer_label, self.minister_panel):
            if text_needs_shadow:
                shadow = QGraphicsDropShadowEffect()
                shadow.setColor(QColor(0, 0, 0, 220))
                shadow.setBlurRadius(40)
                shadow.setOffset(0, 4)
                label.setGraphicsEffect(shadow)
                self.text_shadows.append(shadow)
            else:
                label.setGraphicsEffect(None)

        self.update()
        self.window_is_updated()

    def set_window_transparency(self, transparent: bool):
        """Turns the window's see-through background on or off

        Windows only applies transparency when the native window is created, so the native window is destroyed and
        created again with the new settings, then shown again if it was visible

        """

        if transparent == self.background_is_transparent:
            return

        self.background_is_transparent = transparent

        was_visible = self.isVisible()

        self.hide()
        self.destroy()  # Destroys only the native window. The widget and its contents are kept

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, transparent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, transparent)

        if was_visible:
            if self.display_monitor is not None:
                self.setGeometry(self.display_monitor.geometry())
            self.show_timer()

    def paintEvent(self, event):
        """Paints the selected background behind the labels"""

        if self.background_is_transparent:
            return

        painter = QPainter(self)

        if self.background_image is not None:
            # Scale the image to cover the window, keeping its aspect ratio, and crop the overflow evenly
            scaled_image = self.background_image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                        Qt.TransformationMode.SmoothTransformation)
            x = (scaled_image.width() - self.width()) // 2
            y = (scaled_image.height() - self.height()) // 2
            painter.drawPixmap(0, 0, scaled_image, x, y, self.width(), self.height())
        else:
            painter.fillRect(self.rect(), self.background_color)

        painter.end()

    def snapshot(self) -> QImage:
        """Renders the timer window to an image, keeping transparent areas transparent

        Used for the preview in the main window and for the NDI output. Unlike grab(), this does not fill the image
        with the window's default background first, so a transparent background stays transparent

        """

        pixel_ratio = self.devicePixelRatioF()
        image = QImage(round(self.width() * pixel_ratio), round(self.height() * pixel_ratio),
                       QImage.Format.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(pixel_ratio)
        image.fill(Qt.GlobalColor.transparent)

        self.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)

        return image

    def show_timer(self):
        """ Show timer window in full screen"""
        self.showFullScreen()

    def set_display_monitor(self, display_monitor):
        """Sets the monitor the timer window is be displayed in"""

        self.display_monitor = display_monitor
        self.setGeometry(self.display_monitor.geometry())

    def switch_window_size(self):
        """ Switches the size of the timer window

        This function allows you to switch between full screen and maximized, by double-clicking on the timer window.

        """

        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def window_is_updated(self):
        """Emits a signal when a change happens on the timer window.

        This signal is intercepted in the main interface and used to update the timer preview window

        """

        self.position_labels()
        self.window_update_signal.emit()

    def add_flash_effect(self):
        """Adds a flash effect to a text"""
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(255, 255, 255))  # Shadow color
        self.shadow.setBlurRadius(150)  # Shadow blur radius
        self.shadow.setOffset(0, 0)  # Shadow offset
        self.time_up_label.setGraphicsEffect(self.shadow)
        self.time_up_flash_is_on = True

    def remove_flash_effect(self):
        """Removes the flash effect from a text"""
        self.time_up_label.setGraphicsEffect(None)
        self.time_up_flash_is_on = False

    def toggle_time_up_flash_effect(self):
        """Activates the flash effect on the Time Up text

        This function adds a flash effect to a text by executing the add_flash_effect and remove_flash_effect
        simultaneously functions within a specified time interval which is set when the start time function is called.

        """

        # This code block removes the flash effect if the effect is enabled, and adds it, if disabled
        # The self.time_up_flash_is_on variable is used to determine when the effect is enabled or disabled

        if self.time_up_flash_is_on:
            self.remove_flash_effect()
        elif not self.time_up_flash_is_on:
            self.add_flash_effect()
        else:
            pass

        # This signal is intercepted in the main interface and used to update the timer window
        # A dedicated signal was created for this because of the time interval difference between when the timer's
        # values are updated (1000ms) and when the flash effect happens (500ms)
        self.time_up_flash_signal.emit()

    def enable_time_up_flash_effect(self):
        """Sets the flash_time_up_alert variable to True

        This function is called whenever the "Flash" button is toggled on.

        """
        self.flash_time_up_alert_is_enabled = True

    def disable_time_up_flash_effect(self):
        """Disables the time up flash effect

        This function is called whenever the "Flash" button is toggled on.

        """

        self.flash_time_up_alert_is_enabled = False
        self.remove_flash_effect()  # Remove the flash effect
        self.time_up_flash_timer.stop()  # Stop the timer that controls the flash effect

    def keyPressEvent(self, event):

        # Emit signal when Ctrl + L is pressed
        # This signal is intercepted by the main interface window, which in turn activates the display mode toggle
        if event.key() == Qt.Key_L and event.modifiers() == Qt.ControlModifier:
            self.display_shortcut_signal.emit()

    def mouseDoubleClickEvent(self, event):
        """Switch between full screen and maximize when the timer window is double-clicked"""
        self.switch_window_size()

    def closeEvent(self, event):
        """Emits a signal whenever this window(timer window) is closed/destroyed

        This signal is intercepted in the main interface and used to set the checked state of the display mode button

        """
        self.timer_window_destroyed_signal.emit()
        # self.window_is_active = False
