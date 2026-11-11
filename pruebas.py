"""
pruebas.py - Casos de prueba del núcleo matemático (sin librerías extra).

Ejecutar:   python pruebas.py
"""
import pandas as pd

import reglas

HOY = "2026-11-09"


def df_prueba():
    return pd.DataFrame([
        # codigo, nombre, categoria, stock, minimo, precio, vencimiento, ventas
        ["A", "Leche", "Lácteos", 2, 10, 4000, "2026-11-12", 50],   # B, V
        ["B", "Mantequilla", "Lácteos", 8, 4, 3900, "2026-11-10", 0],  # V, S
        ["C", "Arroz", "Granos", 30, 10, 2600, "2027-05-01", 80],      # normal
        ["D", "Esponja", "Aseo", 5, 5, 1200, None, 0],                 # B, S
        ["E", "Energizante", "Aseo", 1, 5, 4500, "2026-11-11", 0],     # B, V, S
    ], columns=reglas.COLUMNAS).assign(
        vencimiento=lambda d: pd.to_datetime(d["vencimiento"])
    )


def test_conjuntos():
    U, B, V, S = reglas.conjuntos(df_prueba(), HOY, 7)
    assert U == {"A", "B", "C", "D", "E"}
    assert B == {"A", "D", "E"}
    assert V == {"A", "B", "E"}
    assert S == {"B", "D", "E"}


def test_operaciones():
    U, B, V, S = reglas.conjuntos(df_prueba(), HOY, 7)
    op = reglas.operaciones(U, B, V, S)
    assert op["Urgentes (B ∩ V)"] == {"A", "E"}
    assert op["Para promoción (V ∩ S)"] == {"B", "E"}
    assert op["Alertas totales (B ∪ V ∪ S)"] == {"A", "B", "D", "E"}
    assert op["Productos normales U \\ (B ∪ V ∪ S)"] == {"C"}
    assert op["Críticos (B ∩ V ∩ S)"] == {"E"}


def test_reglas():
    assert reglas.evaluar_reglas(True, False, False) == ["Reabastecer"]
    assert reglas.evaluar_reglas(False, True, True) == ["Hacer promoción"]
    assert reglas.evaluar_reglas(True, True, False) == ["Reabastecer", "Prioridad alta"]
    assert reglas.evaluar_reglas(True, True, True) == [
        "Reabastecer", "Hacer promoción", "Prioridad alta"]
    assert reglas.evaluar_reglas(False, False, False) == []


def test_tabla_verdad():
    t = reglas.tabla_verdad()
    assert len(t) == 8                       # 2^3 combinaciones
    assert len(t[["p", "q", "r"]].drop_duplicates()) == 8


def test_clasificar():
    res = reglas.clasificar(df_prueba(), HOY, 7).set_index("codigo")
    assert res.loc["C", "acciones"] == "Normal"
    assert "Prioridad alta" in res.loc["A", "acciones"]
    assert res.loc["E", "gravedad"] == 3


def test_particion():
    df = df_prueba()
    assert reglas.verificar_particion(df)
    df_malo = pd.concat([df, df.iloc[[0]].assign(categoria="Otra")])  # código repetido
    assert not reglas.verificar_particion(df_malo)


def test_validar():
    df = df_prueba()
    assert reglas.validar(df) == []
    repetido = pd.concat([df, df.iloc[[0]]])
    assert any("repetidos" in e for e in reglas.validar(repetido))
    negativo = df.copy()
    negativo.loc[0, "stock"] = -3
    assert any("negativos" in e for e in reglas.validar(negativo))


if __name__ == "__main__":
    pruebas = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas superadas.")
