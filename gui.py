"""Tkinter UI for the media tracker."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from config import APP_TITLE, COLORS, FONT_FAMILY_UI
from database import Database, validate_media_row
from models import MEDIA_TYPES, STATUSES, MediaRow


class MediaTrackerApp(tk.Tk):
    def __init__(self, db: Database | None = None) -> None:
        super().__init__()
        self.db = db or Database()
        self.db.init_schema()

        self._current_id: int | None = None
        self._font_normal = (FONT_FAMILY_UI, 10)
        self._font_small = (FONT_FAMILY_UI, 9)
        self._font_heading = (FONT_FAMILY_UI, 11, "bold")

        self.title(APP_TITLE)
        self.geometry("980x620")
        self.minsize(780, 520)
        self.configure(bg=COLORS["bg"])

        self._setup_styles()
        self._build_ui()
        self._refresh_table()

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure(
            "Card.TFrame",
            background=COLORS["surface"],
            relief="flat",
        )
        style.configure(
            "Header.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["header"],
            font=self._font_heading,
        )
        style.configure(
            "Muted.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["muted"],
            font=self._font_small,
        )
        style.configure(
            "TLabel",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            font=self._font_normal,
        )
        style.configure(
            "TEntry",
            fieldbackground=COLORS["surface"],
            font=self._font_normal,
        )
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["surface"],
            font=self._font_normal,
        )
        style.configure(
            "Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            rowheight=26,
            font=self._font_normal,
        )
        style.configure(
            "Treeview.Heading",
            font=(FONT_FAMILY_UI, 10, "bold"),
            background=COLORS["border"],
            foreground=COLORS["header"],
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Accent.TButton",
            font=self._font_normal,
            padding=(14, 8),
        )
        style.configure(
            "Ghost.TButton",
            font=self._font_normal,
            padding=(12, 6),
        )

    def _card(self, parent: tk.Widget, **grid_kw) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=16)
        frame.grid(**grid_kw)
        frame.columnconfigure(1, weight=1)
        return frame

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=COLORS["bg"], padx=20, pady=16)
        outer.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(outer, bg=COLORS["bg"])
        header.pack(fill=tk.X, pady=(0, 12))
        tk.Label(
            header,
            text=APP_TITLE,
            font=(FONT_FAMILY_UI, 18, "bold"),
            fg=COLORS["header"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Track movies and TV shows — search, add, edit, and delete entries.",
            font=self._font_small,
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W)

        body = tk.Frame(outer, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        form_card = self._card(body, row=0, column=0, sticky="nsew", padx=(0, 10))
        list_card = self._card(body, row=0, column=1, sticky="nsew")

        self._build_form(form_card)
        self._build_list(list_card)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(
            outer,
            textvariable=self.status_var,
            font=self._font_small,
            fg=COLORS["muted"],
            bg=COLORS["bg"],
            anchor=tk.W,
        )
        status.pack(fill=tk.X, pady=(12, 0))

    def _build_form(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Add or edit", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4)
        )
        ttk.Label(
            parent,
            text="Fill the form and click Save. Select a row below to edit.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))

        row = 2
        ttk.Label(parent, text="Title *").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.var_title = tk.StringVar()
        ttk.Entry(parent, textvariable=self.var_title, width=28).grid(
            row=row, column=1, sticky="ew", pady=4
        )

        row += 1
        ttk.Label(parent, text="Type").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.var_type = tk.StringVar(value=MEDIA_TYPES[0])
        ttk.Combobox(
            parent,
            textvariable=self.var_type,
            values=MEDIA_TYPES,
            state="readonly",
            width=26,
        ).grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        ttk.Label(parent, text="Status").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.var_status = tk.StringVar(value=STATUSES[0])
        ttk.Combobox(
            parent,
            textvariable=self.var_status,
            values=STATUSES,
            state="readonly",
            width=26,
        ).grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        ttk.Label(parent, text="Year").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.var_year = tk.StringVar()
        ttk.Entry(parent, textvariable=self.var_year, width=28).grid(
            row=row, column=1, sticky="ew", pady=4
        )

        row += 1
        ttk.Label(parent, text="Rating (0–10)").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.var_rating = tk.StringVar()
        ttk.Entry(parent, textvariable=self.var_rating, width=28).grid(
            row=row, column=1, sticky="ew", pady=4
        )

        row += 1
        ttk.Label(parent, text="Notes").grid(row=row, column=0, sticky=tk.NW, pady=4)
        notes_frame = ttk.Frame(parent, style="Card.TFrame")
        notes_frame.grid(row=row, column=1, sticky="ew", pady=4)
        self.txt_notes = tk.Text(
            notes_frame,
            height=5,
            width=28,
            font=self._font_normal,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        self.txt_notes.pack(fill=tk.BOTH, expand=True)

        row += 1
        btn_row = ttk.Frame(parent, style="Card.TFrame")
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Button(btn_row, text="Save", style="Accent.TButton", command=self._on_save).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(btn_row, text="Clear form", style="Ghost.TButton", command=self._on_clear).pack(
            side=tk.LEFT
        )

    def _build_list(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Library", style="Header.TLabel").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 4)
        )

        search_row = ttk.Frame(parent, style="Card.TFrame")
        search_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        search_row.columnconfigure(1, weight=1)
        ttk.Label(search_row, text="Search").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.var_search = tk.StringVar()
        ent = ttk.Entry(search_row, textvariable=self.var_search)
        ent.grid(row=0, column=1, sticky="ew")
        self.var_search.trace_add("write", lambda *_: self.after_idle(self._refresh_table))

        tree_frame = ttk.Frame(parent, style="Card.TFrame")
        tree_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)

        cols = ("title", "type", "status", "year", "rating")
        headings = ("Title", "Type", "Status", "Year", "Rating")
        widths = (240, 90, 110, 60, 70)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            selectmode="browse",
            height=14,
        )
        for c, h, w in zip(cols, headings, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor=tk.W if c != "year" and c != "rating" else tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self._load_selection_into_form())

        btn_bar = ttk.Frame(parent, style="Card.TFrame")
        btn_bar.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Button(btn_bar, text="Delete selected", style="Ghost.TButton", command=self._on_delete).pack(
            side=tk.LEFT
        )

    def _parse_optional_int(self, raw: str) -> int | None:
        raw = raw.strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            raise ValueError("Year must be a whole number or empty.")

    def _parse_optional_float(self, raw: str) -> float | None:
        raw = raw.strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            raise ValueError("Rating must be a number between 0 and 10 or empty.")

    def _form_to_row(self) -> MediaRow:
        year = self._parse_optional_int(self.var_year.get())
        rating = self._parse_optional_float(self.var_rating.get())
        return MediaRow(
            id=self._current_id,
            title=self.var_title.get(),
            media_type=self.var_type.get(),
            status=self.var_status.get(),
            year=year,
            rating=rating,
            notes=self.txt_notes.get("1.0", tk.END).rstrip(),
        )

    def _on_save(self) -> None:
        try:
            row = self._form_to_row()
        except ValueError as e:
            messagebox.showwarning("Invalid input", str(e))
            return

        ok, msg = validate_media_row(
            row.title,
            row.media_type,
            row.status,
            row.year,
            row.rating,
        )
        if not ok:
            messagebox.showwarning("Cannot save", msg)
            return

        try:
            if self._current_id is None:
                new_id = self.db.insert(row)
                self._current_id = new_id
                self.status_var.set(f'Added "{row.title.strip()}".')
            else:
                self.db.update(self._current_id, row)
                self.status_var.set(f'Updated "{row.title.strip()}".')
        except Exception as exc:
            messagebox.showerror("Database error", str(exc))
            return

        self._refresh_table()
        self._select_row_by_id(self._current_id)

    def _on_clear(self) -> None:
        self._current_id = None
        self.var_title.set("")
        self.var_type.set(MEDIA_TYPES[0])
        self.var_status.set(STATUSES[0])
        self.var_year.set("")
        self.var_rating.set("")
        self.txt_notes.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())
        self.status_var.set("New entry — fill the form and click Save.")

    def _on_delete(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a row first.")
            return
        item = sel[0]
        values = self.tree.item(item, "values")
        title = values[0] if values else "this entry"
        try:
            row_id = int(item)
        except ValueError:
            messagebox.showerror("Delete", "Could not resolve row id.")
            return
        if not messagebox.askyesno("Confirm delete", f'Remove "{title}" from your library?'):
            return
        try:
            self.db.delete(row_id)
        except Exception as exc:
            messagebox.showerror("Database error", str(exc))
            return
        self._on_clear()
        self._refresh_table()
        self.status_var.set(f'Deleted "{title}".')

    def _refresh_table(self) -> None:
        search = self.var_search.get()
        rows = self.db.list_all(search)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            rating_disp = "" if r.rating is None else f"{r.rating:g}"
            year_disp = "" if r.year is None else str(r.year)
            iid = str(r.id)
            self.tree.insert(
                "",
                tk.END,
                iid=iid,
                values=(r.title, r.media_type, r.status, year_disp, rating_disp),
            )

    def _on_tree_select(self, _event=None) -> None:
        self._load_selection_into_form()

    def _load_selection_into_form(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        try:
            self._current_id = int(iid)
        except ValueError:
            return
        values = self.tree.item(iid, "values")
        if len(values) < 5:
            return
        title, mtype, status, year_disp, rating_disp = values[:5]
        self.var_title.set(title)
        self.var_type.set(mtype if mtype in MEDIA_TYPES else MEDIA_TYPES[0])
        self.var_status.set(status if status in STATUSES else STATUSES[0])
        self.var_year.set(year_disp)
        self.var_rating.set(rating_disp)
        self.txt_notes.delete("1.0", tk.END)
        row_notes = self._fetch_notes(self._current_id)
        self.txt_notes.insert("1.0", row_notes)
        self.status_var.set(f"Editing: {title}")

    def _fetch_notes(self, row_id: int) -> str:
        with self.db.connect() as conn:
            cur = conn.execute("SELECT notes FROM media WHERE id = ?", (row_id,))
            one = cur.fetchone()
        return (one["notes"] or "") if one else ""

    def _select_row_by_id(self, row_id: int | None) -> None:
        if row_id is None:
            return
        iid = str(row_id)
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)


def run_app() -> None:
    app = MediaTrackerApp()
    app.mainloop()
