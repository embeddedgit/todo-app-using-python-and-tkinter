import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
import sys

# ── DB setup ────────────────────────────────────────────────────────────────
def get_db_path():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "tasks.db")

def init_db():
    conn = sqlite3.connect(get_db_path())
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def fetch_tasks():
    conn = sqlite3.connect(get_db_path())
    rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    conn.close()
    return rows

def add_task(title):
    conn = sqlite3.connect(get_db_path())
    conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()

def toggle_task(task_id, done):
    conn = sqlite3.connect(get_db_path())
    conn.execute("UPDATE tasks SET done=? WHERE id=?", (done, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(get_db_path())
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def update_task_title(task_id, new_title):
    conn = sqlite3.connect(get_db_path())
    conn.execute("UPDATE tasks SET title=? WHERE id=?", (new_title, task_id))
    conn.commit()
    conn.close()

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#0f0f13"
SURFACE   = "#1a1a24"
CARD      = "#22222f"
ACCENT    = "#7c6af7"
ACCENT2   = "#a78bfa"
TEXT      = "#e8e8f0"
SUBTEXT   = "#6b6b80"
DONE_CLR  = "#3d3d50"
DONE_TXT  = "#55556b"
BORDER    = "#2e2e3f"
RED       = "#f87171"
GREEN     = "#4ade80"
FONT_MAIN = ("Segoe UI", 11)
FONT_BTN  = ("Segoe UI", 10, "bold")
FONT_TASK = ("Segoe UI", 11)

# ── App ──────────────────────────────────────────────────────────────────────
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Do It.")
        self.geometry("520x680")
        self.minsize(420, 500)
        self.configure(bg=BG)
        self.resizable(True, True)

        try:
            self.iconbitmap(self._get_icon_path())
        except Exception:
            pass

        init_db()
        self._task_widgets = []
        self._editing_id = None  # track which task is being edited
        self._build_ui()
        self._load_tasks()

    def _get_icon_path(self):
        if getattr(sys, "frozen", False):
            return os.path.join(sys._MEIPASS, "icon.ico")
        return os.path.join(os.path.dirname(__file__), "icon.ico")

    def _build_ui(self):
        # ── Header
        header = tk.Frame(self, bg=BG, padx=28, pady=24)
        header.pack(fill="x")
        tk.Label(header, text="Do It.", font=("Segoe UI", 26, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(header, text="Keep it simple. Get it done.",
                 font=("Segoe UI", 10), bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(2, 0))

        # ── Hint label
        tk.Label(header, text="💡 Double-click any task to edit it",
                 font=("Segoe UI", 9), bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(4, 0))

        # ── Accent line
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x", padx=28)

        # ── Input row
        input_frame = tk.Frame(self, bg=BG, padx=28, pady=18)
        input_frame.pack(fill="x")

        self.entry = tk.Entry(
            input_frame, font=FONT_MAIN, bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT2, relief="flat",
            bd=0, highlightthickness=2,
            highlightbackground=BORDER, highlightcolor=ACCENT
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=10, ipadx=10)
        self.entry.bind("<Return>", lambda e: self._add())
        self.entry.focus()

        add_btn = tk.Button(
            input_frame, text="+ Add", font=FONT_BTN,
            bg=ACCENT, fg="#ffffff", activebackground=ACCENT2,
            activeforeground="#ffffff", relief="flat", bd=0,
            cursor="hand2", command=self._add, padx=16, pady=10
        )
        add_btn.pack(side="left", padx=(10, 0))

        # ── Stats bar
        self.stats_var = tk.StringVar()
        stats_bar = tk.Frame(self, bg=BG, padx=28)
        stats_bar.pack(fill="x")
        tk.Label(stats_bar, textvariable=self.stats_var,
                 font=("Segoe UI", 9), bg=BG, fg=SUBTEXT).pack(anchor="w")

        # ── Scrollable task list
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y", pady=(10, 10))
        self.canvas.pack(side="left", fill="both", expand=True, padx=(28, 4), pady=(10, 20))

        self.task_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.task_frame, anchor="nw")

        self.task_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load_tasks(self):
        for w in self._task_widgets:
            w.destroy()
        self._task_widgets.clear()
        self._editing_id = None

        tasks = fetch_tasks()
        for task_id, title, done in tasks:
            self._render_task(task_id, title, bool(done))

        self._update_stats(tasks)

    def _render_task(self, task_id, title, done):
        card_bg = DONE_CLR if done else CARD

        card = tk.Frame(self.task_frame, bg=card_bg, pady=0)
        card.pack(fill="x", pady=(0, 6))

        strip = tk.Frame(card, bg=ACCENT if not done else SUBTEXT, width=4)
        strip.pack(side="left", fill="y")

        inner = tk.Frame(card, bg=card_bg, padx=14, pady=12)
        inner.pack(side="left", fill="both", expand=True)

        var = tk.BooleanVar(value=done)

        def on_toggle(tid=task_id, v=var):
            toggle_task(tid, int(v.get()))
            self._load_tasks()

        chk = tk.Checkbutton(
            inner, variable=var, command=on_toggle,
            bg=card_bg, activebackground=card_bg,
            fg=DONE_TXT if done else TEXT, selectcolor=SURFACE,
            bd=0, highlightthickness=0, cursor="hand2"
        )
        chk.pack(side="left")

        lbl = tk.Label(
            inner, text=title, font=("Segoe UI", 11, "overstrike") if done else FONT_TASK,
            bg=card_bg, fg=DONE_TXT if done else TEXT,
            anchor="w", wraplength=320, justify="left", cursor="hand2"
        )
        lbl.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ── Edit button (pencil)
        edit_btn = tk.Button(
            inner, text="✏", font=("Segoe UI", 9),
            bg=card_bg, fg=SUBTEXT, activebackground=ACCENT,
            activeforeground="#fff", relief="flat", bd=0,
            cursor="hand2",
            command=lambda tid=task_id, ttl=title, c=card, l=lbl, eb=None: self._start_edit(tid, ttl, inner, lbl, card)
        )
        edit_btn.pack(side="right", padx=(4, 0))

        del_btn = tk.Button(
            inner, text="✕", font=("Segoe UI", 9, "bold"),
            bg=card_bg, fg=SUBTEXT, activebackground=RED,
            activeforeground="#fff", relief="flat", bd=0,
            cursor="hand2",
            command=lambda tid=task_id: self._delete(tid)
        )
        del_btn.pack(side="right")

        # Double click label to edit too
        lbl.bind("<Double-Button-1>", lambda e, tid=task_id, ttl=title: self._start_edit(tid, ttl, inner, lbl, card))

        self._task_widgets.append(card)

    def _start_edit(self, task_id, current_title, inner, lbl, card):
        # If already editing something else, cancel it first
        if self._editing_id is not None and self._editing_id != task_id:
            self._load_tasks()
            return

        self._editing_id = task_id

        # Hide the label
        lbl.pack_forget()

        # Inline edit entry
        edit_var = tk.StringVar(value=current_title)
        edit_entry = tk.Entry(
            inner, textvariable=edit_var, font=FONT_TASK,
            bg=SURFACE, fg=TEXT, insertbackground=ACCENT2,
            relief="flat", bd=0, highlightthickness=2,
            highlightbackground=ACCENT, highlightcolor=ACCENT2
        )
        edit_entry.pack(side="left", fill="x", expand=True, ipady=4, ipadx=6, padx=(6, 6))
        edit_entry.focus()
        edit_entry.select_range(0, "end")

        def save_edit(event=None):
            new_title = edit_var.get().strip()
            if new_title and new_title != current_title:
                update_task_title(task_id, new_title)
            self._load_tasks()

        def cancel_edit(event=None):
            self._load_tasks()

        edit_entry.bind("<Return>", save_edit)
        edit_entry.bind("<Escape>", cancel_edit)
        edit_entry.bind("<FocusOut>", save_edit)

    def _add(self):
        title = self.entry.get().strip()
        if not title:
            return
        add_task(title)
        self.entry.delete(0, "end")
        self._load_tasks()

    def _delete(self, task_id):
        delete_task(task_id)
        self._load_tasks()

    def _update_stats(self, tasks):
        total = len(tasks)
        done = sum(1 for _, _, d in tasks if d)
        if total == 0:
            self.stats_var.set("No tasks yet — add one above.")
        else:
            remaining = total - done
            self.stats_var.set(f"{done}/{total} done  ·  {remaining} remaining")


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
