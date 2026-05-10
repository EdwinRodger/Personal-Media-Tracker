# Personal Movies & Shows Tracker

A small desktop application for keeping a **personal library** of films and TV series: add entries, track watch status, optional year and rating, free-form notes, search the list, and persist everything locally with **SQLite**. The interface is built with **Tkinter** (`ttk`) using a simple card-style layout and consistent typography.

There are **no third-party Python packages**. Everything runs on the standard library (`tkinter`, `sqlite3`, `pathlib`, `dataclasses`, etc.).

---

## Features

- **Create** new movies or TV shows with title (required), type, status, optional year (1888–2100), optional rating (0–10), and notes.
- **Read** all entries in a sortable table view (ordered by most recently updated, then title).
- **Update** an existing row by selecting it (form fills automatically), editing fields, and clicking **Save**.
- **Delete** the selected row after confirmation.
- **Search** filters rows by **title** or **notes** (case-insensitive substring match), updating as you type.
- **Notes** are stored in the database and loaded when you select a row; they are **not** shown in the table columns (only title, type, status, year, rating appear there).

---

## Requirements

- **Python 3.10+** (the code uses union types like `Path | None` and built-in generics like `list[str]`).
- A working **Tkinter** install:
  - **Windows / macOS**: usually included with the official Python installer.
  - **Linux**: you may need your distro’s Tk package (for example `python3-tk` on Debian/Ubuntu).

---

## How to run

From the project directory (activate your virtual environment if you use one):

```bash
python main.py
```

If your shell uses the venv explicitly:

```bash
# Windows (PowerShell / CMD)
venv\Scripts\python.exe main.py
```

On first launch, the app creates a SQLite file **`media_tracker.db`** in the **same folder as the Python modules** (next to `main.py`), unless you change the path in `config.py`.

---

## Project structure

| File | Purpose |
|------|---------|
| **`main.py`** | Entry point: imports `run_app()` from `gui` and starts the event loop. |
| **`config.py`** | Application title, database filename/path (`APP_DIR / DB_FILENAME`), UI fonts (Segoe UI / Consolas), and color palette for backgrounds, accents, and text. |
| **`models.py`** | **`MediaRow`** dataclass holding one logical record. Defines allowed **`MEDIA_TYPES`** (`Movie`, `TV Show`) and **`STATUSES`** (`Plan to watch`, `Watching`, `Watched`) used consistently in the UI and validation. |
| **`database.py`** | **`Database`** class: opens connections, creates schema and indexes, and implements **`list_all`**, **`insert`**, **`update`**, **`delete`**. Also exposes **`validate_media_row`** for form validation before writes. |
| **`gui.py`** | **`MediaTrackerApp`** (`tk.Tk` subclass): builds the window, styles (`ttk.Style`, `clam` theme), form fields, `Treeview`, search binding, and wires buttons to the database. **`run_app()`** constructs the app and calls **`mainloop()`**. |

Data flow is intentionally linear: the GUI collects strings and numbers, validates them (with helpers in `database.py`), converts them to **`MediaRow`**, then calls **`Database`** methods. Listing and search always go through **`Database.list_all`**, which returns **`MediaRow`** instances the GUI renders into table rows.

---

## Database design

### Table: `media`

| Column | Type | Meaning |
|--------|------|---------|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Stable row identifier; also used as the **Treeview item id (`iid`)** so the UI can map a selected row back to the database without a hidden column. |
| `title` | `TEXT NOT NULL` | Display name of the movie or show. |
| `media_type` | `TEXT NOT NULL` | Either **`Movie`** or **`TV Show`** (`CHECK` constraint matches `models.MEDIA_TYPES`). |
| `status` | `TEXT NOT NULL` | **`Plan to watch`**, **`Watching`**, or **`Watched`** (`CHECK` constraint matches `models.STATUSES`). |
| `year` | `INTEGER` | Optional release year (`NULL` if omitted). |
| `rating` | `REAL` | Optional score from 0 to 10 (`NULL` if omitted). |
| `notes` | `TEXT` | Optional longer text; defaults to empty string at insert. |
| `created_at` | `TEXT NOT NULL` | UTC timestamp when the row was created (ISO 8601 with seconds). |
| `updated_at` | `TEXT NOT NULL` | UTC timestamp updated on every **`UPDATE`** (and set equal to `created_at` on **`INSERT`**). |

### Indexes

- **`idx_media_title`**: index on `title COLLATE NOCASE` for faster case-insensitive matching aligned with search behavior.
- **`idx_media_status`**: index on `status` for potential filtering or reporting by status.

### Connections and safety

- Each operation uses a short-lived connection via **`with self.connect() as conn`** where applicable, so transactions commit on successful exit.
- **`row_factory = sqlite3.Row`** allows column access by name when mapping rows to **`MediaRow`**.
- **`PRAGMA foreign_keys = ON`** is enabled for consistency (no foreign keys are defined today, but the pragma is set for future-safe behavior).

---

## Application behavior (detailed)

### Startup

1. **`run_app()`** in `gui.py` instantiates **`MediaTrackerApp`**.
2. The app creates a **`Database`** instance (default path from **`config.DB_PATH`**).
3. **`init_schema()`** runs **`CREATE TABLE IF NOT EXISTS`** and **`CREATE INDEX IF NOT EXISTS`**, so existing databases are left intact and only missing objects are added.
4. Styles are applied (`clam` theme where available), widgets are laid out, and **`_refresh_table()`** loads rows from **`list_all`** into the **`Treeview`**.

### Add vs update (Save)

- **`_current_id`** is **`None`** after **Clear form** or after deleting an entry: **Save** performs an **`INSERT`** and stores the new **`lastrowid`** in **`_current_id`** so the new row stays selected after refresh.
- If a row is selected (or double-clicked), **`_current_id`** is set to that row’s database **`id`**: **Save** performs an **`UPDATE`** for that id.

Validation happens **before** SQL:

- Title non-empty after strip.
- Type and status must be one of the allowed literals from **`models.py`**.
- Year, if present, must be between **1888** and **2100**.
- Rating, if present, must be between **0** and **10**.
- Year and rating parsing errors (non-numeric input) surface as **warning** dialogs before validation runs.

### Selection and notes

- Clicking a row triggers **`<<TreeviewSelect>>`**, which loads title, type, status, year, and rating from the **visible** **`Treeview`** values.
- **Notes** are fetched separately with **`SELECT notes FROM media WHERE id = ?`** so the full note text does not need to live in the tree columns.

### Search

- The search field is bound with **`trace_add("write", …)`** so each change schedules **`_refresh_table`** via **`after_idle`**, which re-queries **`Database.list_all(search)`** with a **`LIKE '%term%'`** pattern on title and notes.

### Delete

- Requires a selection. Confirms with a **yes/no** dialog, then **`DELETE FROM media WHERE id = ?`** using the **`Treeview`** item **`iid`** (same as primary key).

---

## UI notes

- Layout: header title and subtitle, left **card** with the form, right **card** with search + table + delete button, bottom **status bar** string for short feedback (e.g. “Added …”, “Editing: …”).
- **`ttk.Treeview`** uses **`show='headings'`** with columns **Title**, **Type**, **Status**, **Year**, **Rating**; empty optional numeric fields appear blank in the grid.
- Styling centralizes colors in **`config.COLORS`** so you can retheme without hunting through widget code.

---

## Backups and portability

- Your data is **only** in **`media_tracker.db`**. Copy that file to back up or move your library to another machine with the same app.

---

## Troubleshooting

- **`ModuleNotFoundError: No module named '_tkinter'`** (common on minimal Linux installs): install your OS Tk bindings for Python, then retry.
- **`TclError` on theme**: the code falls back if **`clam`** is unavailable; you still get a working UI with the default theme.

---

## License / usage

This repository is structured as a personal assignment-style project. Use and modify as needed for learning or your own tracking workflow.
