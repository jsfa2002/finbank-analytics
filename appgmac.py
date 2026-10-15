"""Sprint Review & Demo Operacional - FinBank (DMS Consulting) - GMAC Corte 2, Producto C."""
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

NAVY, BLUE, LIGHT = "#12335B", "#0B5FAE", "#9BB7D4"
REPO = "https://github.com/AndresAvella09/finbank-analytics"  # confirmar que es el repo oficial
LOGO, DATA = ROOT / "assets" / "dms_logo.png", ROOT / "data" / "sample_clientes.csv"
PASOS = ["Inicio", "Sprints", "Demo", "Definition of Done", "Lecciones"]

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

st.session_state.setdefault("paso", 0)


def ir(i):
    st.session_state.paso = max(0, min(len(PASOS) - 1, i))


# ---------- Datos ----------
SPRINTS = {
    "Sprint 1": {
        "meta": "Completar el diagnóstico, dejar el Charter listo para aprobación e implementar el tablero ágil.",
        "comprometidos": 11, "completados": 8, "cierres": {6: 3, 8: 5},
        "historias": [["Business Diagnosis & Goal Definition", 3, "✅ Done · día 6"],
                      ["Agile Board & Backlog Setup", 5, "✅ Done · día 8"],
                      ["Data Requirements Definition", 3, "⏳ Pasó al Sprint 2"]],
    },
    "Sprint 2": {
        "meta": "Cerrar gobierno, definir requisitos de datos y arquitectura, y arrancar recolección y limpieza.",
        "comprometidos": 16, "completados": 11, "cierres": {6: 3, 7: 5, 9: 3},
        "historias": [["Governance & Charter Approval (arrastrada)", 3, "✅ Done · día 6"],
                      ["Data Requirements Definition", 5, "✅ Done · día 7"],
                      ["Solution Architecture Document", 3, "✅ Done · día 9"],
                      ["Data Collection & Cleaning", 5, "⏳ Pasa al Sprint 3"]],
    },
}


def cards(items):
    """Tarjetas en grilla: todas de la misma altura. items = [(título, html, clase)]."""
    html = "".join(f"<div class='card {c}'><h4>{t}</h4>{d}</div>" for t, d, c in items)
    st.markdown(f"<div class='grid'>{html}</div>", unsafe_allow_html=True)


def burndown(nombre):
    s = SPRINTS[nombre]
    dias, real, rest = list(range(11)), [], s["comprometidos"]
    for d in dias:
        rest -= s["cierres"].get(d, 0)
        real.append(rest)
    fig, ax = plt.subplots(figsize=(6, 2.8))
    ax.plot(dias, [s["comprometidos"] * (1 - d / 10) for d in dias], "--", color="gray", label="Ideal")
    ax.step(dias, real, where="post", color=BLUE, lw=2.5, label="Real")
    ax.set_xlabel("Día hábil"); ax.set_ylabel("Puntos restantes"); ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def validar(df):
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
            imp.append({"fila": i + 2, "cliente_id": r["cliente_id"], "campo": "saldo_mora_30d",
                        "acción": "Nulo imputado a 0"})
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


# ---------- Cabecera + navegación por pasos ----------
h1, h2 = st.columns([1, 3])
if LOGO.exists():
    h1.image(str(LOGO), width=210)
h2.markdown("<div style='padding-top:14px'><span class='tag'>GMAC · Corte 2</span>"
            "<span class='tag'>Producto C</span><span class='tag'>Sprint Review & Demo</span></div>",
            unsafe_allow_html=True)
h2.progress((st.session_state.paso + 1) / len(PASOS), text=f"Paso {st.session_state.paso + 1} de {len(PASOS)}")
for i, (col, nombre) in enumerate(zip(st.columns(len(PASOS)), PASOS)):
    col.button(f"{i + 1}. {nombre}", key=f"nav{i}", on_click=ir, args=(i,),
               type="primary" if i == st.session_state.paso else "secondary")
st.divider()
paso = st.session_state.paso

# ---------- 1. Inicio ----------
if paso == 0:
    st.markdown("<div class='hero'><h1>Ejecución ágil del proyecto predictivo FinBank</h1>"
                "<p>Scrum + XP · 2 sprints · incremento entregado a FinBank S.A.</p></div>", unsafe_allow_html=True)
    st.write("")
    kpis = [("$420,000M COP", "Cartera administrada"), ("125,000", "Clientes"),
            ("$77,000M COP", "Exposición a morosidad y churn"), ("12 semanas", "Plan CRISP-DM")]
    st.markdown("<div class='grid'>" + "".join(f"<div class='kpi'><b>{v}</b><span>{t}</span></div>" for v, t in kpis)
                + "</div>", unsafe_allow_html=True)
    st.write("")
    izq, der = st.columns([2, 3])
    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    ax.pie([58800, 18200], labels=["Morosidad\n$58,800M", "Churn\n$18,200M"], colors=[NAVY, BLUE],
           startangle=90, wedgeprops=dict(width=.42, edgecolor="white"), textprops={"fontsize": 8})
    ax.text(0, 0, "$77,000M\nexposición", ha="center", va="center", fontsize=9, color=NAVY, fontweight="bold")
    izq.pyplot(fig)
    der.markdown("**Este recorrido te guía en 4 pasos.** Usa los botones de arriba o *Siguiente* para avanzar.")
    with der:
        cards([("2 · Sprints", "Velocity, historias y burndown de cada sprint.", ""),
               ("3 · Demo", "El pipeline de validación de datos corriendo en vivo.", ""),
               ("4 · Definition of Done", "Evidencia: PRs, TDD y prácticas XP.", ""),
               ("5 · Lecciones", "Retrospectiva y plan del Sprint 3.", "")])
    st.write("")
    st.button("Comenzar recorrido ▶", on_click=ir, args=(1,), type="primary")

# ---------- 2. Sprints ----------
elif paso == 1:
    st.header("Resultados de los sprints")
    vista = st.radio("¿Qué quieres ver?", ["Sprint 1", "Sprint 2", "Comparación"], horizontal=True)
    if vista == "Comparación":
        c1, c2, c3 = st.columns(3)
        c1.metric("Velocity Sprint 1", "8 pts", "de 11 comprometidos")
        c2.metric("Velocity Sprint 2", "11 pts", "de 16 comprometidos")
        c3.metric("Velocity promedio", "9.5 pts")
        fig, ax = plt.subplots(figsize=(6, 2.6))
        x = [0, 1]
        ax.bar([i - .18 for i in x], [11, 16], .36, color=LIGHT, label="Comprometidos")
        ax.bar([i + .18 for i in x], [8, 11], .36, color=BLUE, label="Completados")
        ax.set_xticks(x, ["Sprint 1", "Sprint 2"]); ax.set_ylabel("Puntos"); ax.legend()
        ax.spines[["top", "right"]].set_visible(False)
        izq, _ = st.columns([3, 2])
        izq.pyplot(fig)
        p1, p2 = st.columns(2)
        p1.progress(8 / 11, text="Sprint 1 · 73% de lo comprometido")
        p2.progress(11 / 16, text="Sprint 2 · 69% de lo comprometido")
        st.markdown("**Hoja de ruta del proyecto (12 semanas)**")
        fases = [("1 · Diagnóstico y gobierno", 1, 2, NAVY), ("2 · Requisitos y datos", 3, 3, BLUE),
                 ("3 · Modelado", 6, 4, "#5C8FC7"), ("4 · Validación y despliegue", 10, 3, LIGHT)]
        fig, ax = plt.subplots(figsize=(7, 2.3))
        for i, (n, ini, dur, col) in enumerate(fases):
            ax.barh(i, dur, left=ini - 1, color=col, edgecolor="white")
            ax.text(ini - 1 + dur / 2, i, f"sem {ini}–{ini + dur - 1}", ha="center", va="center",
                    color="white" if col != LIGHT else NAVY, fontsize=8)
        ax.set_yticks(range(4), [f[0] for f in fases], fontsize=8); ax.invert_yaxis()
        ax.set_xticks(range(0, 13, 2)); ax.set_xlabel("Semana")
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig)
        st.info("**Desvío clave:** *Governance & Charter Approval* se planeó para el día 10 y cerró el día 16. "
                "Se trabajó en paralelo y el impacto fue de 1–2 días hábiles, absorbido por la reserva de "
                "contingencia (10 días).")
    else:
        s = SPRINTS[vista]
        st.markdown(f"**Meta del sprint:** {s['meta']}")
        c1, c2 = st.columns(2)
        c1.metric("Puntos completados", f"{s['completados']} pts", f"de {s['comprometidos']} comprometidos")
        c2.metric("Historias terminadas", f"{sum('✅' in h[2] for h in s['historias'])} de {len(s['historias'])}")
        izq, der = st.columns([3, 2])
        izq.pyplot(burndown(vista))
        der.dataframe(pd.DataFrame(s["historias"], columns=["Historia", "Pts", "Estado"]), hide_index=True)

# ---------- 3. Demo ----------
elif paso == 2:
    st.header("Demo: pipeline de validación de datos (US-04)")
    st.caption("El pipeline aplica el contrato del diccionario de datos (US-03) a la base de clientes.")
    st.subheader("① Elige los datos")
    origen = st.radio("¿Con qué datos?", ["Muestra sintética del repo", "Subir mi CSV"], horizontal=True)
    archivo = st.file_uploader("CSV de clientes", type="csv") if origen == "Subir mi CSV" else None
    df = pd.read_csv(archivo) if archivo else (pd.read_csv(DATA) if origen.startswith("Muestra") else None)
    if df is not None:
        st.dataframe(df, height=200)
    else:
        st.info("Sube un archivo para continuar.")

    st.subheader("② Ejecuta la validación")
    if st.button("▶ Ejecutar validación", type="primary", disabled=df is None):
        st.session_state.ejecutado = True

    if df is not None and st.session_state.get("ejecutado"):
        st.subheader("③ Resultados")
        faltan = {"cliente_id", "edad", "ingreso_mensual", "saldo_mora_30d", "score_riesgo",
                  "tipo_cliente", "activo"} - set(df.columns)
        if faltan:
            st.error(f"Faltan columnas del contrato: {sorted(faltan)}")
        else:
            errores = validate_dataset(df)["errors"]
            viol, imp = validar(df)
            ids_malos = set(viol["cliente_id"]) if len(viol) else set()
            limpio = df.copy()
            limpio["saldo_mora_30d"] = limpio["saldo_mora_30d"].fillna(0)
            limpio = limpio[~limpio["cliente_id"].isin(ids_malos)]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Registros", len(df)); c2.metric("Inconsistencias", len(errores))
            c3.metric("Registros con error", len(ids_malos)); c4.metric("Pasan a modelado", len(limpio))
            t1, t2, t3, t4, t5 = st.tabs(["Reporte del pipeline", "Detalle por registro", "Base limpia", "Distribución de score", "Completitud"])
            with t1:
                st.caption("Salida de `finbank.validators.validate_dataset`")
                if errores:
                    st.dataframe(pd.DataFrame(errores), hide_index=True)
                else:
                    st.success("Dataset íntegro: 0 inconsistencias.")
            with t2:
                st.dataframe(viol, hide_index=True) if len(viol) else st.success("Sin violaciones.")
                if len(imp):
                    st.caption("Imputaciones (la política de nulos permite imputar `saldo_mora_30d` a 0):")
                    st.dataframe(imp, hide_index=True)
            with t3:
                st.write(f"{len(limpio)} de {len(df)} registros pasan a modelado.")
                st.dataframe(limpio, height=240)
                st.download_button("⬇ Descargar CSV limpio", limpio.to_csv(index=False).encode(), "clientes_limpio.csv")
            with t4:
                fig, ax = plt.subplots(figsize=(6, 2.6))
                ax.hist(df["score_riesgo"].dropna(), bins=range(300, 900, 50), color=BLUE, edgecolor="white")
                ax.set_xlabel("score_riesgo"); ax.set_ylabel("Clientes")
                ax.spines[["top", "right"]].set_visible(False)
                izq, _ = st.columns([3, 2])
                izq.pyplot(fig)

            with t5:
                comp = (1 - df[list(df.columns)].isna().mean()) * 100
                fig, ax = plt.subplots(figsize=(6, 2.8))
                ax.barh(comp.index, comp.values, color=[NAVY if v == 100 else "#C0392B" for v in comp.values])
                ax.set_xlim(0, 100); ax.set_xlabel("% de registros con dato"); ax.invert_yaxis()
                for i, v in enumerate(comp.values):
                    ax.text(min(v, 94), i, f"{v:.0f}%", va="center", ha="right", color="white", fontsize=8)
                ax.spines[["top", "right"]].set_visible(False)
                izq, _ = st.columns([3, 2])
                izq.pyplot(fig)
                st.caption("En rojo: columnas con datos faltantes.")

# ---------- 4. DoD ----------
elif paso == 3:
    st.header("Definition of Done")
    st.write("Una historia está **Done** cuando: ① su checklist de 3 ítems está completo, ② pasó por un Pull Request "
             "revisado y aprobado, ③ las pruebas pasan sin errores y ④ la tarjeta está en la columna Done.")
    hist = pd.DataFrame([
        ["US-03 Requisitos de datos", "Diccionario de datos", "PR #6", "—", "✅"],
        ["US-04 Datos de muestra", "Dataset sintético", "PR #5", "—", "✅"],
        ["US-04 Validadores", "feat → test (red) → fix (green) → refactor", "PR #8 (refactor)",
         "089febe · ccf0bd0 · ceaa33b", "✅"],
    ], columns=["Historia", "Artefacto", "Pull Request", "Commits TDD", "DoD"])
    st.dataframe(hist, hide_index=True)
    st.subheader("Prácticas XP")
    cards([("Pair programming", "Piloto y copiloto en diagnóstico, requisitos y arquitectura.", ""),
           ("TDD", "Ciclo rojo → verde → refactor con la suite de pruebas.", ""),
           ("Integración continua", "Ramas por funcionalidad y PRs revisados antes del merge.", ""),
           ("Refactoring", "Validadores divididos en funciones de responsabilidad única.", "")])
    st.write("")
    st.subheader("Evidencia verificable")
    st.caption("Cada enlace abre la prueba directamente en GitHub.")
    e1, e2, e3 = st.columns(3)
    e1.markdown("**Pull Requests revisados**")
    e1.link_button("PR #5 · Dataset de muestra", f"{REPO}/pull/5")
    e1.link_button("PR #6 · Diccionario de datos", f"{REPO}/pull/6")
    e1.link_button("PR #8 · Refactor de validadores", f"{REPO}/pull/8")
    e2.markdown("**Ciclo TDD (commits)**")
    e2.link_button("Rojo · 089febe · tests", f"{REPO}/commit/089febe")
    e2.link_button("Verde · ccf0bd0 · implementación", f"{REPO}/commit/ccf0bd0")
    e2.link_button("Refactor · ceaa33b", f"{REPO}/commit/ceaa33b")
    e3.markdown("**Bitácora y código**")
    e3.link_button("Bitácora XP (pairing, pruebas, refactoring)", f"{REPO}/tree/main/bitacora")
    e3.link_button("Antes vs. después del refactor", f"{REPO}/compare/b82764f...ceaa33b")
    e3.link_button("Repositorio completo", REPO)
    with st.expander("Refactorización: qué cambió"):
        st.write("Antes (b82764f) había una sola función que hacía todas las validaciones. Después (ceaa33b) quedó "
                 "dividida en funciones de una sola responsabilidad, con constantes y type hints:")
        st.code("check_missing_columns(df)\ncheck_nulls(df)\ncheck_score_range(df, min_score, max_score)\n"
                "check_variable_types(df, expected_types)\nvalidate_dataset(df)  # las orquesta y devuelve el reporte",
                language="python")
        st.write("Las pruebas escritas en el paso rojo siguieron pasando sin cambios, lo que confirma que el "
                 "refactor no alteró el comportamiento.")

# ---------- 5. Lecciones ----------
else:
    st.header("Lecciones aprendidas y plan de mejora")
    cards([("Start", "• Comprometer puntos según velocity real (8–11)<br>• Dividir historias en tareas ≤ 3 pts<br>"
                     "• Trabajo en paralelo con criterios acordados<br>• Commits con <i>Co-authored-by</i>", ""),
           ("Stop", "• Comprometer más puntos de los que permite la velocity<br>• Dejar tarjetas para la segunda semana<br>"
                    "• Esperar aprobaciones sin plan B", "stop"),
           ("Continue", "• Tablero Kanban con checklist de 3 ítems<br>• Revisión por pares antes de Done<br>"
                        "• Dailies cortas<br>• Etiquetas por fase del Charter", "cont")])
    st.write("")
    st.subheader("Por qué surgieron y cómo las abordamos")
    with st.expander("Comprometimos más puntos de los que podíamos entregar"):
        st.write("Los dos primeros sprints no tenían velocity histórica: se comprometieron 11 y 16 puntos y se "
                 "completaron 8 y 11. Para el Sprint 3 usamos la velocity real promedio (9.5) como techo.")
    with st.expander("El Charter se aprobó con retraso"):
        st.write("Governance & Charter Approval se planeó para el día 10 y cerró el día 16 por depender de una "
                 "aprobación externa. Se trabajó en paralelo y el impacto fue de 1–2 días hábiles, absorbido por la "
                 "reserva de contingencia. Medida: dividir historias en tareas de 3 puntos o menos y tener un plan B.")
    with st.expander("Por qué el Sprint 3 es de 9–10 puntos"):
        st.write("Coincide con la velocity real y deja espacio para el trabajo arrastrado: Data Collection & "
                 "Cleaning (5 pts) quedó pendiente al cierre del Sprint 2.")
    st.success("**Sprint 3:** planear entre 9 y 10 puntos, considerando el trabajo pendiente de Data Collection & Cleaning.")
    st.write("¡Gracias! Quedamos atentos a sus preguntas.")

# ---------- Navegación inferior ----------
st.divider()
a, _, b = st.columns([1, 4, 1])
a.button("◀ Anterior", on_click=ir, args=(paso - 1,), disabled=paso == 0)
b.button("Siguiente ▶", on_click=ir, args=(paso + 1,), disabled=paso == len(PASOS) - 1, type="primary")
