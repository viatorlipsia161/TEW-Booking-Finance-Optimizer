"""
TEW Booking & Finance Optimizer – Calculation Engine
Show calculator, match quality prediction, staleness checks, budget analysis.
"""

import pandas as pd
import random
from dataclasses import dataclass, field
from itertools import combinations


# ──────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────

@dataclass
class ShowConfig:
    """Configuration for a show calculation."""
    ticket_revenue: float = 2200.0
    production_cost: float = 0.0
    road_agent_cost: float = 0.0
    referee_cost: float = 0.0
    other_staff_cost: float = 0.0
    venue_cost: float = 0.0


@dataclass
class MatchSlot:
    """A single match on the card."""
    worker_uids: list = field(default_factory=list)
    worker_names: list = field(default_factory=list)
    wages: list = field(default_factory=list)
    match_type: str = "Singles"

    @property
    def total_wage(self) -> float:
        return sum(self.wages)

    @property
    def label(self) -> str:
        return " vs ".join(self.worker_names)


@dataclass
class ShowResult:
    """Result of a show calculation."""
    matches: list
    total_talent_cost: float
    total_staff_cost: float
    production_cost: float
    venue_cost: float
    ticket_revenue: float

    @property
    def total_cost(self) -> float:
        return self.total_talent_cost + self.total_staff_cost + self.production_cost + self.venue_cost

    @property
    def profit(self) -> float:
        return self.ticket_revenue - self.total_cost

    @property
    def is_profitable(self) -> bool:
        return self.profit > 0

    @property
    def staff_ratio(self) -> float:
        if self.total_cost == 0:
            return 0
        return self.total_staff_cost / self.total_cost

    @property
    def staff_warning(self) -> bool:
        """Ospreay Warning: staff costs > 15% of budget."""
        return self.staff_ratio > 0.15


# ──────────────────────────────────────────────
# Show Calculation
# ──────────────────────────────────────────────

def calculate_show(matches: list[MatchSlot], config: ShowConfig) -> ShowResult:
    """Calculates the complete show financials."""
    total_talent = sum(m.total_wage for m in matches)
    total_staff = config.road_agent_cost + config.referee_cost + config.other_staff_cost

    return ShowResult(
        matches=matches,
        total_talent_cost=total_talent,
        total_staff_cost=total_staff,
        production_cost=config.production_cost,
        venue_cost=config.venue_cost,
        ticket_revenue=config.ticket_revenue,
    )


# ──────────────────────────────────────────────
# Staleness
# ──────────────────────────────────────────────

def check_staleness(
    worker1_uid: int,
    worker2_uid: int,
    staleness_df: pd.DataFrame,
    threshold: int = 3,
) -> dict:
    """Checks if a pairing is 'stale' (>= threshold times)."""
    if staleness_df.empty:
        return {"is_stale": False, "count": 0, "warning_message": ""}

    pair = tuple(sorted([worker1_uid, worker2_uid]))
    col1 = "WorkerUID1" if "WorkerUID1" in staleness_df.columns else staleness_df.columns[0]
    col2 = "WorkerUID2" if "WorkerUID2" in staleness_df.columns else staleness_df.columns[1]

    mask = (staleness_df[col1] == pair[0]) & (staleness_df[col2] == pair[1])
    matches = staleness_df[mask]

    count = 0
    if not matches.empty:
        count = int(matches["Count"].iloc[0]) if "Count" in staleness_df.columns else len(matches)

    is_stale = count >= threshold
    warning = f"⚠️ STALE MATCH: This pairing has happened {count}x already!" if is_stale else ""

    return {"is_stale": is_stale, "count": count, "warning_message": warning}


def _get_staleness_count(w1_uid: int, w2_uid: int, staleness_df: pd.DataFrame) -> int:
    """Helper: gets staleness count for a worker pair."""
    if staleness_df is None or staleness_df.empty:
        return 0
    pair = tuple(sorted([w1_uid, w2_uid]))
    col1 = "WorkerUID1" if "WorkerUID1" in staleness_df.columns else staleness_df.columns[0]
    col2 = "WorkerUID2" if "WorkerUID2" in staleness_df.columns else staleness_df.columns[1]
    mask = (staleness_df[col1] == pair[0]) & (staleness_df[col2] == pair[1])
    if mask.any() and "Count" in staleness_df.columns:
        return int(staleness_df.loc[mask, "Count"].iloc[0])
    return 0


# ──────────────────────────────────────────────
# Efficiency Ranking
# ──────────────────────────────────────────────

def calculate_efficiency_ranking(roster: pd.DataFrame) -> pd.DataFrame:
    """Sorts roster by Efficiency Score and adds ranking categories."""
    df = roster.copy()
    if "EfficiencyScore" not in df.columns:
        return df

    df = df.sort_values("EfficiencyScore", ascending=False).reset_index(drop=True)
    df["Rank"] = range(1, len(df) + 1)

    def categorize(score):
        if score > 2.0:
            return "💎 Elite Value"
        elif score > 1.0:
            return "✅ Good Value"
        elif score > 0.5:
            return "⚠️ Overpaid"
        else:
            return "🔴 Bad Deal"

    df["ValueCategory"] = df["EfficiencyScore"].apply(categorize)
    return df


# ──────────────────────────────────────────────
# Match Quality Prediction
# ──────────────────────────────────────────────

SKILL_COLS = ["Brawling", "Technical", "Aerial", "Puroresu", "Flashiness",
              "Selling", "Basics", "Psychology"]


def _safe_val(series: pd.Series, col: str, default: float = 50.0) -> float:
    return float(series.get(col, default)) if col in series.index else default


def _calc_base_and_bonuses(workers: list[pd.Series]) -> tuple[float, float, float, float, float, float]:
    """
    Core rating calculation shared between singles and tag team.
    Returns: (base_rating, psych_bonus, sell_bonus, star_bonus, consistency_range, avg_skill)
    """
    n = len(workers)
    all_avgs = []
    psych_total = sell_total = sq_total = charisma_total = consistency_total = 0

    for w in workers:
        skills = [_safe_val(w, c) for c in SKILL_COLS]
        all_avgs.append(sum(skills) / len(skills))
        psych_total += _safe_val(w, "Psychology")
        sell_total += _safe_val(w, "Selling")
        sq_total += _safe_val(w, "Star_Quality")
        charisma_total += _safe_val(w, "Charisma")
        consistency_total += _safe_val(w, "Consistency")

    base_rating = sum(all_avgs) / n
    psych_bonus = (psych_total / n - 50) * 0.2
    sell_bonus = (sell_total / n - 50) * 0.1
    star_bonus = ((sq_total / n + charisma_total / n) / 2 - 50) * 0.15
    consistency_range = max(0, (100 - consistency_total / n) * 0.15)

    return base_rating, psych_bonus, sell_bonus, star_bonus, consistency_range, sum(all_avgs) / n


def _rating_to_grade(rating: float) -> str:
    if rating >= 80: return "A+"
    if rating >= 70: return "A"
    if rating >= 60: return "B+"
    if rating >= 50: return "B"
    if rating >= 40: return "C+"
    if rating >= 30: return "C"
    return "D"


def predict_match_quality(
    worker1: pd.Series,
    worker2: pd.Series,
    staleness_count: int = 0,
) -> dict:
    """
    Predicts singles match quality based on worker skills.

    Factors: base skills, psychology, selling, star quality/charisma, staleness, consistency.
    """
    base, psych, sell, star, cons_range, _ = _calc_base_and_bonuses([worker1, worker2])
    stale_malus = min(staleness_count * 3, 15)

    predicted = max(0, min(100, base + psych + sell + star - stale_malus))
    grade = _rating_to_grade(predicted)

    return {
        "predicted_rating": round(predicted, 1),
        "grade": grade,
        "base_rating": round(base, 1),
        "psych_bonus": round(psych, 1),
        "sell_bonus": round(sell, 1),
        "star_bonus": round(star, 1),
        "stale_malus": stale_malus,
        "consistency_range": round(cons_range, 1),
        "rating_range": f"{max(0, predicted - cons_range):.0f}–{min(100, predicted + cons_range):.0f}",
    }


def predict_tag_match_quality(
    team1: list[pd.Series],
    team2: list[pd.Series],
    staleness_count: int = 0,
) -> dict:
    """
    Predicts tag team match quality.
    Additional factors: team chemistry (similar styles boost), weakest link penalty.
    """
    all_workers = team1 + team2
    base, psych, sell, star, cons_range, _ = _calc_base_and_bonuses(all_workers)

    # Tag team bonus: if team members have similar styles, +bonus
    def team_synergy(team):
        if len(team) < 2:
            return 0
        avgs = []
        for w in team:
            skills = [_safe_val(w, c) for c in SKILL_COLS]
            avgs.append(sum(skills) / len(skills))
        # Smaller gap = better synergy
        gap = abs(avgs[0] - avgs[1]) if len(avgs) == 2 else max(avgs) - min(avgs)
        return max(0, (30 - gap) * 0.1)

    synergy_bonus = (team_synergy(team1) + team_synergy(team2)) / 2

    # Weakest link penalty: worst worker drags down the match
    all_avgs = []
    for w in all_workers:
        skills = [_safe_val(w, c) for c in SKILL_COLS]
        all_avgs.append(sum(skills) / len(skills))
    weakest = min(all_avgs)
    weakest_penalty = max(0, (40 - weakest) * 0.15)

    stale_malus = min(staleness_count * 3, 15)

    predicted = base + psych + sell + star + synergy_bonus - weakest_penalty - stale_malus
    predicted = max(0, min(100, predicted))
    grade = _rating_to_grade(predicted)

    return {
        "predicted_rating": round(predicted, 1),
        "grade": grade,
        "base_rating": round(base, 1),
        "synergy_bonus": round(synergy_bonus, 1),
        "weakest_penalty": round(weakest_penalty, 1),
        "stale_malus": stale_malus,
        "consistency_range": round(cons_range, 1),
        "rating_range": f"{max(0, predicted - cons_range):.0f}–{min(100, predicted + cons_range):.0f}",
    }


# ──────────────────────────────────────────────
# Auto-Suggest Matches (with Variety)
# ──────────────────────────────────────────────

def suggest_best_matches(
    roster: pd.DataFrame,
    staleness_df: pd.DataFrame = None,
    top_n: int = 10,
    variety: bool = True,
) -> list[dict]:
    """
    Generates automatic match suggestions based on predicted quality.
    When variety=True, uses weighted random sampling from top matches
    to ensure different suggestions each time instead of always the same top-N.
    """
    # Filter to wrestlers only
    wrestler_col = None
    for col in ["C_Wrestler", "Wrestler"]:
        if col in roster.columns:
            wrestler_col = col
            break

    if wrestler_col:
        wrestlers = roster[roster[wrestler_col] == True].copy()
    else:
        wrestlers = roster[roster["AvgSkill"] > 0].copy()

    if wrestlers.empty:
        wrestlers = roster[roster["AvgSkill"] > 0].copy()

    if len(wrestlers) < 2:
        return []

    # Calculate all possible pairings
    all_suggestions = []
    for idx1, idx2 in combinations(wrestlers.index, 2):
        w1 = wrestlers.loc[idx1]
        w2 = wrestlers.loc[idx2]

        stale_count = _get_staleness_count(
            int(w1.get("WorkerUID", 0)), int(w2.get("WorkerUID", 0)), staleness_df
        )

        pred = predict_match_quality(w1, w2, stale_count)
        all_suggestions.append({
            "Worker1": w1.get("WorkerName", "?"),
            "Worker2": w2.get("WorkerName", "?"),
            "Worker1UID": int(w1.get("WorkerUID", 0)),
            "Worker2UID": int(w2.get("WorkerUID", 0)),
            "PredictedRating": pred["predicted_rating"],
            "Grade": pred["grade"],
            "Range": pred["rating_range"],
            "Staleness": stale_count,
            "TotalWage": float(w1.get("Wage", 0)) + float(w2.get("Wage", 0)),
        })

    if not all_suggestions:
        return []

    if variety and len(all_suggestions) > top_n:
        # Take top 50% of matches, then randomly sample from them
        # ensuring variety while maintaining quality
        all_suggestions.sort(key=lambda x: x["PredictedRating"], reverse=True)
        pool_size = max(top_n * 3, len(all_suggestions) // 2)
        pool = all_suggestions[:pool_size]

        # Weighted random: higher rated matches more likely to be picked
        weights = [s["PredictedRating"] ** 2 for s in pool]
        total_w = sum(weights)
        if total_w > 0:
            weights = [w / total_w for w in weights]

        # Ensure unique workers in suggestions for card variety
        selected = []
        used_workers = set()
        attempts = 0
        max_attempts = pool_size * 3

        while len(selected) < top_n and attempts < max_attempts:
            pick = random.choices(pool, weights=weights, k=1)[0]
            attempts += 1

            # Enforce unique workers: no wrestler appears in two matches
            if pick["Worker1UID"] in used_workers or pick["Worker2UID"] in used_workers:
                continue

            if pick not in selected:
                selected.append(pick)
                used_workers.add(pick["Worker1UID"])
                used_workers.add(pick["Worker2UID"])

        # Fill remaining if needed (still enforce uniqueness)
        if len(selected) < top_n:
            for s in pool:
                if s not in selected and s["Worker1UID"] not in used_workers and s["Worker2UID"] not in used_workers:
                    selected.append(s)
                    used_workers.add(s["Worker1UID"])
                    used_workers.add(s["Worker2UID"])
                if len(selected) >= top_n:
                    break

        selected.sort(key=lambda x: x["PredictedRating"], reverse=True)
        return selected[:top_n]
    else:
        all_suggestions.sort(key=lambda x: x["PredictedRating"], reverse=True)
        # Still enforce unique workers even without variety randomization
        unique_selected = []
        used = set()
        for s in all_suggestions:
            if s["Worker1UID"] not in used and s["Worker2UID"] not in used:
                unique_selected.append(s)
                used.add(s["Worker1UID"])
                used.add(s["Worker2UID"])
            if len(unique_selected) >= top_n:
                break
        return unique_selected


# ──────────────────────────────────────────────
# Budget Analysis
# ──────────────────────────────────────────────

def budget_analysis(roster: pd.DataFrame, config: ShowConfig) -> dict:
    """Analyzes the overall promotion budget."""
    total_roster_cost = roster["Wage"].sum() if "Wage" in roster.columns else 0
    staff_cost = config.road_agent_cost + config.referee_cost + config.other_staff_cost
    total_monthly = total_roster_cost + staff_cost + config.production_cost

    shows_per_month = 4
    monthly_revenue = config.ticket_revenue * shows_per_month
    monthly_profit = monthly_revenue - total_monthly

    return {
        "total_roster_cost": total_roster_cost,
        "staff_cost": staff_cost,
        "production_cost": config.production_cost,
        "total_monthly_cost": total_monthly,
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_profit,
        "is_profitable": monthly_profit > 0,
        "avg_wage": roster["Wage"].mean() if "Wage" in roster.columns else 0,
        "roster_size": len(roster),
    }
