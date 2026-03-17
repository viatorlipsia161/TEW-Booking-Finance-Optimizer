# 🤼 TEW Booking & Finance Optimizer v4.0

**The ultimate companion tool for Total Extreme Wrestling (TEW) IX.**
Analyze your roster, plan shows, track storylines, and optimize your booking — all from a modern web dashboard.

---

> 🇩🇪 **[Deutsche Anleitung weiter unten](#-deutsche-anleitung)**

---

# 🇬🇧 English Guide

## What is this?

This tool reads your TEW IX save game database (`.mdb` file) and gives you a powerful dashboard with **19 features** to help you run your promotion smarter:

### Core Features
| Feature | Description |
|---------|-------------|
| **📋 Roster Overview** | Full roster with Efficiency Score (value per dollar), popularity, skills |
| **🎤 Show Calculator** | Build your match card, predict match quality, calculate profit/loss |
| **🔀 Worker Compare** | Side-by-side radar charts and stats for any two workers |
| **📄 Contract Overview** | All contracts with type, expiry, role detection |
| **💰 Budget Analysis** | Revenue vs. costs breakdown, staff cost warnings |
| **📈 Financial History** | Income/expense charts from your in-game financial data |
| **📊 Push Tracking** | Momentum & popularity trends over time (auto-saved on each load) |
| **🔄 Staleness Check** | Check how often two workers have faced each other |

### Advanced Analytics
| Feature | Description |
|---------|-------------|
| **📖 Storyline Tracker** | Create & manage feuds with status tracking and timeline events |
| **📅 Event Planner** | Plan upcoming shows with match assignments |
| **🧪 Chemistry Detection** | Find proven pairings based on actual match ratings |
| **🏥 Roster Health** | Face/heel balance, experience distribution, roster gap detection |
| **🔮 Popularity Forecast** | Predict who's rising or falling based on momentum trends |
| **🌟 Development Suggestions** | Find underused workers with high skill ceilings |
| **🎭 Angle Suggestions** | Best workers for promos, interviews, run-ins, comedy, etc. |
| **🏆 Title Reign Tracker** | Belt prestige, defences, reign health assessment |
| **🌍 Touring Optimizer** | Best workers for a region based on popularity vs. cost |
| **🔄 Talent Trade Analyzer** | Compare worker values for potential trades |

### Tools
| Feature | Description |
|---------|-------------|
| **📄 PDF Export** | Download your show card as a formatted PDF |
| **💾 Auto-Backup** | Create timestamped backups of all your data |
| **🔍 DB Explorer** | Inspect your TEW database structure |

---

## Requirements

You need the following installed on your Windows PC:

### 1. Python 3.10–3.13 (recommended: 3.12)
- Download: https://www.python.org/downloads/release/python-3129/
- **Important:** During installation, check ✅ **"Add Python to PATH"**
- ⚠️ Python 3.14+ may cause issues installing `pyodbc` (no pre-built wheels available yet)

### 2. Microsoft Access Database Engine
- This is needed to read TEW's `.mdb` database files
- Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920
- **Choose the same architecture as your Python** (64-bit or 32-bit)
- If you already have Microsoft Office installed, you may already have this

### 3. TEW IX Save Game
- You need an active save game. The tool reads the `.mdb` file from:
  ```
  [TEW9 Folder]\Databases\[Your Database]\SaveGames\[Promotion]\MDBFiles\
  ```
- Example: `G:\TEW9\Databases\RWCFeb26JPG\SaveGames\EVE!\MDBFiles\EVE!_2026-03-02.mdb`

---

## Installation

### Option A: Double-click (easiest)
1. Extract the ZIP file to any folder
2. Double-click **`start.bat`**
3. Done! The app opens in your browser automatically

### Option B: Manual
1. Extract the ZIP file
2. Open a terminal/command prompt in the folder
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Open http://localhost:8501 in your browser

---

## First-Time Setup

1. **Start the app** (double-click `start.bat` or run manually)
2. In the **sidebar** on the left:
   - **MDB Path**: Paste the full path to your TEW save game `.mdb` file
   - **Promotion**: Enter your promotion's abbreviation (e.g. `EVE`, `WWE`, `AEW`)
3. Click **"Connect & Load"**
4. Your roster, contracts, and all data will load automatically
5. These settings are saved — you won't need to enter them again

---

## Tips

- **Auto-Reload**: If you save in TEW and a new `.mdb` file appears, the app will detect it and offer to reload
- **Push Tracking**: Every time you connect, a momentum snapshot is saved. Over time, you'll see trends
- **Card Templates**: Save your show cards as templates to reuse later
- **Backup**: Use the Tools tab to create backups before making changes
- **Desktop Shortcut**: The `start.bat` can be placed on your desktop or pinned to your taskbar

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Install Python and check "Add to PATH" during installation |
| "No driver found" or ODBC error | Install Microsoft Access Database Engine (same bit as Python) |
| `pyproject.toml` / `pyodbc` install error | Use **Python 3.12** (recommended). Python 3.14+ may not have pre-built pyodbc wheels. Download: https://www.python.org/downloads/release/python-3129/ Alternatively install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |
| Empty roster after connecting | Check that the promotion abbreviation matches exactly (e.g. `WWF`, `WCW`) |
| Popularity shows 0 for all workers | Make sure you enter the **Initials** of your promotion (e.g. `WWF` not `World Wrestling Federation`) |
| App won't start | Make sure port 8501 is free. Close other Streamlit instances first |
| Charts not showing | Try refreshing the browser page (F5) |

---

---

# 🇩🇪 Deutsche Anleitung

## Was ist das?

Dieses Tool liest deine TEW IX Spielstand-Datenbank (`.mdb`-Datei) und gibt dir ein modernes Dashboard mit **19 Features**, um deine Promotion besser zu managen:

### Kern-Features
| Feature | Beschreibung |
|---------|-------------|
| **📋 Roster-Übersicht** | Kompletter Kader mit Effizienz-Score (Preis-Leistung), Popularität, Skills |
| **🎤 Show-Kalkulator** | Match-Card zusammenstellen, Qualität vorhersagen, Gewinn/Verlust berechnen |
| **🔀 Worker-Vergleich** | Zwei Worker nebeneinander mit Radar-Charts und Statistiken |
| **📄 Vertragsübersicht** | Alle Verträge mit Typ, Ablaufdatum, Rollenerkennung |
| **💰 Budget-Analyse** | Einnahmen vs. Ausgaben, Warnung bei hohen Staff-Kosten |
| **📈 Finanz-Historie** | Einnahmen/Ausgaben-Charts aus deinen Spieldaten |
| **📊 Push-Tracking** | Momentum- & Popularitätstrends über Zeit (wird bei jedem Laden gespeichert) |
| **🔄 Staleness-Check** | Prüfe, wie oft zwei Worker schon gegeneinander gekämpft haben |

### Erweiterte Analyse
| Feature | Beschreibung |
|---------|-------------|
| **📖 Storyline-Tracker** | Fehden erstellen & verwalten mit Status-Tracking und Timeline |
| **📅 Event-Planer** | Kommende Shows planen mit Match-Zuweisungen |
| **🧪 Chemie-Erkennung** | Bewährte Paarungen finden basierend auf echten Match-Bewertungen |
| **🏥 Roster-Gesundheit** | Face/Heel-Balance, Erfahrungsverteilung, Kaderlücken erkennen |
| **🔮 Popularitäts-Prognose** | Vorhersage wer steigt oder fällt basierend auf Momentum-Trends |
| **🌟 Entwicklungs-Vorschläge** | Unterbenutzte Worker mit hohem Skill-Potenzial finden |
| **🎭 Angle-Vorschläge** | Beste Worker für Promos, Interviews, Run-Ins, Comedy, usw. |
| **🏆 Titel-Tracker** | Belt-Prestige, Titelverteidigungen, Gesundheitsbewertung |
| **🌍 Touring-Optimierer** | Beste Worker für eine Region nach Popularität vs. Kosten |
| **🔄 Trade-Analyse** | Worker-Werte vergleichen für potenzielle Trades |

### Werkzeuge
| Feature | Beschreibung |
|---------|-------------|
| **📄 PDF-Export** | Show-Card als formatiertes PDF herunterladen |
| **💾 Auto-Backup** | Zeitgestempelte Backups aller Daten erstellen |
| **🔍 DB-Explorer** | TEW-Datenbankstruktur inspizieren |

---

## Voraussetzungen

Du brauchst Folgendes auf deinem Windows-PC:

### 1. Python 3.10–3.13 (empfohlen: 3.12)
- Download: https://www.python.org/downloads/release/python-3129/
- **Wichtig:** Bei der Installation ✅ **"Add Python to PATH"** anhaken!
- ⚠️ Python 3.14+ kann Probleme bei der `pyodbc`-Installation verursachen (keine fertigen Pakete verfügbar)

### 2. Microsoft Access Database Engine
- Wird benötigt, um TEWs `.mdb`-Dateien zu lesen
- Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920
- **Wähle die gleiche Architektur wie dein Python** (64-Bit oder 32-Bit)
- Falls du Microsoft Office installiert hast, hast du das evtl. schon

### 3. TEW IX Spielstand
- Du brauchst einen aktiven Spielstand. Das Tool liest die `.mdb`-Datei aus:
  ```
  [TEW9-Ordner]\Databases\[Deine Datenbank]\SaveGames\[Promotion]\MDBFiles\
  ```
- Beispiel: `G:\TEW9\Databases\RWCFeb26JPG\SaveGames\EVE!\MDBFiles\EVE!_2026-03-02.mdb`

---

## Installation

### Option A: Doppelklick (am einfachsten)
1. ZIP-Datei in einen beliebigen Ordner entpacken
2. **`start.bat`** doppelklicken
3. Fertig! Die App öffnet sich automatisch im Browser

### Option B: Manuell
1. ZIP-Datei entpacken
2. Terminal/Eingabeaufforderung im Ordner öffnen
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. App starten:
   ```bash
   streamlit run app.py
   ```
5. http://localhost:8501 im Browser öffnen

---

## Ersteinrichtung

1. **App starten** (Doppelklick auf `start.bat` oder manuell)
2. In der **Seitenleiste** links:
   - **MDB Path**: Vollständigen Pfad zu deiner TEW-Spielstand-`.mdb`-Datei einfügen
   - **Promotion**: Kürzel deiner Promotion eingeben (z.B. `EVE`, `WWE`, `AEW`)
3. **"Connect & Load"** klicken
4. Roster, Verträge und alle Daten laden automatisch
5. Die Einstellungen werden gespeichert — du musst sie nicht nochmal eingeben

---

## Tipps

- **Auto-Reload**: Wenn du in TEW speicherst und eine neue `.mdb` erscheint, erkennt die App das und bietet Neuladen an
- **Push-Tracking**: Bei jeder Verbindung wird ein Momentum-Snapshot gespeichert. Mit der Zeit siehst du Trends
- **Card-Templates**: Show-Cards als Vorlagen speichern und wiederverwenden
- **Backup**: Im Tools-Tab Backups erstellen bevor du Änderungen machst
- **Desktop-Verknüpfung**: Die `start.bat` kann auf den Desktop gelegt oder an die Taskleiste angeheftet werden

---

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "Python not found" | Python installieren und "Add to PATH" bei der Installation anhaken |
| "No driver found" / ODBC-Fehler | Microsoft Access Database Engine installieren (gleiche Bit-Version wie Python) |
| `pyproject.toml` / `pyodbc` Installationsfehler | **Python 3.12** verwenden (empfohlen). Python 3.14+ hat evtl. keine fertigen pyodbc-Pakete. Download: https://www.python.org/downloads/release/python-3129/ Alternativ [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installieren |
| Leerer Roster nach Verbindung | Promotions-Kürzel prüfen (z.B. `WWF`, `WCW`) |
| Popularität zeigt 0 für alle Worker | Die **Initialen** der Promotion eingeben (z.B. `WWF` statt `World Wrestling Federation`) |
| App startet nicht | Port 8501 muss frei sein. Andere Streamlit-Instanzen vorher schließen |
| Charts werden nicht angezeigt | Browser-Seite neu laden (F5) |

---

## Lizenz / Credits

Made with ❤️ for the TEW community.
Built with [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/), [Pandas](https://pandas.pydata.org/), and [ReportLab](https://www.reportlab.com/).
