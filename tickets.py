import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import font, messagebox, simpledialog, ttk

# next to the .exe when frozen by PyInstaller (__file__ would be a temp dir that gets wiped)
DB = Path(sys.executable if getattr(sys, "frozen", False) else __file__).with_name("tickets.db")
DAYS = ["1. dan", "2. dan", "3. dan", "4. dan"]


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


def remove_faculty(con, name):
    # sold tickets keep the faculty name, only the dropdown entry goes away
    with con:
        con.execute("DELETE FROM faculty WHERE name = ?", (name,))


def sell(con, idx, faculty, day):
    """Returns None on success, error message otherwise."""
    if not idx:
        return "Unesite indeks."
    if not faculty:
        return "Izaberite fakultet."
    try:
        with con:
            con.execute("INSERT INTO ticket VALUES (?, ?, ?)", (idx, faculty, day))
    except sqlite3.IntegrityError:
        return f"{idx} ({faculty}) već ima kartu za {DAYS[day - 1]}."


def latest(con, n=5):
    return con.execute("SELECT idx, faculty, day FROM ticket ORDER BY rowid DESC LIMIT ?", (n,)).fetchall()


def search(con, q):
    # ponytail: LIKE full scan, add an index on idx if it ever gets slow (it won't at student-event scale)
    like = f"%{q.strip()}%"
    return con.execute("SELECT idx, faculty, day FROM ticket WHERE idx LIKE ? OR faculty LIKE ? "
                       "ORDER BY idx, day", (like, like)).fetchall()


def table(parent, height):
    t = ttk.Treeview(parent, columns=("idx", "fac", "day"), show="headings", height=height)
    for col, text, w in (("idx", "Indeks", 180), ("fac", "Fakultet", 360), ("day", "Dan", 120)):
        t.heading(col, text=text, anchor="w")
        t.column(col, width=w, anchor="w")
    return t


def fill(t, rows):
    t.delete(*t.get_children())
    for idx, fac, day in rows:
        t.insert("", "end", values=(idx, fac, DAYS[day - 1]))


def main():
    con = connect()
    root = tk.Tk()
    root.title("Prodaja studentskih karata")
    root.geometry("800x600")
    root.resizable(False, False)
    font.nametofont("TkDefaultFont").configure(size=11)
    ttk.Style().configure("Treeview", rowheight=24)

    P = {"padx": 12, "pady": 6}
    idx = tk.StringVar()
    fac = tk.StringVar()
    day = tk.StringVar(value=DAYS[0])
    q = tk.StringVar()

    # --- nova karta ---
    form = ttk.LabelFrame(root, text="Nova karta", padding=10)
    form.pack(fill="x", **P)

    ttk.Label(form, text="Indeks:").grid(row=0, column=0, sticky="w", **P)
    idx_entry = ttk.Entry(form, textvariable=idx, width=20)
    idx_entry.grid(row=0, column=1, sticky="w", **P)

    ttk.Label(form, text="Fakultet:").grid(row=0, column=2, sticky="w", **P)
    fac_box = ttk.Combobox(form, textvariable=fac, values=faculties(con), state="readonly", width=20)
    fac_box.grid(row=0, column=3, sticky="w", **P)

    def new_faculty():
        name = simpledialog.askstring("Novi fakultet", "Naziv fakulteta:", parent=root)
        if name and name.strip():
            add_faculty(con, name)
            fac_box["values"] = faculties(con)
            fac.set(name.strip())

    def del_faculty():
        name = fac.get()
        if not name:
            messagebox.showinfo("Obriši fakultet", "Prvo izaberite fakultet.")
            return
        if messagebox.askyesno("Obriši fakultet", f"Obrisati „{name}” iz liste?\nProdate karte ostaju sačuvane."):
            remove_faculty(con, name)
            fac_box["values"] = faculties(con)
            fac.set("")

    btns = ttk.Frame(form)
    btns.grid(row=0, column=4, sticky="w", **P)
    ttk.Button(btns, text="+ Novi", width=7, command=new_faculty).pack(side="left")
    ttk.Button(btns, text="− Obriši", width=8, command=del_faculty).pack(side="left", padx=(6, 0))

    ttk.Label(form, text="Dan:").grid(row=1, column=0, sticky="w", **P)
    ttk.Combobox(form, textvariable=day, values=DAYS, state="readonly", width=17).grid(row=1, column=1, sticky="w", **P)

    status = ttk.Label(form, text="", foreground="green")
    status.grid(row=1, column=2, columnspan=3, sticky="w", **P)

    # --- poslednjih 5 ---
    last = ttk.LabelFrame(root, text="Poslednje dodati", padding=10)
    last.pack(fill="x", **P)
    last_t = table(last, 5)
    last_t.pack(fill="x")

    # --- pretraga ---
    find = ttk.LabelFrame(root, text="Pretraga (indeks ili fakultet)", padding=10)
    find.pack(fill="both", expand=True, **P)
    ttk.Entry(find, textvariable=q).pack(fill="x", pady=(0, 8))
    found_t = table(find, 4)  # expands to fill the rest of the window
    found_t.pack(fill="both", expand=True)

    def refresh(*_):
        fill(last_t, latest(con))
        fill(found_t, search(con, q.get()) if q.get().strip() else [])

    def on_sell(_=None):
        err = sell(con, idx.get().strip(), fac.get(), DAYS.index(day.get()) + 1)
        if err:
            messagebox.showerror("Karta nije prodata", err)
            return
        status["text"] = f"Prodato: {idx.get().strip()} / {fac.get()} / {day.get()}"
        idx.set("")
        idx_entry.focus()
        refresh()

    ttk.Button(form, text="Prodaj kartu", command=on_sell).grid(row=2, column=1, sticky="ew", **P)
    idx_entry.bind("<Return>", on_sell)
    q.trace_add("write", refresh)

    refresh()
    idx_entry.focus()
    root.mainloop()


if __name__ == "__main__":
    main()
