"""Sprint Review & Demo Operacional - FinBank (DMS Consulting) - Corte 2, Producto C."""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from finbank.validators import validate_dataset  # noqa: E402  (código real del equipo, US-04)

st.set_page_config(page_title="FinBank · Sprint Review", page_icon="🏦", layout="wide")
DATA = ROOT / "data" / "sample_clientes.csv"

# ---------- Datos del reporte de sprints ----------
SPRINTS = pd.DataFrame(
    {"Sprint": ["Sprint 1", "Sprint 2"], "Comprometidos": [11, 16], "Completados": [8, 11]}
)
# Burndown: puntos restantes por día hábil (según días de cierre del reporte)
BURNDOWN = {
    "Sprint 1": {"total": 11, "cierres": {6: 3, 8: 5}},
    "Sprint 2": {"total": 16, "cierres": {6: 3, 7: 5, 9: 3}},
}


def burndown_df(total, cierres):
    rows, restante = [], total
    for dia in range(0, 11):
        restante -= cierres.get(dia, 0)
        rows.append({"Día": dia, "Ideal": total * (1 - dia / 10), "Real": restante})
    return pd.DataFrame(rows).set_index("Día")


# ---------- Contrato de datos (docs/data_dictionary.md) ----------
def validar(df: pd.DataFrame):
    """Devuelve (violaciones, imputaciones) según el diccionario de datos."""
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


# ---------- Navegación ----------
st.sidebar.title("🏦 FinBank · DMS Consulting")
st.sidebar.caption("GMAC · Corte 2 · Producto C")
pagina = st.sidebar.radio(
    "Sección",
    ["1. Resumen del Sprint Review", "2. Demo: pipeline de validación",
     "3. Definition of Done", "4. Lecciones y plan de mejora"],
)

# ---------- 1. Resumen ----------
if pagina.startswith("1"):
    st.title("Sprint Review · Sprints 1 y 2")
    st.write("Incremento entregado a FinBank: diagnóstico, gobierno y Charter, tablero ágil, "
             "requisitos de datos, arquitectura y pipeline de validación de datos.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Velocity Sprint 1", "8 pts", "de 11 comprometidos")
    c2.metric("Velocity Sprint 2", "11 pts", "de 16 comprometidos")
    c3.metric("Velocity promedio", "9.5 pts")
    st.subheader("Estimado vs. real")
    fig, ax = plt.subplots(figsize=(7, 3))
    SPRINTS.set_index("Sprint").plot.bar(ax=ax, rot=0, color=["#9bb7d4", "#0b5a8e"])
    ax.set_ylabel("Puntos")
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig)
    st.subheader("Burndown")
    cols = st.columns(2)
    for col, (nombre, cfg) in zip(cols, BURNDOWN.items()):
        col.caption(nombre)
        bd = burndown_df(cfg["total"], cfg["cierres"])
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(bd.index, bd["Ideal"], "--", color="gray", label="Ideal")
        ax.step(bd.index, bd["Real"], where="post", color="#0b5a8e", label="Real")
        ax.set_xlabel("Día hábil"); ax.set_ylabel("Puntos restantes"); ax.legend()
        ax.spines[["top", "right"]].set_visible(False)
        col.pyplot(fig)
    st.info("Desvío clave: *Governance & Charter Approval* se planeó para el día 10 y cerró el día 16. "
            "Se trabajó en paralelo y el impacto fue de 1–2 días hábiles, absorbido por la reserva de "
            "contingencia (10 días).")

# ---------- 2. Demo ----------
elif pagina.startswith("2"):
    st.title("Demo operacional · validación de datos (US-04)")
    st.write("El pipeline aplica el contrato del diccionario de datos (US-03) a la base de clientes.")
    archivo = st.file_uploader("Sube un CSV de clientes (opcional)", type="csv")
    df = pd.read_csv(archivo) if archivo else pd.read_csv(DATA)
    st.caption("Fuente: " + (archivo.name if archivo else "data/sample_clientes.csv (datos sintéticos)"))
    st.dataframe(df, width="stretch", height=250)

    faltan = {"cliente_id", "edad", "ingreso_mensual", "saldo_mora_30d",
              "score_riesgo", "tipo_cliente", "activo"} - set(df.columns)
    if faltan:
        st.error(f"Faltan columnas del contrato: {sorted(faltan)}")
        st.stop()

    st.subheader("Reporte del pipeline · `finbank.validators.validate_dataset`")
    errores = validate_dataset(df)["errors"]
    if errores:
        st.error(f"{len(errores)} inconsistencias detectadas")
        st.dataframe(pd.DataFrame(errores), width="stretch", hide_index=True)
    else:
        st.success("Dataset íntegro: 0 inconsistencias.")
    st.caption("Debajo, el detalle por registro (qué filas fallan) según el diccionario de datos.")

    viol, imp = validar(df)
    filas_malas = viol["cliente_id"].nunique() if len(viol) else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", len(df))
    c2.metric("Violaciones", len(viol))
    c3.metric("Registros con error", filas_malas)
    c4.metric("Imputaciones", len(imp))

    st.subheader("Violaciones al contrato")
    if len(viol):
        st.dataframe(viol, width="stretch", hide_index=True)
    else:
        st.success("Sin violaciones.")
    if len(imp):
        st.subheader("Imputaciones aplicadas (política de nulos)")
        st.dataframe(imp, width="stretch", hide_index=True)

    limpio = df.copy()
    limpio["saldo_mora_30d"] = limpio["saldo_mora_30d"].fillna(0)
    ids_malos = set(viol["cliente_id"]) if len(viol) else set()
    limpio = limpio[~limpio["cliente_id"].isin(ids_malos)]
    st.subheader("Base limpia (sin registros inválidos)")
    st.write(f"{len(limpio)} de {len(df)} registros pasan a modelado.")
    st.download_button("Descargar CSV limpio", limpio.to_csv(index=False).encode(), "clientes_limpio.csv")

    st.subheader("Distribución de score de riesgo")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.hist(df["score_riesgo"].dropna(), bins=range(300, 900, 50), color="#0b5a8e", edgecolor="white")
    ax.set_xlabel("score_riesgo"); ax.set_ylabel("Clientes")
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig)

# ---------- 3. DoD ----------
elif pagina.startswith("3"):
    st.title("Definition of Done")
    st.write("Una historia está *Done* cuando: (1) su checklist de 3 ítems está completo, "
             "(2) pasó por un Pull Request revisado y aprobado, (3) las pruebas pasan sin errores y "
             "(4) la tarjeta está en la columna Done.")
    hist = pd.DataFrame([
        ["US-03 Requisitos de datos", "Diccionario de datos", "PR #6", "—", "✅"],
        ["US-04 Datos de muestra", "Dataset sintético", "PR #5", "—", "✅"],
        ["US-04 Validadores", "feat → test (red) → fix (green) → refactor",
         "PR #8 (refactor)", "TDD: 089febe · ccf0bd0 · ceaa33b", "✅"],
    ], columns=["Historia", "Artefacto", "Pull Request", "Evidencia TDD (commits)", "DoD"])
    st.dataframe(hist, width="stretch", hide_index=True)
    st.caption("Repo: github.com/AndresAvella09/finbank-analytics")
    st.markdown("**Prácticas XP aplicadas:** pair programming (piloto/copiloto), TDD, "
                "integración continua con ramas por funcionalidad y refactorización de validadores "
                "en funciones de responsabilidad única.")

# ---------- 4. Lecciones ----------
else:
    st.title("Lecciones aprendidas y plan de mejora")
    c1, c2, c3 = st.columns(3)
    c1.subheader("Start")
    c1.markdown("- Comprometer puntos según velocity real (8–11)\n- Dividir historias en tareas ≤ 3 pts\n"
                "- Trabajo en paralelo con criterios de aceptación acordados\n- Commits con *Co-authored-by*")
    c2.subheader("Stop")
    c2.markdown("- Comprometer más puntos de los que permite la velocity\n"
                "- Dejar tarjetas para la segunda semana\n- Esperar aprobaciones sin plan B")
    c3.subheader("Continue")
    c3.markdown("- Tablero Kanban con checklist de 3 ítems\n- Revisión por pares antes de Done\n"
                "- Dailies cortas\n- Etiquetas por fase del Charter")
    st.success("Sprint 3: planear entre 9 y 10 puntos, considerando el trabajo pendiente de "
               "Data Collection & Cleaning.")
