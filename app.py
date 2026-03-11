"""
TEW Booking & Finance Optimizer v4.0
Streamlit Dashboard – Universal for all promotions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from pathlib import Path

from db_reader import (
    build_roster,
    get_staleness,
    get_title_belts,
    get_show_defaults,
    get_previous_shows,
    get_financial_histories,
    get_contracts_detailed,
    get_match_histories,
    get_match_participants,
    get_free_agents,
    detect_table_structure,
    MACRO_REGIONS,
    BASED_IN_GROUPS,
)
from calculator import (
    ShowConfig,
    MatchSlot,
    ShowResult,
    calculate_show,
    check_staleness,
    calculate_efficiency_ranking,
    budget_analysis,
    predict_match_quality,
    predict_tag_match_quality,
    suggest_best_matches,
    SKILL_COLS,
)
from config_store import (
    load_config, save_config,
    save_momentum_snapshot, load_momentum_history,
    save_card_template, load_card_templates, delete_card_template,
    get_latest_mdb,
    load_storylines, add_storyline, update_storyline,
    add_storyline_event, delete_storyline,
    load_events, add_event, update_event, delete_event,
    create_backup, list_backups,
    generate_show_card_pdf,
)
from analytics import (
    detect_chemistry,
    analyze_roster_health,
    forecast_popularity,
    suggest_development,
    suggest_angles,
    analyze_title_reigns,
    optimize_touring,
    calculate_worker_value,
    compare_trade,
    score_free_agent_wrestler,
    score_free_agent_referee,
    score_free_agent_road_agent,
)

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="TEW Booking & Finance Optimizer",
    page_icon="🤼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom Dark Theme CSS
# ──────────────────────────────────────────────
st.markdown("""<style>
.stApp { background-color: #0e1117; color: #e0e0e0; }
[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
.metric-card { background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%); border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin: 8px 0; text-align: center; }
.metric-card h3 { color: #8b949e; font-size: 0.85rem; margin-bottom: 4px; font-weight: 400; }
.metric-card .value { font-size: 1.8rem; font-weight: 700; }
.metric-card .positive { color: #3fb950; } .metric-card .negative { color: #f85149; } .metric-card .neutral { color: #58a6ff; }
.warning-box { background-color: #2d1b00; border: 1px solid #d29922; border-radius: 8px; padding: 12px 16px; margin: 8px 0; color: #e3b341; }
.stale-warning { background-color: #3d0e0e; border: 1px solid #f85149; border-radius: 8px; padding: 12px 16px; margin: 8px 0; color: #f85149; }
.success-box { background-color: #0d2818; border: 1px solid #3fb950; border-radius: 8px; padding: 12px 16px; margin: 8px 0; color: #3fb950; }
.main-header { text-align: center; padding: 10px 0 20px 0; }
.main-header h1 { background: linear-gradient(90deg, #58a6ff, #bc8cff, #f778ba); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; font-weight: 800; }
.dataframe { font-size: 0.85rem; }
.stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
.nav-header { color: #8b949e; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px; margin-bottom: -6px; padding-left: 4px; font-weight: 600; }
[data-testid="stSidebar"] button[kind="secondary"] { background: transparent; border: 1px solid #30363d; color: #c9d1d9; padding: 4px 8px; font-size: 0.82rem; margin: 1px 0; text-align: left; justify-content: flex-start; }
[data-testid="stSidebar"] button[kind="secondary"]:hover { background: #1a1f2e; border-color: #58a6ff; color: #58a6ff; }
[data-testid="stSidebar"] button[kind="primary"] { padding: 4px 8px; font-size: 0.82rem; margin: 1px 0; text-align: left; justify-content: flex-start; }
.champ-card { background: #1a1f2e; border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; margin: 4px 0; }
.champ-card .belt { color: #d29922; font-weight: 700; font-size: 0.85rem; }
.champ-card .holder { color: #e0e0e0; font-size: 0.95rem; }
.top5-item { background: #1a1f2e; border: 1px solid #30363d; border-radius: 6px; padding: 6px 10px; margin: 3px 0; display: flex; justify-content: space-between; }
.top5-item .name { color: #e0e0e0; } .top5-item .score { color: #58a6ff; font-weight: 700; }
.quality-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: 0.9rem; }
.grade-a { background: #0d2818; color: #3fb950; border: 1px solid #3fb950; }
.grade-b { background: #1a1f2e; color: #58a6ff; border: 1px solid #58a6ff; }
.grade-c { background: #2d1b00; color: #d29922; border: 1px solid #d29922; }
.grade-d { background: #3d0e0e; color: #f85149; border: 1px solid #f85149; }
</style>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def metric_card(title: str, value: str, style: str = "neutral") -> str:
    return f'<div class="metric-card"><h3>{title}</h3><div class="value {style}">{value}</div></div>'

def grade_badge(grade: str) -> str:
    css = "grade-a" if grade.startswith("A") else "grade-b" if grade.startswith("B") else "grade-c" if grade.startswith("C") else "grade-d"
    return f'<span class="quality-badge {css}">{grade}</span>'

DARK_LAYOUT = dict(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="#e0e0e0")

def make_radar(worker_row: pd.Series, name: str) -> go.Scatterpolar:
    """Creates a radar trace for a single worker."""
    vals = [float(worker_row.get(c, 0)) for c in SKILL_COLS] + [float(worker_row.get(SKILL_COLS[0], 0))]
    labels = [c.replace("_", " ") for c in SKILL_COLS] + [SKILL_COLS[0].replace("_", " ")]
    return go.Scatterpolar(r=vals, theta=labels, fill="toself", name=name)

# ──────────────────────────────────────────────
# Load persistent config
# ──────────────────────────────────────────────
saved_cfg = load_config()

for key, default in [("mdb_path", saved_cfg.get("mdb_path", "")),
                     ("promotion", saved_cfg.get("promotion", "")),
                     ("roster", None), ("staleness", None), ("title_belts", None),
                     ("show_defaults", None), ("card_matches", []),
                     ("show_config", ShowConfig()),
                     ("notes", saved_cfg.get("notes", "")),
                     ("free_agents_df", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤼 TEW Optimizer")

    mdb_path = st.text_input("Path to TEW .mdb file", value=st.session_state.mdb_path,
                             placeholder=r"G:\TEW9\...\SaveGame.mdb")
    promotion = st.text_input("Promotion Abbreviation", value=st.session_state.promotion,
                              placeholder="e.g. EVE, WWE, AEW ...",
                              help="Must appear in the CompanyName in the DB.")

    # Auto-reload detection
    if st.session_state.mdb_path:
        newer = get_latest_mdb(st.session_state.mdb_path)
        if newer:
            st.markdown(f'<div class="warning-box">📂 Newer save found:<br><code>{Path(newer).name}</code></div>',
                        unsafe_allow_html=True)
            if st.button("🔄 Load newer save", use_container_width=True):
                mdb_path = newer
                st.session_state.mdb_path = newer

    if st.button("🔌 Connect Database", use_container_width=True):
        if mdb_path and promotion:
            try:
                with st.spinner("Connecting..."):
                    st.session_state.mdb_path = mdb_path
                    st.session_state.promotion = promotion
                    roster = build_roster(mdb_path, promotion)
                    roster = calculate_efficiency_ranking(roster)
                    st.session_state.roster = roster
                    st.session_state.staleness = get_staleness(mdb_path, promotion)
                    st.session_state.title_belts = get_title_belts(mdb_path, promotion)
                    sd = get_show_defaults(mdb_path, promotion)
                    st.session_state.show_defaults = sd
                    if sd["estimated_revenue"] > 0:
                        st.session_state.show_config.ticket_revenue = float(sd["estimated_revenue"])
                    st.session_state.free_agents_df = None  # reset so it reloads
                    save_config({"mdb_path": mdb_path, "promotion": promotion, "notes": st.session_state.notes})
                    # Momentum snapshot
                    save_momentum_snapshot(roster, mdb_path)
                st.success(f"✅ {len(roster)} workers loaded!")
            except FileNotFoundError:
                st.error("❌ MDB file not found!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter MDB path and promotion abbreviation.")

    # ── Navigation ──
    st.markdown("---")
    PAGE_OPTIONS = {
        "📋 Booking": [
            "📋 Roster", "🎤 Show Calculator", "🔀 Worker Compare",
            "📄 Contracts", "💰 Budget",
        ],
        "📈 Analytics": [
            "📈 Financials", "📊 Push Tracking", "🔄 Staleness",
            "🧪 Chemistry", "🏥 Roster Health", "🔮 Forecast",
        ],
        "🌟 Creative": [
            "📖 Storylines", "📅 Event Planner", "🌟 Development",
            "🎭 Angles", "🏆 Titles",
        ],
        "🔍 Scouting": [
            "🔥 Free Agents", "🧑‍⚖️ Staff Scout",
            "🌍 Touring", "🔄 Trade",
        ],
        "⚙️ System": [
            "⚙️ Tools",
        ],
    }
    all_pages = []
    for cat, pages in PAGE_OPTIONS.items():
        all_pages.extend(pages)

    # Build formatted options with category headers
    if "current_page" not in st.session_state:
        st.session_state.current_page = "📋 Roster"

    for cat, pages in PAGE_OPTIONS.items():
        st.markdown(f'<div class="nav-header">{cat}</div>', unsafe_allow_html=True)
        for p in pages:
            btn_type = "primary" if st.session_state.current_page == p else "secondary"
            if st.button(p, key=f"nav_{p}", use_container_width=True, type=btn_type):
                st.session_state.current_page = p
                st.rerun()

    # Champions
    if st.session_state.title_belts is not None and not st.session_state.title_belts.empty:
        st.markdown("---")
        st.markdown("### 🏆 Champions")
        for _, belt in st.session_state.title_belts.iterrows():
            if not belt.get("Active", False):
                continue
            holders = [str(belt.get(h)) for h in ["HolderName1", "HolderName2", "HolderName3"]
                       if belt.get(h) and str(belt.get(h)) != "None" and str(belt.get(h)).strip()]
            holder_str = " & ".join(holders) if holders else "Vacant"
            st.markdown(f'<div class="champ-card"><div class="belt">🥇 {belt["Name"]}</div>'
                        f'<div class="holder">{holder_str}</div></div>', unsafe_allow_html=True)

    # Top 5
    if st.session_state.roster is not None:
        st.markdown("---")
        st.markdown("### ⭐ Top 5 Workers")
        for _, w in st.session_state.roster.head(5).iterrows():
            st.markdown(f'<div class="top5-item"><span class="name">{w.get("Rank","")}) {w["WorkerName"]}</span>'
                        f'<span class="score">{w["EfficiencyScore"]:.2f}</span></div>', unsafe_allow_html=True)

    # Company Info
    if st.session_state.show_defaults:
        sd = st.session_state.show_defaults
        st.markdown("---")
        st.markdown("### 🏢 Company")
        st.markdown(f"**Size:** {sd['company_size']}  \n**Prestige:** {sd['company_prestige']}  \n"
                    f"**Budget:** ${sd['company_money']:,}")
        if sd["avg_attendance"] > 0:
            st.markdown(f"**Avg Attendance:** {sd['avg_attendance']}")

    # Show Settings
    with st.expander("⚙️ Show Settings", expanded=False):
        config = st.session_state.show_config
        config.ticket_revenue = st.number_input("Ticket Revenue ($)", value=config.ticket_revenue, step=100.0, min_value=0.0)
        config.production_cost = st.number_input("Production Cost ($)", value=config.production_cost, step=50.0, min_value=0.0)
        config.road_agent_cost = st.number_input("Road Agent Cost ($)", value=config.road_agent_cost, step=25.0, min_value=0.0)
        config.referee_cost = st.number_input("Referee Cost ($)", value=config.referee_cost, step=25.0, min_value=0.0)
        config.other_staff_cost = st.number_input("Other Staff Cost ($)", value=config.other_staff_cost, step=25.0, min_value=0.0)
        config.venue_cost = st.number_input("Venue Cost ($)", value=config.venue_cost, step=50.0, min_value=0.0)
        st.session_state.show_config = config

# ──────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────
st.markdown('<div class="main-header"><h1>🤼 TEW Booking & Finance Optimizer</h1></div>', unsafe_allow_html=True)

if st.session_state.roster is None:
    st.markdown('<div style="text-align:center; padding:60px 20px;"><h2 style="color:#8b949e;">Welcome!</h2>'
                '<p style="color:#8b949e; font-size:1.1rem;">Connect your TEW database via the sidebar.<br>'
                'Enter the path to your <code>.mdb</code> file and the <strong>Promotion Abbreviation</strong>.</p></div>',
                unsafe_allow_html=True)
    st.stop()

roster = st.session_state.roster
config = st.session_state.show_config
staleness_df = st.session_state.staleness
worker_names = roster["WorkerName"].tolist() if "WorkerName" in roster.columns else []

# Notes
with st.expander("📝 Notes", expanded=False):
    new_notes = st.text_area("Your booking notes (auto-saved)", value=st.session_state.notes,
                             height=150, key="notes_input", placeholder="Storyline ideas, booking plans...")
    if new_notes != st.session_state.notes:
        st.session_state.notes = new_notes
        save_config({"mdb_path": st.session_state.mdb_path, "promotion": st.session_state.promotion, "notes": new_notes})

# ──────────────────────────────────────────────
# Page Router
# ──────────────────────────────────────────────
page = st.session_state.current_page

# ═══════════════════════════════════════════════
# TAB: Roster & Efficiency
# ═══════════════════════════════════════════════
if page == "📋 Roster":
    home_region = roster.attrs.get("home_region", "")
    macro_region = roster.attrs.get("macro_region", "")
    if home_region:
        st.markdown(f'<div class="success-box">🏠 Home Region: <strong>{home_region}</strong> ({macro_region}) — '
                    f'Popularity = regional popularity in {home_region}</div>', unsafe_allow_html=True)

    st.markdown("### Roster by Efficiency Score")

    display_cols = [c for c in ["Rank", "WorkerName", "GimmickName", "Popularity", "Star_Quality",
                                "Momentum", "Looks", "AvgSkill", "Wage", "Pop_USA", "Pop_UK",
                                "Pop_Japan", "Pop_Europe", "EfficiencyScore", "ValueCategory"]
                    if c in roster.columns] or roster.columns.tolist()[:10]

    display_df = roster[display_cols].copy()
    if "EfficiencyScore" in display_df.columns: display_df["EfficiencyScore"] = display_df["EfficiencyScore"].round(3)
    if "AvgSkill" in display_df.columns: display_df["AvgSkill"] = display_df["AvgSkill"].round(1)
    for pc in ["Pop_USA", "Pop_UK", "Pop_Japan", "Pop_Europe"]:
        if pc in display_df.columns: display_df[pc] = display_df[pc].round(1)
    if "Wage" in display_df.columns: display_df["Wage"] = display_df["Wage"].apply(lambda x: f"${x:,.0f}")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card("Roster Size", str(len(roster)), "neutral"), unsafe_allow_html=True)
    with c2:
        avg_pop = roster["Popularity"].mean() if "Popularity" in roster.columns else 0
        st.markdown(metric_card(f"Avg Pop ({home_region})", f"{avg_pop:.1f}", "neutral"), unsafe_allow_html=True)
    with c3:
        tw = roster["Wage"].sum() if "Wage" in roster.columns else 0
        st.markdown(metric_card("Total Wage Cost", f"${tw:,.0f}", "negative"), unsafe_allow_html=True)
    with c4:
        ae = roster["EfficiencyScore"].mean() if "EfficiencyScore" in roster.columns else 0
        st.markdown(metric_card("Avg Efficiency", f"{ae:.2f}", "positive"), unsafe_allow_html=True)

    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

    # Export
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        csv = roster[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export Roster CSV", csv, "roster.csv", "text/csv")

    # Efficiency chart
    if "WorkerName" in roster.columns and "EfficiencyScore" in roster.columns:
        st.markdown("### Efficiency Score Distribution")
        chart_df = roster[["WorkerName", "EfficiencyScore"]].head(20).copy()
        fig = px.bar(chart_df, x="WorkerName", y="EfficiencyScore", color="EfficiencyScore",
                     color_continuous_scale=["#f85149", "#d29922", "#3fb950", "#58a6ff"],
                     title="Top 20 Workers by Efficiency Score")
        fig.update_layout(**DARK_LAYOUT, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Regional popularity heatmap
    pop_cols = [c for c in roster.columns if c.startswith("Pop_")]
    if pop_cols and "WorkerName" in roster.columns:
        st.markdown("### Regional Popularity")
        pop_df = roster[["WorkerName"] + pop_cols].copy().set_index("WorkerName")
        pop_df = pop_df.sort_values(pop_cols[0], ascending=False)
        fig = px.imshow(pop_df.values, x=[c.replace("Pop_", "") for c in pop_cols], y=pop_df.index.tolist(),
                        color_continuous_scale=["#0e1117", "#1a1f2e", "#d29922", "#3fb950", "#58a6ff"],
                        title="Popularity by Region (0–100)", aspect="auto")
        fig.update_layout(**DARK_LAYOUT, height=max(400, len(roster) * 22))
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB: Show Calculator
# ═══════════════════════════════════════════════
if page == "🎤 Show Calculator":
    st.markdown("### 🎤 Build Show Card")

    # Card Templates
    with st.expander("💾 Card Templates", expanded=False):
        templates = load_card_templates()
        tc1, tc2 = st.columns(2)
        with tc1:
            tpl_name = st.text_input("Template name", placeholder="Standard Show", key="tpl_name")
            if st.button("Save current card", key="btn_save_tpl") and tpl_name:
                # Gather current card from session
                matches_data = []
                for i in range(st.session_state.get("num_matches_val", 5)):
                    w1k = st.session_state.get(f"match_{i}_w1", "-- Select --")
                    w2k = st.session_state.get(f"match_{i}_w2", "-- Select --")
                    mtk = st.session_state.get(f"match_{i}_type", "Singles")
                    if w1k != "-- Select --" and w2k != "-- Select --":
                        matches_data.append({"worker1": w1k, "worker2": w2k, "match_type": mtk})
                if matches_data:
                    save_card_template(tpl_name, matches_data)
                    st.success(f"Saved '{tpl_name}' ({len(matches_data)} matches)")
                else:
                    st.warning("No matches to save.")
        with tc2:
            if templates:
                tpl_names = [t["name"] for t in templates]
                sel_tpl = st.selectbox("Load template", ["-- Select --"] + tpl_names, key="sel_tpl")
                if sel_tpl != "-- Select --":
                    st.info(f"Template '{sel_tpl}' selected. Set matches manually based on the template below.")
                    tpl = next((t for t in templates if t["name"] == sel_tpl), None)
                    if tpl:
                        for j, m in enumerate(tpl.get("matches", [])):
                            st.caption(f"Match {j+1}: {m['worker1']} vs {m['worker2']} ({m['match_type']})")

    # Auto-suggestions
    with st.expander("🤖 Auto Match Suggestions", expanded=False):
        n_sug = st.slider("Number of suggestions", 5, 30, 10, key="n_suggest")
        if st.button("Generate suggestions", key="btn_suggest"):
            with st.spinner("Calculating best pairings..."):
                suggestions = suggest_best_matches(roster, staleness_df, top_n=n_sug, variety=True)
                if suggestions:
                    sug_df = pd.DataFrame(suggestions).rename(columns={
                        "Worker1": "Worker 1", "Worker2": "Worker 2",
                        "PredictedRating": "Rating", "TotalWage": "Cost"})
                    st.dataframe(sug_df[["Worker 1", "Worker 2", "Grade", "Rating", "Range", "Staleness", "Cost"]],
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("Not enough wrestlers for suggestions.")

    st.markdown("---")
    num_matches = st.slider("Number of matches", 1, 10, 5, key="num_matches_val")
    card_matches = []
    total_pred = []

    for i in range(num_matches):
        st.markdown(f"**Match {i + 1}**")
        cols = st.columns([2, 2, 1, 1])
        with cols[0]: w1 = st.selectbox("Worker 1", ["-- Select --"] + worker_names, key=f"match_{i}_w1")
        with cols[1]: w2 = st.selectbox("Worker 2", ["-- Select --"] + worker_names, key=f"match_{i}_w2")
        with cols[2]: mtype = st.selectbox("Type", ["Singles", "Tag Team", "Triple Threat", "Fatal 4-Way"], key=f"match_{i}_type")

        if w1 != "-- Select --" and w2 != "-- Select --" and w1 != w2:
            w1d, w2d = roster[roster["WorkerName"] == w1], roster[roster["WorkerName"] == w2]
            w1w = float(w1d["Wage"].iloc[0]) if not w1d.empty else 0
            w2w = float(w2d["Wage"].iloc[0]) if not w2d.empty else 0
            w1u = int(w1d["WorkerUID"].iloc[0]) if not w1d.empty else 0
            w2u = int(w2d["WorkerUID"].iloc[0]) if not w2d.empty else 0
            card_matches.append(MatchSlot(worker_uids=[w1u, w2u], worker_names=[w1, w2], wages=[w1w, w2w], match_type=mtype))

            if not w1d.empty and not w2d.empty:
                sc = 0
                if staleness_df is not None and not staleness_df.empty:
                    sr = check_staleness(w1u, w2u, staleness_df)
                    sc = sr["count"]
                    if sr["is_stale"]:
                        st.markdown(f'<div class="stale-warning">{sr["warning_message"]}</div>', unsafe_allow_html=True)
                pred = predict_match_quality(w1d.iloc[0], w2d.iloc[0], sc)
                total_pred.append(pred["predicted_rating"])
                with cols[3]:
                    st.markdown(f'{grade_badge(pred["grade"])} **{pred["predicted_rating"]}**', unsafe_allow_html=True)
                    st.caption(f'Range: {pred["rating_range"]}')
            st.caption(f"💰 ${w1w + w2w:,.0f} ({w1}: ${w1w:,.0f} + {w2}: ${w2w:,.0f})")

    st.markdown("---")
    if card_matches:
        result = calculate_show(card_matches, config)
        avg_q = sum(total_pred) / len(total_pred) if total_pred else 0
        st.markdown("### 📊 Show Calculation")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.markdown(metric_card("Talent Cost", f"${result.total_talent_cost:,.0f}", "negative"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Staff Cost", f"${result.total_staff_cost:,.0f}", "negative"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("Revenue", f"${result.ticket_revenue:,.0f}", "positive"), unsafe_allow_html=True)
        with c4:
            ps = "positive" if result.is_profitable else "negative"
            st.markdown(metric_card("Profit", f"{'+'if result.profit>=0 else ''}${result.profit:,.0f}", ps), unsafe_allow_html=True)
        with c5:
            qs = "positive" if avg_q >= 50 else "neutral" if avg_q >= 30 else "negative"
            st.markdown(metric_card("Avg Rating", f"{avg_q:.0f}", qs), unsafe_allow_html=True)

        if result.staff_warning:
            st.markdown(f'<div class="warning-box">⚠️ <strong>OSPREAY WARNING:</strong> Staff costs {result.staff_ratio:.1%} (limit: 15%)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-box">✅ Staff costs OK: {result.staff_ratio*100:.1f}%</div>', unsafe_allow_html=True)
    else:
        st.info("Select workers for your matches to see the calculation.")

# ═══════════════════════════════════════════════
# TAB: Worker Compare
# ═══════════════════════════════════════════════
if page == "🔀 Worker Compare":
    st.markdown("### 🔀 Worker Comparison")
    cc1, cc2 = st.columns(2)
    with cc1: cmp_w1 = st.selectbox("Worker A", ["-- Select --"] + worker_names, key="cmp_w1")
    with cc2: cmp_w2 = st.selectbox("Worker B", ["-- Select --"] + worker_names, key="cmp_w2")

    if cmp_w1 != "-- Select --" and cmp_w2 != "-- Select --" and cmp_w1 != cmp_w2:
        w1r = roster[roster["WorkerName"] == cmp_w1].iloc[0]
        w2r = roster[roster["WorkerName"] == cmp_w2].iloc[0]

        # Radar Chart
        fig = go.Figure()
        fig.add_trace(make_radar(w1r, cmp_w1))
        fig.add_trace(make_radar(w2r, cmp_w2))
        fig.update_layout(polar=dict(bgcolor="#1a1f2e", radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d"),
                                     angularaxis=dict(gridcolor="#30363d")),
                          title="Skill Radar Comparison", **DARK_LAYOUT, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # Stats comparison
        compare_cols = ["Popularity", "Star_Quality", "AvgSkill", "Wage", "MomentumNum", "Looks",
                        "Charisma", "Microphone", "Consistency", "Experience"]
        comp_data = []
        for col in compare_cols:
            if col in roster.columns:
                v1, v2 = float(w1r.get(col, 0)), float(w2r.get(col, 0))
                comp_data.append({"Stat": col.replace("_", " "), cmp_w1: v1, cmp_w2: v2,
                                  "Winner": cmp_w1 if v1 > v2 else cmp_w2 if v2 > v1 else "Tie"})
        if comp_data:
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        # Match prediction
        pred = predict_match_quality(w1r, w2r)
        st.markdown(f"### Predicted Match: {grade_badge(pred['grade'])} **{pred['predicted_rating']}** (Range: {pred['rating_range']})",
                    unsafe_allow_html=True)

    # Single worker radar
    st.markdown("---")
    st.markdown("### 📊 Individual Skill Radar")
    sel_worker = st.selectbox("Select worker", ["-- Select --"] + worker_names, key="radar_single")
    if sel_worker != "-- Select --":
        wr = roster[roster["WorkerName"] == sel_worker].iloc[0]
        all_skills = SKILL_COLS + ["Power", "Athleticism", "Stamina", "Toughness", "Hardcore",
                                   "Charisma", "Microphone", "Menace", "Acting"]
        avail = [c for c in all_skills if c in roster.columns]
        vals = [float(wr.get(c, 0)) for c in avail] + [float(wr.get(avail[0], 0))]
        labels = [c.replace("_", " ") for c in avail] + [avail[0].replace("_", " ")]
        fig = go.Figure(go.Scatterpolar(r=vals, theta=labels, fill="toself", name=sel_worker,
                                         line_color="#58a6ff", fillcolor="rgba(88,166,255,0.2)"))
        fig.update_layout(polar=dict(bgcolor="#1a1f2e", radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d"),
                                     angularaxis=dict(gridcolor="#30363d")),
                          title=f"{sel_worker} – Full Skill Profile", **DARK_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB: Contracts
# ═══════════════════════════════════════════════
if page == "📄 Contracts":
    st.markdown("### 📄 Contract Overview")
    try:
        contracts_df = get_contracts_detailed(st.session_state.mdb_path, st.session_state.promotion)
        if not contracts_df.empty:
            # Highlight expiring
            expiring = contracts_df[contracts_df["Status"] == "Expiring Soon!"] if "Status" in contracts_df.columns else pd.DataFrame()
            if not expiring.empty:
                st.markdown(f'<div class="warning-box">⚠️ {len(expiring)} contract(s) expiring soon!</div>', unsafe_allow_html=True)

            st.dataframe(contracts_df, use_container_width=True, height=500, hide_index=True)

            # Role breakdown
            if "Role" in contracts_df.columns:
                st.markdown("### Role Breakdown")
                role_counts = contracts_df["Role"].value_counts().reset_index()
                role_counts.columns = ["Role", "Count"]
                fig = px.pie(role_counts, names="Role", values="Count", title="Roster by Role",
                             color_discrete_sequence=["#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff"])
                fig.update_layout(**DARK_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            # Export
            csv = contracts_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Export Contracts CSV", csv, "contracts.csv", "text/csv")
        else:
            st.info("No contract data available.")
    except Exception as e:
        st.error(f"Error loading contracts: {e}")

# ═══════════════════════════════════════════════
# TAB: Budget
# ═══════════════════════════════════════════════
if page == "💰 Budget":
    st.markdown("### 💰 Budget Analysis")
    analysis = budget_analysis(roster, config)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(metric_card("Total Roster Cost/Show", f"${analysis['total_roster_cost']:,.0f}", "negative"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Avg Wage/Worker", f"${analysis['avg_wage']:,.0f}", "neutral"), unsafe_allow_html=True)
    with c3:
        ps = "positive" if analysis["is_profitable"] else "negative"
        st.markdown(metric_card("Monthly Profit (4 Shows)", f"${analysis['monthly_profit']:,.0f}", ps), unsafe_allow_html=True)

    if "WorkerName" in roster.columns and "Wage" in roster.columns:
        wc = roster[["WorkerName", "Wage"]].sort_values("Wage", ascending=False).head(20).copy()
        fig = px.bar(wc, x="WorkerName", y="Wage", color="Wage",
                     color_continuous_scale=["#3fb950", "#d29922", "#f85149"], title="Top 20 Wages")
        fig.update_layout(**DARK_LAYOUT, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    if all(c in roster.columns for c in ["WorkerName", "Wage", "AvgSkill", "Popularity"]):
        sc = ["WorkerName", "Wage", "AvgSkill", "Popularity"]
        if "EfficiencyScore" in roster.columns: sc.append("EfficiencyScore")
        sdf = roster[sc].copy()
        sdf["PopSize"] = sdf["Popularity"].clip(lower=1)
        fig = px.scatter(sdf, x="Wage", y="AvgSkill", size="PopSize",
                         color="EfficiencyScore" if "EfficiencyScore" in sdf.columns else None,
                         hover_name="WorkerName", color_continuous_scale=["#f85149", "#d29922", "#3fb950"],
                         title="Value Map: Skill vs. Cost")
        fig.update_layout(**DARK_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB: Financial History
# ═══════════════════════════════════════════════
if page == "📈 Financials":
    st.markdown("### 📈 Financial History")
    try:
        fin = get_financial_histories(st.session_state.mdb_path, st.session_state.promotion)
        if not fin.empty:
            fin = fin.sort_values("MonthsAgo", ascending=False)
            inc_cols = [c for c in fin.columns if c.startswith("Inc_")]
            exp_cols = [c for c in fin.columns if c.startswith("Exp_")]

            if inc_cols and exp_cols:
                total_inc = fin[inc_cols].sum(axis=1)
                total_exp = fin[exp_cols].sum(axis=1)
                chart_data = pd.DataFrame({
                    "Months Ago": fin["MonthsAgo"],
                    "Income": total_inc,
                    "Expenses": total_exp,
                    "Cash": fin.get("EndOfMonthCash", 0),
                })

                c1, c2, c3 = st.columns(3)
                latest = fin.iloc[0] if len(fin) > 0 else {}
                with c1: st.markdown(metric_card("Cash", f"${int(latest.get('EndOfMonthCash', 0)):,}", "neutral"), unsafe_allow_html=True)
                with c2: st.markdown(metric_card("Last Income", f"${int(total_inc.iloc[0]):,}", "positive"), unsafe_allow_html=True)
                with c3: st.markdown(metric_card("Last Expenses", f"${int(total_exp.iloc[0]):,}", "negative"), unsafe_allow_html=True)

                # Income breakdown
                st.markdown("### Income Breakdown")
                inc_data = fin[["MonthsAgo"] + inc_cols].melt(id_vars="MonthsAgo", var_name="Source", value_name="Amount")
                inc_data["Source"] = inc_data["Source"].str.replace("Inc_", "")
                fig = px.bar(inc_data, x="MonthsAgo", y="Amount", color="Source", title="Income by Source",
                             color_discrete_sequence=["#3fb950", "#58a6ff", "#bc8cff", "#d29922", "#f778ba"])
                fig.update_layout(**DARK_LAYOUT, xaxis_title="Months Ago")
                st.plotly_chart(fig, use_container_width=True)

                # Expense breakdown
                st.markdown("### Expense Breakdown")
                exp_data = fin[["MonthsAgo"] + exp_cols].melt(id_vars="MonthsAgo", var_name="Source", value_name="Amount")
                exp_data["Source"] = exp_data["Source"].str.replace("Exp_", "")
                fig = px.bar(exp_data, x="MonthsAgo", y="Amount", color="Source", title="Expenses by Source",
                             color_discrete_sequence=["#f85149", "#d29922", "#bc8cff", "#58a6ff"])
                fig.update_layout(**DARK_LAYOUT, xaxis_title="Months Ago")
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(fin, use_container_width=True, hide_index=True)
        else:
            st.info("No financial history data available.")
    except Exception as e:
        st.error(f"Error loading financial data: {e}")

# ═══════════════════════════════════════════════
# TAB: Push Tracking / Momentum History
# ═══════════════════════════════════════════════
if page == "📊 Push Tracking":
    st.markdown("### 📊 Push Tracking / Momentum History")
    st.caption("Momentum snapshots are taken automatically each time you connect a new save file.")

    history = load_momentum_history()
    snapshots = history.get("snapshots", [])

    if len(snapshots) >= 1:
        st.markdown(f"**{len(snapshots)} snapshot(s)** recorded.")

        # Current momentum overview
        if snapshots:
            latest = snapshots[-1]
            st.markdown(f"#### Latest Snapshot: {latest['date']}")
            mom_data = []
            for name, info in latest["workers"].items():
                mom_data.append({"Worker": name, "Momentum": info["momentum"], "Popularity": info["popularity"]})
            mom_df = pd.DataFrame(mom_data).sort_values("Popularity", ascending=False)
            st.dataframe(mom_df, use_container_width=True, hide_index=True)

        # Trend chart if multiple snapshots
        if len(snapshots) >= 2:
            st.markdown("### Momentum Trend")
            all_workers_in_history = set()
            for s in snapshots:
                all_workers_in_history.update(s["workers"].keys())

            mom_map = {"Very Cold": 10, "Cold": 20, "Cooled": 30, "Cool": 35,
                       "Neutral": 50, "Warm": 65, "Very Warm": 75, "Hot": 85, "Very Hot": 95}

            # Build trend data
            trend_rows = []
            for s in snapshots:
                for wname, info in s["workers"].items():
                    trend_rows.append({
                        "Date": s["date"],
                        "Worker": wname,
                        "MomentumNum": mom_map.get(info["momentum"], 50),
                        "Popularity": info["popularity"],
                    })
            trend_df = pd.DataFrame(trend_rows)

            selected_workers = st.multiselect("Select workers to track",
                                              sorted(all_workers_in_history),
                                              default=sorted(all_workers_in_history)[:5],
                                              key="push_track_workers")
            if selected_workers:
                filtered = trend_df[trend_df["Worker"].isin(selected_workers)]
                fig = px.line(filtered, x="Date", y="MomentumNum", color="Worker",
                              title="Momentum Over Time", markers=True)
                fig.update_layout(**DARK_LAYOUT, yaxis_title="Momentum (10=Very Cold, 95=Very Hot)")
                st.plotly_chart(fig, use_container_width=True)

                fig2 = px.line(filtered, x="Date", y="Popularity", color="Worker",
                               title="Popularity Over Time", markers=True)
                fig2.update_layout(**DARK_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No momentum snapshots yet. Connect to a database to create the first snapshot.")

# ═══════════════════════════════════════════════
# TAB: Staleness
# ═══════════════════════════════════════════════
if page == "🔄 Staleness":
    st.markdown("### 🔄 Booking History & Staleness Check")
    if staleness_df is not None and not staleness_df.empty:
        st.markdown(f"**{len(staleness_df)} staleness entries loaded.**")
        sc1, sc2 = st.columns(2)
        with sc1: ck_w1 = st.selectbox("Worker 1", ["-- Select --"] + worker_names, key="stale_w1")
        with sc2: ck_w2 = st.selectbox("Worker 2", ["-- Select --"] + worker_names, key="stale_w2")

        if ck_w1 != "-- Select --" and ck_w2 != "-- Select --":
            w1d = roster[roster["WorkerName"] == ck_w1]
            w2d = roster[roster["WorkerName"] == ck_w2]
            u1 = int(w1d["WorkerUID"].iloc[0]) if not w1d.empty else 0
            u2 = int(w2d["WorkerUID"].iloc[0]) if not w2d.empty else 0
            if u1 and u2:
                r = check_staleness(u1, u2, staleness_df)
                if r["is_stale"]:
                    st.markdown(f'<div class="stale-warning">{r["warning_message"]}</div>', unsafe_allow_html=True)
                elif r["count"] > 0:
                    st.info(f"ℹ️ This pairing has happened {r['count']}x. Still fresh.")
                else:
                    st.markdown('<div class="success-box">✅ Fresh pairing – no staleness risk!</div>', unsafe_allow_html=True)

        with st.expander("📋 Raw staleness data"):
            st.dataframe(staleness_df.head(100), use_container_width=True, hide_index=True)
    else:
        st.info("No staleness data. Connect database first.")

# ═══════════════════════════════════════════════
# TAB: Storyline Tracker
# ═══════════════════════════════════════════════
if page == "📖 Storylines":
    st.markdown("### 📖 Storyline Tracker")
    storylines = load_storylines()

    # Add new storyline
    with st.expander("➕ New Storyline", expanded=False):
        sl_title = st.text_input("Storyline Title", placeholder="Championship Chase", key="sl_title")
        sl_workers = st.multiselect("Workers Involved", worker_names, key="sl_workers")
        sl_status = st.selectbox("Status", ["building", "climax", "cooldown", "finished"], key="sl_status")
        sl_notes = st.text_area("Notes", key="sl_notes", height=80)
        if st.button("Create Storyline", key="btn_add_sl") and sl_title and sl_workers:
            add_storyline(sl_title, sl_workers, sl_notes, sl_status)
            st.success(f"Created: {sl_title}")
            st.rerun()

    # Display storylines
    status_icons = {"building": "🔨", "climax": "🔥", "cooldown": "❄️", "finished": "✅"}
    for sl in storylines:
        icon = status_icons.get(sl["status"], "📖")
        with st.expander(f'{icon} {sl["title"]} ({sl["status"]}) — {", ".join(sl["workers"])}'):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Workers:** {', '.join(sl['workers'])}")
                st.markdown(f"**Created:** {sl['created']} | **Updated:** {sl['updated']}")
                if sl["notes"]:
                    st.markdown(f"**Notes:** {sl['notes']}")
                if sl["events"]:
                    st.markdown("**Timeline:**")
                    for ev in sl["events"]:
                        st.caption(f"  • {ev}")
            with c2:
                new_status = st.selectbox("Status", ["building", "climax", "cooldown", "finished"],
                                          index=["building", "climax", "cooldown", "finished"].index(sl["status"]),
                                          key=f"sl_st_{sl['id']}")
                if new_status != sl["status"]:
                    update_storyline(sl["id"], status=new_status)
                    st.rerun()
                ev_text = st.text_input("Add event", key=f"sl_ev_{sl['id']}", placeholder="What happened?")
                if st.button("Add", key=f"sl_ev_btn_{sl['id']}") and ev_text:
                    add_storyline_event(sl["id"], ev_text)
                    st.rerun()
                if st.button("🗑️ Delete", key=f"sl_del_{sl['id']}"):
                    delete_storyline(sl["id"])
                    st.rerun()

    if not storylines:
        st.info("No storylines yet. Create your first one above!")

# ═══════════════════════════════════════════════
# TAB: Event Planner
# ═══════════════════════════════════════════════
if page == "📅 Event Planner":
    st.markdown("### 📅 Event Planner")
    events = load_events()

    with st.expander("➕ Plan New Event", expanded=False):
        ev_name = st.text_input("Event Name", placeholder="Weekly Show #5", key="ev_name")
        ev_c1, ev_c2 = st.columns(2)
        with ev_c1:
            ev_date = st.date_input("Date", key="ev_date")
        with ev_c2:
            ev_type = st.selectbox("Type", ["weekly", "ppv", "special"], key="ev_type")
        ev_notes = st.text_area("Notes", key="ev_notes", height=68)

        # Quick match assignment
        st.markdown("**Matches:**")
        ev_matches = []
        for mi in range(5):
            ec1, ec2, ec3 = st.columns([2, 2, 1])
            with ec1:
                ew1 = st.selectbox("W1", ["-- Skip --"] + worker_names, key=f"ev_m{mi}_w1")
            with ec2:
                ew2 = st.selectbox("W2", ["-- Skip --"] + worker_names, key=f"ev_m{mi}_w2")
            with ec3:
                emt = st.selectbox("T", ["Singles", "Tag Team"], key=f"ev_m{mi}_t")
            if ew1 != "-- Skip --" and ew2 != "-- Skip --" and ew1 != ew2:
                ev_matches.append({"worker1": ew1, "worker2": ew2, "type": emt})

        if st.button("Create Event", key="btn_add_ev") and ev_name:
            add_event(ev_name, str(ev_date), ev_type, ev_matches, ev_notes)
            st.success(f"Created: {ev_name}")
            st.rerun()

    # Display events
    type_icons = {"weekly": "📺", "ppv": "🎪", "special": "⭐"}
    for ev in sorted(events, key=lambda x: x.get("date", "")):
        icon = type_icons.get(ev.get("type", ""), "📅")
        status_tag = "✅" if ev.get("status") == "completed" else "📋"
        with st.expander(f'{icon} {ev["name"]} — {ev["date"]} {status_tag}'):
            if ev.get("notes"):
                st.markdown(f"**Notes:** {ev['notes']}")
            if ev.get("matches"):
                for j, m in enumerate(ev["matches"], 1):
                    st.caption(f"Match {j}: {m['worker1']} vs {m['worker2']} ({m.get('type', 'Singles')})")
            ec1, ec2 = st.columns(2)
            with ec1:
                if ev.get("status") != "completed":
                    if st.button("Mark Completed", key=f"ev_done_{ev['id']}"):
                        update_event(ev["id"], status="completed")
                        st.rerun()
            with ec2:
                if st.button("🗑️ Delete", key=f"ev_del_{ev['id']}"):
                    delete_event(ev["id"])
                    st.rerun()

    if not events:
        st.info("No events planned yet. Create your first event above!")

# ═══════════════════════════════════════════════
# TAB: Chemistry Detection
# ═══════════════════════════════════════════════
if page == "🧪 Chemistry":
    st.markdown("### 🧪 Chemistry Detection")
    st.caption("Analyzes past match ratings to find proven pairings.")
    try:
        mh = get_match_histories(st.session_state.mdb_path, st.session_state.promotion)
        mp = get_match_participants(st.session_state.mdb_path)
        chem_df = detect_chemistry(roster, mh, mp)
        if not chem_df.empty:
            # Summary metrics
            proven = chem_df[chem_df["Status"].str.contains("Proven")]
            good = chem_df[chem_df["Status"].str.contains("Good")]
            bad = chem_df[chem_df["Status"].str.contains("Bad")]
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.markdown(metric_card("Proven Chemistry", str(len(proven)), "positive"), unsafe_allow_html=True)
            with cc2:
                st.markdown(metric_card("Good Pairings", str(len(good)), "neutral"), unsafe_allow_html=True)
            with cc3:
                st.markdown(metric_card("Bad Chemistry", str(len(bad)), "negative"), unsafe_allow_html=True)

            st.dataframe(chem_df, use_container_width=True, hide_index=True)
        else:
            st.info("Not enough match history data to detect chemistry patterns.")
    except Exception as e:
        st.error(f"Error: {e}")

# ═══════════════════════════════════════════════
# TAB: Roster Health Dashboard
# ═══════════════════════════════════════════════
if page == "🏥 Roster Health":
    st.markdown("### 🏥 Roster Health Dashboard")
    try:
        contracts_det = get_contracts_detailed(st.session_state.mdb_path, st.session_state.promotion)
    except Exception:
        contracts_det = pd.DataFrame()
    health = analyze_roster_health(roster, contracts_det)

    # Overview metrics
    hc1, hc2, hc3, hc4 = st.columns(4)
    with hc1:
        st.markdown(metric_card("Total Roster", str(health["total"]), "neutral"), unsafe_allow_html=True)
    with hc2:
        st.markdown(metric_card("Wrestlers", str(health["wrestlers"]), "neutral"), unsafe_allow_html=True)
    with hc3:
        st.markdown(metric_card("Avg Skill", f'{health["avg_skill"]}', "positive"), unsafe_allow_html=True)
    with hc4:
        st.markdown(metric_card("Expiring Soon", str(health["expiring_soon"]),
                    "negative" if health["expiring_soon"] > 2 else "neutral"), unsafe_allow_html=True)

    # Face/Heel balance
    hc5, hc6 = st.columns(2)
    with hc5:
        if health["faces"] + health["heels"] > 0:
            fig = go.Figure(go.Pie(labels=["Faces", "Heels"], values=[health["faces"], health["heels"]],
                                   marker_colors=["#3fb950", "#f85149"]))
            fig.update_layout(title="Face / Heel Balance", **DARK_LAYOUT, height=300)
            st.plotly_chart(fig, use_container_width=True)
    with hc6:
        if health["veterans"] + health["midcard"] + health["young"] > 0:
            fig = go.Figure(go.Pie(labels=["Veterans", "Midcard", "Young"],
                                   values=[health["veterans"], health["midcard"], health["young"]],
                                   marker_colors=["#d29922", "#58a6ff", "#3fb950"]))
            fig.update_layout(title="Experience Distribution", **DARK_LAYOUT, height=300)
            st.plotly_chart(fig, use_container_width=True)

    # Issues & Strengths
    if health["issues"]:
        st.markdown("### Issues")
        for issue in health["issues"]:
            st.markdown(f'<div class="warning-box">{issue}</div>', unsafe_allow_html=True)
    if health["strengths"]:
        st.markdown("### Strengths")
        for s in health["strengths"]:
            st.markdown(f'<div class="success-box">{s}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB: Popularity Forecast
# ═══════════════════════════════════════════════
if page == "🔮 Forecast":
    st.markdown("### 🔮 Popularity Forecast")
    st.caption("Predicts future popularity based on momentum trends. More snapshots = better accuracy.")
    history = load_momentum_history()
    months_ahead = st.slider("Forecast months ahead", 1, 12, 3, key="forecast_months")

    forecasts = []
    for name in worker_names:
        fc = forecast_popularity(history, name, months_ahead)
        if fc["current"] > 0:
            forecasts.append({"Worker": name, **fc})

    if forecasts:
        fc_df = pd.DataFrame(forecasts)
        fc_df = fc_df.sort_values("change", ascending=False)

        # Summary
        rising = fc_df[fc_df["change"] > 2]
        falling = fc_df[fc_df["change"] < -2]
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(metric_card("Rising Stars", str(len(rising)), "positive"), unsafe_allow_html=True)
        with fc2:
            st.markdown(metric_card("Declining", str(len(falling)), "negative"), unsafe_allow_html=True)
        with fc3:
            st.markdown(metric_card("Snapshots", str(len(history.get("snapshots", []))), "neutral"), unsafe_allow_html=True)

        display_fc = fc_df[["Worker", "current", "predicted", "change", "trend", "momentum", "confidence"]].copy()
        display_fc.columns = ["Worker", "Current Pop", "Predicted Pop", "Change", "Trend", "Momentum", "Confidence"]
        st.dataframe(display_fc, use_container_width=True, hide_index=True)

        # Chart top movers
        top_movers = pd.concat([fc_df.head(5), fc_df.tail(5)])
        fig = px.bar(top_movers, x="Worker", y="change", color="change",
                     color_continuous_scale=["#f85149", "#d29922", "#3fb950"],
                     title=f"Predicted Popularity Change ({months_ahead} months)")
        fig.update_layout(**DARK_LAYOUT, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Connect to a database to generate forecasts.")

# ═══════════════════════════════════════════════
# TAB: Worker Development Suggestions
# ═══════════════════════════════════════════════
if page == "🌟 Development":
    st.markdown("### 🌟 Worker Development Suggestions")
    st.caption("Workers with high skill ceiling but low popularity – best push candidates.")

    dev_suggestions = suggest_development(roster, top_n=15)
    if dev_suggestions:
        dev_df = pd.DataFrame(dev_suggestions)
        st.dataframe(dev_df, use_container_width=True, hide_index=True)

        # Ceiling vs Popularity chart
        fig = px.scatter(dev_df, x="Popularity", y="Ceiling", size="Gap", color="Gap",
                         hover_name="Worker", text="Worker",
                         color_continuous_scale=["#d29922", "#3fb950", "#58a6ff"],
                         title="Push Potential: Ceiling vs Current Popularity")
        fig.update_traces(textposition="top center")
        fig.update_layout(**DARK_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No development suggestions available.")

# ═══════════════════════════════════════════════
# TAB: Angle Suggestions
# ═══════════════════════════════════════════════
if page == "🎭 Angles":
    st.markdown("### 🎭 Angle Suggestions")
    st.caption("Best workers for each angle type based on Charisma, Microphone, Acting, Menace, etc.")
    angles = suggest_angles(roster)

    for angle_type, workers_list in angles.items():
        st.markdown(f"#### {angle_type}")
        for rank, (name, score) in enumerate(workers_list, 1):
            bar_pct = min(score, 100)
            st.markdown(f"**{rank}. {name}** — Score: {score}")
            st.progress(bar_pct / 100)

# ═══════════════════════════════════════════════
# TAB: Title Reign Tracker
# ═══════════════════════════════════════════════
if page == "🏆 Titles":
    st.markdown("### 🏆 Title Reign Tracker")
    belts = st.session_state.title_belts
    reigns = analyze_title_reigns(belts)

    if reigns:
        reign_df = pd.DataFrame(reigns)
        st.dataframe(reign_df, use_container_width=True, hide_index=True)

        # Prestige chart
        fig = px.bar(reign_df, x="Belt", y="Prestige", color="Status",
                     color_discrete_map={"🏆 Prestigious": "#d29922", "✅ Healthy": "#3fb950",
                                         "⚠️ Declining": "#f85149", "❌ Worthless": "#484f58"},
                     title="Title Prestige")
        fig.update_layout(**DARK_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

        # Defence chart
        if "Defences" in reign_df.columns:
            fig2 = px.bar(reign_df, x="Belt", y="Defences", color="Champion",
                          title="Title Defences This Reign")
            fig2.update_layout(**DARK_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No active title belts found.")

# ═══════════════════════════════════════════════
# TAB: Touring Schedule Optimizer
# ═══════════════════════════════════════════════
if page == "🌍 Touring":
    st.markdown("### 🌍 Touring Schedule Optimizer")
    st.caption("Find the best workers to bring on a touring show based on regional popularity vs cost.")

    tc1, tc2 = st.columns(2)
    with tc1:
        regions = list(MACRO_REGIONS.keys())
        target_region = st.selectbox("Target Region", regions, key="tour_region")
    with tc2:
        tour_budget = st.number_input("Touring Budget ($)", value=5000.0, step=500.0, min_value=0.0, key="tour_budget")

    tour_results = optimize_touring(roster, target_region, tour_budget)
    if tour_results:
        tour_df = pd.DataFrame(tour_results)
        st.dataframe(tour_df, use_container_width=True, hide_index=True)

        # Budget visualization
        within = tour_df[tour_df["WithinBudget"] == "✅"]
        if not within.empty:
            st.markdown(f'<div class="success-box">✅ {len(within)} workers fit within ${tour_budget:,.0f} budget '
                        f'(Total: ${within["Wage"].sum():,.0f})</div>', unsafe_allow_html=True)

        fig = px.bar(tour_df.head(15), x="Worker", y="TouringValue", color="WithinBudget",
                     color_discrete_map={"✅": "#3fb950", "❌": "#f85149"},
                     title=f"Touring Value for {target_region}")
        fig.update_layout(**DARK_LAYOUT, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB: Talent Trade Analyzer
# ═══════════════════════════════════════════════
if page == "🔄 Trade":
    st.markdown("### 🔄 Talent Trade Analyzer")
    st.caption("Compare worker values to evaluate potential trades.")

    tr1, tr2 = st.columns(2)
    with tr1:
        trade_w1 = st.selectbox("Worker A", ["-- Select --"] + worker_names, key="trade_w1")
    with tr2:
        trade_w2 = st.selectbox("Worker B", ["-- Select --"] + worker_names, key="trade_w2")

    if trade_w1 != "-- Select --" and trade_w2 != "-- Select --" and trade_w1 != trade_w2:
        trade = compare_trade(roster, trade_w1, trade_w2)
        if "error" not in trade:
            v1, v2 = trade["worker1"], trade["worker2"]

            # Verdict
            st.markdown(f"### {trade['verdict']}")

            vc1, vc2 = st.columns(2)
            with vc1:
                st.markdown(f"#### {trade_w1}")
                st.markdown(metric_card("Total Value", f'{v1["total_value"]}', "neutral"), unsafe_allow_html=True)
                st.markdown(f"- **In-Ring:** {v1['in_ring']}")
                st.markdown(f"- **Star Power:** {v1['star_power']}")
                st.markdown(f"- **Popularity:** {v1['popularity']}")
                st.markdown(f"- **Reliability:** {v1['reliability']}")
                st.markdown(f"- **Current Wage:** ${v1['current_wage']:,.0f}")
                st.markdown(f"- **Market Wage:** ${v1['market_wage']:,.0f}")
                if v1["overpaid"]:
                    st.markdown('<div class="warning-box">⚠️ Overpaid</div>', unsafe_allow_html=True)
                elif v1["underpaid"]:
                    st.markdown('<div class="success-box">💰 Underpaid (bargain)</div>', unsafe_allow_html=True)
            with vc2:
                st.markdown(f"#### {trade_w2}")
                st.markdown(metric_card("Total Value", f'{v2["total_value"]}', "neutral"), unsafe_allow_html=True)
                st.markdown(f"- **In-Ring:** {v2['in_ring']}")
                st.markdown(f"- **Star Power:** {v2['star_power']}")
                st.markdown(f"- **Popularity:** {v2['popularity']}")
                st.markdown(f"- **Reliability:** {v2['reliability']}")
                st.markdown(f"- **Current Wage:** ${v2['current_wage']:,.0f}")
                st.markdown(f"- **Market Wage:** ${v2['market_wage']:,.0f}")
                if v2["overpaid"]:
                    st.markdown('<div class="warning-box">⚠️ Overpaid</div>', unsafe_allow_html=True)
                elif v2["underpaid"]:
                    st.markdown('<div class="success-box">💰 Underpaid (bargain)</div>', unsafe_allow_html=True)

            # Value comparison bar
            fig = go.Figure()
            cats = ["In-Ring", "Star Power", "Popularity", "Reliability"]
            fig.add_trace(go.Bar(x=cats, y=[v1["in_ring"], v1["star_power"], v1["popularity"], v1["reliability"]],
                                 name=trade_w1, marker_color="#58a6ff"))
            fig.add_trace(go.Bar(x=cats, y=[v2["in_ring"], v2["star_power"], v2["popularity"], v2["reliability"]],
                                 name=trade_w2, marker_color="#f778ba"))
            fig.update_layout(title="Value Breakdown Comparison", barmode="group", **DARK_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB: Free Agent Scout (Wrestlers)
# ═══════════════════════════════════════════════
if page == "🔥 Free Agents":
    st.markdown("### 🔥 Hot Free Agents")
    st.caption("Unsigned wrestlers ranked by value for your promotion. Filter to find the perfect signing.")

    try:
        if "free_agents_df" not in st.session_state or st.session_state.free_agents_df is None:
            st.session_state.free_agents_df = get_free_agents(st.session_state.mdb_path)
        fa_df = st.session_state.free_agents_df
    except Exception as e:
        fa_df = pd.DataFrame()
        st.error(f"Could not load free agents: {e}")

    if not fa_df.empty:
        # Filters
        st.markdown("#### 🔎 Filters")
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            fa_gender = st.selectbox("Gender", ["All", "Female", "Male"], key="fa_gender")
        with fc2:
            fa_region_group = st.selectbox("Region", ["All"] + list(BASED_IN_GROUPS.keys()), key="fa_region")
        with fc3:
            fa_age_range = st.slider("Age Range", 16, 65, (18, 45), key="fa_age")
        with fc4:
            fa_min_skill = st.slider("Min Avg Skill", 0, 100, 30, key="fa_min_skill")

        fc5, fc6, fc7 = st.columns(3)
        with fc5:
            fa_freelance = st.selectbox("Freelance Only?", ["All", "Yes", "No"], key="fa_freelance")
        with fc6:
            fa_min_pop = st.slider("Min Popularity", 0, 100, 0, key="fa_min_pop")
        with fc7:
            fa_sort = st.selectbox("Sort by", ["Overall", "InRing", "StarPower", "Popularity", "EstWage"], key="fa_sort")

        # Apply filters — wrestlers only
        filtered = fa_df[(fa_df["Wrestler"] == True) | (fa_df["Occasional_Wrestler"] == True)].copy()

        if fa_gender != "All":
            filtered = filtered[filtered["Gender"] == fa_gender]
        if fa_region_group != "All":
            region_values = BASED_IN_GROUPS.get(fa_region_group, [])
            filtered = filtered[filtered["Based_In"].isin(region_values)]
        if fa_age_range:
            filtered = filtered[(filtered["Age"] >= fa_age_range[0]) & (filtered["Age"] <= fa_age_range[1])]
        filtered = filtered[filtered["AvgSkill"] >= fa_min_skill]
        if fa_freelance == "Yes":
            filtered = filtered[filtered["Freelance"] == True]
        elif fa_freelance == "No":
            filtered = filtered[filtered["Freelance"] == False]
        filtered = filtered[filtered["MaxPop"] >= fa_min_pop]

        # Determine home region pop column from roster attrs
        home_region = roster.attrs.get("home_region", "British_Isles")
        # Map home_region name to the MACRO_REGIONS pop column
        pop_col = "British_Isles"
        for macro, regions in MACRO_REGIONS.items():
            if home_region in regions:
                pop_col = macro.replace(" ", "_")
                break
        # Fix common name mismatches
        pop_col_map = {"UK": "British_Isles", "North_America": "USA"}
        pop_col = pop_col_map.get(pop_col, pop_col)

        # Score all filtered wrestlers
        scored = []
        for _, row in filtered.iterrows():
            scored.append(score_free_agent_wrestler(row, pop_col))

        if scored:
            scored_df = pd.DataFrame(scored)
            scored_df = scored_df.sort_values(fa_sort, ascending=False).head(50)

            # Summary
            st.markdown(f'<div class="success-box">Found <strong>{len(filtered)}</strong> free agent wrestlers matching filters. '
                        f'Showing top 50 by {fa_sort}.</div>', unsafe_allow_html=True)

            display_cols = ["Name", "Overall", "InRing", "StarPower", "Popularity",
                           "Safety", "Experience", "EstWage", "Age", "Gender", "Based_In", "Freelance"]
            st.dataframe(scored_df[display_cols], use_container_width=True, hide_index=True)

            # Chart: Overall vs Est Wage (value picks)
            fig = px.scatter(scored_df, x="EstWage", y="Overall", hover_name="Name",
                            color="Overall", size="Popularity", text="Name",
                            color_continuous_scale=["#f85149", "#d29922", "#3fb950"],
                            title="Free Agent Value Map (higher Overall + lower wage = bargain)")
            fig.update_traces(textposition="top center", textfont_size=8)
            fig.update_layout(**DARK_LAYOUT, xaxis_title="Estimated Wage ($)", yaxis_title="Overall Score")
            st.plotly_chart(fig, use_container_width=True)

            # CSV export
            csv = scored_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Export Free Agents CSV", csv, "free_agents.csv", "text/csv")
        else:
            st.info("No wrestlers match the current filters.")
    else:
        st.info("Connect to a database to scout free agents.")

# ═══════════════════════════════════════════════
# TAB: Staff Scout (Refs & Road Agents)
# ═══════════════════════════════════════════════
if page == "🧑‍⚖️ Staff Scout":
    st.markdown("### 🧑‍⚖️ Staff Scout — Refs & Road Agents")
    st.caption("Find the best available referees and road agents by cost/value ratio.")

    try:
        if "free_agents_df" not in st.session_state or st.session_state.free_agents_df is None:
            st.session_state.free_agents_df = get_free_agents(st.session_state.mdb_path)
        fa_df = st.session_state.free_agents_df
    except Exception:
        fa_df = pd.DataFrame()

    if not fa_df.empty:
        staff_tab1, staff_tab2 = st.tabs(["🧑‍⚖️ Referees", "📋 Road Agents"])

        # ─── Referees ───
        with staff_tab1:
            st.markdown("#### 🧑‍⚖️ Available Referees")
            refs = fa_df[fa_df["Referee"] == True].copy()

            sf1, sf2, sf3 = st.columns(3)
            with sf1:
                ref_gender = st.selectbox("Gender", ["All", "Female", "Male"], key="ref_gender")
            with sf2:
                ref_region = st.selectbox("Region", ["All"] + list(BASED_IN_GROUPS.keys()), key="ref_region")
            with sf3:
                ref_age = st.slider("Age Range", 16, 65, (20, 55), key="ref_age")

            if ref_gender != "All":
                refs = refs[refs["Gender"] == ref_gender]
            if ref_region != "All":
                refs = refs[refs["Based_In"].isin(BASED_IN_GROUPS.get(ref_region, []))]
            refs = refs[(refs["Age"] >= ref_age[0]) & (refs["Age"] <= ref_age[1])]

            scored_refs = [score_free_agent_referee(row) for _, row in refs.iterrows()]
            if scored_refs:
                ref_df = pd.DataFrame(scored_refs).sort_values("Overall", ascending=False).head(30)
                st.markdown(f"**{len(refs)} referees found.** Showing top 30.")
                st.dataframe(ref_df, use_container_width=True, hide_index=True)

                fig = px.scatter(ref_df, x="EstWage", y="Overall", hover_name="Name",
                                color="ValueRatio", size="Refereeing", text="Name",
                                color_continuous_scale=["#f85149", "#d29922", "#3fb950"],
                                title="Referee Value Map (high ValueRatio = best deal)")
                fig.update_traces(textposition="top center", textfont_size=8)
                fig.update_layout(**DARK_LAYOUT, xaxis_title="Estimated Wage ($)", yaxis_title="Overall Score")
                st.plotly_chart(fig, use_container_width=True)

                csv = ref_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Referees CSV", csv, "free_referees.csv", "text/csv")
            else:
                st.info("No referees match the current filters.")

        # ─── Road Agents ───
        with staff_tab2:
            st.markdown("#### 📋 Available Road Agents")
            agents = fa_df[fa_df["Road_Agent"] == True].copy()

            sa1, sa2, sa3 = st.columns(3)
            with sa1:
                ra_gender = st.selectbox("Gender", ["All", "Female", "Male"], key="ra_gender")
            with sa2:
                ra_region = st.selectbox("Region", ["All"] + list(BASED_IN_GROUPS.keys()), key="ra_region")
            with sa3:
                ra_age = st.slider("Age Range", 16, 75, (25, 65), key="ra_age")

            if ra_gender != "All":
                agents = agents[agents["Gender"] == ra_gender]
            if ra_region != "All":
                agents = agents[agents["Based_In"].isin(BASED_IN_GROUPS.get(ra_region, []))]
            agents = agents[(agents["Age"] >= ra_age[0]) & (agents["Age"] <= ra_age[1])]

            scored_agents = [score_free_agent_road_agent(row) for _, row in agents.iterrows()]
            if scored_agents:
                agent_df = pd.DataFrame(scored_agents).sort_values("Overall", ascending=False).head(30)
                st.markdown(f"**{len(agents)} road agents found.** Showing top 30.")
                st.dataframe(agent_df, use_container_width=True, hide_index=True)

                fig = px.scatter(agent_df, x="EstWage", y="Overall", hover_name="Name",
                                color="ValueRatio", size="Booking_Skill", text="Name",
                                color_continuous_scale=["#f85149", "#d29922", "#3fb950"],
                                title="Road Agent Value Map (high ValueRatio = best deal)")
                fig.update_traces(textposition="top center", textfont_size=8)
                fig.update_layout(**DARK_LAYOUT, xaxis_title="Estimated Wage ($)", yaxis_title="Overall Score")
                st.plotly_chart(fig, use_container_width=True)

                csv = agent_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Road Agents CSV", csv, "free_road_agents.csv", "text/csv")
            else:
                st.info("No road agents match the current filters.")
    else:
        st.info("Connect to a database to scout staff.")

# ═══════════════════════════════════════════════
# TAB: Tools (PDF Export, Backup, DB Explorer)
# ═══════════════════════════════════════════════
if page == "⚙️ Tools":
    st.markdown("### ⚙️ Tools")

    # PDF Export
    st.markdown("#### 📄 PDF Export")
    pdf_name = st.text_input("Show name for PDF", value="Show Card", key="pdf_name")
    if st.button("Generate Show Card PDF", key="btn_pdf"):
        # Gather current card from session
        pdf_matches = []
        for i in range(st.session_state.get("num_matches_val", 5)):
            w1k = st.session_state.get(f"match_{i}_w1", "-- Select --")
            w2k = st.session_state.get(f"match_{i}_w2", "-- Select --")
            mtk = st.session_state.get(f"match_{i}_type", "Singles")
            if w1k != "-- Select --" and w2k != "-- Select --":
                w1d = roster[roster["WorkerName"] == w1k]
                w2d = roster[roster["WorkerName"] == w2k]
                wage = 0
                grade = "-"
                rating = 0
                if not w1d.empty and not w2d.empty:
                    wage = float(w1d["Wage"].iloc[0]) + float(w2d["Wage"].iloc[0])
                    pred = predict_match_quality(w1d.iloc[0], w2d.iloc[0])
                    grade = pred["grade"]
                    rating = pred["predicted_rating"]
                pdf_matches.append({"worker1": w1k, "worker2": w2k, "match_type": mtk,
                                    "grade": grade, "predicted_rating": rating, "wage": wage})
        if pdf_matches:
            config = st.session_state.show_config
            financials = {
                "revenue": config.ticket_revenue,
                "talent_cost": sum(m["wage"] for m in pdf_matches),
                "staff_cost": config.road_agent_cost + config.referee_cost + config.other_staff_cost,
                "production": config.production_cost,
                "profit": config.ticket_revenue - sum(m["wage"] for m in pdf_matches) - config.road_agent_cost - config.referee_cost - config.other_staff_cost - config.production_cost,
            }
            pdf_bytes = generate_show_card_pdf(pdf_name, pdf_matches, financials, st.session_state.notes)
            ext = "pdf" if pdf_bytes[:4] == b"%PDF" else "txt"
            st.download_button(f"📥 Download {ext.upper()}", pdf_bytes, f"{pdf_name}.{ext}",
                               f"application/{ext}")
        else:
            st.warning("No matches set in Show Calculator tab.")

    st.markdown("---")

    # Auto-Backup
    st.markdown("#### 💾 Auto-Backup")
    if st.button("Create Backup Now", key="btn_backup"):
        result = create_backup()
        if result:
            st.success(f"Backup created: {Path(result).name}")
        else:
            st.error("Backup failed.")

    backups = list_backups()
    if backups:
        st.markdown(f"**{len(backups)} backup(s) available:**")
        for b in backups:
            st.caption(f"📁 {b['name']} — {b['size']} — {b['created']}")

    st.markdown("---")

    # DB Explorer
    st.markdown("#### 🔍 DB Structure Explorer")
    if st.session_state.mdb_path and st.button("Scan DB Structure", key="btn_scan_db"):
        try:
            structure = detect_table_structure(st.session_state.mdb_path)
            for table, cols in structure.items():
                with st.expander(f"📋 {table} ({len(cols)} cols)"):
                    st.text("\n".join(f"  • {c}" for c in cols))
        except Exception as e:
            st.error(str(e))

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown('<div style="text-align:center; color:#484f58; font-size:0.8rem; padding:10px 0;">'
            'TEW Booking & Finance Optimizer v4.0 🤼</div>', unsafe_allow_html=True)
