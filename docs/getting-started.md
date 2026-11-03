# Getting started with the ScheduleTimer beta

ScheduleTimer times live events. You run a schedule from the **control window**, and a clean
full-screen countdown shows on a projector, stage screen or confidence monitor.

Thank you for testing. This is an early beta, so please report anything odd (see
[Report a problem](#report-a-problem)).

## Install

**Windows:** download the installer (`ScheduleTimer-Setup-…exe`) from the
[releases page](https://github.com/seyiadesigbin/schedule_timer/releases) and run it. The beta is
not code signed yet, so Windows may show a "Windows protected your PC" screen. Choose **More
info**, then **Run anyway**.

**Mac:** download the Mac build from the same page. It is not signed or notarised yet, so macOS
will block it the first time. Open **System Settings > Privacy & Security**, find the message
about ScheduleTimer and choose **Open Anyway**.

## Build your first schedule

1. Choose **Add item** (Ctrl+Enter, or Cmd+Enter on a Mac).
2. Type a title and a duration. Any of these work: `5`, `5:30`, `1:05:00`, `90s`, `1h 30m`.
3. Add more items. Drag the handle on the left of an item to reorder it. Use the item's
   buttons to duplicate or delete it.
4. Made a mistake? Undo and redo cover every change.

## Run the timer

- **Space** starts or pauses the current item.
- **N** starts the next item, **B** cues the previous one without starting it, **R** resets the
  current item to its full time.
- **+** and **-** add or remove a minute while the timer runs.
- The timer turns amber as time runs low and red in overtime. You can set when the warning
  starts, and choose whether to show a "Time up" message, flash the time or play alert sounds,
  in **Settings** (Ctrl+, or Cmd+,).

The single-key shortcuts work whenever the cursor is not in a text field. **Help > Keyboard
Shortcuts** lists all of them.

## Go live on a second screen

1. Connect the projector or second monitor and set it to extend your desktop, not mirror it.
2. In **Settings**, choose the screen the timer is shown on.
3. Choose **Go live** in the toolbar, or press Ctrl+L (Cmd+L on a Mac). The full-screen timer opens on that
   screen. The control window also shows a live preview.
4. To hide it again, press Ctrl+L (Cmd+L), or press Esc while the timer screen has focus.

If you turn on **Go live automatically** in Settings, the timer opens on its own whenever a
second screen is connected. It never covers your main screen.

**Blackout** (the full stop key, `.`) blanks the timer screen without stopping the timer, for
moments when the audience should not see it. Press it again to bring the timer back.

## Save your work

- **File > Save** (Ctrl+S, or Cmd+S) saves the schedule as a `.stschedule` file.
- **File > Open** opens a saved schedule. It also imports schedules from version 1 (`.sch`
  files).
- The app opens with a blank schedule. To continue with your last schedule instead, open
  **Settings** and choose **Last schedule** under **When the app opens**.
- If you closed the app normally and want your last schedule back, choose **File > Reopen Previous
  Schedule**.
- If the app closes unexpectedly, your schedule comes back the next time you open it, whichever
  setting you chose. Save to a file anyway before an event.

## Beta end date and updates

- Beta 1 stops working after **31 March 2027**. From 14 days before that, the app
  warns you when it starts and offers a link to the releases page. After the date it opens that
  page and closes. The warning shows the exact date.
- There are no automatic updates yet. When a new beta comes out, download and install it over the
  old one from the [releases page](https://github.com/seyiadesigbin/schedule_timer/releases). Your
  saved schedules and settings stay.
- Later releases may have different terms. The beta licence is in the `LICENSE` file, and the
  notices for the software it includes are under **Help > Third-Party Notices**.

## Report a problem

Choose **Help > Report a Problem**. The app copies its diagnostics to your clipboard and opens a
short form. Paste the diagnostics into the form and tell us what you were doing, what you
expected and what happened. A screenshot helps.

Diagnostics stay on your computer until you paste them. They contain the app version, details of
your system and recent log lines, with your user name removed from file paths. Read them before
you send them if you like.

## Known limits in this beta

- Not code signed, so Windows and macOS show warnings when you first install.
- No automatic updates.
- Multiple screens and macOS full screen have had limited testing on real hardware. Please tell us
  how they behave for you.
