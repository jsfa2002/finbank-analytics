"""Cierre del proyecto - FinBank (DMS Consulting) - GMAC Corte 3. Producto final de gestión."""
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
from finbank.validators import validate_dataset  # noqa: E402  (código real del equipo, US-04)

NAVY, BLUE, LIGHT, MID, RED, GREEN = "#12335B", "#0B5FAE", "#9BB7D4", "#5C8FC7", "#C0392B", "#1E8E5A"
REPO = "https://github.com/AndresAvella09/finbank-analytics"
LOGO, DATA, EVID = ROOT / "assets" / "dms_logo.png", ROOT / "data" / "sample_clientes.csv", ROOT / "assets" / "evidence"
STEPS = ["Resumen", "Sprints", "Cronograma y presupuesto", "Demo y resultados", "Definition of Done", "Lecciones"]

st.set_page_config(page_title="DMS Consulting · Cierre FinBank", page_icon="📈", layout="wide")
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
    """Tarjetas de igual altura. items = [(título, html, clase_css)]."""
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


# ---------- Datos (del Informe Final de Gestión) ----------
SPRINTS = {
    1: dict(weeks="1–2", committed=11, completed=8, closures={6: 3, 8: 5},
            goal="Diagnóstico (US-01) y tablero ágil (US-09).",
            blocker="La aprobación del Charter (US-02) pasa al Sprint 2.",
            cols=["Historia", "Pts", "Estado"],
            rows=[["Diagnóstico del negocio y definición de objetivos", 3, "Done · día 6"],
                  ["Tablero ágil y backlog", 5, "Done · día 8"],
                  ["Definición de requisitos de datos", 3, "Pasó al Sprint 2"]]),
    2: dict(weeks="3–4", committed=16, completed=11, closures={6: 3, 7: 5, 9: 3},
            goal="Charter aprobado (US-02), requisitos de datos (US-03) y arquitectura (US-10).",
            blocker="Charter aprobado el día 16 (planeado: día 10); US-04 pasa al Sprint 3.",
            cols=["Historia", "Pts", "Estado"],
            rows=[["Gobernanza y aprobación del Charter (arrastrada)", 3, "Done · día 6"],
                  ["Definición de requisitos de datos", 5, "Done · día 7"],
                  ["Documento de arquitectura de la solución", 3, "Done · día 9"],
                  ["Recolección y limpieza de datos", 5, "Pasa al Sprint 3"]]),
    3: dict(weeks="5–6", committed=10, completed=10, closures=None,
            goal="Validación y limpieza de datos (US-04.1, US-04.2), definición de churn (US-06.1) y modelo base de morosidad "
                 "(US-05.1). La mitad del compromiso se cerró en la primera semana.",
            blocker="El extracto real de FinBank no llega (I-2); una subida directa a main sin PR (I-1) lleva a proteger la rama."),
    4: dict(weeks="7–8", committed=9, completed=9, closures=None,
            goal="Modelo de morosidad a 60 días (US-05.2) y de churn a 3 meses (US-06.2, US-06.3). Regresión logística; "
                 "AUC de 0,871 y 0,737 en validación cruzada.",
            blocker="El extracto llega el día 33, con 2 días de retraso (I-2 cerrado). Desde aquí, main exige un Approve."),
    5: dict(weeks="9–10", committed=10, completed=10, closures={2: 2, 4: 2, 6: 3, 9: 3},
            goal="Validar los dos modelos fuera de tiempo, fijar con FinBank el umbral de alerta y entregar el sistema con su "
                 "roadmap de despliegue.",
            blocker="Umbral por costo (I-4), deriva del churn en la cohorte 12 (I-5) y un PR esperando aprobación (I-6).",
            cols=["ID", "Historia", "Pts", "Pairing", "Revisor", "Cierre"],
            rows=[["US-05.3", "Umbral de alerta por costo y capacidad de cobranza, acordado con FinBank", 2, "Diego + Miguel", "Juanse", "Día 2"],
                  ["US-07.2", "Validación fuera de tiempo del modelo de churn", 2, "Diego + Juanse", "Miguel", "Día 4"],
                  ["US-07.1", "Validación fuera de tiempo del modelo de morosidad", 3, "Diego + Juanse", "Miguel", "Día 6"],
                  ["US-08", "Lista de alertas, fichas de los modelos y roadmap de despliegue", 3, "Diego + Miguel", "Juanse", "Día 9"]]),
}
MILESTONES = [  # nombre, día planeado, día real, observación
    ("A · Diagnóstico y objetivos (US-01)", 5, 6, "Sprint 1"),
    ("I · Tablero ágil operando (US-09)", 10, 8, "Criterio de éxito del Charter"),
    ("B · Charter aprobado (US-02)", 10, 16, "Absorbido con trabajo en paralelo"),
    ("C · Requisitos de datos (US-03)", 15, 17, "Arrancó en paralelo a la aprobación"),
    ("J · Arquitectura de la solución (US-10)", 15, 19, "Con holgura, fuera de la ruta crítica"),
    ("D · Datos listos para modelar (US-04)", 25, 26, "Sprint 3"),
    ("E · Modelo de morosidad (US-05)", 35, 37, "Extracto 2 días tarde (I-2)"),
    ("F · Modelo de churn (US-06)", 35, 39, "Con holgura; arrancó el día 21"),
    ("G · Validación de ambos modelos (US-07)", 45, 46, "6 días en lugar de 10, gracias a la automatización"),
    ("H · Entrega final y roadmap (US-08)", 50, 49, "Desvíos de la ruta crítica recuperados"),
    ("K · Presentación ejecutiva", 40, 56, "Con holgura; se movió al cierre para presentar los resultados finales"),
    ("Aceptación y cierre del proyecto", 60, 56, "6 de 10 días de reserva usados"),
]
BUDGET = [("1. Diagnóstico y gobernanza", 27.0, 29.5, "Sesiones adicionales por el retraso en la aprobación del Charter"),
          ("2. Requisitos y datos", 63.0, 64.0, "Día adicional en US-04"),
          ("3. Modelado y validación", 63.0, 61.5, "Validación automatizada: 6 días en lugar de 10"),
          ("4. Entrega (tarea H)", 9.0, 9.3, "Ajustes de las fichas de los modelos"),
          ("4. Reserva de contingencia (tarea L)", 18.0, 10.8, "6 de 10 días usados ($1,8M por día de equipo)")]
PRS = [(15, "feature/models-sprint4", "Diego + Juanse", "Approve de Miguel", "Extracto simulado y modelos (Sprint 4)"),
       (16, "feature/threshold-calibration", "Diego + Miguel", "Approve de Juanse", "Umbral por costo (US-05.3)"),
       (17, "feature/churn-validation", "Diego + Juanse", "Revisión de Miguel; entró con el #19", "Validación del churn y PSI (US-07.2)"),
       (18, "feature/delinquency-validation", "Diego + Juanse", "Revisión de Miguel; entró con el #19", "Validación de la morosidad (US-07.1)"),
       (19, "docs/final-delivery", "Diego + Miguel", "Approve de Juanse", "Scoring, fichas y roadmap (US-08)"),
       (20, "feature/reserve-adjustments", "Diego + Juanse", "Revisión de Miguel; entró con el #21", "Ajustes de la reserva: deriva y motivo de cada alerta"),
       (21, "docs/sprint5-closure", "Diego", "Approve de Juanse", "Bitácora del Sprint 5 y acta de cierre")]


def burndown(committed, closures):
    days, left, actual = list(range(11)), committed, []
    for d in days:
        left -= closures.get(d, 0)
        actual.append(left)
    fig, ax = plot()
    ax.plot(days, [committed * (1 - d / 10) for d in days], "--", color="gray", label="Ideal")
    ax.step(days, actual, where="post", color=BLUE, lw=2.5, label="Real")
    ax.set_xlabel("Día hábil del Sprint"); ax.set_ylabel("Puntos restantes"); ax.legend()
    return fig


def validate_records(df):
    """Detalle por registro según docs/data_dictionary.md. Devuelve (violaciones, imputaciones)."""
    v, imp = [], []

    def add(i, campo, regla):
        val = df.at[i, campo]
        v.append({"fila": i + 2, "cliente_id": df.at[i, "cliente_id"], "campo": campo,
                  "regla": regla, "valor": "(vacío)" if pd.isna(val) else str(val)})

    dup = df["cliente_id"].duplicated(keep=False)
    for i in df.index:
        r = df.loc[i]
        if pd.isna(r["cliente_id"]) or not re.fullmatch(r"C-\d{4}", str(r["cliente_id"])):
            add(i, "cliente_id", "Formato C-XXXX")
        if dup[i]:
            add(i, "cliente_id", "Debe ser único")
        if pd.isna(r["edad"]):
            add(i, "edad", "No admite nulos")
        elif not 18 <= r["edad"] <= 75:
            add(i, "edad", "Rango 18–75")
        if pd.isna(r["ingreso_mensual"]):
            add(i, "ingreso_mensual", "No admite nulos")
        elif r["ingreso_mensual"] < 0:
            add(i, "ingreso_mensual", "Debe ser >= 0")
        if pd.isna(r["saldo_mora_30d"]):
            imp.append({"fila": i + 2, "cliente_id": r["cliente_id"], "campo": "saldo_mora_30d", "acción": "Nulo imputado a 0"})
        elif r["saldo_mora_30d"] < 0:
            add(i, "saldo_mora_30d", "Debe ser >= 0")
        if pd.isna(r["score_riesgo"]):
            add(i, "score_riesgo", "No admite nulos")
        elif not 300 <= r["score_riesgo"] <= 850:
            add(i, "score_riesgo", "Rango 300–850")
        if r["tipo_cliente"] not in ("preferente", "regular"):
            add(i, "tipo_cliente", "'preferente' o 'regular'")
        if r["activo"] not in ("si", "no"):
            add(i, "activo", "'si' o 'no'")
    return pd.DataFrame(v), pd.DataFrame(imp)


# ---------- Cabecera + navegación ----------
h1, h2 = st.columns([1, 3])
if LOGO.exists():
    h1.image(str(LOGO), width=210)
h2.markdown("<div style='padding-top:14px'><span class='tag'>GMAC · Corte 3</span>"
            "<span class='tag'>Cierre del proyecto</span><span class='tag'>Grupo 3</span></div>", unsafe_allow_html=True)
h2.progress((st.session_state.step + 1) / len(STEPS), text=f"Paso {st.session_state.step + 1} de {len(STEPS)}")
for i, (col, name) in enumerate(zip(st.columns(len(STEPS)), STEPS)):
    col.button(f"{i + 1}. {name}", key=f"nav{i}", on_click=go, args=(i,),
               type="primary" if i == st.session_state.step else "secondary")
st.divider()
step = st.session_state.step

# ================= 1. Resumen =================
if step == 0:
    st.markdown("<div class='hero'><h1>De la planeación a la certeza de entregar</h1>"
                "<p>Sistema predictivo de morosidad temprana y churn para FinBank S.A. · 12 semanas · 5 Sprints</p></div>",
                unsafe_allow_html=True)
    st.write("")
    kpis([("48 / 48 pts", "Puntos del backlog entregados (100 %)"), ("9,6 pts", "Velocidad promedio de los 5 Sprints"),
          ("Día 56", "Cierre en la semana 12; 6 de 10 días de reserva usados"), ("$175,1M COP", "Costo final frente a $180M (−2,7 %)")])
    st.write("")
    left, right = st.columns([2, 3])
    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    ax.pie([58800, 18200], labels=["Morosidad\n$58.800M", "Churn\n$18.200M"], colors=[NAVY, BLUE], startangle=90,
           wedgeprops=dict(width=.42, edgecolor="white"), textprops={"fontsize": 8})
    ax.text(0, 0, "$77.000M\nen riesgo", ha="center", va="center", fontsize=9, color=NAVY, fontweight="bold")
    left.pyplot(fig)
    right.markdown("**El problema.** FinBank administra una cartera de $420.000M COP con 125.000 clientes y no tiene una alerta "
                   "temprana para los clientes que van a caer en mora (30–60 días) ni para los preferentes que se van a ir "
                   "(con 3 meses de anticipación). Planeamos, ejecutamos y hoy cerramos el proyecto que resuelve ambos, "
                   "a tiempo y dentro del presupuesto.")
    with right:
        cards([("Corte 1 · Planear", "Charter, 4 fases CRISP-DM, ruta crítica, 10 días de reserva y un backlog de 48 puntos.", ""),
               ("Corte 2 · Ejecutar", "Scrum + XP en los Sprints 1 y 2: 8 y 11 puntos. Comprometimos de más y aprendimos a planear con la velocidad real.", ""),
               ("Corte 3 · Cerrar", "Sprints 3 a 5 al 100 %: modelos validados, umbral acordado y roadmap entregado.", "")])
    st.write("")
    cards([("Diego Andrés Avella", "Project Lead / Product Owner", ""), ("Miguel Ángel Hernández", "Business Analyst", ""),
           ("Juan Sebastián Fajardo", "Scrum Facilitator / Scrum Master", "")])
    st.caption("Los días de cierre, las dailies y los costos ejecutados se simularon a partir del tablero, del historial del "
               "repositorio y de las horas del equipo, como se declara en el Informe Final de Gestión.")
    st.write("")
    st.button("Comenzar recorrido ▶", on_click=go, args=(1,), type="primary")

# ================= 2. Sprints =================
elif step == 1:
    st.header("Resultados de los Sprints")
    view = st.radio("Vista", ["Todos los Sprints", "Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"], horizontal=True)
    if view == "Todos los Sprints":
        c1, c2, c3 = st.columns(3)
        c1.metric("Backlog entregado", "48 / 48 pts", "100 %")
        c2.metric("Velocidad promedio", "9,6 pts", "desv. estándar 1,1", delta_color="off")
        c3.metric("Comprometido → completado", "56 → 48 pts", "8 pts se cerraron en el Sprint siguiente", delta_color="off")
        fig, ax = plot(7, 3)
        xs = range(5)
        ax.bar([i - .19 for i in xs], [SPRINTS[n]["committed"] for n in SPRINTS], .38, color=LIGHT, label="Comprometido")
        ax.bar([i + .19 for i in xs], [SPRINTS[n]["completed"] for n in SPRINTS], .38, color=BLUE, label="Completado (velocidad)")
        ax.axhline(9.6, ls="--", color="gray", lw=1); ax.text(4.55, 9.9, "promedio 9,6", fontsize=8, color="gray", ha="right")
        ax.set_xticks(list(xs), [f"Sprint {n}\n({round(100 * s['completed'] / s['committed'])} %)" for n, s in SPRINTS.items()])
        ax.set_ylabel("Puntos de historia"); ax.legend(loc="upper right", fontsize=8)
        st.pyplot(fig)
        st.info("**El resultado de gestión es la predictibilidad.** Tras la retrospectiva del Corte 2, el equipo dejó de comprometer "
                "más de lo que su velocidad respaldaba: tres Sprints seguidos cerraron al 100 %. Solo cuentan los puntos de las "
                "historias que llegaron a Done.")
    else:
        n = int(view[-1]); s = SPRINTS[n]
        st.markdown(f"**Semanas {s['weeks']}** · **Objetivo:** {s['goal']}")
        c1, c2 = st.columns(2)
        c1.metric("Puntos completados", f"{s['completed']} pts", f"de {s['committed']} comprometidos", delta_color="off")
        c2.metric("Cumplimiento", f"{round(100 * s['completed'] / s['committed'])} %")
        st.markdown(f"**Impedimento principal:** {s['blocker']}")
        if s["closures"]:
            left, right = st.columns([3, 2]) if n != 5 else (st.container(), st.container())
            left.pyplot(burndown(s["committed"], s["closures"]))
            right.dataframe(pd.DataFrame(s["rows"], columns=s["cols"]), hide_index=True)
            if n == 5:
                st.caption("Meseta de los días 6 a 8: el PR de US-08 quedó listo el día 8, pero con main protegida esperó el Approve "
                           "del revisor (I-6). Done el día 9.")
        else:
            st.info("El detalle por historia de este Sprint está en la bitácora.")
            st.link_button("Abrir la bitácora", f"{REPO}/tree/main/bitacora")

# ================= 3. Cronograma y presupuesto =================
elif step == 2:
    st.header("Cronograma y presupuesto: línea base frente a ejecución")
    t1, t2, t3, t4 = st.tabs(["Hitos", "Reserva de contingencia", "Presupuesto por fase", "Valor ganado"])
    with t1:
        fig, ax = plot(7.5, 4.2)
        for i, (name, plan, real, _) in enumerate(MILESTONES):
            ax.plot([plan, real], [i, i], color=LIGHT, lw=3, zorder=1)
            ax.scatter(plan, i, color="#B8B8B0", s=45, zorder=2)
            ax.scatter(real, i, color=BLUE if real <= plan else NAVY, s=45, zorder=3)
        ax.set_yticks(range(len(MILESTONES)), [m[0] for m in MILESTONES], fontsize=8); ax.invert_yaxis()
        ax.axvline(56, color=RED, lw=1, ls=":"); ax.text(56.5, 11.4, "cierre\ndía 56", fontsize=7, color=RED)
        ax.set_xlabel("Día hábil del proyecto (5 días = 1 semana; 60 días = 12 semanas)")
        ax.scatter([], [], color="#B8B8B0", label="Línea base (Charter)"); ax.scatter([], [], color=NAVY, label="Real")
        ax.legend(fontsize=8, loc="lower left")
        st.pyplot(fig)
        st.dataframe(pd.DataFrame([[m, p, r, f"{r - p:+d}", note] for m, p, r, note in MILESTONES],
                     columns=["Hito", "Día planeado", "Día real", "Desvío", "Observación"]), hide_index=True)
        st.info("Las tareas A–H de la ruta crítica terminaron el día 49, uno antes de la línea base: la validación automatizada "
                "tomó 6 días en lugar de 10.")
    with t2:
        cards([("Días 51–54 · Deriva del churn (I-5)", "Riesgo de calidad de datos del Charter. La deriva está aislada en la cohorte 12 y viene con "
                "un aumento real del churn (16,8 %) que el modelo reproduce (17,5 %). Es un cambio de comportamiento, no un error de "
                "datos: el modelo se mantiene, con monitoreo mensual del PSI (PR #20).", ""),
               ("Días 55–56 · Reporte de alertas", "Riesgo de alineación con el cliente del Charter. Cada alerta ahora indica su motivo principal y el "
                "comité de FinBank recibe un resumen por prioridad y motivo (PR #20). El día 56 FinBank aceptó los entregables y se "
                "firmó el acta de cierre (PR #21).", ""),
               ("4 días de reserva sin usar", "La reserva se usó solo para riesgos identificados, y los 4 días sobrantes se reportan en lugar de "
                "gastarse. El proyecto cerró en la semana 12 sin mover la fecha comprometida.", "cont")])
    with t3:
        c1, c2, c3 = st.columns(3)
        c1.metric("Costo final", "$175,1M", "−$4,9M frente a $180M (−2,7 %)", delta_color="off")
        c2.metric("Trabajo A–H", "$164,3M", "+$2,3M frente a $162,0M (+1,4 %)", delta_color="off")
        c3.metric("Reserva usada", "$10,8M", "de $18,0M", delta_color="off")
        fig, ax = plot(7, 3)
        xs = range(len(BUDGET))
        ax.bar([i - .19 for i in xs], [b[1] for b in BUDGET], .38, color=LIGHT, label="Presupuesto (Charter)")
        ax.bar([i + .19 for i in xs], [b[2] for b in BUDGET], .38, color=BLUE, label="Ejecutado")
        ax.set_xticks(list(xs), [b[0].replace(" (", "\n(").replace(" y ", " y\n") for b in BUDGET], fontsize=7)
        ax.set_ylabel("COP millones"); ax.legend(fontsize=8)
        st.pyplot(fig)
        fm = lambda x: f"${x:.1f}M".replace(".", ",")
        st.dataframe(pd.DataFrame([[b[0], fm(b[1]), fm(b[2]), f"{b[2] - b[1]:+.1f}M".replace(".", ","), b[3]] for b in BUDGET],
                     columns=["Fase", "Presupuesto", "Ejecutado", "Variación", "Causa"]), hide_index=True)
        st.caption("El total quedó por debajo del presupuesto porque solo se usaron 6 de los 10 días de reserva, no porque el trabajo "
                   "fuera más eficiente. Así se reporta a FinBank.")
    with t4:
        c1, c2 = st.columns(2)
        c1.metric("SPI al final de A–H", "1,00", "cronograma exactamente en línea base", delta_color="off")
        c2.metric("CPI al final de A–H", "0,986", "+1,4 % de sobrecosto, heredado de la gobernanza", delta_color="off")
        wk = [0, 6, 8, 10]
        fig, ax = plot(6.5, 3)
        ax.plot(wk, [0, 105.75, 137.25, 162.0], "--", color="gray", marker="o", label="PV (valor planeado)")
        ax.plot(wk, [0, 105.0, 132.0, 162.0], color=BLUE, marker="o", lw=2, label="EV (valor ganado)")
        ax.plot(wk, [0, 107.0, 137.6, 164.3], color="#E8643C", marker="o", label="AC (costo real)")
        ax.set_xlabel("Semana del proyecto (cortes en las semanas 6, 8 y 10)"); ax.set_ylabel("COP millones (acumulado)"); ax.legend(fontsize=8)
        half(fig)
        st.dataframe(pd.DataFrame([["PV", "$105,75M", "$137,25M", "$162,0M"], ["EV", "$105,0M", "$132,0M", "$162,0M"],
                                   ["AC", "$107,0M", "$137,6M", "$164,3M"], ["SPI = EV / PV", "0,99", "0,96", "1,00"],
                                   ["CPI = EV / AC", "0,98", "0,96", "0,986"]],
                     columns=["Indicador", "Semana 6", "Semana 8", "Semana 10 (fin A–H)"]), hide_index=True)
        st.caption("El valor ganado usa la regla 0/100, coherente con la velocidad: una historia aporta su valor solo cuando llega a "
                   "Done. El atraso por los datos de la semana 8 se recuperó en la validación.")

# ================= 4. Demo y resultados =================
elif step == 3:
    st.header("Demo y resultados")
    mode = st.radio("Quiero ver", ["Demo en vivo: pipeline de validación de datos", "Resultados finales de los modelos"], horizontal=True)
    if mode.startswith("Demo"):
        st.caption("El pipeline aplica el contrato del diccionario de datos (US-03) a la base de clientes con los validadores del equipo (US-04).")
        st.subheader("① Elige los datos")
        source = st.radio("¿Con qué datos?", ["Muestra sintética del repositorio", "Subir mi CSV"], horizontal=True)
        upload = st.file_uploader("CSV de clientes", type="csv") if source == "Subir mi CSV" else None
        df = pd.read_csv(upload) if upload else (pd.read_csv(DATA) if source.startswith("Muestra") else None)
        if df is not None:
            st.dataframe(df, height=200)
        else:
            st.info("Sube un archivo para continuar.")
        st.subheader("② Ejecuta la validación")
        if st.button("▶ Ejecutar validación", type="primary", disabled=df is None):
            st.session_state.ran = True
        if df is not None and st.session_state.get("ran"):
            st.subheader("③ Resultados")
            missing = {"cliente_id", "edad", "ingreso_mensual", "saldo_mora_30d", "score_riesgo", "tipo_cliente", "activo"} - set(df.columns)
            if missing:
                st.error(f"Faltan columnas del contrato: {sorted(missing)}")
            else:
                errors = validate_dataset(df)["errors"]
                viol, imp = validate_records(df)
                bad_ids = set(viol["cliente_id"]) if len(viol) else set()
                clean = df.copy()
                clean["saldo_mora_30d"] = clean["saldo_mora_30d"].fillna(0)
                clean = clean[~clean["cliente_id"].isin(bad_ids)]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Registros", len(df)); c2.metric("Inconsistencias", len(errors))
                c3.metric("Registros con error", len(bad_ids)); c4.metric("Listos para modelar", len(clean))
                a, b, c, d, e = st.tabs(["Reporte del pipeline", "Detalle por registro", "Base limpia", "Distribución del score", "Completitud"])
                with a:
                    st.caption("Salida de `finbank.validators.validate_dataset`")
                    if errors:
                        st.dataframe(pd.DataFrame([{"tipo": x["type"], "columna": x["column"], "mensaje": x["message"]} for x in errors]), hide_index=True)
                    else:
                        st.success("Base íntegra: 0 inconsistencias.")
                with b:
                    st.dataframe(viol, hide_index=True) if len(viol) else st.success("Sin violaciones.")
                    if len(imp):
                        st.caption("Imputaciones (la política de nulos permite imputar `saldo_mora_30d` como 0):")
                        st.dataframe(imp, hide_index=True)
                with c:
                    st.write(f"{len(clean)} de {len(df)} registros quedan listos para modelar.")
                    st.dataframe(clean, height=240)
                    st.download_button("⬇ Descargar CSV limpio", clean.to_csv(index=False).encode(), "clientes_limpio.csv")
                with d:
                    fig, ax = plot(6, 2.6)
                    ax.hist(df["score_riesgo"].dropna(), bins=range(300, 900, 50), color=BLUE, edgecolor="white")
                    ax.set_xlabel("Score de riesgo (score_riesgo)"); ax.set_ylabel("Clientes")
                    half(fig)
                with e:
                    comp = (1 - df.isna().mean()) * 100
                    fig, ax = plot(6, 2.8)
                    ax.barh(comp.index, comp.values, color=[NAVY if v == 100 else RED for v in comp.values])
                    ax.set_xlim(0, 100); ax.set_xlabel("% de registros con dato"); ax.invert_yaxis()
                    for i, v in enumerate(comp.values):
                        ax.text(min(v, 94), i, f"{v:.0f} %", va="center", ha="right", color="white", fontsize=8)
                    half(fig)
                    st.caption("En rojo: columnas con datos faltantes.")
    else:
        st.caption("Validación fuera de tiempo en las cohortes 11 y 12 (datos que los modelos nunca vieron). Los reportes completos están en `reports/` del repositorio.")
        kpis([("0,855", "AUC de morosidad a 60 días (regla de solo score: 0,822)"), ("0,786", "AUC de churn a 3 meses (lift 2,5 en el 20 % de mayor riesgo)"),
              ("61,5 %", "De los morosos detectados alertando solo al 13,6 % de la cartera"), ("−47,3 %", "De costo esperado frente a no usar modelo")])
        st.write("")
        left, right = st.columns(2)
        fig, ax = plot(4.4, 3)
        ax.bar(["Regla de\nsolo score", "Modelo de\nmorosidad"], [0.822, 0.855], color=[LIGHT, BLUE])
        ax.axhline(0.80, ls="--", color=RED, lw=1); ax.text(1.45, 0.805, "aceptación 0,80", fontsize=7, color=RED, ha="right")
        ax.set_ylim(0.5, 0.9); ax.set_ylabel("AUC fuera de tiempo"); ax.set_title("Morosidad a 60 días", fontsize=9)
        left.pyplot(fig)
        fig, ax = plot(4.4, 3)
        ax.bar(["Azar", "Modelo de\nchurn"], [0.5, 0.786], color=[LIGHT, BLUE])
        ax.axhline(0.70, ls="--", color=RED, lw=1); ax.text(1.45, 0.705, "aceptación 0,70", fontsize=7, color=RED, ha="right")
        ax.set_ylim(0.4, 0.9); ax.set_title("Churn a 3 meses", fontsize=9)
        right.pyplot(fig)
        st.dataframe(pd.DataFrame([
            ["Regla de alerta", "Probabilidad ≥ 0,09", "20 % de mayor riesgo"],
            ["Casos detectados", "61,5 % de los morosos con 13,6 % de alertas", "50 % del churn en el 20 % alertado"],
            ["Estabilidad (PSI del puntaje)", "0,012 (estable)", "0,231 (monitorear)"],
            ["Alertas entregadas (cohorte 12)", "62 alertas de mora", "24 alertas de retención"]],
            columns=["Indicador", "Morosidad · 60 días", "Churn · 3 meses"]), hide_index=True)
        st.info("Ambos modelos superan su umbral de aceptación y agregan valor sobre lo que el banco ya usa. La deriva del churn "
                "(PSI 0,231) se investigó en la reserva: refleja un cambio real de comportamiento, por eso se recomienda monitorear el PSI cada mes.")

# ================= 5. Definition of Done =================
elif step == 4:
    st.header("Definition of Done: cumplimiento en el Sprint 5")
    st.write("Una historia está **Done** cuando: ① su checklist de 3 ítems está completo, ② su PR fue aprobado y mezclado por un "
             "integrante distinto a sus autores y co-autores, ③ las pruebas pasan sin fallos y ④ la tarjeta está en Done. Desde el "
             "Sprint 4, la revisión por pares la fuerza la configuración del repositorio.")
    st.dataframe(pd.DataFrame([
        ["US-05.3", "Sí", "Sí (#16, Juanse)", "Sí (35/35)", "Día 2"],
        ["US-07.2", "Sí", "Parcial (#17: revisión de Miguel; entró con el #19)", "Sí (40/40)", "Día 4"],
        ["US-07.1", "Sí", "Parcial (#18: revisión de Miguel; entró con el #19)", "Sí (45/45)", "Día 6"],
        ["US-08", "Sí", "Sí (#19, Juanse)", "Sí (49/49)", "Día 9"]],
        columns=["Historia", "Checklist 3/3", "PR aprobado y mezclado por un par", "Pruebas en verde", "Tarjeta en Done"]), hide_index=True)
    st.warning("**Se reporta tal como quedó en GitHub.** Los PR del Sprint 5 estaban apilados y se mezclaron fuera de orden: el #17, el #18 "
               "y el #20 entraron dentro del #19 y del #21, sin su propio Approve. Miguel revisó los tres con un comentario, pero la "
               "aprobación formal no quedó registrada. El contenido sí pasó por la revisión de un par: el #19 y el #21 tienen el Approve "
               "de Juanse, y el PR #22 lo deja registrado. Lección: mezclar los PR apilados en orden.")
    st.subheader("Pull Requests de los Sprints 4 y 5 y del cierre")
    md = "| PR | Rama | Pairing | Revisión | Contenido |\n|---|---|---|---|---|\n" + "\n".join(
        f"| [#{n}]({REPO}/pull/{n}) | `{b}` | {p} | {r} | {c} |" for n, b, p, r, c in PRS)
    st.markdown(md)
    st.caption("4 de 7 PR con Approve formal (#15, #16, #19 y #21). Registro completo en bitacora/prs.md.")
    st.subheader("XP en la práctica")
    cards([("Pair programming", "Cada historia tuvo una pareja y un revisor distinto; los commits llevan <i>Co-authored-by</i>.", ""),
           ("TDD", "Primero las pruebas (<i>test: … (red)</i>) y después la funcionalidad. 53 pruebas automáticas, todas en verde.", ""),
           ("Integración continua", "Una rama y un PR por historia. La rama main está protegida desde el Sprint 4.", ""),
           ("Diseño simple", "Funciones de una sola responsabilidad; validadores refactorizados sin cambiar sus pruebas.", "")])
    st.write("")
    st.subheader("Evidencia")
    ev = [("Revisión por pares", "pr16_approval.png", "Aprobación formal de Juanse en el PR #16 (US-05.3), del que no es autor."),
          ("Pairing y TDD", "pair_commits_tdd.png", "Commits co-autorados y ciclo rojo → verde (US-07.1)."),
          ("53 pruebas", "pytest_53.png", "La suite automática completa en verde."),
          ("Ejecución del pipeline", "pipeline_run.png", "Entrenamiento, umbral, validación y alertas."),
          ("PR mezclados", "merged_prs.png", "Pull Requests cerrados al final del proyecto.")]
    for tab, (name, fname, cap) in zip(st.tabs([e[0] for e in ev]), ev):
        with tab:
            if (EVID / fname).exists():
                st.image(str(EVID / fname), caption=cap)
            else:
                st.info(f"Agrega assets/evidence/{fname} para mostrar esta captura.")
    c1, c2, c3 = st.columns(3)
    c1.link_button("Repositorio completo", REPO)
    c2.link_button("Bitácora", f"{REPO}/tree/main/bitacora")
    c3.link_button("Todos los Pull Requests", f"{REPO}/pulls?q=is%3Apr")

# ================= 6. Lecciones =================
else:
    st.header("Retrospectiva y lecciones aprendidas")
    st.subheader("¿Cumplimos los acuerdos de la retrospectiva del Sprint 3?")
    st.dataframe(pd.DataFrame([
        ["Proteger main con 1 aprobación obligatoria", "Activo desde el Sprint 4; 4 de 7 PR tienen Approve y 3 entraron apilados", "Parcial"],
        ["Pedir los datos con un Sprint de anticipación", "Se pidieron en el Sprint 3; llegaron 2 días tarde sin frenar el Sprint 4", "Sí"],
        ["Registrar los impedimentos externos con fecha", "I-2, I-4 e I-5 registrados con su día de detección", "Sí"],
        ["Comprometer según la velocidad, con historias de 3 pts o menos", "9 y 10 pts, historias de 2–3 pts, 100 % de cumplimiento", "Sí"],
        ["No dejar la bitácora para el último día", "La bitácora del Sprint 5 se cerró el día del cierre del proyecto", "Parcial"]],
        columns=["Acuerdo", "Evidencia en los Sprints 4 y 5", "Cumplido"]), hide_index=True)
    st.write("")
    cards([("Lo que funcionó", "• Planear con la velocidad real: el compromiso coincidió con la capacidad en los tres últimos Sprints<br>"
                               "• Automatizar temprano (pipeline y 53 pruebas): la validación tomó 6 días en lugar de 10<br>"
                               "• Checkpoints de riesgo con el cliente: el de umbrales evitó entregar un punto de corte que FinBank no iba a usar<br>"
                               "• Usar la reserva solo para riesgos identificados", "cont"),
           ("Lo que mejoraríamos", "• Formalizar desde el día 1 un acuerdo de entrega de datos con el cliente<br>"
                                   "• Activar la protección de la rama desde el primer Sprint, no después de una desviación<br>"
                                   "• Medir la estabilidad (PSI) desde el primer modelo<br>"
                                   "• Llevar la bitácora al día y mezclar los PR apilados en orden", "stop")])
    st.subheader("Lecciones de gestión")
    lessons = [("La velocidad real es una herramienta de planeación, no un reporte", "En el Corte 2 se comprometieron 13,5 puntos en promedio y se entregaron 9,5. Desde el Sprint 3 se planeó con el dato real y se cumplió al 100 %."),
               ("La automatización es una decisión de cronograma", "Las pruebas y el pipeline parecían un costo extra en los Sprints 2 y 3, pero fueron la razón por la que el proyecto recuperó sus desvíos en el Sprint 5."),
               ("Las dependencias se gestionan con criterios de aceptación, no esperando", "Acordar los contratos de antemano (diccionario de datos, definición de churn, criterios de cada historia) permitió avanzar en paralelo en todas las fases."),
               ("Una regla de equipo que no está automatizada, se rompe", "La subida directa a main del Sprint 3 llevó a proteger la rama. Desde entonces la revisión por pares es verificable y no depende de la disciplina individual."),
               ("La reserva de contingencia es para riesgos, no para holgura", "Se usó solo cuando ocurrieron riesgos identificados en el Charter, y se reportan los 4 días no usados en lugar de gastarlos."),
               ("Coordinación interdisciplinaria", "La rotación de roles (piloto/copiloto y revisor) llevó el criterio de negocio al código: Miguel aportó la matriz de costos del umbral y Juanse el suavizado del PSI para las cohortes pequeñas.")]
    for t, d in lessons:
        with st.expander(t):
            st.write(d)
    st.subheader("Recomendaciones para la implementación")
    st.caption("El Charter excluye la puesta en producción. El roadmap entregado (docs/entrega/) le recomienda a FinBank cuatro fases:")
    cards([("Reentrenar con datos productivos · 3 semanas", "Repetir el desarrollo y la validación dentro de la infraestructura del banco. Se avanza si el AUC fuera de tiempo es ≥ 0,80 en morosidad y ≥ 0,70 en churn, y el PSI < 0,10.", ""),
           ("Piloto controlado · 8 semanas", "Aplicar las alertas en una regional, con un grupo de control, para medir la reducción real de la mora a 60 días y del churn.", ""),
           ("Integración · 6 semanas", "Automatizar el scoring mensual y conectarlo al core bancario y al CRM de cobranza y retención.", ""),
           ("Operación y gobierno", "Monitoreo mensual del PSI, recalibración trimestral, un dueño de negocio por modelo y un acuerdo formal de entrega de datos.", "")])
    st.write("")
    st.success("**Conclusión.** El proyecto cerró el día 56, dentro de las 12 semanas del Charter, con el 100 % del alcance entregado y aceptado "
               "por FinBank, y con un costo de $175,1M frente a los $180M presupuestados. Scrum dio la cadencia para detectar cada "
               "desviación dentro del Sprint en que ocurrió, y XP dio la calidad técnica que hizo posible recuperar el cronograma. "
               "Para atacar los $77.000M en riesgo, el siguiente paso es el reentrenamiento con datos productivos y el piloto controlado.")
    st.write("Gracias por revisar nuestro trabajo.")

# ---------- Navegación inferior ----------
st.divider()
a, _, b = st.columns([1, 4, 1])
a.button("◀ Anterior", on_click=go, args=(step - 1,), disabled=step == 0)
b.button("Siguiente ▶", on_click=go, args=(step + 1,), disabled=step == len(STEPS) - 1, type="primary")
