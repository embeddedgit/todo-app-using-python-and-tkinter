# Do It. ✅
> A minimal, dark-themed To-Do app for Windows.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)
![Storage](https://img.shields.io/badge/Storage-Local%20SQLite-green?style=flat-square)

---

## 📸 About
**Do It.** is a lightweight, offline To-Do manager built with Python and Tkinter.  
No accounts. No cloud. No bloat. Just tasks.

---

## ✨ Features
- Add tasks instantly — type and hit Enter
- Check off tasks with a satisfying strikethrough
- Delete tasks with one click
- Live stats — see how many tasks are done vs remaining
- 100% offline — data stored locally on your PC
- Shareable — send the `.exe` + `tasks.db` to a friend

---

## 🚀 Running the App

### Option 1 — Just use the .exe (easiest)
1. Go to the `dist/` folder
2. Double-click `todo_app.exe`
3. Done. No Python needed.

### Option 2 — Run from source
Make sure you have Python 3.8+ installed, then:
```bash
python todo_app.py
```

---

## 🔨 Building the .exe yourself

Install PyInstaller:
```bash
pip install pyinstaller
```

Build with icon:
```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." todo_app.py
```

Build without icon:
```bash
pyinstaller --onefile --windowed todo_app.py
```

The `.exe` will appear in the `dist/` folder.

---

## 💾 Data & Sharing

Your tasks are saved in a file called `tasks.db` in the same folder as the app.

| What you want | What to send |
|---|---|
| Share just the app | `todo_app.exe` only |
| Share app + your tasks | `todo_app.exe` + `tasks.db` |

> ⚠️ `tasks.db` is created automatically on first run — don't worry if you don't see it yet.

---

## 🛡️ Windows SmartScreen Warning
When opening the `.exe` for the first time, Windows may show a warning.  
This is normal for unsigned apps. Click **"More info" → "Run anyway"** to proceed.

---

## 🛠️ Built With
- [Python](https://python.org) — Language
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — UI
- [SQLite](https://sqlite.org) — Local database
- [PyInstaller](https://pyinstaller.org) — Packaging

---

## 📁 Project Structure
```
do-it/
├── todo_app.py        # Main application source
├── todo_app.spec      # PyInstaller build config
├── icon.ico           # App icon
├── dist/
│   └── todo_app.exe   # Built Windows executable
└── README.md          # You are here
```

---

Made with 🖤 — Keep it simple. Get it done.
