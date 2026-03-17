"""
TEW Booking & Finance Optimizer – Persistent Storage
Handles: config, momentum history, card templates, storylines,
event planner, auto-reload detection, auto-backup, PDF export.
"""
import json
import glob
import shutil
import io
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "tew_data"
CONFIG_FILE = DATA_DIR / "config.json"
MOMENTUM_FILE = DATA_DIR / "momentum_history.json"
TEMPLATES_DIR = DATA_DIR / "card_templates"
STORYLINES_FILE = DATA_DIR / "storylines.json"
EVENTS_FILE = DATA_DIR / "events.json"
BACKUP_DIR = DATA_DIR / "backups"

DEFAULTS = {
    "mdb_path": "",
    "promotion": "",
    "notes": "",
}


def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

def load_config() -> dict:
    """Loads saved configuration or returns defaults."""
    _ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return {**DEFAULTS, **saved}
        except (json.JSONDecodeError, IOError):
            return DEFAULTS.copy()
    return DEFAULTS.copy()


def save_config(config: dict) -> None:
    """Saves configuration persistently."""
    _ensure_dirs()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError:
        pass


# ──────────────────────────────────────────────
# Momentum History (Push Tracking)
# ──────────────────────────────────────────────

def load_momentum_history() -> dict:
    """
    Loads momentum history. Structure:
    {
        "snapshots": [
            {"date": "2026-03-02", "workers": {"Rhio": "Hot", "Lucia Lee": "Warm", ...}},
            ...
        ]
    }
    """
    _ensure_dirs()
    if MOMENTUM_FILE.exists():
        try:
            with open(MOMENTUM_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"snapshots": []}


def save_momentum_snapshot(roster_df, mdb_path: str = "") -> dict:
    """
    Takes a momentum snapshot from the current roster.
    Extracts date from MDB filename if possible.
    """
    import pandas as pd

    history = load_momentum_history()

    # Try to extract date from MDB filename (e.g. EVE!_2026-03-02.mdb)
    date_str = datetime.now().strftime("%Y-%m-%d")
    if mdb_path:
        stem = Path(mdb_path).stem
        # Try pattern like EVE!_2026-03-02
        parts = stem.split("_")
        for p in parts:
            if len(p) == 10 and p.count("-") == 2:
                date_str = p
                break

    # Check if we already have a snapshot for this date
    existing_dates = {s["date"] for s in history["snapshots"]}
    if date_str in existing_dates:
        return history

    # Build snapshot
    workers = {}
    if "WorkerName" in roster_df.columns and "Momentum" in roster_df.columns:
        for _, row in roster_df.iterrows():
            name = str(row["WorkerName"])
            momentum = str(row.get("Momentum", "Neutral"))
            pop = float(row.get("Popularity", 0))
            workers[name] = {"momentum": momentum, "popularity": pop}

    if workers:
        history["snapshots"].append({
            "date": date_str,
            "workers": workers,
        })
        # Keep last 24 snapshots (2 years of monthly data)
        history["snapshots"] = history["snapshots"][-24:]

        try:
            with open(MOMENTUM_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    return history


# ──────────────────────────────────────────────
# Card Templates
# ──────────────────────────────────────────────

def save_card_template(name: str, matches: list[dict]) -> Path:
    """
    Saves a card template as JSON.
    matches: list of dicts with worker_names, worker_uids, match_type, wages.
    """
    _ensure_dirs()
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    path = TEMPLATES_DIR / f"{safe_name}.json"
    template = {
        "name": name,
        "created": datetime.now().isoformat(),
        "matches": matches,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    return path


def load_card_templates() -> list[dict]:
    """Returns list of all saved card templates."""
    _ensure_dirs()
    templates = []
    for path in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                t = json.load(f)
                t["_path"] = str(path)
                templates.append(t)
        except (json.JSONDecodeError, IOError):
            continue
    return templates


def load_card_template(name: str) -> dict | None:
    """Loads a specific card template by name."""
    _ensure_dirs()
    for path in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                t = json.load(f)
                if t.get("name") == name:
                    return t
        except (json.JSONDecodeError, IOError):
            continue
    return None


def delete_card_template(name: str) -> bool:
    """Deletes a card template by name."""
    _ensure_dirs()
    for path in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                t = json.load(f)
                if t.get("name") == name:
                    path.unlink()
                    return True
        except (json.JSONDecodeError, IOError):
            continue
    return False


# ──────────────────────────────────────────────
# Auto-Reload Detection
# ──────────────────────────────────────────────

def get_latest_mdb(mdb_path: str) -> str | None:
    """
    Checks if a newer MDB file exists in the same directory.
    TEW saves create new MDB files with incrementing dates.
    Returns the newest MDB path if different from current, else None.
    """
    if not mdb_path:
        return None
    p = Path(mdb_path)
    if not p.exists():
        return None

    mdb_dir = p.parent
    pattern = str(mdb_dir / "*.mdb")
    all_mdbs = sorted(glob.glob(pattern), key=lambda x: Path(x).stat().st_mtime)

    if not all_mdbs:
        return None

    newest = all_mdbs[-1]
    if Path(newest).resolve() != p.resolve():
        return newest
    return None


# ──────────────────────────────────────────────
# Storyline Tracker
# ──────────────────────────────────────────────

def load_storylines() -> list[dict]:
    """
    Loads all storylines. Each storyline:
    {
        "id": "uuid-string",
        "title": "Championship Chase",
        "workers": ["Dakota Kai", "Rhio"],
        "status": "building",  # building / climax / cooldown / finished
        "notes": "Rhio wants the belt...",
        "created": "2026-03-02",
        "updated": "2026-03-02",
        "events": ["Won tag match at Show 1", "Confrontation at Show 2"]
    }
    """
    _ensure_dirs()
    if STORYLINES_FILE.exists():
        try:
            with open(STORYLINES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_storylines(storylines: list[dict]) -> None:
    _ensure_dirs()
    with open(STORYLINES_FILE, "w", encoding="utf-8") as f:
        json.dump(storylines, f, indent=2, ensure_ascii=False)


def add_storyline(title: str, workers: list[str], notes: str = "", status: str = "building") -> dict:
    storylines = load_storylines()
    import uuid
    sl = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "workers": workers,
        "status": status,
        "notes": notes,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "events": [],
    }
    storylines.append(sl)
    save_storylines(storylines)
    return sl


def update_storyline(sl_id: str, **kwargs) -> bool:
    storylines = load_storylines()
    for sl in storylines:
        if sl["id"] == sl_id:
            for k, v in kwargs.items():
                if k in sl:
                    sl[k] = v
            sl["updated"] = datetime.now().strftime("%Y-%m-%d")
            save_storylines(storylines)
            return True
    return False


def add_storyline_event(sl_id: str, event_text: str) -> bool:
    storylines = load_storylines()
    for sl in storylines:
        if sl["id"] == sl_id:
            sl["events"].append(f"[{datetime.now().strftime('%Y-%m-%d')}] {event_text}")
            sl["updated"] = datetime.now().strftime("%Y-%m-%d")
            save_storylines(storylines)
            return True
    return False


def delete_storyline(sl_id: str) -> bool:
    storylines = load_storylines()
    before = len(storylines)
    storylines = [s for s in storylines if s["id"] != sl_id]
    if len(storylines) < before:
        save_storylines(storylines)
        return True
    return False


# ──────────────────────────────────────────────
# Event Planner
# ──────────────────────────────────────────────

def load_events() -> list[dict]:
    """
    Loads planned events. Each event:
    {
        "id": "uuid",
        "name": "Weekly Show #5",
        "date": "2026-03-15",
        "type": "weekly",  # weekly / ppv / special
        "matches": [{"worker1": "A", "worker2": "B", "type": "Singles", "storyline": "id or null"}],
        "notes": "",
        "status": "planned"  # planned / completed
    }
    """
    _ensure_dirs()
    if EVENTS_FILE.exists():
        try:
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_events(events: list[dict]) -> None:
    _ensure_dirs()
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)


def add_event(name: str, date: str, event_type: str = "weekly", matches: list = None, notes: str = "") -> dict:
    events = load_events()
    import uuid
    ev = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "date": date,
        "type": event_type,
        "matches": matches or [],
        "notes": notes,
        "status": "planned",
    }
    events.append(ev)
    save_events(events)
    return ev


def update_event(ev_id: str, **kwargs) -> bool:
    events = load_events()
    for ev in events:
        if ev["id"] == ev_id:
            for k, v in kwargs.items():
                if k in ev:
                    ev[k] = v
            save_events(events)
            return True
    return False


def delete_event(ev_id: str) -> bool:
    events = load_events()
    before = len(events)
    events = [e for e in events if e["id"] != ev_id]
    if len(events) < before:
        save_events(events)
        return True
    return False


# ──────────────────────────────────────────────
# Auto-Backup
# ──────────────────────────────────────────────

def create_backup() -> str | None:
    """Creates a timestamped zip backup of the tew_data directory."""
    _ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"tew_backup_{timestamp}"
    backup_path = BACKUP_DIR / backup_name

    try:
        # Collect files to backup (exclude backups dir itself)
        files_to_backup = []
        for f in DATA_DIR.rglob("*"):
            if f.is_file() and "backups" not in f.parts:
                files_to_backup.append(f)

        if not files_to_backup:
            return None

        archive = shutil.make_archive(
            str(backup_path), "zip",
            root_dir=str(DATA_DIR),
        )

        # Keep only last 10 backups
        existing = sorted(BACKUP_DIR.glob("*.zip"), key=lambda x: x.stat().st_mtime)
        while len(existing) > 10:
            existing[0].unlink()
            existing.pop(0)

        return archive
    except Exception:
        return None


def list_backups() -> list[dict]:
    """Lists available backups."""
    _ensure_dirs()
    backups = []
    for f in sorted(BACKUP_DIR.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True):
        size_kb = f.stat().st_size / 1024
        backups.append({
            "name": f.stem,
            "path": str(f),
            "size": f"{size_kb:.1f} KB",
            "created": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        })
    return backups


# ──────────────────────────────────────────────
# PDF Export
# ──────────────────────────────────────────────

def generate_show_card_pdf(
    show_name: str,
    matches: list[dict],
    financials: dict | None = None,
    notes: str = "",
) -> bytes:
    """
    Generates a show card as PDF bytes.
    matches: list of {"worker1", "worker2", "match_type", "predicted_rating", "grade", "wage"}
    financials: dict with revenue, costs, profit
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"<b>{show_name}</b>", styles["Title"]))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Match Card table
        if matches:
            table_data = [["#", "Match", "Type", "Grade", "Rating", "Cost"]]
            for i, m in enumerate(matches, 1):
                table_data.append([
                    str(i),
                    f"{m.get('worker1', '?')} vs {m.get('worker2', '?')}",
                    m.get("match_type", "Singles"),
                    m.get("grade", "-"),
                    str(m.get("predicted_rating", "-")),
                    f"${m.get('wage', 0):,.0f}",
                ])

            t = Table(table_data, colWidths=[30, 200, 80, 50, 50, 70])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1f2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f8f8"), colors.white]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

        # Financials
        if financials:
            elements.append(Paragraph("<b>Financial Summary</b>", styles["Heading2"]))
            fin_data = [
                ["Revenue", f"${financials.get('revenue', 0):,.0f}"],
                ["Talent Cost", f"${financials.get('talent_cost', 0):,.0f}"],
                ["Staff Cost", f"${financials.get('staff_cost', 0):,.0f}"],
                ["Production", f"${financials.get('production', 0):,.0f}"],
                ["Profit", f"${financials.get('profit', 0):,.0f}"],
            ]
            ft = Table(fin_data, colWidths=[150, 100])
            ft.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(ft)
            elements.append(Spacer(1, 15))

        # Notes
        if notes:
            elements.append(Paragraph("<b>Notes</b>", styles["Heading2"]))
            elements.append(Paragraph(notes, styles["Normal"]))

        doc.build(elements)
        return buf.getvalue()

    except ImportError:
        # Fallback: plain text "PDF" if reportlab not available
        lines = [f"=== {show_name} ===", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
        if matches:
            lines.append("MATCH CARD:")
            for i, m in enumerate(matches, 1):
                lines.append(f"  {i}. {m.get('worker1','?')} vs {m.get('worker2','?')} "
                           f"({m.get('match_type','Singles')}) - Grade: {m.get('grade','-')} "
                           f"Rating: {m.get('predicted_rating','-')} Cost: ${m.get('wage',0):,.0f}")
        if financials:
            lines.append("")
            lines.append(f"Revenue: ${financials.get('revenue',0):,.0f}")
            lines.append(f"Total Cost: ${financials.get('talent_cost',0)+financials.get('staff_cost',0)+financials.get('production',0):,.0f}")
            lines.append(f"Profit: ${financials.get('profit',0):,.0f}")
        if notes:
            lines.append("")
            lines.append(f"Notes: {notes}")
        return "\n".join(lines).encode("utf-8")
