# KeyRecord

<p align="center">
  <img src="docs/images/icon.png" alt="KeyRecord icon" width="96" />
</p>

<p align="center">
  <strong>Local keyboard and mouse usage heatmap for Windows.</strong>
</p>

<p align="center">
  Track how you actually use your keyboard and mouse, then visualize it with a clear heatmap.
</p>

<p align="center">
  <a href="https://github.com/adriaabad/keyrecord/releases">Download latest release</a>
</p>

---

## Preview

### Main window

![KeyRecord main screenshot](docs/images/screenshot-main.png)

### System tray

![KeyRecord tray screenshot](docs/images/screenshot-tray.png)

---

## Features

- Keyboard usage heatmap
- Mouse usage heatmap
- Session and total statistics
- ISO-ES and ANSI-US keyboard layouts
- System tray support
- Minimize to tray
- Local data storage
- Windows executable support

---

## Why use KeyRecord?

KeyRecord helps you understand how you really use your hardware.

It can help answer questions such as:

- Do I really use the numpad?
- Do I use function keys often?
- Do I use mouse side buttons?
- Would a smaller keyboard layout work for me?
- Which inputs do I actually use the most?

---

## Privacy

KeyRecord is designed as a local usage analysis tool.

It does **not** store:

- typed text
- words or sentences
- passwords
- websites
- window titles
- screenshots
- clipboard content

It only stores local usage counters such as key presses, mouse clicks and scroll activity.

All data is stored locally on your computer.

---

## Download

You can download the latest Windows executable from the [Releases page](https://github.com/adriaabad/keyrecord/releases).

---

## Run from source

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
