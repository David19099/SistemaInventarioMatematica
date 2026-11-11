"""
reglas.py - Núcleo matemático del sistema de inventario.

Aquí viven SOLO las ideas de Matemática Discreta (conjuntos, lógica
proposicional, funciones). No hay nada de interfaz; así se puede probar
por separado (ver pruebas.py).

Modelo:
    U = conjunto de todos los productos (identificados por su código)
    B = {p in U : stock(p) <= stock_minimo(p)}          (stock bajo)
    V = {p in U : vencimiento(p) <= hoy + d dias}        (próximo a vencer)
    S = {p in U : ventas_mensuales(p) = 0}               (sin rotación)
"""
from datetime import date
from itertools import product, combinations

import pandas as pd

COLUMNAS = [
    "codigo", "nombre", "categoria", "stock", "stock_minimo",
    "precio", "vencimiento", "ventas_mensuales",
]


# ---------------------------------------------------------------- datos
def cargar_inventario(origen):
    """Lee el inventario desde una ruta o un archivo CSV subido."""
    df = pd.read_csv(origen)
    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas en el CSV: {', '.join(faltantes)}")
    df = df[COLUMNAS].copy()
    df["vencimiento"] = pd.to_datetime(df["vencimiento"], errors="coerce")
    return df


def guardar_inventario(df, ruta):
    df.to_csv(ruta, index=False)


def validar(df):
    """Devuelve una lista de errores (vacía si el inventario es válido).

    Comprueba que 'categoria' y 'stock' sean funciones bien definidas:
    cada código aparece una sola vez y tiene un único valor.
    """
    errores = []
    if df["codigo"].isna().any() or (df["codigo"].astype(str).str.strip() == "").any():
        errores.append("Hay productos sin código.")
    duplicados = df["codigo"][df["codigo"].duplicated()].unique()
    if len(duplicados):
        errores.append(f"Códigos repetidos: {', '.join(map(str, duplicados))}")
    for col in ["nombre", "categoria", "stock", "stock_minimo", "precio", "ventas_mensuales"]:
        if df[col].isna().any():
            errores.append(f"La columna '{col}' tiene valores vacíos.")
    for col in ["stock", "stock_minimo", "ventas_mensuales"]:
        if (pd.to_numeric(df[col], errors="coerce") < 0).any():
            errores.append(f"La columna '{col}' no puede tener valores negativos.")
    if (pd.to_numeric(df["precio"], errors="coerce") <= 0).any():
        errores.append("El precio debe ser mayor que cero.")
    return errores


# ------------------------------------------------------------ conjuntos
def conjuntos(df, hoy=None, dias=7):
    """Construye U, B, V, S como conjuntos (set) de códigos de producto."""
    hoy = pd.Timestamp(hoy or date.today())
    limite = hoy + pd.Timedelta(days=dias)
    venc = pd.to_datetime(df["vencimiento"], errors="coerce")

    U = set(df["codigo"])
    B = set(df.loc[df["stock"] <= df["stock_minimo"], "codigo"])
    V = set(df.loc[venc.notna() & (venc <= limite), "codigo"])
    S = set(df.loc[df["ventas_mensuales"] == 0, "codigo"])
    return U, B, V, S


def operaciones(U, B, V, S):
    """Operaciones entre conjuntos usadas por el negocio."""
    alertas = B | V | S
    return {
        "Urgentes (B ∩ V)": B & V,
        "Para promoción (V ∩ S)": V & S,
        "Alertas totales (B ∪ V ∪ S)": alertas,
        "Productos normales U \\ (B ∪ V ∪ S)": U - alertas,
        "Críticos (B ∩ V ∩ S)": B & V & S,
    }


def verificar_particion(df):
    """¿Las categorías forman una partición de U?
    (no vacías, disjuntas dos a dos y con unión igual a U)."""
    clases = {c: set(g["codigo"]) for c, g in df.groupby("categoria")}
    if not clases:
        return False
    disjuntas = all(a.isdisjoint(b) for a, b in combinations(clases.values(), 2))
    union = set().union(*clases.values())
    return disjuntas and union == set(df["codigo"])


# ------------------------------------------------------- lógica proposicional
# p = "stock bajo", q = "próximo a vencer", r = "sin rotación"
#   Regla 1:  p        -> Reabastecer
#   Regla 2:  q ^ r    -> Hacer promoción
#   Regla 3:  p ^ q    -> Prioridad alta
def evaluar_reglas(p, q, r):
    acciones = []
    if p:
        acciones.append("Reabastecer")
    if q and r:
        acciones.append("Hacer promoción")
    if p and q:
        acciones.append("Prioridad alta")
    return acciones


def tabla_verdad():
    """Tabla de verdad de las 2^3 = 8 combinaciones de (p, q, r)."""
    filas = []
    for p, q, r in product([True, False], repeat=3):
        filas.append({
            "p": p, "q": q, "r": r,
            "p → Reabastecer": p,
            "(q ∧ r) → Promoción": q and r,
            "(p ∧ q) → Prioridad alta": p and q,
        })
    tabla = pd.DataFrame(filas)
    return tabla.map(lambda x: "V" if x is True else "F" if x is False else x)


def clasificar(df, hoy=None, dias=7):
    """Agrega las proposiciones p, q, r y las acciones resultantes a cada producto."""
    U, B, V, S = conjuntos(df, hoy, dias)
    out = df.copy()
    out["p_stock_bajo"] = out["codigo"].isin(B)
    out["q_por_vencer"] = out["codigo"].isin(V)
    out["r_sin_rotacion"] = out["codigo"].isin(S)
    out["acciones"] = [
        ", ".join(evaluar_reglas(p, q, r)) or ("Vigilar" if (q or r) else "Normal")
        for p, q, r in zip(out["p_stock_bajo"], out["q_por_vencer"], out["r_sin_rotacion"])
    ]
    out["gravedad"] = (
        out["p_stock_bajo"].astype(int)
        + out["q_por_vencer"].astype(int)
        + out["r_sin_rotacion"].astype(int)
    )
    return out


def nombres(df, codigos):
    """Devuelve el DataFrame (código, nombre, categoría) de un conjunto de códigos."""
    sub = df[df["codigo"].isin(codigos)][["codigo", "nombre", "categoria"]]
    return sub.sort_values("codigo").reset_index(drop=True)
