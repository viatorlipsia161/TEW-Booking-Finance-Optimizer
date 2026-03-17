"""
TEW Booking & Finance Optimizer – Database Module
Reads data from the TEW IX Microsoft Access database (.mdb).

TEW IX Table Structure:
  - Workers              (135 cols) – All workers with skills, popularity etc.
  - Contracts            (44 cols)  – Contracts incl. Wage (=Amount), Role
  - Companies            (100+ cols)– Promotions
  - Match_Histories      (17 cols)  – Past matches
  - Match_Histories_Wrestlers (3)   – Workers per match (MatchHistoryUID, WorkerUID, Which_Side)
  - Previous_Shows       (11 cols)  – Shows with Attendance, Rating
  - Financial_Histories  (24 cols)  – Income/expenses per month
  - Title_Belts          (28 cols)  – Championship belts and current holders
"""

import pyodbc
import pandas as pd
from pathlib import Path


# ──────────────────────────────────────────────
# Core Functions
# ──────────────────────────────────────────────

def get_connection(mdb_path: str) -> pyodbc.Connection:
    """Opens a connection to the MDB file."""
    path = Path(mdb_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"MDB file not found: {path}")

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={path};"
    )
    return pyodbc.connect(conn_str)


def list_tables(mdb_path: str) -> list[str]:
    """Lists all tables in the MDB file."""
    conn = get_connection(mdb_path)
    cursor = conn.cursor()
    tables = [
        row.table_name
        for row in cursor.tables(tableType="TABLE")
    ]
    conn.close()
    return tables


def read_table(mdb_path: str, table_name: str) -> pd.DataFrame:
    """Reads a complete table as DataFrame."""
    conn = get_connection(mdb_path)
    df = pd.read_sql(f"SELECT * FROM [{table_name}]", conn)
    conn.close()
    return df


def read_query(mdb_path: str, query: str) -> pd.DataFrame:
    """Executes an arbitrary SQL query."""
    conn = get_connection(mdb_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ──────────────────────────────────────────────
# Worker Data
# ──────────────────────────────────────────────

def get_workers(mdb_path: str) -> pd.DataFrame:
    """
    Reads all workers from [Workers].
    Selects only columns relevant to the tool.
    """
    query = """
    SELECT
        UID,
        Name,
        Gender_ID,
        Active,
        Status,
        Style,
        Based_In,
        Nationality,
        Wrestler,
        Occasional_Wrestler,
        Referee,
        Announcer,
        Colour_Commentator,
        Manager,
        On_Screen_Personality,
        Road_Agent,
        Brawling,
        Aerial,
        Technical,
        Power,
        Athleticism,
        Stamina,
        Psychology,
        Basics,
        Toughness,
        Selling,
        Charisma,
        Microphone,
        Menace,
        Respect,
        Safety,
        Looks,
        Star_Quality,
        Consistency,
        Acting,
        Resilience,
        Puroresu,
        Flashiness,
        Hardcore,
        Experience,
        Great_Lakes, Mid_Atlantic, Mid_South, Mid_West, New_England,
        North_West, South_East, South_West, Tri_State, Puerto_Rico, Hawaii,
        Maritimes, Quebec, Ontario, Alberta, Saskatchewan, Manitoba, British_Columbia,
        Noreste, Noroccidente, Sureste, Sur, Centro, Occidente,
        Midlands, Northern_England, Scotland, Southern_England, Ireland, Wales,
        Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu, Hokkaido,
        Western_Europe, Iberia, Southern_Med, Southern_Europe,
        Central_Europe, Northern_Europe, Eastern_Central_Europe, Eastern_Europe,
        New_South_Wales, Queensland, South_Australia, Victoria,
        Western_Australia, Tasmania, New_Zealand,
        Northern_India, Eastern_India, Southern_India, Western_India
    FROM [Workers]
    """
    return read_query(mdb_path, query)


# ──────────────────────────────────────────────
# Contracts
# ──────────────────────────────────────────────

def get_contracts(mdb_path: str, promotion_name: str = None) -> pd.DataFrame:
    """
    Reads contracts from [Contracts].
    Per-show wage is the 'Amount' column.
    Optionally filtered by promotion via CompanyName.
    """
    query = """
    SELECT
        CompanyUID,
        CompanyName,
        WorkerUID,
        WorkerName,
        Name        AS GimmickName,
        Perception,
        Babyface,
        Gimmick,
        Gimmick_Rating,
        Exclusive_Contract,
        Written_Contract,
        Touring,
        RosterUsage,
        IntendedRole,
        ExpectedShows,
        Amount,
        Downside,
        Paid,
        Days_Left,
        Dates_Left,
        Contract_Began,
        BonusAmount,
        BonusType,
        Creative_Control,
        Momentum,
        Wrestler        AS C_Wrestler,
        Occasional_Wrestler AS C_Occasional_Wrestler,
        Referee         AS C_Referee,
        Announcer       AS C_Announcer,
        Colour_Commentator AS C_Colour_Commentator,
        Manager         AS C_Manager,
        On_Screen_Personality AS C_On_Screen_Personality,
        Road_Agent      AS C_Road_Agent
    FROM [Contracts]
    """
    contracts = read_query(mdb_path, query)

    if promotion_name:
        mask = contracts["CompanyName"].str.contains(promotion_name, case=False, na=False)
        contracts = contracts[mask]

    return contracts


def get_contracts_detailed(mdb_path: str, promotion_name: str) -> pd.DataFrame:
    """
    Returns a clean contract overview DataFrame for display.
    Includes role detection, contract type, days left.
    """
    contracts = get_contracts(mdb_path, promotion_name)
    if contracts.empty:
        return contracts

    df = contracts.copy()

    # Detect primary role
    role_cols = {
        "C_Wrestler": "Wrestler", "C_Occasional_Wrestler": "Occasional",
        "C_Referee": "Referee", "C_Announcer": "Announcer",
        "C_Colour_Commentator": "Commentator", "C_Manager": "Manager",
        "C_On_Screen_Personality": "Personality", "C_Road_Agent": "Road Agent",
    }
    def detect_role(row):
        roles = [label for col, label in role_cols.items() if row.get(col, False)]
        return ", ".join(roles) if roles else "Unknown"

    df["Role"] = df.apply(detect_role, axis=1)

    # Contract type
    def contract_type(row):
        parts = []
        if row.get("Written_Contract", False):
            parts.append("Written")
        if row.get("Exclusive_Contract", False):
            parts.append("Exclusive")
        if not parts:
            parts.append("PPA")
        return ", ".join(parts)

    df["ContractType"] = df.apply(contract_type, axis=1)

    # Days left formatting
    df["DaysLeft"] = pd.to_numeric(df["Days_Left"], errors="coerce").fillna(-1).astype(int)
    df["Status"] = df["DaysLeft"].apply(
        lambda d: "Open-ended" if d == -1 else f"{d} days" if d > 30 else "Expiring Soon!" if d > 0 else "Expired"
    )

    keep = ["WorkerName", "GimmickName", "Role", "ContractType", "Status", "DaysLeft",
            "Amount", "Downside", "Momentum", "Perception", "RosterUsage",
            "IntendedRole", "Contract_Began", "Touring"]
    keep = [c for c in keep if c in df.columns]
    return df[keep].rename(columns={"Amount": "Wage"})


# ──────────────────────────────────────────────
# Promotions / Companies
# ──────────────────────────────────────────────

def get_companies(mdb_path: str) -> pd.DataFrame:
    """Reads all companies/promotions from [Companies]."""
    query = """
    SELECT
        UID,
        Name,
        Initials,
        Size,
        Prestige,
        Money,
        Ranking,
        Momentum,
        Based_In,
        Currently_Open,
        User_Controlled
    FROM [Companies]
    """
    return read_query(mdb_path, query)


def get_promotions(mdb_path: str) -> pd.DataFrame:
    """Alias for get_companies (compatibility)."""
    return get_companies(mdb_path)


# Mapping: Based_In value in DB → column name in [Workers]
REGION_COLUMN_MAP = {
    "Great Lakes": "Great_Lakes", "Mid Atlantic": "Mid_Atlantic",
    "Mid South": "Mid_South", "Mid West": "Mid_West",
    "New England": "New_England", "North West": "North_West",
    "South East": "South_East", "South West": "South_West",
    "Tri State": "Tri_State", "Puerto Rico": "Puerto_Rico", "Hawaii": "Hawaii",
    "Maritimes": "Maritimes", "Quebec": "Quebec", "Ontario": "Ontario",
    "Alberta": "Alberta", "Saskatchewan": "Saskatchewan",
    "Manitoba": "Manitoba", "British Columbia": "British_Columbia",
    "Noreste": "Noreste", "Noroccidente": "Noroccidente",
    "Sureste": "Sureste", "Sur": "Sur", "Centro": "Centro", "Occidente": "Occidente",
    "Midlands": "Midlands", "Northern England": "Northern_England",
    "Scotland": "Scotland", "Southern England": "Southern_England",
    "Ireland": "Ireland", "Wales": "Wales",
    "Tohoku": "Tohoku", "Kanto": "Kanto", "Chubu": "Chubu", "Kinki": "Kinki",
    "Chugoku": "Chugoku", "Shikoku": "Shikoku", "Kyushu": "Kyushu", "Hokkaido": "Hokkaido",
    "Western Europe": "Western_Europe", "Iberia": "Iberia",
    "Southern Med": "Southern_Med", "Southern Europe": "Southern_Europe",
    "Central Europe": "Central_Europe", "Northern Europe": "Northern_Europe",
    "Eastern Central Europe": "Eastern_Central_Europe", "Eastern Europe": "Eastern_Europe",
    "New South Wales": "New_South_Wales", "Queensland": "Queensland",
    "South Australia": "South_Australia", "Victoria": "Victoria",
    "Western Australia": "Western_Australia", "Tasmania": "Tasmania",
    "New Zealand": "New_Zealand",
    "Northern India": "Northern_India", "Eastern India": "Eastern_India",
    "Southern India": "Southern_India", "Western India": "Western_India",
}

# Macro regions: which sub-regions belong together?
MACRO_REGIONS = {
    "USA": ["Great_Lakes", "Mid_Atlantic", "Mid_South", "Mid_West", "New_England",
            "North_West", "South_East", "South_West", "Tri_State", "Puerto_Rico", "Hawaii"],
    "Canada": ["Maritimes", "Quebec", "Ontario", "Alberta", "Saskatchewan",
               "Manitoba", "British_Columbia"],
    "Mexico": ["Noreste", "Noroccidente", "Sureste", "Sur", "Centro", "Occidente"],
    "UK": ["Midlands", "Northern_England", "Scotland", "Southern_England", "Ireland", "Wales"],
    "Japan": ["Tohoku", "Kanto", "Chubu", "Kinki", "Chugoku", "Shikoku", "Kyushu", "Hokkaido"],
    "Europe": ["Western_Europe", "Iberia", "Southern_Med", "Southern_Europe",
               "Central_Europe", "Northern_Europe", "Eastern_Central_Europe", "Eastern_Europe"],
    "Oceania": ["New_South_Wales", "Queensland", "South_Australia", "Victoria",
                "Western_Australia", "Tasmania", "New_Zealand"],
    "India": ["Northern_India", "Eastern_India", "Southern_India", "Western_India"],
}


def get_company_home_region(mdb_path: str, promotion_name: str) -> tuple[str, str]:
    """
    Determines the company's home region.
    Checks both Name and Initials columns so abbreviations (e.g. 'WWF') work.
    Returns: (based_in_label, column_name) e.g. ("Southern England", "Southern_England")
    """
    companies = get_companies(mdb_path)
    # Try Initials first (exact match, most common user input)
    if "Initials" in companies.columns:
        mask = companies["Initials"].str.strip().str.upper() == promotion_name.strip().upper()
        if mask.any():
            based_in = companies.loc[mask, "Based_In"].iloc[0]
            col_name = REGION_COLUMN_MAP.get(based_in, "")
            return based_in, col_name
    # Fallback: search in full Name
    mask = companies["Name"].str.contains(promotion_name, case=False, na=False)
    if mask.any():
        based_in = companies.loc[mask, "Based_In"].iloc[0]
        col_name = REGION_COLUMN_MAP.get(based_in, "")
        return based_in, col_name
    return "", ""


def get_macro_region_for(column_name: str) -> str:
    """Returns the macro region for a sub-region column name."""
    for macro, subs in MACRO_REGIONS.items():
        if column_name in subs:
            return macro
    return ""


# ──────────────────────────────────────────────
# Title Belts / Champions
# ──────────────────────────────────────────────

def get_title_belts(mdb_path: str, promotion_name: str = None) -> pd.DataFrame:
    """Reads current title holders from [Title_Belts]."""
    query = """
    SELECT
        UID, Name, CompanyUID, CompanyName, BeltLevel, Prestige,
        Active, HolderName1, HolderName2, HolderName3, Defences,
        Reign_Began, Last_Defence
    FROM [Title_Belts]
    """
    df = read_query(mdb_path, query)
    if promotion_name:
        mask = df["CompanyName"].str.contains(promotion_name, case=False, na=False)
        df = df[mask]
    return df


# ──────────────────────────────────────────────
# Previous Shows
# ──────────────────────────────────────────────

def get_previous_shows(mdb_path: str, promotion_name: str = None) -> pd.DataFrame:
    """Reads past shows from [Previous_Shows]."""
    query = """
    SELECT
        UID, ShowName, CompanyUID, CompanyName, Region, Venue,
        Attendance, PPV_Rating, TV_Rating, Overall_Rating, Held
    FROM [Previous_Shows]
    """
    df = read_query(mdb_path, query)
    if promotion_name:
        mask = df["CompanyName"].str.contains(promotion_name, case=False, na=False)
        df = df[mask]
    return df


# ──────────────────────────────────────────────
# TV Shows / Schedule
# ──────────────────────────────────────────────

def get_tv_shows(mdb_path: str, promotion_name: str = None) -> pd.DataFrame:
    """Reads TV show schedule from [TV_Shows]."""
    query = """
    SELECT
        Name, CompanyUID, Company_Name, Prestige, B_Show, Length,
        Brand, Showday, Currently_On_Air
    FROM [TV_Shows]
    """
    df = read_query(mdb_path, query)
    if promotion_name:
        mask = df["Company_Name"].str.contains(promotion_name, case=False, na=False)
        df = df[mask]
    return df


def get_show_defaults(mdb_path: str, promotion_name: str) -> dict:
    """
    Determines show defaults from the DB:
    - Average attendance & revenue from Previous_Shows
    - Company money/size
    """
    defaults = {
        "avg_attendance": 0,
        "avg_rating": 0,
        "estimated_revenue": 0,
        "company_money": 0,
        "company_size": "",
        "company_prestige": 0,
    }
    try:
        shows = get_previous_shows(mdb_path, promotion_name)
        if not shows.empty:
            defaults["avg_attendance"] = int(shows["Attendance"].mean())
            valid_ratings = shows["Overall_Rating"][shows["Overall_Rating"] > 0]
            if not valid_ratings.empty:
                defaults["avg_rating"] = round(float(valid_ratings.mean()), 1)
            # Rough ticket revenue estimate: Attendance * $11 (TEW default ticket price)
            defaults["estimated_revenue"] = int(shows["Attendance"].mean() * 11)

        companies = get_companies(mdb_path)
        mask = companies["Name"].str.contains(promotion_name, case=False, na=False)
        if mask.any():
            comp = companies[mask].iloc[0]
            defaults["company_money"] = int(comp.get("Money", 0))
            defaults["company_size"] = str(comp.get("Size", ""))
            defaults["company_prestige"] = int(comp.get("Prestige", 0))
    except Exception:
        pass
    return defaults


# ──────────────────────────────────────────────
# Match History & Staleness
# ──────────────────────────────────────────────

def get_match_histories(mdb_path: str, company_name: str = None) -> pd.DataFrame:
    """Reads match histories from [Match_Histories]. Optionally filtered by company."""
    df = read_table(mdb_path, "Match_Histories")
    if company_name:
        mask = df["CompanyName"].str.contains(company_name, case=False, na=False)
        df = df[mask]
    return df


def get_match_participants(mdb_path: str) -> pd.DataFrame:
    """Reads [Match_Histories_Wrestlers] – which workers were in which match."""
    return read_table(mdb_path, "Match_Histories_Wrestlers")


def get_staleness(mdb_path: str, company_name: str = None) -> pd.DataFrame:
    """
    Builds a staleness table: how often has each worker pairing faced each other?
    Uses Match_Histories + Match_Histories_Wrestlers.
    """
    try:
        matches = get_match_histories(mdb_path, company_name)
        participants = get_match_participants(mdb_path)

        if matches.empty or participants.empty:
            return pd.DataFrame()

        match_uids = set(matches["UID"].tolist())
        relevant = participants[participants["MatchHistoryUID"].isin(match_uids)]

        # Per match: form all worker pairs (Side 1 vs Side 2)
        pairings = []
        for match_uid, group in relevant.groupby("MatchHistoryUID"):
            side1 = group[group["Which_Side"] == 1]["WorkerUID"].tolist()
            side2 = group[group["Which_Side"] == 2]["WorkerUID"].tolist()
            for w1 in side1:
                for w2 in side2:
                    pair = tuple(sorted([w1, w2]))
                    pairings.append(pair)

        if not pairings:
            return pd.DataFrame()

        pair_df = pd.DataFrame(pairings, columns=["WorkerUID1", "WorkerUID2"])
        staleness = pair_df.groupby(["WorkerUID1", "WorkerUID2"]).size().reset_index(name="Count")
        return staleness

    except Exception:
        return pd.DataFrame()


# ──────────────────────────────────────────────
# Financial Histories
# ──────────────────────────────────────────────

def get_financial_histories(mdb_path: str, company_name: str = None) -> pd.DataFrame:
    """Reads [Financial_Histories] – monthly income/expense breakdown."""
    df = read_table(mdb_path, "Financial_Histories")
    if company_name:
        mask = df["Company_Name"].str.contains(company_name, case=False, na=False)
        df = df[mask]
    return df


# ──────────────────────────────────────────────
# Staff Detection
# ──────────────────────────────────────────────

def get_staff(mdb_path: str, promotion_name: str = None) -> pd.DataFrame:
    """
    Reads non-wrestler staff (Road Agents, Referees, etc.).
    Detects role from boolean columns in the Contract.
    """
    contracts = get_contracts(mdb_path, promotion_name)

    staff_mask = (
        (contracts.get("C_Wrestler", pd.Series([False])) == False)
        & (contracts.get("C_Occasional_Wrestler", pd.Series([False])) == False)
    )
    return contracts[staff_mask]


# ──────────────────────────────────────────────
# Roster Builder (Main Function)
# ──────────────────────────────────────────────

def build_roster(mdb_path: str, promotion_name: str) -> pd.DataFrame:
    """
    Main function: Builds the complete roster DataFrame with Efficiency Score.

    Efficiency Score = (AvgSkill + (Popularity * 0.5)) / Wage

    AvgSkill = Average of primary in-ring skills:
               Brawling, Technical, Aerial, Puroresu, Flashiness, Selling, Basics, Psychology
    """
    workers = get_workers(mdb_path)
    contracts = get_contracts(mdb_path, promotion_name)

    if contracts.empty:
        raise ValueError(
            f"No contracts found for '{promotion_name}'. "
            f"Available companies: {contracts['CompanyName'].unique().tolist() if not contracts.empty else 'none'}"
        )

    roster = pd.merge(
        workers, contracts,
        left_on="UID", right_on="WorkerUID",
        how="inner", suffixes=("", "_contract"),
    )

    # Clean duplicates after merge
    drop_cols = []
    if "WorkerUID" in roster.columns and "UID" in roster.columns:
        drop_cols.append("WorkerUID")
    if "WorkerName" in roster.columns and "Name" in roster.columns:
        drop_cols.append("WorkerName")
    if drop_cols:
        roster.drop(columns=drop_cols, inplace=True)

    roster.rename(columns={"UID": "WorkerUID", "Name": "WorkerName", "Amount": "Wage"}, inplace=True)

    # In-Ring Skill average
    skill_cols = ["Brawling", "Technical", "Aerial", "Puroresu", "Flashiness",
                  "Selling", "Basics", "Psychology"]
    available_skills = [c for c in skill_cols if c in roster.columns]
    roster["AvgSkill"] = roster[available_skills].mean(axis=1) if available_skills else 50

    # Home-Region Popularity
    based_in_label, home_region_col = get_company_home_region(mdb_path, promotion_name)
    macro_region = get_macro_region_for(home_region_col)

    if home_region_col and home_region_col in roster.columns:
        roster["HomePopularity"] = pd.to_numeric(roster[home_region_col], errors="coerce").fillna(0)
    else:
        roster["HomePopularity"] = 0

    # Macro-region popularity averages
    for macro_name, sub_cols in MACRO_REGIONS.items():
        available = [c for c in sub_cols if c in roster.columns]
        if available:
            roster[f"Pop_{macro_name}"] = roster[available].apply(
                pd.to_numeric, errors="coerce"
            ).mean(axis=1).round(1)
        else:
            roster[f"Pop_{macro_name}"] = 0

    # Momentum numeric
    momentum_map = {
        "Very Cold": 10, "Cold": 20, "Cooled": 30, "Cool": 35,
        "Neutral": 50, "Warm": 65, "Very Warm": 75, "Hot": 85, "Very Hot": 95,
    }
    roster["MomentumNum"] = roster["Momentum"].map(momentum_map).fillna(50) if "Momentum" in roster.columns else 50

    # Popularity = Home-Region Popularity
    roster["Popularity"] = roster["HomePopularity"]

    if "Star_Quality" in roster.columns:
        roster["Star_Quality"] = pd.to_numeric(roster["Star_Quality"], errors="coerce").fillna(0)

    roster["Wage"] = pd.to_numeric(roster["Wage"], errors="coerce").fillna(0).replace(0, 1)

    # Efficiency Score: (AvgSkill + (HomePopularity * 0.5)) / Wage
    roster["EfficiencyScore"] = (roster["AvgSkill"] + (roster["Popularity"] * 0.5)) / roster["Wage"]

    if "Looks" not in roster.columns:
        roster["Looks"] = 0

    # Store metadata
    roster.attrs["home_region"] = based_in_label
    roster.attrs["home_region_col"] = home_region_col
    roster.attrs["macro_region"] = macro_region

    return roster


# ──────────────────────────────────────────────
# DB Structure Explorer
# ──────────────────────────────────────────────

def detect_table_structure(mdb_path: str) -> dict:
    """
    Detects the table structure of the MDB file.
    Useful for debugging and adapting to different TEW versions.
    """
    conn = get_connection(mdb_path)
    cursor = conn.cursor()
    tables = [row.table_name for row in cursor.tables(tableType="TABLE")]

    structure = {}
    for table in tables:
        try:
            cols = [col.column_name for col in cursor.columns(table=table)]
            structure[table] = cols
        except Exception:
            structure[table] = []

    conn.close()
    return structure


# ──────────────────────────────────────────────
# Free Agent Scouting
# ──────────────────────────────────────────────

# Region groupings for Based_In filtering
BASED_IN_GROUPS = {
    "North America": [
        "Great Lakes", "Mid Atlantic", "Mid South", "Mid West", "New England",
        "North West", "South East", "South West", "Tri State", "Puerto Rico", "Hawaii",
    ],
    "Canada": [
        "The Maritimes", "Quebec", "Ontario", "Alberta", "Saskatchewan",
        "Manitoba", "British Columbia",
    ],
    "Mexico": ["Noreste", "Noroccidente", "Sureste", "Sur", "Centro", "Occidente"],
    "UK & Ireland": [
        "Midlands", "Northern England", "Scotland", "Southern England", "Ireland", "Wales",
    ],
    "Europe": [
        "Western Europe", "Iberia", "Southern Mediterranean", "Southern Europe",
        "Central Europe", "Northern Europe", "Eastern-Central Europe", "Eastern Europe",
    ],
    "Japan": ["Tohoku", "Kanto", "Chubu", "Kansai", "Chugoku", "Shikoku", "Kyushu", "Hokkaido"],
    "Oceania": [
        "New South Wales", "Queensland", "South Australia", "Victoria",
        "Western Australia", "Tasmania", "New Zealand",
    ],
    "India": ["Northern India", "Eastern India", "Southern India", "Western India"],
}

# Gender simplification
GENDER_GROUPS = {
    "Female": ["Cisgender Female", "Transgender Female", "Non-Binary AFAB"],
    "Male": ["Cisgender Male", "Transgender Male", "Non-Binary AMAB", "Other Male"],
}


def _parse_tew_birthday(bday_str: str) -> int | None:
    """Parse TEW birthday string like 'Dienstag 26 Januar 1982' -> extract year."""
    if not bday_str or not isinstance(bday_str, str):
        return None
    parts = bday_str.strip().split()
    for p in reversed(parts):
        try:
            year = int(p)
            if 1900 <= year <= 2100:
                return year
        except ValueError:
            continue
    return None


def get_free_agents(mdb_path: str) -> pd.DataFrame:
    """
    Returns all active free agents (not signed to any company).
    Includes wrestlers, refs, road agents, announcers, managers, etc.
    """
    conn = get_connection(mdb_path)

    # Get all contracted worker UIDs
    contracted = pd.read_sql("SELECT DISTINCT WorkerUID FROM [Contracts]", conn)
    contracted_uids = set(contracted["WorkerUID"].tolist())

    # Get all active workers
    skill_cols = [
        "Brawling", "Aerial", "Technical", "Power", "Athleticism", "Stamina",
        "Psychology", "Basics", "Toughness", "Selling", "Charisma", "Microphone",
        "Menace", "Respect", "Reputation", "Safety", "Looks", "Star_Quality",
        "Consistency", "Acting", "Resilience", "Puroresu", "Flashiness", "Hardcore",
        "Refereeing", "Experience", "Booking_Skill",
    ]
    pop_cols = [
        "USA", "Canada", "Mexico", "Japan", "British_Isles", "Europe", "Oceania", "India",
    ]

    cols = (
        ["UID", "Name", "Gender_ID", "Based_In", "Birthday", "Status",
         "Freelance", "Wrestler", "Occasional_Wrestler", "Referee",
         "Road_Agent", "Announcer", "Colour_Commentator", "Manager",
         "On_Screen_Personality", "Style"]
        + skill_cols + pop_cols
    )

    query = f"SELECT {', '.join(cols)} FROM [Workers] WHERE Active=True"
    df = pd.read_sql(query, conn)
    conn.close()

    # Filter to free agents only
    mask = (~df["UID"].isin(contracted_uids)) & (df["Status"].isin(["Active Wrestler", "Non-Wrestler"]))
    df = df.loc[mask].copy()

    # Parse birth year and calculate age (approximate)
    df["BirthYear"] = df["Birthday"].apply(_parse_tew_birthday)
    # Use current game year from the mdb filename if possible, else 2026
    import re
    year_match = re.search(r"(\d{4})", str(mdb_path))
    game_year = int(year_match.group(1)) if year_match else 2026
    df["Age"] = df["BirthYear"].apply(lambda y: game_year - y if y else None)

    # Simplify gender
    def simplify_gender(g):
        for group, values in GENDER_GROUPS.items():
            if g in values:
                return group
        return "Other"
    df["Gender"] = df["Gender_ID"].apply(simplify_gender)

    # Compute avg skill for wrestlers
    wrestling_skills = ["Brawling", "Aerial", "Technical", "Power", "Athleticism",
                        "Stamina", "Psychology", "Basics", "Toughness", "Selling"]
    for c in wrestling_skills:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["AvgSkill"] = df[wrestling_skills].mean(axis=1).round(1)

    # Star power
    for c in ["Charisma", "Microphone", "Star_Quality", "Looks", "Menace"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["StarPower"] = df[["Charisma", "Microphone", "Star_Quality", "Looks"]].mean(axis=1).round(1)

    # Max popularity
    for c in pop_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["MaxPop"] = df[pop_cols].max(axis=1)

    # Refereeing & road agent skills
    df["Refereeing"] = pd.to_numeric(df["Refereeing"], errors="coerce").fillna(0)
    df["Experience"] = pd.to_numeric(df["Experience"], errors="coerce").fillna(0)
    df["Booking_Skill"] = pd.to_numeric(df["Booking_Skill"], errors="coerce").fillna(0)
    df["Psychology"] = pd.to_numeric(df["Psychology"], errors="coerce")
    df["Safety"] = pd.to_numeric(df["Safety"], errors="coerce").fillna(0)
    df["Reputation"] = pd.to_numeric(df["Reputation"], errors="coerce").fillna(0)
    df["Respect"] = pd.to_numeric(df["Respect"], errors="coerce").fillna(0)

    # Role flags to bool
    for rc in ["Wrestler", "Occasional_Wrestler", "Referee", "Road_Agent",
               "Announcer", "Colour_Commentator", "Manager", "On_Screen_Personality"]:
        df[rc] = df[rc].astype(bool)

    return df
