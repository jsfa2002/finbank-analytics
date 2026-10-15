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
LOGO, DATA = ROOT / "assets" / "dms_logo.png", ROOT / "data" / "sample_clientes.csv"
PASOS = ["Inicio", "Sprints", "Demo", "Definition of Done", "Lecciones"]

st.set_page_config(page_title="DMS Consulting · FinBank", page_icon="📈", layout="wide")
st.markdown(f"""<style>
.block-container {{padding-top: 1.2rem; max-width: 1150px;}}
.stButton > button {{width: 100%; border-radius: 10px; font-weight: 600;}}
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
    st.write("**Este recorrido te guía en 4 pasos.** Usa los botones de arriba o *Siguiente* para avanzar.")
    c = st.columns(4)
    guia = [("2 · Sprints", "Velocity, historias y burndown de cada sprint."),
            ("3 · Demo", "El pipeline de validación de datos corriendo en vivo."),
            ("4 · Definition of Done", "Evidencia: PRs, TDD y prácticas XP."),
            ("5 · Lecciones", "Retrospectiva y plan del Sprint 3.")]
    for col, (t, d) in zip(c, guia):
        col.markdown(f"<div class='card'><h4>{t}</h4>{d}</div>", unsafe_allow_html=True)
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
            t1, t2, t3, t4 = st.tabs(["Reporte del pipeline", "Detalle por registro", "Base limpia", "Distribución de score"])
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
    c = st.columns(4)
    xp = [("Pair programming", "Piloto y copiloto en diagnóstico, requisitos y arquitectura."),
          ("TDD", "Ciclo rojo → verde → refactor con la suite de pruebas."),
          ("Integración continua", "Ramas por funcionalidad y PRs revisados antes del merge."),
          ("Refactoring", "Validadores divididos en funciones de responsabilidad única.")]
    for col, (t, d) in zip(c, xp):
        col.markdown(f"<div class='card'><h4>{t}</h4>{d}</div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("Ver repositorio en GitHub ↗", "https://github.com/AndresAvella09/finbank-analytics")

# ---------- 5. Lecciones ----------
else:
    st.header("Lecciones aprendidas y plan de mejora")
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='card'><h4>▶ Start</h4>• Comprometer puntos según velocity real (8–11)<br>"
                "• Dividir historias en tareas ≤ 3 pts<br>• Trabajo en paralelo con criterios acordados<br>"
                "• Commits con <i>Co-authored-by</i></div>", unsafe_allow_html=True)
    c2.markdown("<div class='card stop'><h4>■ Stop</h4>• Comprometer más puntos de los que permite la velocity<br>"
                "• Dejar tarjetas para la segunda semana<br>• Esperar aprobaciones sin plan B</div>", unsafe_allow_html=True)
    c3.markdown("<div class='card cont'><h4>⟳ Continue</h4>• Tablero Kanban con checklist de 3 ítems<br>"
                "• Revisión por pares antes de Done<br>• Dailies cortas<br>• Etiquetas por fase del Charter</div>",
                unsafe_allow_html=True)
    st.write("")
    st.success("**Sprint 3:** planear entre 9 y 10 puntos, considerando el trabajo pendiente de Data Collection & Cleaning.")
    st.write("¡Gracias! Quedamos atentos a sus preguntas.")

# ---------- Navegación inferior ----------
st.divider()
a, _, b = st.columns([1, 4, 1])
a.button("◀ Anterior", on_click=ir, args=(paso - 1,), disabled=paso == 0)
b.button("Siguiente ▶", on_click=ir, args=(paso + 1,), disabled=paso == len(PASOS) - 1, type="primary")
