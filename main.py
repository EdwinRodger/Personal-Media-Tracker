"""
Personal Movies & Shows tracker — Tkinter + SQLite.
"""

import tkinter as tk
from tkinter import messagebox, ttk

import database as db


def validate_inputs(title, media_type, status, year, rating):
    """
    Check user input before we touch sqlite.

    Returns (True, "") if everything is okay, or (False, "short error message").
    """
    if not title or not str(title).strip():
        return False, "Title is required."
    if media_type not in db.TYPES:
        return False, "Type must be Movie or TV Show."
    if status not in db.STATUSES:
        return False, "Pick a valid status."
    if year is not None and (year < 1888 or year > 2100):
        return False, "Year should be between 1888 and 2100."
    if rating is not None and (rating < 0 or rating > 10):
        return False, "Rating must be between 0 and 10."
    return True, ""


def parse_year(text):
    """Turn the year box into an int or None. Raises ValueError if junk text."""
    text = (text or "").strip()
    if text == "":
        return None
    return int(text)


def parse_rating(text):
    """Turn the rating box into a float or None. Raises ValueError if junk text."""
    text = (text or "").strip()
    if text == "":
        return None
    return float(text)


class MovieTrackerApp(tk.Tk):
    """
    Main window.

    current_id keeps track of whether we are editing an existing row:
      - None means "new entry"
      - a number means "update this id when Save is pressed"
    """

    def __init__(self):
        super().__init__()
        db.init_db()

        self.title("My Movies & Shows Tracker")
        self.geometry("900x560")
        self.minsize(700, 480)

        self.current_id = None  # which database row the form is tied to

        self._build_widgets()
        self.refresh_table()

    def _build_widgets(self):
        """Create labels, entries, the tree (table), and hook up button commands."""
        top = ttk.Label(
            self,
            text="Track movies and TV — add rows, click one to edit, or delete.",
            padding=(10, 8),
        )
        top.pack(fill=tk.X)

        body = ttk.Frame(self, padding=10)
        body.pack(fill=tk.BOTH, expand=True)

        # Left = form, Right = list
        left = ttk.LabelFrame(body, text="Add / edit", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 8))

        right = ttk.LabelFrame(body, text="Library", padding=10)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Form fields ---
        ttk.Label(left, text="Title *").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.var_title = tk.StringVar()
        ttk.Entry(left, textvariable=self.var_title, width=32).grid(
            row=0, column=1, sticky=tk.EW, pady=3
        )

        ttk.Label(left, text="Type").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.var_type = tk.StringVar(value=db.TYPES[0])
        ttk.Combobox(
            left,
            textvariable=self.var_type,
            values=db.TYPES,
            state="readonly",
            width=30,
        ).grid(row=1, column=1, sticky=tk.EW, pady=3)

        ttk.Label(left, text="Status").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.var_status = tk.StringVar(value=db.STATUSES[0])
        ttk.Combobox(
            left,
            textvariable=self.var_status,
            values=db.STATUSES,
            state="readonly",
            width=30,
        ).grid(row=2, column=1, sticky=tk.EW, pady=3)

        ttk.Label(left, text="Year (optional)").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.var_year = tk.StringVar()
        ttk.Entry(left, textvariable=self.var_year, width=32).grid(
            row=3, column=1, sticky=tk.EW, pady=3
        )

        ttk.Label(left, text="Rating 0-10 (optional)").grid(
            row=4, column=0, sticky=tk.W, pady=3
        )
        self.var_rating = tk.StringVar()
        ttk.Entry(left, textvariable=self.var_rating, width=32).grid(
            row=4, column=1, sticky=tk.EW, pady=3
        )

        ttk.Label(left, text="Notes").grid(row=5, column=0, sticky=tk.NW, pady=3)
        self.text_notes = tk.Text(left, height=5, width=28, wrap=tk.WORD)
        self.text_notes.grid(row=5, column=1, sticky=tk.EW, pady=3)

        btn_row = ttk.Frame(left)
        btn_row.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_row, text="Save", command=self.on_save).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Clear", command=self.on_clear).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Delete selected row", command=self.on_delete).pack(side=tk.LEFT)

        left.columnconfigure(1, weight=1)

        # --- Search + table ---
        search_fr = ttk.Frame(right)
        search_fr.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(search_fr, text="Search:").pack(side=tk.LEFT, padx=(0, 6))
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *_: self.after_idle(self.refresh_table))
        ttk.Entry(search_fr, textvariable=self.var_search).pack(side=tk.LEFT, fill=tk.X, expand=True)

        cols = ("title", "kind", "status", "year", "rating")
        self.tree = ttk.Treeview(
            right,
            columns=cols,
            show="headings",
            height=16,
            selectmode="browse",
        )
        self.tree.heading("title", text="Title")
        self.tree.heading("kind", text="Type")
        self.tree.heading("status", text="Status")
        self.tree.heading("year", text="Year")
        self.tree.heading("rating", text="Rating")
        self.tree.column("title", width=220)
        self.tree.column("kind", width=85)
        self.tree.column("status", width=110)
        self.tree.column("year", width=55, anchor=tk.CENTER)
        self.tree.column("rating", width=60, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.load_selection_into_form())

        self.var_status_msg = tk.StringVar(value="Tip: click a row to edit it.")
        ttk.Label(self, textvariable=self.var_status_msg, padding=(10, 4)).pack(
            fill=tk.X, side=tk.BOTTOM
        )

    def refresh_table(self):
        """Reload rows from sqlite into the Treeview. Uses the search box text."""
        q = self.var_search.get()
        rows = db.fetch_all(q)

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            rid = str(row["id"])
            year_show = "" if row["year"] is None else str(row["year"])
            r = row["rating"]
            rating_show = "" if r is None else str(r)
            self.tree.insert(
                "",
                tk.END,
                iid=rid,
                values=(
                    row["title"],
                    row["media_type"],
                    row["status"],
                    year_show,
                    rating_show,
                ),
            )

    def load_selection_into_form(self):
        """When user picks a table row, copy values into the form (notes loaded separately)."""
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        try:
            self.current_id = int(iid)
        except ValueError:
            return

        vals = self.tree.item(iid, "values")
        if len(vals) < 5:
            return

        title, kind, status, year_s, rating_s = vals[:5]
        self.var_title.set(title)
        self.var_type.set(kind if kind in db.TYPES else db.TYPES[0])
        self.var_status.set(status if status in db.STATUSES else db.STATUSES[0])
        self.var_year.set(year_s)
        self.var_rating.set(rating_s)

        self.text_notes.delete("1.0", tk.END)
        self.text_notes.insert("1.0", db.fetch_notes(self.current_id))
        self.var_status_msg.set("Editing row id %s" % self.current_id)

    def on_clear(self):
        """Blank the form and stop pointing at an old id — next Save inserts a new row."""
        self.current_id = None
        self.var_title.set("")
        self.var_type.set(db.TYPES[0])
        self.var_status.set(db.STATUSES[0])
        self.var_year.set("")
        self.var_rating.set("")
        self.text_notes.delete("1.0", tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.var_status_msg.set("Ready for a new entry.")

    def on_save(self):
        """Validate, then INSERT if current_id is None else UPDATE."""
        title = self.var_title.get()
        media_type = self.var_type.get()
        status = self.var_status.get()
        notes = self.text_notes.get("1.0", tk.END).rstrip()

        try:
            year = parse_year(self.var_year.get())
            rating = parse_rating(self.var_rating.get())
        except ValueError:
            messagebox.showwarning("Bad input", "Year must be a whole number (or empty). Rating must be a number (or empty).")
            return

        ok, msg = validate_inputs(title, media_type, status, year, rating)
        if not ok:
            messagebox.showwarning("Cannot save", msg)
            return

        try:
            if self.current_id is None:
                new_id = db.insert_row(title, media_type, status, year, rating, notes)
                self.current_id = new_id
                self.var_status_msg.set('Saved new row as id %s.' % new_id)
            else:
                db.update_row(self.current_id, title, media_type, status, year, rating, notes)
                self.var_status_msg.set('Updated row id %s.' % self.current_id)
        except Exception as ex:
            messagebox.showerror("Database problem", str(ex))
            return

        self.refresh_table()
        if self.current_id is not None:
            sid = str(self.current_id)
            if self.tree.exists(sid):
                self.tree.selection_set(sid)
                self.tree.see(sid)

    def on_delete(self):
        """Delete the highlighted row after a yes/no popup."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Click a row in the table first.")
            return
        try:
            row_id = int(sel[0])
        except ValueError:
            messagebox.showerror("Delete", "Could not read row id.")
            return

        vals = self.tree.item(sel[0], "values")
        name = vals[0] if vals else "this entry"
        if not messagebox.askyesno("Confirm Delete?", 'Delete "%s"?' % name):
            return

        try:
            db.delete_row(row_id)
        except Exception as ex:
            messagebox.showerror("Database problem", str(ex))
            return

        self.on_clear()
        self.refresh_table()
        self.var_status_msg.set('Deleted "%s".' % name)


def main():
    """Create the window and start Tkinter's event loop."""
    app = MovieTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
