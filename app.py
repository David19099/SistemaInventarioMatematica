"""
app.py - Interfaz web (Streamlit) del sistema de inventario "Tienda de barrio".

Ejecutar:   streamlit run app.py
"""
from datetime import date

import streamlit as st

import reglas

RUTA = "datos_tienda.csv"

st.set_page_config(page_title="Inventario - Tienda de barrio", page_icon="🛒", layout="wide")
st.title("🛒 Inventario - Tienda de barrio")
st.caption("Conjuntos y lógica proposicional aplicados a la gestión de inventario")

# ------------------------------------------------------------------ estado
if "df" not in st.session_state:
    try:
        st.session_state.df = reglas.cargar_inventario(RUTA)
    except FileNotFoundError:
        st.error(f"No se encontró '{RUTA}'. Ejecute primero: python generar_datos.py")
        st.stop()


def guardar():
    reglas.guardar_inventario(st.session_state.df, RUTA)


# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Parámetros")
    hoy = st.date_input("Fecha de referencia", value=date.today())
    dias = st.slider("Días para considerar 'próximo a vencer'", 1, 30, 7)

    st.divider()
    st.subheader("Importar / exportar")
    archivo = st.file_uploader("Importar inventario (CSV)", type="csv")
    if archivo is not None and st.button("Cargar archivo"):
        try:
            nuevo = reglas.cargar_inventario(archivo)
            errores = reglas.validar(nuevo)
            if errores:
                for e in errores:
                    st.error(e)
            else:
                st.session_state.df = nuevo
                guardar()
                st.rerun()
        except ValueError as e:
            st.error(str(e))
    st.download_button(
        "⬇️ Exportar CSV",
        st.session_state.df.to_csv(index=False).encode("utf-8"),
        file_name="inventario.csv",
        mime="text/csv",
    )

df = st.session_state.df
tab1, tab2, tab3, tab4 = st.tabs(
    ["📦 Inventario", "🚨 Alertas", "🔢 Conjuntos", "🧠 Lógica"]
)

# ------------------------------------------------------------ 1. inventario
with tab1:
    st.write("Edite las celdas, agregue filas al final o elimine filas "
             "(seleccione la fila y presione Supr). Luego pulse **Guardar**.")
    editado = st.data_editor(
        df,
        num_rows="dynamic",
        key="editor",
        column_config={
            "vencimiento": st.column_config.DateColumn("vencimiento"),
            "precio": st.column_config.NumberColumn("precio (COP)", format="$%d"),
        },
    )
    if st.button("💾 Guardar cambios"):
        errores = reglas.validar(editado)
        if errores:
            for e in errores:
                st.error(e)
        else:
            st.session_state.df = editado.reset_index(drop=True)
            guardar()
            st.success("Inventario guardado.")
            st.rerun()

# --------------------------------------------------------------- 2. alertas
with tab2:
    res = reglas.clasificar(df, hoy, dias)
    U, B, V, S = reglas.conjuntos(df, hoy, dias)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Productos (|U|)", len(U))
    c2.metric("Stock bajo (|B|)", len(B))
    c3.metric("Por vencer (|V|)", len(V))
    c4.metric("Sin rotación (|S|)", len(S))

    solo_alertas = st.checkbox("Mostrar solo productos con alertas", value=True)
    vista = res[res["gravedad"] > 0] if solo_alertas else res
    vista = vista.sort_values(["gravedad", "codigo"], ascending=[False, True])
    st.dataframe(
        vista[["codigo", "nombre", "categoria", "stock", "stock_minimo", "vencimiento",
               "ventas_mensuales", "p_stock_bajo", "q_por_vencer", "r_sin_rotacion", "acciones"]],
        hide_index=True,
    )

# -------------------------------------------------------------- 3. conjuntos
with tab3:
    st.subheader("Conjuntos base")
    st.markdown(
        "- **B** = stock ≤ stock mínimo  \n"
        f"- **V** = vence en ≤ {dias} días (o ya venció)  \n"
        "- **S** = ventas mensuales = 0"
    )
    for nombre, conj in reglas.operaciones(U, B, V, S).items():
        with st.expander(f"{nombre} - {len(conj)} producto(s)"):
            if conj:
                st.dataframe(reglas.nombres(df, conj), hide_index=True)
            else:
                st.info("Conjunto vacío (∅).")

    st.subheader("Categorías como partición de U")
    if reglas.verificar_particion(df):
        st.success("Las categorías son disjuntas y su unión es U: forman una partición.")
    else:
        st.error("Las categorías NO forman una partición (revise códigos repetidos).")
    st.bar_chart(df.groupby("categoria")["codigo"].count())

# ---------------------------------------------------------------- 4. lógica
with tab4:
    st.subheader("Reglas del negocio")
    st.markdown(
        "Sean **p** = «stock bajo», **q** = «próximo a vencer», **r** = «sin rotación».\n\n"
        "1. p → Reabastecer\n"
        "2. (q ∧ r) → Hacer promoción\n"
        "3. (p ∧ q) → Prioridad alta"
    )
    st.subheader("Tabla de verdad (2³ = 8 casos)")
    st.dataframe(reglas.tabla_verdad(), hide_index=True)
