import re
import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

# next to the .exe when frozen by PyInstaller (__file__ would be a temp dir that gets wiped)
DB = Path(sys.executable if getattr(sys, "frozen", False) else __file__).with_name("tickets.db")
DAYS = ["1st day", "2nd day", "3rd day", "4th day"]
INDEX_RE = re.compile(r"\d{4}/\d{4}")


def connect(path=DB):
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS faculty (name TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS ticket (
            idx TEXT NOT NULL, faculty TEXT NOT NULL REFERENCES faculty(name), day INTEGER NOT NULL,
            UNIQUE (idx, faculty, day));
    """)
    return con


def faculties(con):
    return [r[0] for r in con.execute("SELECT name FROM faculty ORDER BY name")]


def add_faculty(con, name):
    with con:
        con.execute("INSERT OR IGNORE INTO faculty VALUES (?)", (name.strip(),))


def sell(con, idx, faculty, day):
    """Returns None on success, error message otherwise."""
    if not INDEX_RE.fullmatch(idx):
        return "Index must be in format bbbb/gggg (e.g. 0123/2024)."
    if not faculty:
        return "Pick a faculty."
    try:
        with con:
            con.execute("INSERT INTO ticket VALUES (?, ?, ?)", (idx, faculty, day))
    except sqlite3.IntegrityError:
        return f"{idx} ({faculty}) already has a ticket for {DAYS[day - 1]}."


def main():
    con = connect()
    root = tk.Tk()
    root.title("Student tickets")

    idx = tk.StringVar()
    fac = tk.StringVar()
    day = tk.StringVar(value=DAYS[0])

    ttk.Label(root, text="Index (bbbb/gggg)").grid(row=0, column=0, sticky="w", padx=6, pady=4)
    ttk.Entry(root, textvariable=idx).grid(row=0, column=1, sticky="ew", padx=6)

    ttk.Label(root, text="Faculty").grid(row=1, column=0, sticky="w", padx=6, pady=4)
    fac_box = ttk.Combobox(root, textvariable=fac, values=faculties(con), state="readonly")
    fac_box.grid(row=1, column=1, sticky="ew", padx=6)

    def new_faculty():
        name = simpledialog.askstring("New faculty", "Faculty name:", parent=root)
        if name and name.strip():
            add_faculty(con, name)
            fac_box["values"] = faculties(con)
            fac.set(name.strip())

    ttk.Button(root, text="+", width=3, command=new_faculty).grid(row=1, column=2, padx=6)

    ttk.Label(root, text="Day").grid(row=2, column=0, sticky="w", padx=6, pady=4)
    ttk.Combobox(root, textvariable=day, values=DAYS, state="readonly").grid(row=2, column=1, sticky="ew", padx=6)

    status = ttk.Label(root, text="")
    status.grid(row=4, column=0, columnspan=3, padx=6, pady=4)

    def on_sell(_=None):
        err = sell(con, idx.get().strip(), fac.get(), DAYS.index(day.get()) + 1)
        if err:
            messagebox.showerror("Not sold", err)
        else:
            status["text"] = f"Sold: {idx.get().strip()} / {fac.get()} / {day.get()}"
            idx.set("")

    ttk.Button(root, text="Sell ticket", command=on_sell).grid(row=3, column=1, sticky="ew", padx=6, pady=6)
    root.bind("<Return>", on_sell)
    root.columnconfigure(1, weight=1)
    root.mainloop()


if __name__ == "__main__":
    main()
