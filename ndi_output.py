# This module broadcasts the timer display as an NDI video source, so it can be picked up by NDI receivers on the
# network (OBS, vMix, NDI Studio Monitor, etc.) without needing a physical output monitor.

import threading

from PySide6.QtCore import QObject, Signal, Qt, QRectF
from PySide6.QtGui import QImage, QPainter, QColor

try:
    import numpy as np
    import NDIlib as ndi
    NDI_IS_AVAILABLE = True
except ImportError:
    NDI_IS_AVAILABLE = False

NDI_SOURCE_NAME = "ScheduleTimer"
NDI_FRAME_WIDTH = 1920
NDI_FRAME_HEIGHT = 1080
NDI_FRAME_RATE = 30


class NdiOutput(QObject):

    connections_changed_signal = Signal(int)  # Emits the number of receivers connected to the NDI source

    def __init__(self):
        super().__init__()

        self.sender = None
        self.send_thread = None
        self.stop_event = threading.Event()

        # The most recent frame to be sent, and its pixel format. It is replaced whenever the timer window changes and
        # re-sent at a steady frame rate by the send thread, since NDI receivers expect a continuous video stream
        self.latest_frame = None
        self.latest_frame_fourcc = None
        self.frame_lock = threading.Lock()

    def is_running(self) -> bool:
        return self.sender is not None

    def start(self) -> bool:
        """Creates the NDI source and starts sending frames

        :returns: True if the NDI source was created, or False if otherwise
        :rtype: bool

        """

        if not NDI_IS_AVAILABLE or self.is_running():
            return self.is_running()

        if not ndi.initialize():
            return False

        send_settings = ndi.SendCreate()
        send_settings.ndi_name = NDI_SOURCE_NAME
        send_settings.clock_video = True  # Let NDI pace the send loop to the frame rate

        self.sender = ndi.send_create(send_settings)

        if self.sender is None:
            ndi.destroy()
            return False

        self.stop_event.clear()
        self.send_thread = threading.Thread(target=self.send_frames, daemon=True)
        self.send_thread.start()

        return True

    def stop(self):
        """Stops sending frames and removes the NDI source from the network"""

        if not self.is_running():
            return

        self.stop_event.set()
        self.send_thread.join()
        self.send_thread = None

        ndi.send_destroy(self.sender)
        self.sender = None
        ndi.destroy()

        self.connections_changed_signal.emit(0)

    def update_frame(self, snapshot: QImage, letterbox_color: QColor, has_alpha: bool):
        """Replaces the frame being sent with a snapshot of the timer window

        The snapshot is scaled to fit the NDI frame size, keeping its aspect ratio, and centred on the letterbox color

        :param snapshot: Snapshot of the timer window
        :type snapshot: QImage

        :param letterbox_color: Color to fill any space the snapshot does not cover
        :type letterbox_color: QColor

        :param has_alpha: Whether to send the frame with an alpha channel, for a transparent background
        :type has_alpha: bool

        """

        image = QImage(NDI_FRAME_WIDTH, NDI_FRAME_HEIGHT, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent if has_alpha else letterbox_color)

        scale = min(NDI_FRAME_WIDTH / snapshot.width(), NDI_FRAME_HEIGHT / snapshot.height())
        width = snapshot.width() * scale
        height = snapshot.height() * scale
        target = QRectF((NDI_FRAME_WIDTH - width) / 2, (NDI_FRAME_HEIGHT - height) / 2, width, height)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawImage(target, snapshot)
        painter.end()

        # NDI expects straight (non-premultiplied) alpha. Format_ARGB32 is stored as BGRA in memory
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        fourcc = ndi.FOURCC_VIDEO_TYPE_BGRA if has_alpha else ndi.FOURCC_VIDEO_TYPE_BGRX

        frame = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(NDI_FRAME_HEIGHT, NDI_FRAME_WIDTH, 4).copy()

        with self.frame_lock:
            self.latest_frame = frame
            self.latest_frame_fourcc = fourcc

    def send_frames(self):
        """Sends the latest frame continuously at the NDI frame rate. Runs on a background thread"""

        video_frame = ndi.VideoFrameV2()
        connections = 0
        frames_sent = 0

        while not self.stop_event.is_set():
            with self.frame_lock:
                frame = self.latest_frame
                fourcc = self.latest_frame_fourcc

            if frame is None:
                self.stop_event.wait(1 / NDI_FRAME_RATE)
                continue

            video_frame.data = frame
            video_frame.FourCC = fourcc
            video_frame.xres = NDI_FRAME_WIDTH
            video_frame.yres = NDI_FRAME_HEIGHT
            video_frame.line_stride_in_bytes = NDI_FRAME_WIDTH * 4
            video_frame.frame_rate_N = NDI_FRAME_RATE * 1000
            video_frame.frame_rate_D = 1000
            video_frame.picture_aspect_ratio = NDI_FRAME_WIDTH / NDI_FRAME_HEIGHT
            video_frame.frame_format_type = ndi.FRAME_FORMAT_TYPE_PROGRESSIVE

            ndi.send_send_video_v2(self.sender, video_frame)  # Blocks until the next frame is due

            # Check the number of connected receivers about once every second
            frames_sent += 1
            if frames_sent % NDI_FRAME_RATE == 0:
                current_connections = ndi.send_get_no_connections(self.sender, 0)
                if current_connections != connections:
                    connections = current_connections
                    self.connections_changed_signal.emit(connections)
