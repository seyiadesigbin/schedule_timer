# ScheduleTimer

ScheduleTimer is a desktop event-timing application built with Python and PySide6. It helps event teams create a running schedule, start and pause individual timers, and show a clean full-screen countdown on a selected monitor.

I built this project to solve a practical problem I have seen in live events: the person managing the programme needs detailed controls, while speakers, coordinators, or the audience need a simple, readable timer display. ScheduleTimer separates those two experiences into a control window and a dedicated timer window.

## Features

- Create multiple schedule items with a session title, minutes, and seconds.
- Start, pause, resume, reset, and delete individual schedule timers.
- Display the active countdown in a separate full-screen timer window.
- Select the output monitor for the live timer display.
- Preview the timer output inside the main control window.
- Toggle the session title on or off for the live display.
- Continue counting past zero to show overtime with negative time.
- Show an optional "Time Up" alert with a flashing visual effect.
- Export schedule data to a local file for reuse.
- Use keyboard shortcut `Ctrl + L` to toggle live display mode.

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

## Project Structure

```text
schedule_timer/
|-- main.py                     # Application entry point
|-- main_window.py              # Main control window and timer orchestration
|-- timer_window.py             # Full-screen timer display window
|-- schedule_item_interface.py  # Reusable schedule row component
|-- export_schedule.py          # Schedule export logic
|-- import_schedule.py          # Schedule import work-in-progress
|-- globals.py                  # Shared paths, constants, and helpers
|-- resources/
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
git clone https://github.com/seyiadesigbin/schedule_timer.git
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
pip install PySide6 easygui
```

Run the application:

```bash
python main.py
```

## How To Use

1. Add a schedule item and enter a session title, minutes, and seconds.
2. Click the start button on a schedule row to begin the countdown.
3. Use pause, resume, and reset controls as needed.
4. Choose an output monitor from the display settings.
5. Toggle **Live** to show or hide the full-screen timer display.
6. Enable **Time Up Alert** options if you want a visible alert after the timer reaches zero.
7. Export the current schedule when you want to save it for later.

## Implementation Highlights

- Uses Qt signals to keep the main control window, preview, and live timer display in sync.
- Supports multi-monitor workflows by detecting available screens through the Qt application instance.
- Keeps the display window focused and minimal, while the main window handles schedule management.
- Converts each schedule row into total seconds internally, making countdown, overtime, reset, and preview updates easier to manage.
- Uses modular files for the main window, timer window, schedule item widget, shared constants, and import/export concerns.

## Current Status

This is a beta version. The core timer, schedule controls, live display, preview, time-up alert, and export flow are implemented. Schedule import is currently present in the interface but still needs refinement before it is production-ready.

## Future Improvements

- Finish and harden schedule import.
- Add automated tests for timer state changes and schedule serialization.
- Add packaged builds for easier installation.
- Add drag-and-drop schedule reordering.
- Add optional sound alerts when time is up.
- Add screenshots or a short demo video to show the live display workflow.

## Author

Developed by **Oluwaseyi Adesigbin**.

- GitHub: [seyiadesigbin](https://github.com/seyiadesigbin)
- LinkedIn: [Oluwaseyi Adesigbin](https://www.linkedin.com/in/seyiadesigbin/)
