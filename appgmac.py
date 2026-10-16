"""Sprint Review & Operational Demo - FinBank (DMS Consulting) - GMAC Checkpoint 2, Product C."""
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

NAVY, BLUE, LIGHT = "#12335B", "#0B5FAE", "#9BB7D4"
REPO = "https://github.com/AndresAvella09/finbank-analytics"  # confirm this is the official repo
LOGO, DATA = ROOT / "assets" / "dms_logo.png", ROOT / "data" / "sample_clientes.csv"
STEPS = ["Home", "Sprints", "Demo", "Definition of Done", "Lessons"]

st.set_page_config(page_title="DMS Consulting · FinBank", page_icon="📈", layout="wide")
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
.card.stop {{border-top-color:#C0392B;}} .card.cont {{border-top-color:#1E8E5A;}}
.hero {{background:linear-gradient(90deg,{NAVY},{BLUE}); color:#fff; border-radius:16px; padding:22px 26px;}}
.hero h1, .hero p {{color:#fff; margin:0;}}
.tag {{display:inline-block; background:#E3EEF9; color:{NAVY}; border-radius:20px; padding:2px 12px;
       font-size:.8rem; font-weight:600; margin-right:6px;}}
</style>""", unsafe_allow_html=True)

st.session_state.setdefault("step", 0)


def go(i):
    st.session_state.step = max(0, min(len(STEPS) - 1, i))


# ---------- Data ----------
SPRINTS = {
    "Sprint 1": {
        "goal": "Finish the diagnosis, get the Charter ready for approval, and set up the agile board.",
        "committed": 11, "completed": 8, "closures": {6: 3, 8: 5},
        "stories": [["Business Diagnosis & Goal Definition", 3, "✅ Done · day 6"],
                    ["Agile Board & Backlog Setup", 5, "✅ Done · day 8"],
                    ["Data Requirements Definition", 3, "⏳ Moved to Sprint 2"]],
    },
    "Sprint 2": {
        "goal": "Close out governance, define data requirements and architecture, and kick off data collection and cleaning.",
        "committed": 16, "completed": 11, "closures": {6: 3, 7: 5, 9: 3},
        "stories": [["Governance & Charter Approval (carried over)", 3, "✅ Done · day 6"],
                    ["Data Requirements Definition", 5, "✅ Done · day 7"],
                    ["Solution Architecture Document", 3, "✅ Done · day 9"],
                    ["Data Collection & Cleaning", 5, "⏳ Moves to Sprint 3"]],
    },
}


def cards(items):
    """Cards in a grid so they all share the same height. items = [(title, html, css_class)]."""
    html = "".join(f"<div class='card {c}'><h4>{t}</h4>{d}</div>" for t, d, c in items)
    st.markdown(f"<div class='grid'>{html}</div>", unsafe_allow_html=True)


def burndown(name):
    s = SPRINTS[name]
    days, actual, left = list(range(11)), [], s["committed"]
    for d in days:
        left -= s["closures"].get(d, 0)
        actual.append(left)
    fig, ax = plt.subplots(figsize=(6, 2.8))
    ax.plot(days, [s["committed"] * (1 - d / 10) for d in days], "--", color="gray", label="Ideal")
    ax.step(days, actual, where="post", color=BLUE, lw=2.5, label="Actual")
    ax.set_xlabel("Working day"); ax.set_ylabel("Points remaining"); ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
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
            imp.append({"row": i + 2, "client_id": r["cliente_id"], "field": "saldo_mora_30d",
                        "action": "Null imputed as 0"})
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


# ---------- Header + step navigation ----------
h1, h2 = st.columns([1, 3])
if LOGO.exists():
    h1.image(str(LOGO), width=210)
h2.markdown("<div style='padding-top:14px'><span class='tag'>GMAC · Checkpoint 2</span>"
            "<span class='tag'>Product C</span><span class='tag'>Sprint Review & Demo</span></div>",
            unsafe_allow_html=True)
h2.progress((st.session_state.step + 1) / len(STEPS), text=f"Step {st.session_state.step + 1} of {len(STEPS)}")
for i, (col, name) in enumerate(zip(st.columns(len(STEPS)), STEPS)):
    col.button(f"{i + 1}. {name}", key=f"nav{i}", on_click=go, args=(i,),
               type="primary" if i == st.session_state.step else "secondary")
st.divider()
step = st.session_state.step

# ---------- 1. Home ----------
if step == 0:
    st.markdown("<div class='hero'><h1>Agile Execution of the FinBank Predictive Project</h1>"
                "<p>Scrum + XP · 2 sprints · increment delivered to FinBank S.A.</p></div>", unsafe_allow_html=True)
    st.write("")
    kpis = [("$420,000M COP", "Portfolio under management"), ("125,000", "Customers"),
            ("$77,000M COP", "Combined delinquency and churn exposure"), ("12 weeks", "CRISP-DM plan")]
    st.markdown("<div class='grid'>" + "".join(f"<div class='kpi'><b>{v}</b><span>{t}</span></div>" for v, t in kpis)
                + "</div>", unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([2, 3])
    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    ax.pie([58800, 18200], labels=["Delinquency\n$58,800M", "Churn\n$18,200M"], colors=[NAVY, BLUE],
           startangle=90, wedgeprops=dict(width=.42, edgecolor="white"), textprops={"fontsize": 8})
    ax.text(0, 0, "$77,000M\nat risk", ha="center", va="center", fontsize=9, color=NAVY, fontweight="bold")
    left.pyplot(fig)
    right.markdown("**Take the guided tour.** Use the buttons above or *Next* to move through it.")
    with right:
        cards([("2 · Sprints", "Velocity, stories and burndown for each sprint.", ""),
               ("3 · Demo", "The data validation pipeline, running live.", ""),
               ("4 · Definition of Done", "The evidence: PRs, TDD and XP practices.", ""),
               ("5 · Lessons", "The retrospective and the Sprint 3 plan.", "")])
    st.write("")
    st.button("Start the tour ▶", on_click=go, args=(1,), type="primary")

# ---------- 2. Sprints ----------
elif step == 1:
    st.header("Sprint results")
    view = st.radio("What would you like to see?", ["Sprint 1", "Sprint 2", "Comparison"], horizontal=True)
    if view == "Comparison":
        c1, c2, c3 = st.columns(3)
        c1.metric("Sprint 1 velocity", "8 pts", "of 11 committed")
        c2.metric("Sprint 2 velocity", "11 pts", "of 16 committed")
        c3.metric("Average velocity", "9.5 pts")
        fig, ax = plt.subplots(figsize=(6, 2.6))
        x = [0, 1]
        ax.bar([i - .18 for i in x], [11, 16], .36, color=LIGHT, label="Committed")
        ax.bar([i + .18 for i in x], [8, 11], .36, color=BLUE, label="Completed")
        ax.set_xticks(x, ["Sprint 1", "Sprint 2"]); ax.set_ylabel("Points"); ax.legend()
        ax.spines[["top", "right"]].set_visible(False)
        left, _ = st.columns([3, 2])
        left.pyplot(fig)
        p1, p2 = st.columns(2)
        p1.progress(8 / 11, text="Sprint 1 · 73% of committed points delivered")
        p2.progress(11 / 16, text="Sprint 2 · 69% of committed points delivered")
        st.markdown("**Project roadmap (12 weeks)**")
        phases = [("1 · Diagnosis & governance", 1, 2, NAVY), ("2 · Requirements & data", 3, 3, BLUE),
                  ("3 · Modeling", 6, 4, "#5C8FC7"), ("4 · Validation & deployment", 10, 3, LIGHT)]
        fig, ax = plt.subplots(figsize=(7, 2.3))
        for i, (n, start, dur, col) in enumerate(phases):
            ax.barh(i, dur, left=start - 1, color=col, edgecolor="white")
            ax.text(start - 1 + dur / 2, i, f"wk {start}–{start + dur - 1}", ha="center", va="center",
                    color="white" if col != LIGHT else NAVY, fontsize=8)
        ax.set_yticks(range(4), [p[0] for p in phases], fontsize=8); ax.invert_yaxis()
        ax.set_xticks(range(0, 13, 2)); ax.set_xlabel("Week")
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig)
        st.info("**Key deviation:** *Governance & Charter Approval* was planned for day 10 and closed on day 16. "
                "The team worked in parallel, and the impact was 1–2 working days, absorbed by the 10-day "
                "contingency reserve.")
    else:
        s = SPRINTS[view]
        st.markdown(f"**Sprint goal:** {s['goal']}")
        c1, c2 = st.columns(2)
        c1.metric("Points completed", f"{s['completed']} pts", f"of {s['committed']} committed")
        c2.metric("Stories finished", f"{sum('✅' in h[2] for h in s['stories'])} of {len(s['stories'])}")
        left, right = st.columns([3, 2])
        left.pyplot(burndown(view))
        right.dataframe(pd.DataFrame(s["stories"], columns=["Story", "Pts", "Status"]), hide_index=True)

# ---------- 3. Demo ----------
elif step == 2:
    st.header("Demo: data validation pipeline (US-04)")
    st.caption("The pipeline applies the data dictionary contract (US-03) to the customer dataset.")
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
        missing = {"cliente_id", "edad", "ingreso_mensual", "saldo_mora_30d", "score_riesgo",
                   "tipo_cliente", "activo"} - set(df.columns)
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
            t1, t2, t3, t4, t5 = st.tabs(["Pipeline report", "Record-level detail", "Clean dataset",
                                          "Score distribution", "Completeness"])
            with t1:
                st.caption("Output of `finbank.validators.validate_dataset` (messages translated for display)")
                if errors:
                    st.dataframe(pd.DataFrame([{"type": e["type"], "column": e["column"], "message": en_msg(e)}
                                               for e in errors]), hide_index=True)
                else:
                    st.success("Dataset is clean: 0 issues.")
            with t2:
                st.dataframe(viol, hide_index=True) if len(viol) else st.success("No violations.")
                if len(imp):
                    st.caption("Imputations (the null policy allows imputing `saldo_mora_30d` as 0):")
                    st.dataframe(imp, hide_index=True)
            with t3:
                st.write(f"{len(clean)} of {len(df)} records are ready for modeling.")
                st.dataframe(clean, height=240)
                st.download_button("⬇ Download clean CSV", clean.to_csv(index=False).encode(), "clean_customers.csv")
            with t4:
                fig, ax = plt.subplots(figsize=(6, 2.6))
                ax.hist(df["score_riesgo"].dropna(), bins=range(300, 900, 50), color=BLUE, edgecolor="white")
                ax.set_xlabel("Risk score (score_riesgo)"); ax.set_ylabel("Customers")
                ax.spines[["top", "right"]].set_visible(False)
                left, _ = st.columns([3, 2])
                left.pyplot(fig)
            with t5:
                comp = (1 - df[list(df.columns)].isna().mean()) * 100
                fig, ax = plt.subplots(figsize=(6, 2.8))
                ax.barh(comp.index, comp.values, color=[NAVY if v == 100 else "#C0392B" for v in comp.values])
                ax.set_xlim(0, 100); ax.set_xlabel("% of records with data"); ax.invert_yaxis()
                for i, v in enumerate(comp.values):
                    ax.text(min(v, 94), i, f"{v:.0f}%", va="center", ha="right", color="white", fontsize=8)
                ax.spines[["top", "right"]].set_visible(False)
                left, _ = st.columns([3, 2])
                left.pyplot(fig)
                st.caption("Red: columns with missing data.")

# ---------- 4. Definition of Done ----------
elif step == 3:
    st.header("Definition of Done")
    st.write("A story is **Done** when: ① its 3-item checklist is complete, ② it went through a reviewed and "
             "approved Pull Request, ③ the tests pass, and ④ the card sits in the Done column.")
    hist = pd.DataFrame([
        ["US-03 Data requirements", "Data dictionary", "PR #6", "—", "✅"],
        ["US-04 Sample data", "Synthetic dataset", "PR #5", "—", "✅"],
        ["US-04 Validators", "feat → test (red) → fix (green) → refactor", "PR #8 (refactor)",
         "089febe · ccf0bd0 · ceaa33b", "✅"],
    ], columns=["Story", "Artifact", "Pull Request", "TDD commits", "DoD"])
    st.dataframe(hist, hide_index=True)
    st.subheader("XP practices")
    cards([("Pair programming", "Driver and navigator on the diagnosis, requirements and architecture work.", ""),
           ("TDD", "A red → green → refactor cycle backed by the test suite.", ""),
           ("Continuous integration", "Feature branches and reviewed PRs before every merge.", ""),
           ("Refactoring", "Validators split into single-responsibility functions.", "")])
    st.write("")
    st.subheader("Verifiable evidence")
    st.caption("Every link opens the proof directly on GitHub.")
    e1, e2, e3 = st.columns(3)
    e1.markdown("**Reviewed pull requests**")
    e1.link_button("PR #5 · Sample dataset", f"{REPO}/pull/5")
    e1.link_button("PR #6 · Data dictionary", f"{REPO}/pull/6")
    e1.link_button("PR #8 · Validator refactor", f"{REPO}/pull/8")
    e2.markdown("**TDD cycle (commits)**")
    e2.link_button("Red · 089febe · tests", f"{REPO}/commit/089febe")
    e2.link_button("Green · ccf0bd0 · implementation", f"{REPO}/commit/ccf0bd0")
    e2.link_button("Refactor · ceaa33b", f"{REPO}/commit/ceaa33b")
    e3.markdown("**Logbook & code**")
    e3.link_button("XP logbook (pairing, tests, refactoring)", f"{REPO}/tree/main/bitacora")
    e3.link_button("Before vs. after the refactor", f"{REPO}/compare/b82764f...ceaa33b")
    e3.link_button("Full repository", REPO)
    with st.expander("Refactoring: what changed"):
        st.write("Before (b82764f), a single function ran every validation. After (ceaa33b), it was split into "
                 "single-responsibility functions with constants and type hints:")
        st.code("check_missing_columns(df)\ncheck_nulls(df)\ncheck_score_range(df, min_score, max_score)\n"
                "check_variable_types(df, expected_types)\nvalidate_dataset(df)  # orchestrates the checks and returns the report",
                language="python")
        st.write("The tests written in the red step kept passing untouched, which confirms the refactor did not "
                 "change behavior.")

# ---------- 5. Lessons ----------
else:
    st.header("Lessons learned & improvement plan")
    cards([("Start", "• Commit points based on real velocity (8–11)<br>• Break stories into tasks of 3 points or fewer<br>"
                     "• Work in parallel with agreed acceptance criteria<br>• Use <i>Co-authored-by</i> in commits", ""),
           ("Stop", "• Committing more points than our velocity allows<br>• Leaving cards for the second week<br>"
                    "• Waiting on approvals without a plan B", "stop"),
           ("Continue", "• Kanban board with a 3-item checklist<br>• Peer review before Done<br>"
                        "• Short dailies<br>• Labels by Charter phase", "cont")])
    st.write("")
    st.subheader("Why they came up and what we're doing about them")
    with st.expander("We committed to more points than we could deliver"):
        st.write("Neither of the first two sprints had a velocity history to plan against: we committed 11 and 16 "
                 "points and completed 8 and 11. For Sprint 3, our real average velocity (9.5) is the ceiling.")
    with st.expander("The Charter approval ran late"):
        st.write("Governance & Charter Approval was planned for day 10 and closed on day 16 because it depended on "
                 "an outside approval. We worked in parallel, and the impact was 1–2 working days, absorbed by the "
                 "contingency reserve. Going forward: tasks of 3 points or fewer, and a plan B for approvals.")
    with st.expander("Why Sprint 3 is 9–10 points"):
        st.write("It matches our real velocity and leaves room for carried-over work: Data Collection & Cleaning "
                 "(5 pts) was still open at the end of Sprint 2.")
    st.success("**Sprint 3:** plan 9–10 points, accounting for the pending Data Collection & Cleaning work.")
    st.write("Thanks for reviewing our work.")

# ---------- Bottom navigation ----------
st.divider()
a, _, b = st.columns([1, 4, 1])
a.button("◀ Previous", on_click=go, args=(step - 1,), disabled=step == 0)
b.button("Next ▶", on_click=go, args=(step + 1,), disabled=step == len(STEPS) - 1, type="primary")
