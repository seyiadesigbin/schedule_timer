# ScheduleTimer

ScheduleTimer is a desktop event-timing application built with Python and PySide6. It helps event teams create a running schedule, start and pause individual timers, and show a clean full-screen countdown on a selected monitor.

I built this project to solve a practical problem I have seen in live events: the person managing the programme needs detailed controls, while speakers, coordinators, or the audience need a simple, readable timer display. ScheduleTimer separates those two experiences into a control window and a dedicated timer window.

## Features

- Create multiple schedule items with a session title, minister, minutes, and seconds.
- Start, pause, resume, reset, and delete individual schedule timers.
- Display the active countdown in a separate full-screen timer window.
- Select the output monitor for the live timer display.
- Preview the timer output inside the main control window.
- Broadcast the timer display over the network as an NDI source for OBS, vMix, NDI Studio Monitor, and other NDI receivers.
- Toggle the session title on or off for the live display.
- Show **Ministering Now** with the minister's name under the timer, so the person speaking knows the time is theirs. Can be toggled on or off.
- Choose the timer background: dark, black, green or blue screen, a custom color, an image, or transparent.
- Continue counting past zero to show overtime with negative time.
- Show an optional "Time Up" alert with a flashing visual effect.
- Large, readable display in the bundled Barlow font. The timer stays at a fixed position regardless of title length.
- Export schedule data (including minister names) to a local file for reuse.
- Use keyboard shortcut `Ctrl + L` to toggle live display mode.
- Build a single-file Windows executable with PyInstaller.

## Why This Project Is Useful

ScheduleTimer is designed for environments where timing has to stay visible and reliable, such as:

- church services
- conferences
- seminars
- presentations
- rehearsals
- workshops
- live-streamed events

The application gives the operator detailed control without cluttering the display that other people see.

## Tech Stack

- **Python** - application logic
- **PySide6 / Qt** - desktop GUI framework
- **Qt stylesheets (QSS)** - custom interface styling
- **JSON** - schedule export format
- **NDI (ndi-python)** - network video output of the timer display
- **Barlow** - display and interface font, bundled under the SIL Open Font License
- **PyInstaller** - Windows executable packaging

## Project Structure

```text
schedule_timer/
|-- main.py                     # Application entry point
|-- main_window.py              # Main control window and timer orchestration
|-- timer_window.py             # Full-screen timer display window
|-- ndi_output.py               # NDI network output of the timer display
|-- schedule_item_interface.py  # Reusable schedule row component
|-- export_schedule.py          # Schedule export logic
|-- import_schedule.py          # Schedule import work-in-progress
|-- globals.py                  # Shared paths, constants, and helpers
|-- ScheduleTimer.spec          # PyInstaller build configuration
|-- requirements.txt            # Python dependencies
|-- resources/
|   |-- fonts/                  # Bundled Barlow font files and license
|   |-- icons/                  # App and toolbar icons
|   `-- stylesheets/            # QSS stylesheets
`-- README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Windows, macOS, or Linux with desktop GUI support

### Installation

Clone the repository:

```bash
git clone https://github.com/elijahkato/schedule_timer.git
cd schedule_timer
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

### Building a Windows Executable

With the virtual environment active:

```bash
pip install pyinstaller
python -m PyInstaller ScheduleTimer.spec --noconfirm
```

This produces a single self-contained file at `dist\ScheduleTimer.exe`, with the resources folder, app icon, and NDI runtime bundled in. You can copy it to another Windows PC and run it without installing Python.

## How To Use

1. Add a schedule item and enter a session title, the minister's name (optional), minutes, and seconds.
2. Click the start button on a schedule row to begin the countdown.
3. Use pause, resume, and reset controls as needed.
4. Choose an output monitor from the display settings.
5. Toggle **Live** to show or hide the full-screen timer display.
6. Toggle **NDI** to broadcast the timer display on your network (see [NDI Output](#ndi-output)).
7. Pick a **Background** for the timer display (see [Backgrounds](#backgrounds)).
8. Toggle **Minister** to show or hide **Ministering Now** under the timer (see [Ministering Now](#ministering-now)).
9. Enable **Time Up Alert** options if you want a visible alert after the timer reaches zero.
10. Export the current schedule when you want to save it for later.

## Timer Display

- Text uses the Barlow font, which is bundled with the app, so it does not need to be installed.
- The countdown uses Barlow's fixed-width digits, so the numbers do not shift sideways as the time changes.
- The session title is large, bold, and wraps onto a second line when it is long.
- The timer is always centred at 45% of the screen height, slightly above the middle, whatever the length of the title or whether the minister is shown. The ratio is `TIMER_CENTRE_HEIGHT_RATIO` in `timer_window.py`.

## Ministering Now

Each schedule item has a **Minister** field under its session title. When that session is active, the timer display shows **MINISTERING NOW** and the minister's name just under the timer, so the person on stage knows they are responsible for the time.

- Toggle **Minister** in **Display Settings** to show or hide it. It is on by default.
- Nothing is shown for a session with no minister's name.
- While the Time Up alert is showing, the minister's name is hidden to make room for the alert.
- Minister names are included in exported schedules. Schedules exported before this feature still import, with the minister left empty.

## Backgrounds

Use the **Background** dropdown in **Display Settings** to change what is behind the timer:

- **Dark**, **Black**, **Green Screen**, **Blue Screen** - solid colors. Green and blue are for chroma keying.
- **Custom Color...** - pick any color.
- **Image...** - a PNG, JPG, BMP, or WebP image, scaled to fill the screen.
- **Transparent** - on a monitor, whatever is behind the timer window shows through. Over NDI, the background is sent as alpha.

With an image or transparent background, the title and timer get a soft shadow so they stay readable. The preview shows a checkerboard where the background is transparent. The selected background is not saved when the app closes.

## NDI Output

Toggle the **NDI** button in **Display Settings** to broadcast the timer display as an NDI video source named `ScheduleTimer`. NDI receivers on the same network list it as `COMPUTER-NAME (ScheduleTimer)`.

- The output is 1920x1080 at 30 fps and matches the live display, including the session title, overtime, and the Time Up alert.
- NDI works with or without the live display. When the live display is off, the timer is drawn at 1920x1080 for NDI. When it is on, the full-screen window is scaled to fit 1920x1080.
- While receivers are connected, the button shows the connection count reported by NDI, for example `NDI (1)`.
- The `ndi-python` package includes the NDI library, so nothing else needs to be installed. If `ndi-python` is missing, the NDI button is disabled.
- With the **Transparent** background, frames are sent with an alpha channel, so OBS, vMix, and other receivers can place the timer over other video without keying.

## Implementation Highlights

- Uses Qt signals to keep the main control window, preview, and live timer display in sync.
- Supports multi-monitor workflows by detecting available screens through the Qt application instance.
- Keeps the display window focused and minimal, while the main window handles schedule management.
- Converts each schedule row into total seconds internally, making countdown, overtime, reset, and preview updates easier to manage.
- Uses modular files for the main window, timer window, schedule item widget, shared constants, and import/export concerns.
- Positions the timer display's labels directly instead of with a layout, so the timer's height on screen is fixed.
- Paints the timer background in `paintEvent`, and renders snapshots without a default fill, so a transparent background stays transparent in the preview and in NDI.
- Sends NDI frames from a background thread at a steady frame rate, as BGRX or as BGRA when the background is transparent.

## Current Status

This is a beta version. The core timer, schedule controls, live display, preview, time-up alert, and export flow are implemented. Schedule import is currently present in the interface but still needs refinement before it is production-ready.

## Future Improvements

- Finish and harden schedule import.
- Add automated tests for timer state changes and schedule serialization.
- Track actual time against planned time for each session and produce a report of sessions that ran late.
- Remember the selected background and display settings between sessions.
- Add an installer and code signing for the Windows build.
- Add drag-and-drop schedule reordering.
- Add optional sound alerts when time is up.
- Add screenshots or a short demo video to show the live display workflow.

## Author

Developed by **Oluwaseyi Adesigbin**.

- GitHub: [seyiadesigbin](https://github.com/seyiadesigbin)
- LinkedIn: [Oluwaseyi Adesigbin](https://www.linkedin.com/in/seyiadesigbin/)
