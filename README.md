# Movies & Shows tracker

A small desktop program for keeping a personal list of films and TV series. You can add entries, change them, delete them, and search your library. Everything is saved in a **SQLite** file on disk. The interface is built with **Tkinter** using **`ttk`** widgets (the themed Tk widgets).

The project is split into **two Python files**: one handles the window and user actions, the other handles the database.

---

## What the program does

- **Add** a movie or show: fill the form on the left and click **Save**.
- **Edit** an existing row: click a row in the table so the form fills in, change fields, then **Save**.
- **Start a new row** without overwriting anything: click **Clear** (this clears the form and forgets which database row you were editing).
- **Delete** the selected table row: click **Delete selected row** (you must confirm in a popup).
- **Search**: type in the search box; the table refreshes and shows rows whose **title** or **notes** contain that text (case insensitive). Leave search empty to see everything.

Optional fields: **year**, **rating** (0-10), and **notes**. **Notes** are stored in the database but **not** shown as a column in the table-they appear in the notes box only after you select a row.

---

## Requirements

- **Python 3.x** with Tkinter available (standard on many Windows/macOS Python installs; on Linux you may need a package such as `python3-tk`).
- **No extra pip packages** - the code uses only the standard library (`tkinter`, `sqlite3`, `pathlib`, etc.).

---

## How to run

From this folder:

```bash
python main.py
```

On the first run, the program creates **`media_tracker.db`** in the **same folder as `database.py`** (project root). Your data lives in that file; back it up if you want to keep your list safe.

---

## The two files (big picture)

| File | Role |
|------|------|
| **`main.py`** | Builds the GUI, reads what you typed, validates it, and calls functions in `database.py` to load or save data. |
| **`database.py`** | Knows where the `.db` file is, creates the `media` table if needed, and runs SQL **SELECT / INSERT / UPDATE / DELETE**. |

Entry point: running **`main.py`** calls **`main()`**, which creates **`MovieTrackerApp`** (a subclass of **`tk.Tk`**) and starts **`mainloop()`** so the window stays open and reacts to clicks and typing.

---

## How the GUI is structured (`main.py`)

1. **`MovieTrackerApp.__init__`**  
   Calls **`db.init_db()`** once so the table exists, sets window title/size, then **`_build_widgets()`** and **`refresh_table()`**.

2. **Layout**  
   - Top: short instruction label.  
   - Middle: **left** `LabelFrame` “Add / edit” (form); **right** `LabelFrame` “Library” (search + table).  
   - Bottom: status line tied to **`var_status_msg`**.

3. **Important variables**  
   - **`StringVar`** instances (`var_title`, `var_type`, …) bind the form to Tk’s widgets.  
   - **`text_notes`** is a **`tk.Text`** widget for multi-line notes.  
   - **`current_id`** is **`None`** for a *new* entry, or an **integer** primary key when you are *editing* a row you selected in the table.

4. **The table**  
   A **`ttk.Treeview`** with columns Title, Type, Status, Year, Rating. Each row’s **`iid`** (internal Treeview id) is set to **`str(database id)`**. That way **`on_save`** / **`on_delete`** know exactly which SQLite row to update or remove.

5. **Events**  
   - **`<<TreeviewSelect>>`** → **`load_selection_into_form()`**: copies visible columns into the form and loads **notes** via **`db.fetch_notes(current_id)`**.  
   - Search box → **`trace_add("write", …)`** schedules **`refresh_table`** with **`after_idle`**, so the list reloads shortly after you type.

6. **Helper functions at module level**  
   - **`validate_inputs(...)`** - rules before saving (title required, allowed type/status, year/rating ranges).  
   - **`parse_year`** / **`parse_rating`** - convert text boxes to **`None`** or numbers; invalid text raises **`ValueError`** and **`on_save`** shows a warning.

7. **Buttons**  
   - **Save** → **`on_save`**: parse → **`validate_inputs`** → **`insert_row`** or **`update_row`**.  
   - **Clear** → **`on_clear`**.  
   - **Delete selected row** → **`on_delete`**: confirm → **`delete_row`**.

Docstrings in **`main.py`** describe each of these pieces in more detail.

---

## How the database layer works (`database.py`)

- **`DB_PATH`** - `Path(__file__).parent / "media_tracker.db"` so the database stays next to your code.  
- **`TYPES`** and **`STATUSES`** - tuples of allowed strings; they must stay in sync with the **`CHECK`** constraints in **`CREATE TABLE`** and with the comboboxes in **`main.py`**.

Functions:

| Function | Purpose |
|----------|---------|
| **`get_connection()`** | Opens SQLite and sets **`row_factory = sqlite3.Row`** so you can use **`row["title"]`** style access. |
| **`init_db()`** | **`CREATE TABLE IF NOT EXISTS media`** plus an index on title for faster search. |
| **`fetch_all(search_text)`** | **`SELECT`** all columns; optional **`WHERE`** with **`LIKE '%…%'`** on title and notes; **`ORDER BY updated_at DESC`**, then title. |
| **`insert_row(...)`** | **`INSERT`**, sets **`created_at`** and **`updated_at`** to the current UTC time (ISO text). Returns **`lastrowid`**. |
| **`update_row(...)`** | **`UPDATE`** one row by **`id`**, refreshes **`updated_at`**. |
| **`delete_row(row_id)`** | **`DELETE`** one row. |
| **`fetch_notes(row_id)`** | **`SELECT notes`** for one id (used when filling the form). |

Timestamps use **`datetime.now(timezone.utc)`** written as ISO strings; SQLite stores them as ordinary **`TEXT`**.

---

## Database table: `media`

| Column | Meaning |
|--------|---------|
| **`id`** | Integer primary key (auto-increment). Same value used as Treeview **`iid`**. |
| **`title`** | Required. |
| **`media_type`** | **`Movie`** or **`TV Show`**. |
| **`status`** | **`Plan to watch`**, **`Watching`**, or **`Watched`**. |
| **`year`** | Optional integer (release year). |
| **`rating`** | Optional float (0-10 enforced in the GUI). |
| **`notes`** | Optional longer text. |
| **`created_at`**, **`updated_at`** | Set on insert; **`updated_at`** changes on every update. |

---

## Program flow (short)

1. Start app → create table if missing → show empty or existing rows.  
2. User types search → **`fetch_all`** → refill **`Treeview`**.  
3. User selects row → **`current_id`** set → form + notes filled.  
4. User clicks **Save** → validate → **`INSERT`** or **`UPDATE`** → refresh table → re-select same **`id`** when possible.  
5. User clicks **Clear** → **`current_id = None`** → next **Save** is an **`INSERT`**.  
6. User clicks **Delete** → confirm → **`DELETE`** → clear form → refresh.

---

## Troubleshooting

- **Tkinter missing** - Install your OS/Python Tk bindings (error often mentions `_tkinter`).  
- **Permission errors on `.db`** - Make sure the project folder is writable.

For line-by-line explanations, open **`main.py`** and **`database.py`** and read the **docstrings** above each function and class.
