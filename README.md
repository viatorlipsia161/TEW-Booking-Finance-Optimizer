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

## Complete Setup Guide (Step by Step)

> ⚠️ **You only need to do this ONCE.** After the first setup, just double-click `start.bat` to launch.

### Step 1: Install Python 3.12

1. Download **Python 3.12** from: https://www.python.org/downloads/release/python-3129/
2. Scroll down to **"Files"** and download **"Windows installer (64-bit)"**
3. Run the installer
4. ⚡ **CRITICAL: Check the box ✅ "Add Python to PATH"** at the bottom of the installer!
5. Click "Install Now"
6. When done, **restart your PC**

> ⚠️ **Do NOT use Python 3.14+** — it has compatibility issues with required packages. Use **3.12**.

### Step 2: Install Microsoft Access Database Engine

1. Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920
2. Choose the **64-bit** version (matches Python 64-bit)
3. Install it
4. If you already have **Microsoft Office** installed, you may already have this — try skipping this step first

### Step 3: Create the MDB File in TEW IX

> 🚨 **This is the most important step!** You CANNOT use the raw save game files — they are password-protected and will give an error.

1. Open **TEW IX**
2. **Load your save game** (the one you want to analyze)
3. Once loaded, go to **Game Settings** (or press the Settings button)
4. Click **"Create MDB File"**
5. TEW will create an **unprotected** `.mdb` file in this location:
   ```
   TEW9\Databases\<YourDatabaseName>\SaveGames\<YourSaveName>\MDBFiles\
   ```
   For example:
   ```
   C:\Games\TEW9\Databases\RWCFeb26JPG\SaveGames\EVE!\MDBFiles\EVE!_2026-03-02.mdb
   ```
6. **Copy the full path** to this `.mdb` file — you'll need it in Step 5

> 💡 **Every time you want updated data**, save your game in TEW, then click "Create MDB File" again. A new `.mdb` will appear with the current date.

### Step 4: Launch the Tool

1. Extract the ZIP file to any folder (e.g. `C:\TEW-Optimizer\`)
2. Double-click **`start.bat`**
3. The script will automatically install all required packages
4. Your browser will open to `http://localhost:8501`

> If `start.bat` shows errors, see [Troubleshooting](#troubleshooting) below.

### Step 5: Connect Your Database

1. In the **sidebar** on the left:
   - **Path to TEW .mdb file**: Paste the full path from Step 3
     - Example: `C:\Games\TEW9\Databases\RWCFeb26JPG\SaveGames\EVE!\MDBFiles\EVE!_2026-03-02.mdb`
   - **Promotion Abbreviation**: Enter your promotion's **initials** (e.g. `WWF`, `WCW`, `EVE`)
2. Click **"🔌 Connect Database"**
3. Your roster, contracts, and all data will load automatically
4. These settings are saved — you won't need to enter them again next time

> 📌 The tool does NOT need to be in the same folder as TEW. Just paste the full file path.

### Alternative: Manual Install (advanced users)

If you prefer not to use `start.bat`:
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

---

## Tips

- **Auto-Reload**: If you save in TEW and create a new MDB, the app will detect it and offer to reload
- **Push Tracking**: Every time you connect, a momentum snapshot is saved. Over time, you'll see trends
- **Card Templates**: Save your show cards as templates to reuse later
- **Backup**: Use the Tools tab to create backups before making changes
- **Desktop Shortcut**: Right-click `start.bat` → "Create shortcut" → move it to your desktop

---

## Troubleshooting

### ❌ "Not a valid password" / Password error
**Cause:** You are trying to open a raw TEW save game file, which is password-protected by the game.

**Fix:** You must use TEW's **"Create MDB File"** feature:
1. Open TEW IX → load your save → go to Settings → click **"Create MDB File"**
2. Use the file from the `MDBFiles` folder instead (see [Step 3](#step-3-create-the-mdb-file-in-tew-ix))

### ❌ "No module named streamlit" / Module not found
**Cause:** Python dependencies were not installed correctly, often because you have Python 3.14+ or multiple Python versions.

**Fix:**
1. Install **Python 3.12** (see [Step 1](#step-1-install-python-312)) — do NOT use Python 3.14
2. **Uninstall** any other Python versions (Settings → Apps → search "Python")
3. Restart your PC
4. Run `start.bat` again

### ❌ "Cannot find MDB file" / File not found
**Cause:** The path you entered is incorrect, or you're pointing to the wrong file.

**Fix:**
1. The MDB file must be the one created by TEW's "Create MDB File" feature
2. The path should look like: `C:\Games\TEW9\Databases\...\MDBFiles\SomeName_2026-03-02.mdb`
3. Make sure you paste the **full path including the file name and `.mdb` extension**
4. The tool does NOT need to be in the same folder as TEW — just use the full path
5. Try copying the path directly from File Explorer's address bar, then add `\filename.mdb`

### ❌ "ODBC Driver not found" / Driver error
**Cause:** Microsoft Access Database Engine is not installed.

**Fix:** Download and install it from: https://www.microsoft.com/en-us/download/details.aspx?id=54920 (choose 64-bit)

### ❌ `pyodbc` / `pyproject.toml` install error
**Cause:** Python 3.14+ doesn't have pre-built packages for pyodbc.

**Fix:**
1. Install **Python 3.12** instead: https://www.python.org/downloads/release/python-3129/
2. Or install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (then re-run `start.bat`)

### ❌ "This site can't be reached" / localhost refused
**Cause:** The Streamlit server failed to start (check the black terminal window for errors).

**Fix:**
1. Look at the terminal window (`start.bat`) for red error messages
2. Make sure port 8501 is free — close any other Streamlit instances
3. Try running manually: `py -m streamlit run app.py`

### Other Issues

| Problem | Solution |
|---------|----------|
| Empty roster after connecting | Make sure you enter the **Initials** (e.g. `WWF` not `World Wrestling Federation`) |
| Popularity shows 0 for all workers | Use the promotion's **abbreviation/initials** (e.g. `WWF`, `WCW`) |
| Charts not showing | Refresh the browser page (F5) |
| App is slow | This is normal on first load — subsequent loads are faster |

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

## Komplette Einrichtung (Schritt für Schritt)

> ⚠️ **Das musst du nur EINMAL machen.** Danach reicht ein Doppelklick auf `start.bat`.

### Schritt 1: Python 3.12 installieren

1. Lade **Python 3.12** herunter: https://www.python.org/downloads/release/python-3129/
2. Scrolle runter zu **"Files"** und lade **"Windows installer (64-bit)"** herunter
3. Starte den Installer
4. ⚡ **WICHTIG: Hake ✅ "Add Python to PATH" an** (unten im Installer-Fenster)!
5. Klicke auf "Install Now"
6. Danach **PC neu starten**

> ⚠️ **Benutze NICHT Python 3.14+** — es gibt Kompatibilitätsprobleme mit benötigten Paketen. Nimm **3.12**.

### Schritt 2: Microsoft Access Database Engine installieren

1. Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920
2. Wähle die **64-Bit** Version (passend zu Python 64-Bit)
3. Installieren
4. Falls du **Microsoft Office** installiert hast, hast du das evtl. schon — überspringe diesen Schritt und teste erst

### Schritt 3: MDB-Datei in TEW IX erstellen

> 🚨 **Das ist der wichtigste Schritt!** Du kannst NICHT die normalen Spielstand-Dateien verwenden — die sind passwortgeschützt und erzeugen einen Fehler.

1. Öffne **TEW IX**
2. **Lade deinen Spielstand** (den du analysieren willst)
3. Gehe zu **Einstellungen** (Settings)
4. Klicke auf **"Create MDB File"**
5. TEW erstellt eine **ungeschützte** `.mdb`-Datei hier:
   ```
   TEW9\Databases\<DeinDatenbankName>\SaveGames\<DeinSpielstandName>\MDBFiles\
   ```
   Zum Beispiel:
   ```
   C:\Games\TEW9\Databases\RWCFeb26JPG\SaveGames\EVE!\MDBFiles\EVE!_2026-03-02.mdb
   ```
6. **Kopiere den vollständigen Pfad** zu dieser `.mdb`-Datei — du brauchst ihn in Schritt 5

> 💡 **Für aktuelle Daten**: Speichere dein Spiel in TEW, dann klicke erneut auf "Create MDB File". Eine neue `.mdb` erscheint mit aktuellem Datum.

### Schritt 4: Tool starten

1. Entpacke die ZIP-Datei in einen beliebigen Ordner (z.B. `C:\TEW-Optimizer\`)
2. Doppelklicke auf **`start.bat`**
3. Das Skript installiert automatisch alle benötigten Pakete
4. Dein Browser öffnet sich mit `http://localhost:8501`

> Bei Fehlern siehe [Fehlerbehebung](#fehlerbehebung) weiter unten.

### Schritt 5: Datenbank verbinden

1. In der **Seitenleiste** links:
   - **Path to TEW .mdb file**: Den vollständigen Pfad aus Schritt 3 einfügen
     - Beispiel: `C:\Games\TEW9\Databases\RWCFeb26JPG\SaveGames\EVE!\MDBFiles\EVE!_2026-03-02.mdb`
   - **Promotion Abbreviation**: Die **Initialen** deiner Promotion eingeben (z.B. `WWF`, `WCW`, `EVE`)
2. Klicke auf **"🔌 Connect Database"**
3. Roster, Verträge und alle Daten laden automatisch
4. Die Einstellungen werden gespeichert — beim nächsten Mal musst du sie nicht nochmal eingeben

> 📌 Das Tool muss NICHT im selben Ordner wie TEW sein. Einfach den vollständigen Pfad einfügen.

### Alternativ: Manuell installieren (für Fortgeschrittene)

```bash
pip install -r requirements.txt
streamlit run app.py
```
Dann http://localhost:8501 im Browser öffnen.

---

## Tipps

- **Auto-Reload**: Wenn du in TEW speicherst und eine neue MDB erstellst, erkennt die App das und bietet Neuladen an
- **Push-Tracking**: Bei jeder Verbindung wird ein Momentum-Snapshot gespeichert. Mit der Zeit siehst du Trends
- **Card-Templates**: Show-Cards als Vorlagen speichern und wiederverwenden
- **Backup**: Im Tools-Tab Backups erstellen bevor du Änderungen machst
- **Desktop-Verknüpfung**: Rechtsklick auf `start.bat` → "Verknüpfung erstellen" → auf den Desktop verschieben

---

## Fehlerbehebung

### ❌ "Not a valid password" / Passwort-Fehler
**Ursache:** Du versuchst eine normale TEW-Spielstand-Datei zu öffnen, die vom Spiel passwortgeschützt ist.

**Lösung:** Du musst TEWs **"Create MDB File"** Funktion nutzen:
1. TEW IX öffnen → Spielstand laden → Einstellungen → **"Create MDB File"** klicken
2. Die Datei aus dem `MDBFiles`-Ordner verwenden (siehe [Schritt 3](#schritt-3-mdb-datei-in-tew-ix-erstellen))

### ❌ "No module named streamlit" / Modul nicht gefunden
**Ursache:** Python-Abhängigkeiten wurden nicht korrekt installiert, oft weil Python 3.14+ oder mehrere Python-Versionen installiert sind.

**Lösung:**
1. **Python 3.12** installieren (siehe [Schritt 1](#schritt-1-python-312-installieren)) — NICHT Python 3.14 verwenden
2. Andere Python-Versionen **deinstallieren** (Einstellungen → Apps → nach "Python" suchen)
3. PC neu starten
4. `start.bat` erneut ausführen

### ❌ "MDB-Datei nicht gefunden" / Datei nicht gefunden
**Ursache:** Der eingegebene Pfad ist falsch, oder du zeigst auf die falsche Datei.

**Lösung:**
1. Die MDB-Datei muss die von TEWs "Create MDB File" erstellte sein
2. Der Pfad sieht ungefähr so aus: `C:\Games\TEW9\Databases\...\MDBFiles\Name_2026-03-02.mdb`
3. Den **vollständigen Pfad inklusive Dateiname und `.mdb`-Endung** einfügen
4. Das Tool muss NICHT im selben Ordner wie TEW sein — einfach den vollen Pfad verwenden
5. Pfad direkt aus der Explorer-Adressleiste kopieren, dann `\dateiname.mdb` anhängen

### ❌ "ODBC Driver not found" / Treiber-Fehler
**Ursache:** Microsoft Access Database Engine ist nicht installiert.

**Lösung:** Herunterladen und installieren: https://www.microsoft.com/en-us/download/details.aspx?id=54920 (64-Bit wählen)

### ❌ `pyodbc` / `pyproject.toml` Installationsfehler
**Ursache:** Python 3.14+ hat keine fertigen Pakete für pyodbc.

**Lösung:**
1. Stattdessen **Python 3.12** installieren: https://www.python.org/downloads/release/python-3129/
2. Oder [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installieren (dann `start.bat` erneut ausführen)

### ❌ "This site can't be reached" / Seite nicht erreichbar
**Ursache:** Der Streamlit-Server konnte nicht starten (prüfe das schwarze Terminal-Fenster auf Fehler).

**Lösung:**
1. Im Terminal-Fenster (`start.bat`) nach roten Fehlermeldungen schauen
2. Port 8501 muss frei sein — andere Streamlit-Instanzen schließen
3. Manuell starten probieren: `py -m streamlit run app.py`

### Weitere Probleme

| Problem | Lösung |
|---------|--------|
| Leerer Roster nach Verbindung | Die **Initialen** eingeben (z.B. `WWF` statt `World Wrestling Federation`) |
| Popularität zeigt 0 für alle Worker | Die **Kürzel/Initialen** der Promotion verwenden (z.B. `WWF`, `WCW`) |
| Charts werden nicht angezeigt | Browser-Seite neu laden (F5) |
| App ist langsam | Beim ersten Laden normal — danach schneller |

---

## Lizenz / Credits

Made with ❤️ for the TEW community.
Built with [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/), [Pandas](https://pandas.pydata.org/), and [ReportLab](https://www.reportlab.com/).
