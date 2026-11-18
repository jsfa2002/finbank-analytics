"""Project Closure - FinBank (DMS Consulting) - GMAC Checkpoint 3. Final management product."""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from finbank.validators import validate_dataset  # noqa: E402  (the team's real code, US-04)

NAVY, BLUE, LIGHT, MID, RED, GREEN = "#12335B", "#0B5FAE", "#9BB7D4", "#5C8FC7", "#C0392B", "#1E8E5A"
REPO = "https://github.com/AndresAvella09/finbank-analytics"
LOGO, DATA, EVID = ROOT / "assets" / "dms_logo.png", ROOT / "data" / "sample_clientes.csv", ROOT / "assets" / "evidence"
STEPS = ["Summary", "Sprints", "Schedule & Budget", "Demo & Results", "Definition of Done", "Lessons"]

st.set_page_config(page_title="DMS Consulting · FinBank Closure", page_icon="📈", layout="wide")
st.markdown(f"""<style>
.block-container {{padding-top: 3.5rem; max-width: 1150px;}}
div[data-testid="stButton"], div[data-testid="stDownloadButton"] {{width: 100%;}}
div[data-testid="stButton"] > button {{width: 100%; border-radius: 10px; font-weight: 600;}}
.grid {{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px;}}
.kpi {{background:#EEF3F9; border-radius:12px; padding:14px 16px;}}
.kpi b {{display:block; font-size:1.55rem; color:{NAVY};}} .kpi span {{font-size:.8rem; color:#4A6585;}}
.card {{background:#fff; border:1px solid #D6E2F0; border-top:4px solid {BLUE}; border-radius:14px;
        padding:16px 18px; height:100%;}}
.card h4 {{margin:0 0 6px 0; color:{NAVY};}}
.card.stop {{border-top-color:{RED};}} .card.cont {{border-top-color:{GREEN};}}
.hero {{background:linear-gradient(90deg,{NAVY},{BLUE}); color:#fff; border-radius:16px; padding:22px 26px;}}
.hero h1, .hero p {{color:#fff; margin:0;}}
.tag {{display:inline-block; background:#E3EEF9; color:{NAVY}; border-radius:20px; padding:2px 12px;
       font-size:.8rem; font-weight:600; margin-right:6px;}}
</style>""", unsafe_allow_html=True)
st.session_state.setdefault("step", 0)


def go(i):
    st.session_state.step = max(0, min(len(STEPS) - 1, i))


def cards(items):
    """Equal-height cards. items = [(title, html, css_class)]."""
    html = "".join(f"<div class='card {c}'><h4>{t}</h4>{d}</div>" for t, d, c in items)
    st.markdown(f"<div class='grid'>{html}</div>", unsafe_allow_html=True)


def kpis(items):
    st.markdown("<div class='grid'>" + "".join(f"<div class='kpi'><b>{v}</b><span>{t}</span></div>"
                for v, t in items) + "</div>", unsafe_allow_html=True)


def plot(w=6, h=2.8):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def half(fig):
    left, _ = st.columns([3, 2])
    left.pyplot(fig)


# ---------- Data (from the Final Management Report) ----------
SPRINTS = {
    1: dict(weeks="1–2", committed=11, completed=8, closures={6: 3, 8: 5},
            goal="Diagnosis (US-01) and agile board (US-09).",
            blocker="Charter approval (US-02) moves to Sprint 2.",
            cols=["Story", "Pts", "Status"],
            rows=[["Business Diagnosis & Goal Definition", 3, "Done · day 6"],
                  ["Agile Board & Backlog Setup", 5, "Done · day 8"],
                  ["Data Requirements Definition", 3, "Moved to Sprint 2"]]),
    2: dict(weeks="3–4", committed=16, completed=11, closures={6: 3, 7: 5, 9: 3},
            goal="Charter approval (US-02), data requirements (US-03) and architecture (US-10).",
            blocker="Charter approved on day 16 (planned: day 10); US-04 moves to Sprint 3.",
            cols=["Story", "Pts", "Status"],
            rows=[["Governance & Charter Approval (carried over)", 3, "Done · day 6"],
                  ["Data Requirements Definition", 5, "Done · day 7"],
                  ["Solution Architecture Document", 3, "Done · day 9"],
                  ["Data Collection & Cleaning", 5, "Moves to Sprint 3"]]),
    3: dict(weeks="5–6", committed=10, completed=10, closures=None,
            goal="Data validation and cleaning (US-04.1, US-04.2), churn definition (US-06.1) and baseline delinquency model (US-05.1). "
                 "Half the commitment closed in week 1.",
            blocker="FinBank's real extract does not arrive (I-2); a direct push to main without a PR (I-1) leads to branch protection."),
    4: dict(weeks="7–8", committed=9, completed=9, closures=None,
            goal="60-day delinquency model (US-05.2) and 3-month churn model (US-06.2, US-06.3). Logistic regression; AUC 0.871 and 0.737 in cross-validation.",
            blocker="The extract arrives on day 33, 2 days late (I-2 closed). From here on, main requires an Approve."),
    5: dict(weeks="9–10", committed=10, completed=10, closures={2: 2, 4: 2, 6: 3, 9: 3},
            goal="Validate both models out of time, agree the alert threshold with FinBank, and deliver the system with its deployment roadmap.",
            blocker="Threshold by cost (I-4), churn drift in cohort 12 (I-5), PR waiting for approval (I-6).",
            cols=["ID", "Story", "Pts", "Pairing", "Reviewer", "Closed"],
            rows=[["US-05.3", "Alert threshold by cost and collection capacity, agreed with FinBank", 2, "Diego + Miguel", "Juanse", "Day 2"],
                  ["US-07.2", "Out-of-time validation of the churn model", 2, "Diego + Juanse", "Miguel", "Day 4"],
                  ["US-07.1", "Out-of-time validation of the delinquency model", 3, "Diego + Juanse", "Miguel", "Day 6"],
                  ["US-08", "Alert list, model cards and deployment roadmap", 3, "Diego + Miguel", "Juanse", "Day 9"]]),
}
MILESTONES = [  # name, planned day, actual day, note
    ("A · Diagnosis & goals (US-01)", 5, 6, "Sprint 1"),
    ("I · Agile board running (US-09)", 10, 8, "Charter success criterion"),
    ("B · Charter approved (US-02)", 10, 16, "Absorbed by working in parallel"),
    ("C · Data requirements (US-03)", 15, 17, "Started in parallel with the approval"),
    ("J · Solution architecture (US-10)", 15, 19, "Has float; off the critical path"),
    ("D · Data ready for modeling (US-04)", 25, 26, "Sprint 3"),
    ("E · Delinquency model (US-05)", 35, 37, "Extract 2 days late (I-2)"),
    ("F · Churn model (US-06)", 35, 39, "Has float; started on day 21"),
    ("G · Validation of both models (US-07)", 45, 46, "6 days instead of 10, thanks to automation"),
    ("H · Final delivery & roadmap (US-08)", 50, 49, "Critical-path slippage recovered"),
    ("K · Executive presentation", 40, 56, "Has float; moved to closing to show final results"),
    ("Acceptance & project close", 60, 56, "6 of 10 reserve days used"),
]
BUDGET = [("1. Diagnosis & governance", 27.0, 29.5, "Extra sessions caused by the Charter approval delay"),
          ("2. Requirements & data", 63.0, 64.0, "One extra day in US-04"),
          ("3. Modeling & validation", 63.0, 61.5, "Automated validation: 6 days instead of 10"),
          ("4. Delivery (task H)", 9.0, 9.3, "Model-card adjustments"),
          ("4. Contingency reserve (task L)", 18.0, 10.8, "6 of 10 days used ($1.8M per team day)")]
PRS = [(15, "feature/models-sprint4", "Diego + Juanse", "Approve · Miguel", "Simulated extract and models (Sprint 4)"),
       (16, "feature/threshold-calibration", "Diego + Miguel", "Approve · Juanse", "Cost-based threshold (US-05.3)"),
       (17, "feature/churn-validation", "Diego + Juanse", "Miguel's review · entered with #19", "Churn validation and PSI (US-07.2)"),
       (18, "feature/delinquency-validation", "Diego + Juanse", "Miguel's review · entered with #19", "Delinquency validation (US-07.1)"),
       (19, "docs/final-delivery", "Diego + Miguel", "Approve · Juanse", "Scoring, model cards and roadmap (US-08)"),
       (20, "feature/reserve-adjustments", "Diego + Juanse", "Miguel's review · entered with #21", "Reserve work: drift and alert drivers"),
       (21, "docs/sprint5-closure", "Diego", "Approve · Juanse", "Sprint 5 log and closure act")]


def burndown(committed, closures):
    days, left, actual = list(range(11)), committed, []
    for d in days:
        left -= closures.get(d, 0)
        actual.append(left)
    fig, ax = plot()
    ax.plot(days, [committed * (1 - d / 10) for d in days], "--", color="gray", label="Ideal")
    ax.step(days, actual, where="post", color=BLUE, lw=2.5, label="Actual")
    ax.set_xlabel("Working day of the sprint"); ax.set_ylabel("Points remaining"); ax.legend()
    return fig


def validate_records(df):
    """Record-level detail based on docs/data_dictionary.md. Returns (violations, imputations)."""
    v, imp = [], []

    def add(i, field, rule):
        val = df.at[i, field]
        v.append({"row": i + 2, "client_id": df.at[i, "cliente_id"], "field": field,
                  "rule": rule, "value": "(empty)" if pd.isna(val) else str(val)})

    dup = df["cliente_id"].duplicated(keep=False)
    for i in df.index:
        r = df.loc[i]
        if pd.isna(r["cliente_id"]) or not re.fullmatch(r"C-\d{4}", str(r["cliente_id"])):
            add(i, "cliente_id", "Must match C-XXXX")
        if dup[i]:
            add(i, "cliente_id", "Must be unique")
        if pd.isna(r["edad"]):
            add(i, "edad", "Required (no nulls)")
        elif not 18 <= r["edad"] <= 75:
            add(i, "edad", "Range 18–75")
        if pd.isna(r["ingreso_mensual"]):
            add(i, "ingreso_mensual", "Required (no nulls)")
        elif r["ingreso_mensual"] < 0:
            add(i, "ingreso_mensual", "Must be >= 0")
        if pd.isna(r["saldo_mora_30d"]):
            imp.append({"row": i + 2, "client_id": r["cliente_id"], "field": "saldo_mora_30d", "action": "Null imputed as 0"})
        elif r["saldo_mora_30d"] < 0:
            add(i, "saldo_mora_30d", "Must be >= 0")
        if pd.isna(r["score_riesgo"]):
            add(i, "score_riesgo", "Required (no nulls)")
        elif not 300 <= r["score_riesgo"] <= 850:
            add(i, "score_riesgo", "Range 300–850")
        if r["tipo_cliente"] not in ("preferente", "regular"):
            add(i, "tipo_cliente", "'preferente' or 'regular'")
        if r["activo"] not in ("si", "no"):
            add(i, "activo", "'si' or 'no'")
    return pd.DataFrame(v), pd.DataFrame(imp)


def en_msg(e):
    """Display-only English version of the validator's Spanish messages."""
    m = e["message"]
    if m.startswith("nulos en"):
        col, n = m[len("nulos en "):].split(": ")
        return f"{n} null value(s) in {col}"
    if m.startswith("score fuera de rango"):
        return "score out of range; must be between 300 and 850"
    if m.startswith("columna faltante"):
        return "missing column: " + m.split(": ")[1]
    if "deberia ser" in m:
        col, _, t = m.partition(" deberia ser ")
        return f"{col} should be {t}"
    return m


# ---------- Header + navigation ----------
h1, h2 = st.columns([1, 3])
if LOGO.exists():
    h1.image(str(LOGO), width=210)
h2.markdown("<div style='padding-top:14px'><span class='tag'>GMAC · Checkpoint 3</span>"
            "<span class='tag'>Project closure</span><span class='tag'>Group 3</span></div>", unsafe_allow_html=True)
h2.progress((st.session_state.step + 1) / len(STEPS), text=f"Step {st.session_state.step + 1} of {len(STEPS)}")
for i, (col, name) in enumerate(zip(st.columns(len(STEPS)), STEPS)):
    col.button(f"{i + 1}. {name}", key=f"nav{i}", on_click=go, args=(i,),
               type="primary" if i == st.session_state.step else "secondary")
st.divider()
step = st.session_state.step

# ================= 1. Summary =================
if step == 0:
    st.markdown("<div class='hero'><h1>From Planning to Certainty of Delivery</h1>"
                "<p>FinBank S.A. early-delinquency and churn prediction system · 12 weeks · 5 sprints</p></div>",
                unsafe_allow_html=True)
    st.write("")
    kpis([("48 / 48 pts", "Backlog delivered (100%)"), ("9.6 pts", "Average velocity over 5 sprints"),
          ("Day 56", "Closed in week 12; 6 of 10 reserve days used"), ("$175.1M COP", "Final cost vs. $180M budget (−2.7%)")])
    st.write("")
    left, right = st.columns([2, 3])
    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    ax.pie([58800, 18200], labels=["Delinquency\n$58,800M", "Churn\n$18,200M"], colors=[NAVY, BLUE], startangle=90,
           wedgeprops=dict(width=.42, edgecolor="white"), textprops={"fontsize": 8})
    ax.text(0, 0, "$77,000M\nat risk", ha="center", va="center", fontsize=9, color=NAVY, fontweight="bold")
    left.pyplot(fig)
    right.markdown("**The problem.** FinBank manages a $420,000M COP portfolio for 125,000 customers with no early "
                   "warning for customers about to default (30–60 days) or for preferred customers about to leave "
                   "(3 months ahead). We planned, ran and now close the project that fixes both, on time and on budget.")
    with right:
        cards([("Checkpoint 1 · Plan", "Charter, 4 CRISP-DM phases, critical path, 10-day reserve and a 48-point backlog.", ""),
               ("Checkpoint 2 · Execute", "Scrum + XP in Sprints 1–2: 8 and 11 points. We over-committed and learned to plan with real velocity.", ""),
               ("Checkpoint 3 · Close", "Sprints 3–5 at 100%: models validated, threshold agreed, roadmap delivered.", "")])
    st.write("")
    team = [("Diego Andrés Avella", "Project Lead / Product Owner"), ("Miguel Ángel Hernández", "Business Analyst"),
            ("Juan Sebastián Fajardo", "Scrum Facilitator / Scrum Master")]
    cards([(n, r, "") for n, r in team])
    st.caption("Closing days, dailies and executed costs are simulated from the board, the repository history and team hours, "
               "as declared in the Final Management Report.")
    st.write("")
    st.button("Start the tour ▶", on_click=go, args=(1,), type="primary")

# ================= 2. Sprints =================
elif step == 1:
    st.header("Sprint results")
    view = st.radio("View", ["All sprints", "Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"], horizontal=True)
    if view == "All sprints":
        c1, c2, c3 = st.columns(3)
        c1.metric("Backlog delivered", "48 / 48 pts", "100%")
        c2.metric("Average velocity", "9.6 pts", "σ = 1.1", delta_color="off")
        c3.metric("Committed → completed", "56 → 48 pts", "8 pts finished in the next sprint", delta_color="off")
        fig, ax = plot(7, 3)
        xs = range(5)
        ax.bar([i - .19 for i in xs], [SPRINTS[n]["committed"] for n in SPRINTS], .38, color=LIGHT, label="Committed")
        ax.bar([i + .19 for i in xs], [SPRINTS[n]["completed"] for n in SPRINTS], .38, color=BLUE, label="Completed (velocity)")
        ax.axhline(9.6, ls="--", color="gray", lw=1); ax.text(4.55, 9.9, "avg 9.6", fontsize=8, color="gray", ha="right")
        ax.set_xticks(list(xs), [f"Sprint {n}\n({round(100 * s['completed'] / s['committed'])}%)" for n, s in SPRINTS.items()])
        ax.set_ylabel("Story points"); ax.legend(loc="upper right", fontsize=8)
        st.pyplot(fig)
        st.info("**Predictability is the management result.** After the Checkpoint 2 retrospective, the team stopped committing "
                "beyond its real velocity: three sprints in a row closed at 100%. Only points from stories that reached Done count.")
    else:
        n = int(view[-1]); s = SPRINTS[n]
        st.markdown(f"**Weeks {s['weeks']}** · **Goal:** {s['goal']}")
        c1, c2 = st.columns(2)
        c1.metric("Points completed", f"{s['completed']} pts", f"of {s['committed']} committed", delta_color="off")
        c2.metric("Delivered", f"{round(100 * s['completed'] / s['committed'])}%")
        st.markdown(f"**Main impediment:** {s['blocker']}")
        if s["closures"]:
            left, right = st.columns([3, 2]) if n != 5 else (st.container(), st.container())
            left.pyplot(burndown(s["committed"], s["closures"]))
            right.dataframe(pd.DataFrame(s["rows"], columns=s["cols"]), hide_index=True)
            if n == 5:
                st.caption("Plateau on days 6–8: the US-08 PR was ready on day 8 but waited for the approval required by the "
                           "protected main branch (I-6). Done on day 9.")
        else:
            st.info("Story-level detail for this sprint is in the logbook.")
            st.link_button("Open the logbook", f"{REPO}/tree/main/bitacora")

# ================= 3. Schedule & Budget =================
elif step == 2:
    st.header("Schedule & budget: baseline vs. actual")
    t1, t2, t3, t4 = st.tabs(["Milestones", "Contingency reserve", "Budget by phase", "Earned value"])
    with t1:
        fig, ax = plot(7.5, 4.2)
        for i, (name, plan, real, _) in enumerate(MILESTONES):
            ax.plot([plan, real], [i, i], color=LIGHT, lw=3, zorder=1)
            ax.scatter(plan, i, color="#B8B8B0", s=45, zorder=2)
            ax.scatter(real, i, color=BLUE if real <= plan else NAVY, s=45, zorder=3)
        ax.set_yticks(range(len(MILESTONES)), [m[0] for m in MILESTONES], fontsize=8); ax.invert_yaxis()
        ax.axvline(56, color=RED, lw=1, ls=":"); ax.text(56.5, 11.4, "close\nday 56", fontsize=7, color=RED)
        ax.set_xlabel("Project working day (5 days = 1 week; 60 days = 12 weeks)")
        ax.scatter([], [], color="#B8B8B0", label="Baseline (Charter)"); ax.scatter([], [], color=NAVY, label="Actual")
        ax.legend(fontsize=8, loc="lower left")
        st.pyplot(fig)
        st.dataframe(pd.DataFrame([[m, p, r, f"{r - p:+d}", note] for m, p, r, note in MILESTONES],
                     columns=["Milestone", "Planned day", "Actual day", "Variance", "Note"]), hide_index=True)
        st.info("Critical-path tasks A–H finished on day 49, one day before baseline: automated validation took 6 days instead of 10.")
    with t2:
        cards([("Days 51–54 · Churn drift (I-5)", "Data-quality risk from the Charter. The drift is isolated in cohort 12 and comes with a real "
                "churn increase (16.8%) that the model reproduces (17.5%). It is a behavior change, not a data error: the model stays, "
                "with monthly PSI monitoring (PR #20).", ""),
               ("Days 55–56 · Alert report", "Client-alignment risk from the Charter. Every alert now shows its main driver and the "
                "FinBank committee gets a summary by priority and driver (PR #20). On day 56 FinBank accepted the deliverables and "
                "the closure act was signed (PR #21).", ""),
               ("4 reserve days unused", "The reserve was used only for identified risks, and the 4 unused days are reported "
                "instead of spent. The project closed in week 12 without moving the committed date.", "cont")])
    with t3:
        c1, c2, c3 = st.columns(3)
        c1.metric("Final cost", "$175.1M", "−$4.9M vs. $180M (−2.7%)", delta_color="off")
        c2.metric("Work A–H", "$164.3M", "+$2.3M vs. $162.0M (+1.4%)", delta_color="off")
        c3.metric("Reserve used", "$10.8M", "of $18.0M", delta_color="off")
        fig, ax = plot(7, 3)
        xs = range(len(BUDGET))
        ax.bar([i - .19 for i in xs], [b[1] for b in BUDGET], .38, color=LIGHT, label="Charter budget")
        ax.bar([i + .19 for i in xs], [b[2] for b in BUDGET], .38, color=BLUE, label="Executed")
        ax.set_xticks(list(xs), [b[0].replace(" (", "\n(") .replace(" & ", " &\n") for b in BUDGET], fontsize=7)
        ax.set_ylabel("COP millions"); ax.legend(fontsize=8)
        st.pyplot(fig)
        st.dataframe(pd.DataFrame([[b[0], f"${b[1]:.1f}M", f"${b[2]:.1f}M", f"{b[2] - b[1]:+.1f}M", b[3]] for b in BUDGET],
                     columns=["Phase", "Budget", "Executed", "Variance", "Cause"]), hide_index=True)
        st.caption("The total is below budget because only 6 of the 10 reserve days were used, not because the work was more "
                   "efficient. That is how it is reported to FinBank.")
    with t4:
        c1, c2 = st.columns(2)
        c1.metric("SPI at end of A–H", "1.00", "schedule exactly on baseline", delta_color="off")
        c2.metric("CPI at end of A–H", "0.986", "+1.4% cost overrun, inherited from governance", delta_color="off")
        wk = [0, 6, 8, 10]
        fig, ax = plot(6.5, 3)
        ax.plot(wk, [0, 105.75, 137.25, 162.0], "--", color="gray", marker="o", label="PV (planned value)")
        ax.plot(wk, [0, 105.0, 132.0, 162.0], color=BLUE, marker="o", lw=2, label="EV (earned value)")
        ax.plot(wk, [0, 107.0, 137.6, 164.3], color="#E8643C", marker="o", label="AC (actual cost)")
        ax.set_xlabel("Project week (snapshots at weeks 6, 8 and 10)"); ax.set_ylabel("COP millions (cumulative)"); ax.legend(fontsize=8)
        half(fig)
        st.dataframe(pd.DataFrame([["PV", "$105.75M", "$137.25M", "$162.0M"], ["EV", "$105.0M", "$132.0M", "$162.0M"],
                                   ["AC", "$107.0M", "$137.6M", "$164.3M"], ["SPI = EV / PV", "0.99", "0.96", "1.00"],
                                   ["CPI = EV / AC", "0.98", "0.96", "0.986"]],
                     columns=["Indicator", "Week 6", "Week 8", "Week 10 (end of A–H)"]), hide_index=True)
        st.caption("Earned value uses the 0/100 rule, consistent with velocity: a story earns its value only when it reaches Done. "
                   "The data delay of week 8 was recovered during validation.")

# ================= 4. Demo & Results =================
elif step == 3:
    st.header("Demo & results")
    mode = st.radio("Show me", ["Live demo: data validation pipeline", "Final model results"], horizontal=True)
    if mode.startswith("Live"):
        st.caption("The pipeline applies the data dictionary contract (US-03) to the customer dataset using the team's validators (US-04).")
        st.subheader("① Choose your data")
        source = st.radio("Which data?", ["Synthetic sample from the repo", "Upload my CSV"], horizontal=True)
        upload = st.file_uploader("Customer CSV", type="csv") if source == "Upload my CSV" else None
        df = pd.read_csv(upload) if upload else (pd.read_csv(DATA) if source.startswith("Synthetic") else None)
        if df is not None:
            st.dataframe(df, height=200)
        else:
            st.info("Upload a file to continue.")
        st.subheader("② Run the validation")
        if st.button("▶ Run validation", type="primary", disabled=df is None):
            st.session_state.ran = True
        if df is not None and st.session_state.get("ran"):
            st.subheader("③ Results")
            missing = {"cliente_id", "edad", "ingreso_mensual", "saldo_mora_30d", "score_riesgo", "tipo_cliente", "activo"} - set(df.columns)
            if missing:
                st.error(f"Columns missing from the contract: {sorted(missing)}")
            else:
                errors = validate_dataset(df)["errors"]
                viol, imp = validate_records(df)
                bad_ids = set(viol["client_id"]) if len(viol) else set()
                clean = df.copy()
                clean["saldo_mora_30d"] = clean["saldo_mora_30d"].fillna(0)
                clean = clean[~clean["cliente_id"].isin(bad_ids)]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Records", len(df)); c2.metric("Issues found", len(errors))
                c3.metric("Records with errors", len(bad_ids)); c4.metric("Ready for modeling", len(clean))
                a, b, c, d, e = st.tabs(["Pipeline report", "Record-level detail", "Clean dataset", "Score distribution", "Completeness"])
                with a:
                    st.caption("Output of `finbank.validators.validate_dataset` (messages translated for display)")
                    if errors:
                        st.dataframe(pd.DataFrame([{"type": x["type"], "column": x["column"], "message": en_msg(x)} for x in errors]), hide_index=True)
                    else:
                        st.success("Dataset is clean: 0 issues.")
                with b:
                    st.dataframe(viol, hide_index=True) if len(viol) else st.success("No violations.")
                    if len(imp):
                        st.caption("Imputations (the null policy allows imputing `saldo_mora_30d` as 0):")
                        st.dataframe(imp, hide_index=True)
                with c:
                    st.write(f"{len(clean)} of {len(df)} records are ready for modeling.")
                    st.dataframe(clean, height=240)
                    st.download_button("⬇ Download clean CSV", clean.to_csv(index=False).encode(), "clean_customers.csv")
                with d:
                    fig, ax = plot(6, 2.6)
                    ax.hist(df["score_riesgo"].dropna(), bins=range(300, 900, 50), color=BLUE, edgecolor="white")
                    ax.set_xlabel("Risk score (score_riesgo)"); ax.set_ylabel("Customers")
                    half(fig)
                with e:
                    comp = (1 - df.isna().mean()) * 100
                    fig, ax = plot(6, 2.8)
                    ax.barh(comp.index, comp.values, color=[NAVY if v == 100 else RED for v in comp.values])
                    ax.set_xlim(0, 100); ax.set_xlabel("% of records with data"); ax.invert_yaxis()
                    for i, v in enumerate(comp.values):
                        ax.text(min(v, 94), i, f"{v:.0f}%", va="center", ha="right", color="white", fontsize=8)
                    half(fig)
                    st.caption("Red: columns with missing data.")
    else:
        st.caption("Out-of-time validation on cohorts 11–12 (data the models never saw). Full reports are in `reports/` in the repository.")
        kpis([("0.855", "Delinquency AUC, 60 days (score-only rule: 0.822)"), ("0.786", "Churn AUC, 3 months (lift 2.5 in the top 20%)"),
              ("61.5%", "Of delinquents caught while alerting 13.6% of the portfolio"), ("−47.3%", "Expected cost vs. using no model")])
        st.write("")
        left, right = st.columns(2)
        fig, ax = plot(4.4, 3)
        ax.bar(["Score-only\nrule", "Delinquency\nmodel"], [0.822, 0.855], color=[LIGHT, BLUE])
        ax.axhline(0.80, ls="--", color=RED, lw=1); ax.text(1.45, 0.805, "acceptance 0.80", fontsize=7, color=RED, ha="right")
        ax.set_ylim(0.5, 0.9); ax.set_ylabel("Out-of-time AUC"); ax.set_title("Delinquency, 60 days", fontsize=9)
        left.pyplot(fig)
        fig, ax = plot(4.4, 3)
        ax.bar(["Random", "Churn\nmodel"], [0.5, 0.786], color=[LIGHT, BLUE])
        ax.axhline(0.70, ls="--", color=RED, lw=1); ax.text(1.45, 0.705, "acceptance 0.70", fontsize=7, color=RED, ha="right")
        ax.set_ylim(0.4, 0.9); ax.set_title("Churn, 3 months", fontsize=9)
        right.pyplot(fig)
        st.dataframe(pd.DataFrame([
            ["Alert rule", "Probability ≥ 0.09", "Top 20% by risk"],
            ["Cases detected", "61.5% of delinquents with 13.6% alerts", "50% of churn within the alerted 20%"],
            ["Stability (PSI of the score)", "0.012 (stable)", "0.231 (monitor)"],
            ["Alerts delivered (cohort 12)", "62 delinquency alerts", "24 retention alerts"]],
            columns=["Indicator", "Delinquency · 60 days", "Churn · 3 months"]), hide_index=True)
        st.info("Both models beat their acceptance thresholds and add value over what the bank already uses. The churn drift "
                "(PSI 0.231) was investigated during the reserve: it reflects a real behavior change, so monthly PSI monitoring is recommended.")

# ================= 5. Definition of Done =================
elif step == 4:
    st.header("Definition of Done: Sprint 5 compliance")
    st.write("A story is **Done** when: ① its 3-item checklist is complete, ② its PR was approved and merged by someone other than "
             "its authors and co-authors, ③ the tests pass, and ④ the card is in Done. Since Sprint 4, peer review is enforced by "
             "the repository settings.")
    st.dataframe(pd.DataFrame([
        ["US-05.3", "Yes", "Yes (#16, Juanse)", "Yes (35/35)", "Day 2"],
        ["US-07.2", "Yes", "Partial (#17: Miguel's review; entered with #19)", "Yes (40/40)", "Day 4"],
        ["US-07.1", "Yes", "Partial (#18: Miguel's review; entered with #19)", "Yes (45/45)", "Day 6"],
        ["US-08", "Yes", "Yes (#19, Juanse)", "Yes (49/49)", "Day 9"]],
        columns=["Story", "Checklist 3/3", "PR approved and merged by a peer", "Tests green", "Card in Done"]), hide_index=True)
    st.warning("**Reported as it stands in GitHub.** The Sprint 5 PRs were stacked and merged out of order, so #17, #18 and #20 "
               "entered inside #19 and #21 without their own Approve. Miguel reviewed all three with a comment, but the formal approval "
               "was not recorded. The content still went through a peer's review: #19 and #21 carry Juanse's Approve. "
               "PR #22 documents it. Lesson: merge stacked PRs in order.")
    st.subheader("Pull requests of Sprints 4–5 and closure")
    md = "| PR | Branch | Pairing | Review | Content |\n|---|---|---|---|---|\n" + "\n".join(
        f"| [#{n}]({REPO}/pull/{n}) | `{b}` | {p} | {r} | {c} |" for n, b, p, r, c in PRS)
    st.markdown(md)
    st.caption("4 of 7 PRs with a formal Approve (#15, #16, #19, #21). Full registry: bitacora/prs.md.")
    st.subheader("XP in practice")
    cards([("Pair programming", "Every story had a pair and a different reviewer; commits carry <i>Co-authored-by</i>.", ""),
           ("TDD", "Tests first (<i>test: … (red)</i>), then the feature. 53 automated tests, all passing.", ""),
           ("Continuous integration", "One branch and one PR per story. main has been protected since Sprint 4.", ""),
           ("Simple design", "Single-responsibility functions; validators refactored with tests untouched.", "")])
    st.write("")
    st.subheader("Evidence")
    ev = [("Peer review", "pr16_approval.png", "Juanse's formal approval on PR #16 (US-05.3), of which he is not an author."),
          ("Pairing & TDD", "pair_commits_tdd.png", "Co-authored commits and the red → green cycle (US-07.1)."),
          ("53 tests", "pytest_53.png", "The full automated suite passing."),
          ("Pipeline run", "pipeline_run.png", "Training, threshold, validation and alerts."),
          ("Merged PRs", "merged_prs.png", "Closed pull requests at the end of the project.")]
    for tab, (name, fname, cap) in zip(st.tabs([e[0] for e in ev]), ev):
        with tab:
            if (EVID / fname).exists():
                st.image(str(EVID / fname), caption=cap)
            else:
                st.info(f"Add assets/evidence/{fname} to show this screenshot.")
    c1, c2, c3 = st.columns(3)
    c1.link_button("Full repository", REPO)
    c2.link_button("Logbook", f"{REPO}/tree/main/bitacora")
    c3.link_button("All pull requests", f"{REPO}/pulls?q=is%3Apr")

# ================= 6. Lessons =================
else:
    st.header("Retrospective & lessons learned")
    st.subheader("Did we keep the Sprint 3 agreements?")
    st.dataframe(pd.DataFrame([
        ["Protect main with 1 required approval", "Active since Sprint 4; 4 of 7 PRs have an Approve, 3 entered stacked", "Partial"],
        ["Request data one sprint ahead", "Requested in Sprint 3; arrived 2 days late without stopping Sprint 4", "Met"],
        ["Log external impediments with a date", "I-2, I-4 and I-5 logged with their detection day", "Met"],
        ["Commit by velocity, stories of 3 pts or fewer", "9 and 10 pts, 2–3 pt stories, 100% delivery", "Met"],
        ["Don't leave the logbook for the last day", "Sprint 5 logbook closed on the day of project closure", "Partial"]],
        columns=["Agreement", "Evidence in Sprints 4–5", "Result"]), hide_index=True)
    st.write("")
    cards([("What worked", "• Planning by real velocity: commitment matched capacity in the last 3 sprints<br>"
                           "• Early automation (pipeline + 53 tests): validation took 6 days instead of 10<br>"
                           "• Risk checkpoints with the client: the threshold meeting avoided a cutoff FinBank would not use<br>"
                           "• Reserve used only for identified risks", "cont"),
           ("What we would improve", "• A formal data-delivery agreement with the client from day 1<br>"
                                     "• Branch protection from the first sprint, not after a deviation<br>"
                                     "• Measure stability (PSI) from the first model<br>"
                                     "• Keep the logbook current, and merge stacked PRs in order", "stop")])
    st.subheader("Management lessons")
    lessons = [("Real velocity is a planning tool, not a report", "At Checkpoint 2 we committed 13.5 points on average and delivered 9.5. From Sprint 3 we planned with the real figure and delivered 100%."),
               ("Automation is a schedule decision", "Tests and the pipeline looked like extra cost in Sprints 2–3, but they are why the project recovered its slippage in Sprint 5."),
               ("Manage dependencies with acceptance criteria, not by waiting", "Agreeing contracts up front (data dictionary, churn definition, story criteria) let every phase move in parallel."),
               ("A team rule that is not automated gets broken", "The direct push to main in Sprint 3 led to branch protection, so peer review no longer depends on individual discipline."),
               ("The reserve is for risks, not slack", "It was spent only when Charter risks occurred, and the 4 unused days are reported."),
               ("Interdisciplinary coordination", "Rotating pilot/copilot and reviewer roles carried business judgment into code: Miguel contributed the cost matrix, Juanse the PSI smoothing for small cohorts.")]
    for t, d in lessons:
        with st.expander(t):
            st.write(d)
    st.subheader("Recommendations for implementation")
    st.caption("The Charter excludes production deployment. The delivered roadmap (docs/entrega/) recommends four phases:")
    cards([("Retrain on production data · 3 weeks", "Repeat development and validation inside the bank's infrastructure. Proceed if out-of-time AUC ≥ 0.80 (delinquency) and ≥ 0.70 (churn), and PSI < 0.10.", ""),
           ("Controlled pilot · 8 weeks", "Apply the alerts in one region with a control group to measure the real reduction in 60-day delinquency and churn.", ""),
           ("Integration · 6 weeks", "Automate monthly scoring and connect it to the core banking system and the collections and retention CRM.", ""),
           ("Operation & governance", "Monthly PSI monitoring, quarterly recalibration, a business owner per model and a formal data-delivery agreement.", "")])
    st.write("")
    st.success("**Conclusion.** The project closed on day 56, inside the Charter's 12 weeks, with 100% of the scope delivered and accepted "
               "by FinBank, at $175.1M against a $180M budget. Scrum gave the cadence to detect each deviation within the sprint where it "
               "happened, and XP gave the technical quality that made recovering the schedule possible. The next step to attack the "
               "$77,000M at risk is retraining with production data and the controlled pilot.")
    st.write("Thanks for reviewing our work.")

# ---------- Bottom navigation ----------
st.divider()
a, _, b = st.columns([1, 4, 1])
a.button("◀ Previous", on_click=go, args=(step - 1,), disabled=step == 0)
b.button("Next ▶", on_click=go, args=(step + 1,), disabled=step == len(STEPS) - 1, type="primary")
