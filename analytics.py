"""
TEW Booking & Finance Optimizer – Analytics Engine
Chemistry detection, roster health, popularity forecast, worker development,
angle suggestions, title reign tracking, touring optimizer, talent trade analyzer.
"""

import pandas as pd
import numpy as np
from itertools import combinations

SKILL_COLS = ["Brawling", "Technical", "Aerial", "Puroresu", "Flashiness",
              "Selling", "Basics", "Psychology"]

PERFORMANCE_COLS = ["Charisma", "Microphone", "Acting", "Star_Quality", "Menace", "Respect"]


def _safe(series, col, default=0.0):
    return float(series.get(col, default)) if col in series.index else default


# ──────────────────────────────────────────────
# Chemistry Detection
# ──────────────────────────────────────────────

def detect_chemistry(
    roster: pd.DataFrame,
    match_histories: pd.DataFrame,
    match_participants: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyzes match history to find proven chemistry between workers.
    Compares actual match ratings vs predicted ratings to find pairs
    that consistently over- or under-perform.

    Returns DataFrame with: Worker1, Worker2, MatchCount, AvgRating, Status
    """
    if match_histories.empty or match_participants.empty:
        return pd.DataFrame()

    # Match_Histories uses "Rating" column (not "Overall_Rating")
    rating_col = "Rating" if "Rating" in match_histories.columns else "Overall_Rating"
    if rating_col not in match_histories.columns:
        return pd.DataFrame()

    rated = match_histories[pd.to_numeric(match_histories[rating_col], errors="coerce").fillna(0) > 0].copy()
    if rated.empty:
        return pd.DataFrame()

    match_uids = set(rated["UID"].tolist())
    rel = match_participants[match_participants["MatchHistoryUID"].isin(match_uids)]

    # Build pairing → ratings map
    pair_ratings = {}
    for muid, group in rel.groupby("MatchHistoryUID"):
        rating_row = rated[rated["UID"] == muid]
        if rating_row.empty:
            continue
        rating = float(pd.to_numeric(rating_row[rating_col].iloc[0], errors="coerce") or 0)

        side1 = group[group["Which_Side"] == 1]["WorkerUID"].tolist()
        side2 = group[group["Which_Side"] == 2]["WorkerUID"].tolist()
        for w1 in side1:
            for w2 in side2:
                pair = tuple(sorted([w1, w2]))
                if pair not in pair_ratings:
                    pair_ratings[pair] = []
                pair_ratings[pair].append(rating)

    if not pair_ratings:
        return pd.DataFrame()

    # Build name lookup
    uid_to_name = {}
    if "WorkerUID" in roster.columns and "WorkerName" in roster.columns:
        uid_to_name = dict(zip(roster["WorkerUID"].astype(int), roster["WorkerName"]))

    rows = []
    for (u1, u2), ratings in pair_ratings.items():
        avg_rating = sum(ratings) / len(ratings)
        count = len(ratings)

        if count >= 3 and avg_rating >= 60:
            status = "🔥 Proven Chemistry"
        elif count >= 2 and avg_rating >= 50:
            status = "✅ Good Pairing"
        elif count >= 2 and avg_rating < 30:
            status = "❌ Bad Chemistry"
        elif count == 1:
            status = "🆕 Untested (1 match)"
        else:
            status = "📊 Developing"

        rows.append({
            "Worker1": uid_to_name.get(int(u1), str(u1)),
            "Worker2": uid_to_name.get(int(u2), str(u2)),
            "MatchCount": count,
            "AvgRating": round(avg_rating, 1),
            "BestRating": max(ratings),
            "WorstRating": min(ratings),
            "Status": status,
        })

    df = pd.DataFrame(rows).sort_values("AvgRating", ascending=False).reset_index(drop=True)
    return df


# ──────────────────────────────────────────────
# Roster Health Dashboard
# ──────────────────────────────────────────────

def analyze_roster_health(roster: pd.DataFrame, contracts_detailed: pd.DataFrame = None) -> dict:
    """
    Comprehensive roster health analysis:
    - Role distribution (wrestlers vs staff)
    - Face/Heel balance
    - Experience distribution (veterans/mid/young)
    - Skill gaps
    - Contract timeline
    """
    health = {
        "total": len(roster),
        "wrestlers": 0,
        "staff": 0,
        "faces": 0,
        "heels": 0,
        "neutral": 0,
        "veterans": 0,
        "midcard": 0,
        "young": 0,
        "avg_skill": 0,
        "skill_ceiling": 0,
        "skill_floor": 0,
        "expiring_soon": 0,
        "open_ended": 0,
        "avg_wage": 0,
        "top_heavy": False,
        "issues": [],
        "strengths": [],
    }

    # Wrestler count
    for col in ["C_Wrestler", "Wrestler"]:
        if col in roster.columns:
            health["wrestlers"] = int(roster[col].sum())
            health["staff"] = health["total"] - health["wrestlers"]
            break

    # Face/Heel balance (Babyface column: True=Face, False=Heel)
    if "Babyface" in roster.columns:
        health["faces"] = int(roster["Babyface"].sum())
        health["heels"] = health["total"] - health["faces"]
    elif contracts_detailed is not None and "Babyface" in contracts_detailed.columns:
        health["faces"] = int(contracts_detailed["Babyface"].sum())
        health["heels"] = health["total"] - health["faces"]

    # Experience distribution
    if "Experience" in roster.columns:
        exp = pd.to_numeric(roster["Experience"], errors="coerce").fillna(0)
        health["veterans"] = int((exp >= 70).sum())
        health["midcard"] = int(((exp >= 30) & (exp < 70)).sum())
        health["young"] = int((exp < 30).sum())

    # Skill analysis
    if "AvgSkill" in roster.columns:
        health["avg_skill"] = round(float(roster["AvgSkill"].mean()), 1)
        health["skill_ceiling"] = round(float(roster["AvgSkill"].max()), 1)
        health["skill_floor"] = round(float(roster["AvgSkill"].min()), 1)

    # Wage analysis
    if "Wage" in roster.columns:
        health["avg_wage"] = round(float(roster["Wage"].mean()), 0)
        top3_wages = roster.nlargest(3, "Wage")["Wage"].sum()
        total_wages = roster["Wage"].sum()
        if total_wages > 0:
            health["top_heavy"] = (top3_wages / total_wages) > 0.4

    # Contract timeline
    if contracts_detailed is not None and "Status" in contracts_detailed.columns:
        health["expiring_soon"] = int((contracts_detailed["Status"] == "Expiring Soon!").sum())
        health["open_ended"] = int((contracts_detailed["Status"] == "Open-ended").sum())

    # Issue detection
    if health["wrestlers"] < 8:
        health["issues"].append("⚠️ Very small roster – fewer than 8 wrestlers")
    if health["faces"] > 0 and health["heels"] > 0:
        ratio = health["faces"] / max(health["heels"], 1)
        if ratio > 2.5:
            health["issues"].append("⚠️ Too many faces – need more heels")
        elif ratio < 0.4:
            health["issues"].append("⚠️ Too many heels – need more faces")
    if health["young"] == 0 and health["total"] > 5:
        health["issues"].append("⚠️ No young talent – future depth concern")
    if health["veterans"] == 0 and health["total"] > 5:
        health["issues"].append("⚠️ No veterans – lacking experienced leaders")
    if health["top_heavy"]:
        health["issues"].append("⚠️ Top-heavy wages – top 3 earn >40% of total payroll")
    if health["expiring_soon"] > 3:
        health["issues"].append(f"⚠️ {health['expiring_soon']} contracts expiring soon")

    # Strengths
    if health["avg_skill"] >= 60:
        health["strengths"].append("💪 High average skill level")
    if 0.6 <= (health["faces"] / max(health["heels"], 1)) <= 1.8:
        health["strengths"].append("✅ Good face/heel balance")
    if health["veterans"] >= 2 and health["young"] >= 2:
        health["strengths"].append("✅ Good experience mix (veterans + young talent)")

    return health


# ──────────────────────────────────────────────
# Popularity Forecast
# ──────────────────────────────────────────────

def forecast_popularity(momentum_history: dict, worker_name: str, months_ahead: int = 3) -> dict:
    """
    Predicts future popularity based on momentum trends.
    Uses momentum trajectory: Hot momentum → popularity climbs, Cold → declines.
    """
    snapshots = momentum_history.get("snapshots", [])
    if not snapshots:
        return {"current": 0, "predicted": 0, "trend": "unknown", "confidence": "low"}

    mom_map = {"Very Cold": -4, "Cold": -3, "Cooled": -2, "Cool": -1,
               "Neutral": 0, "Warm": 1, "Very Warm": 2, "Hot": 3, "Very Hot": 4}

    # Gather history for this worker
    history = []
    for s in snapshots:
        if worker_name in s["workers"]:
            info = s["workers"][worker_name]
            history.append({
                "date": s["date"],
                "momentum": info["momentum"],
                "popularity": info["popularity"],
                "mom_val": mom_map.get(info["momentum"], 0),
            })

    if not history:
        return {"current": 0, "predicted": 0, "trend": "unknown", "confidence": "low"}

    current_pop = history[-1]["popularity"]
    current_mom = history[-1]["mom_val"]

    # Calculate trend from history
    if len(history) >= 2:
        pop_changes = []
        for i in range(1, len(history)):
            pop_changes.append(history[i]["popularity"] - history[i-1]["popularity"])
        avg_change = sum(pop_changes) / len(pop_changes)
    else:
        # Estimate from momentum alone
        avg_change = current_mom * 1.5

    # Predict: momentum affects ~1-4 pop points per month
    predicted = current_pop + (avg_change + current_mom * 0.8) * months_ahead
    predicted = max(0, min(100, predicted))

    # Trend
    if current_mom >= 2:
        trend = "📈 Rising Fast"
    elif current_mom >= 1:
        trend = "📈 Rising"
    elif current_mom == 0:
        trend = "➡️ Stable"
    elif current_mom >= -1:
        trend = "📉 Declining"
    else:
        trend = "📉 Declining Fast"

    confidence = "high" if len(history) >= 3 else "medium" if len(history) >= 2 else "low"

    return {
        "current": round(current_pop, 1),
        "predicted": round(predicted, 1),
        "change": round(predicted - current_pop, 1),
        "trend": trend,
        "confidence": confidence,
        "months": months_ahead,
        "momentum": history[-1]["momentum"],
    }


# ──────────────────────────────────────────────
# Worker Development Suggestions
# ──────────────────────────────────────────────

def suggest_development(roster: pd.DataFrame, top_n: int = 10) -> list[dict]:
    """
    Identifies workers with high skill ceiling but low popularity.
    These are the best candidates for a push.

    Factors:
    - High AvgSkill relative to Popularity → underexposed
    - Good Star Quality + Charisma → star potential
    - Young (low Experience) → room to grow
    - Good Consistency → reliable performer
    """
    suggestions = []
    for _, w in roster.iterrows():
        skill = _safe(w, "AvgSkill")
        pop = _safe(w, "Popularity")
        sq = _safe(w, "Star_Quality")
        charisma = _safe(w, "Charisma")
        exp = _safe(w, "Experience")
        consistency = _safe(w, "Consistency")
        momentum = _safe(w, "MomentumNum", 50)

        # Potential score: high skill + star quality + charisma, penalized by current popularity
        ceiling = (skill * 0.3 + sq * 0.25 + charisma * 0.2 + consistency * 0.15 + (100 - exp) * 0.1)
        gap = max(0, ceiling - pop)

        if gap < 10:
            continue

        # Determine suggestion type
        if skill >= 60 and pop < 30:
            suggestion = "🌟 Hidden Gem – High skill, very low exposure"
        elif sq >= 60 and pop < 50:
            suggestion = "⭐ Star Potential – Needs a spotlight push"
        elif charisma >= 60 and _safe(w, "Microphone") >= 50 and pop < 50:
            suggestion = "🎤 Promo Machine – Build around mic work"
        elif exp < 30 and skill >= 45:
            suggestion = "🌱 Future Star – Young talent with potential"
        elif momentum >= 65 and pop < 40:
            suggestion = "🔥 Hot Momentum – Strike while the iron is hot"
        else:
            suggestion = "📈 Push Candidate – Room to grow"

        suggestions.append({
            "Worker": w.get("WorkerName", "?"),
            "Popularity": round(pop, 1),
            "AvgSkill": round(skill, 1),
            "Ceiling": round(ceiling, 1),
            "Gap": round(gap, 1),
            "StarQuality": round(sq, 1),
            "Charisma": round(charisma, 1),
            "Momentum": w.get("Momentum", "Neutral"),
            "Suggestion": suggestion,
        })

    suggestions.sort(key=lambda x: x["Gap"], reverse=True)
    return suggestions[:top_n]


# ──────────────────────────────────────────────
# Angle Suggestions
# ──────────────────────────────────────────────

def suggest_angles(roster: pd.DataFrame) -> dict:
    """
    Suggests which workers are best suited for different angle types:
    - Promos (Microphone + Charisma)
    - Interviews (Charisma + Acting)
    - Run-ins / Attacks (Menace + Toughness)
    - Comedy spots (Acting + Charisma)
    - Authority figures (Respect + Microphone)
    - Managers (Charisma + Microphone)
    """

    def score_workers(cols_weights: list[tuple[str, float]], top_n=5):
        scores = []
        for _, w in roster.iterrows():
            s = sum(_safe(w, col) * weight for col, weight in cols_weights)
            scores.append((w.get("WorkerName", "?"), round(s, 1)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]

    return {
        "🎤 Promos": score_workers([("Microphone", 0.5), ("Charisma", 0.3), ("Star_Quality", 0.2)]),
        "🎙️ Interviews": score_workers([("Charisma", 0.4), ("Acting", 0.3), ("Microphone", 0.3)]),
        "💥 Run-ins / Attacks": score_workers([("Menace", 0.4), ("Toughness", 0.3), ("Star_Quality", 0.3)]),
        "😄 Comedy Segments": score_workers([("Acting", 0.5), ("Charisma", 0.3), ("Microphone", 0.2)]),
        "👔 Authority Figure": score_workers([("Respect", 0.4), ("Microphone", 0.3), ("Charisma", 0.3)]),
        "🤝 Manager Role": score_workers([("Charisma", 0.4), ("Microphone", 0.35), ("Acting", 0.25)]),
    }


# ──────────────────────────────────────────────
# Title Reign Tracker
# ──────────────────────────────────────────────

def analyze_title_reigns(title_belts: pd.DataFrame) -> list[dict]:
    """
    Analyzes current title reigns from the Title_Belts table.
    Extracts: champion, belt, defences, reign began, reign length estimation.
    """
    if title_belts is None or title_belts.empty:
        return []

    reigns = []
    for _, belt in title_belts.iterrows():
        if not belt.get("Active", False):
            continue

        holders = []
        for h in ["HolderName1", "HolderName2", "HolderName3"]:
            name = belt.get(h)
            if name and str(name) != "None" and str(name).strip():
                holders.append(str(name))

        holder_str = " & ".join(holders) if holders else "Vacant"

        defences = int(belt.get("Defences", 0))
        prestige = int(belt.get("Prestige", 0))
        reign_began = str(belt.get("Reign_Began", "Unknown"))
        last_defence = str(belt.get("Last_Defence", "N/A"))

        # Title health assessment
        if prestige >= 80:
            title_status = "🏆 Prestigious"
        elif prestige >= 50:
            title_status = "✅ Healthy"
        elif prestige >= 25:
            title_status = "⚠️ Declining"
        else:
            title_status = "❌ Worthless"

        reigns.append({
            "Belt": belt.get("Name", "Unknown"),
            "Champion": holder_str,
            "Prestige": prestige,
            "Defences": defences,
            "ReignBegan": reign_began,
            "LastDefence": last_defence,
            "Status": title_status,
        })

    return reigns


# ──────────────────────────────────────────────
# Touring Schedule Optimizer
# ──────────────────────────────────────────────

def optimize_touring(roster: pd.DataFrame, target_region: str = "", budget: float = 5000) -> list[dict]:
    """
    Suggests optimal workers for a touring show in a specific region.
    Ranks by: regional popularity vs cost (value for that specific region).
    """
    pop_col = f"Pop_{target_region}" if target_region else None

    results = []
    for _, w in roster.iterrows():
        # Get wrestler flag
        is_wrestler = False
        for col in ["C_Wrestler", "Wrestler"]:
            if col in w.index and w.get(col, False):
                is_wrestler = True
                break
        if not is_wrestler:
            continue

        wage = _safe(w, "Wage", 1)
        skill = _safe(w, "AvgSkill")
        name = w.get("WorkerName", "?")

        if pop_col and pop_col in w.index:
            regional_pop = _safe(w, pop_col)
        else:
            regional_pop = _safe(w, "Popularity")

        # Value = (RegionalPop * 0.6 + Skill * 0.4) / Wage
        value = (regional_pop * 0.6 + skill * 0.4) / max(wage, 1)

        results.append({
            "Worker": name,
            "RegionalPop": round(regional_pop, 1),
            "AvgSkill": round(skill, 1),
            "Wage": wage,
            "TouringValue": round(value, 3),
            "StarQuality": _safe(w, "Star_Quality"),
        })

    results.sort(key=lambda x: x["TouringValue"], reverse=True)

    # Mark who fits within budget
    running_cost = 0
    for r in results:
        running_cost += r["Wage"]
        r["CumulativeCost"] = running_cost
        r["WithinBudget"] = "✅" if running_cost <= budget else "❌"

    return results


# ──────────────────────────────────────────────
# Talent Trade Analyzer
# ──────────────────────────────────────────────

def calculate_worker_value(worker: pd.Series) -> dict:
    """
    Calculates a comprehensive value score for a worker.
    Used for trade comparisons.
    """
    skill = _safe(worker, "AvgSkill")
    pop = _safe(worker, "Popularity")
    sq = _safe(worker, "Star_Quality")
    charisma = _safe(worker, "Charisma")
    exp = _safe(worker, "Experience")
    consistency = _safe(worker, "Consistency")
    momentum_num = _safe(worker, "MomentumNum", 50)
    wage = _safe(worker, "Wage", 1)
    mic = _safe(worker, "Microphone")

    # Overall value (0-100 scale)
    in_ring_value = skill * 0.3
    star_value = (sq * 0.5 + charisma * 0.3 + mic * 0.2) * 0.25
    pop_value = pop * 0.2
    reliability = consistency * 0.1
    upside = max(0, (100 - exp) * 0.05) + max(0, (momentum_num - 50) * 0.1) * 0.1
    total_value = in_ring_value + star_value + pop_value + reliability + upside

    # Market value estimate ($)
    market_wage = total_value * 15

    return {
        "total_value": round(total_value, 1),
        "in_ring": round(in_ring_value / 0.3, 1),
        "star_power": round(star_value / 0.25, 1),
        "popularity": round(pop, 1),
        "reliability": round(consistency, 1),
        "market_wage": round(market_wage, 0),
        "current_wage": wage,
        "overpaid": wage > market_wage * 1.3,
        "underpaid": wage < market_wage * 0.7,
    }


def compare_trade(roster: pd.DataFrame, worker1_name: str, worker2_name: str) -> dict:
    """Compares two workers for a potential trade."""
    w1 = roster[roster["WorkerName"] == worker1_name]
    w2 = roster[roster["WorkerName"] == worker2_name]

    if w1.empty or w2.empty:
        return {"error": "Worker not found"}

    v1 = calculate_worker_value(w1.iloc[0])
    v2 = calculate_worker_value(w2.iloc[0])

    diff = v1["total_value"] - v2["total_value"]
    if abs(diff) < 5:
        verdict = "🤝 Fair Trade"
    elif diff > 0:
        verdict = f"⚠️ {worker1_name} is more valuable (+{diff:.1f})"
    else:
        verdict = f"⚠️ {worker2_name} is more valuable (+{abs(diff):.1f})"

    return {
        "worker1": {**v1, "name": worker1_name},
        "worker2": {**v2, "name": worker2_name},
        "value_diff": round(diff, 1),
        "verdict": verdict,
    }


# ──────────────────────────────────────────────
# Free Agent Scouting & Scoring
# ──────────────────────────────────────────────

def _safe(row, col, default=0):
    try:
        v = row.get(col, default) if isinstance(row, dict) else row[col]
        return float(v) if v and str(v) not in ("", "None", "nan") else default
    except (ValueError, TypeError, KeyError):
        return default


def score_free_agent_wrestler(row, home_region_pop_col: str = "British_Isles") -> dict:
    """
    Scores a free agent wrestler for signing potential.
    Returns dict with sub-scores and overall score.
    """
    in_ring = (
        _safe(row, "Brawling") + _safe(row, "Aerial") + _safe(row, "Technical") +
        _safe(row, "Power") + _safe(row, "Athleticism") + _safe(row, "Stamina") +
        _safe(row, "Psychology") + _safe(row, "Basics") + _safe(row, "Toughness") +
        _safe(row, "Selling")
    ) / 10

    star = (
        _safe(row, "Charisma") + _safe(row, "Microphone") +
        _safe(row, "Star_Quality") + _safe(row, "Looks")
    ) / 4

    pop = _safe(row, home_region_pop_col)
    safety = _safe(row, "Safety")
    consistency = _safe(row, "Consistency")
    exp = _safe(row, "Experience")

    # Overall composite: weighted scoring
    overall = (
        in_ring * 0.35 +
        star * 0.20 +
        pop * 0.20 +
        safety * 0.05 +
        consistency * 0.05 +
        exp * 0.05 +
        _safe(row, "Respect") * 0.05 +
        _safe(row, "Reputation") * 0.05
    )

    # Estimated wage based on popularity and skill
    est_wage = max(20, round(pop * 1.5 + in_ring * 0.8 + star * 0.5, 0))

    return {
        "Name": row.get("Name", "?") if isinstance(row, dict) else row["Name"],
        "InRing": round(in_ring, 1),
        "StarPower": round(star, 1),
        "Popularity": round(pop, 1),
        "Safety": round(safety, 1),
        "Experience": round(exp, 1),
        "Overall": round(overall, 1),
        "EstWage": est_wage,
        "Age": row.get("Age") if isinstance(row, dict) else row.get("Age", None),
        "Gender": row.get("Gender", "?") if isinstance(row, dict) else row["Gender"],
        "Based_In": row.get("Based_In", "?") if isinstance(row, dict) else row["Based_In"],
        "Freelance": row.get("Freelance", False) if isinstance(row, dict) else row["Freelance"],
    }


def score_free_agent_referee(row) -> dict:
    """Scores a free agent referee. Key stats: Refereeing, Experience, Reputation."""
    ref_skill = _safe(row, "Refereeing")
    exp = _safe(row, "Experience")
    rep = _safe(row, "Reputation")
    safety = _safe(row, "Safety")
    consistency = _safe(row, "Consistency")

    overall = (
        ref_skill * 0.45 +
        exp * 0.20 +
        rep * 0.15 +
        safety * 0.10 +
        consistency * 0.10
    )

    # Estimate cost: refs are cheap, scale by skill
    est_wage = max(10, round(ref_skill * 0.5 + exp * 0.2, 0))
    value = overall / max(est_wage, 1) * 10  # value per dollar

    return {
        "Name": row.get("Name", "?") if isinstance(row, dict) else row["Name"],
        "Refereeing": round(ref_skill, 1),
        "Experience": round(exp, 1),
        "Reputation": round(rep, 1),
        "Safety": round(safety, 1),
        "Overall": round(overall, 1),
        "EstWage": est_wage,
        "ValueRatio": round(value, 2),
        "Age": row.get("Age") if isinstance(row, dict) else row.get("Age", None),
        "Gender": row.get("Gender", "?") if isinstance(row, dict) else row["Gender"],
        "Based_In": row.get("Based_In", "?") if isinstance(row, dict) else row["Based_In"],
    }


def score_free_agent_road_agent(row) -> dict:
    """Scores a free agent road agent. Key stats: Psychology, Experience, Booking_Skill, Respect."""
    psych = _safe(row, "Psychology")
    exp = _safe(row, "Experience")
    booking = _safe(row, "Booking_Skill")
    respect = _safe(row, "Respect")
    rep = _safe(row, "Reputation")
    safety = _safe(row, "Safety")

    overall = (
        psych * 0.25 +
        exp * 0.20 +
        booking * 0.25 +
        respect * 0.15 +
        rep * 0.10 +
        safety * 0.05
    )

    est_wage = max(10, round(booking * 0.4 + exp * 0.3 + psych * 0.2, 0))
    value = overall / max(est_wage, 1) * 10

    return {
        "Name": row.get("Name", "?") if isinstance(row, dict) else row["Name"],
        "Psychology": round(psych, 1),
        "Experience": round(exp, 1),
        "Booking_Skill": round(booking, 1),
        "Respect": round(respect, 1),
        "Reputation": round(rep, 1),
        "Overall": round(overall, 1),
        "EstWage": est_wage,
        "ValueRatio": round(value, 2),
        "Age": row.get("Age") if isinstance(row, dict) else row.get("Age", None),
        "Gender": row.get("Gender", "?") if isinstance(row, dict) else row["Gender"],
        "Based_In": row.get("Based_In", "?") if isinstance(row, dict) else row["Based_In"],
    }
