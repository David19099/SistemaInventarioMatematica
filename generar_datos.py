"""
generar_datos.py - Crea datos_tienda.csv con 42 productos de una tienda de barrio.

Las fechas de vencimiento se calculan a partir de HOY para que siempre haya
productos próximos a vencer al probar el programa.

Uso:
    python generar_datos.py              # usa la fecha de hoy
    python generar_datos.py 2026-11-09   # usa una fecha específica
"""
import csv
import sys
from datetime import date, timedelta

# (codigo, nombre, categoria, stock, stock_minimo, precio COP,
#  dias_para_vencer (None = no perecedero), ventas_mensuales)
PRODUCTOS = [
    # Granos y abarrotes
    ("P001", "Arroz blanco 500 g", "Granos y abarrotes", 40, 15, 2600, 300, 85),
    ("P002", "Frijol cargamanto 500 g", "Granos y abarrotes", 8, 10, 6500, 280, 22),
    ("P003", "Lentejas 500 g", "Granos y abarrotes", 25, 10, 3800, 260, 0),
    ("P004", "Azúcar 1 kg", "Granos y abarrotes", 30, 12, 4200, 350, 60),
    ("P005", "Sal 500 g", "Granos y abarrotes", 20, 8, 1500, 500, 30),
    ("P006", "Aceite vegetal 1 L", "Granos y abarrotes", 6, 8, 11500, 200, 28),
    ("P007", "Pasta espagueti 250 g", "Granos y abarrotes", 35, 12, 2200, 250, 45),
    ("P008", "Panela en bloque", "Granos y abarrotes", 12, 6, 3500, 120, 18),
    ("P009", "Atún en lata 160 g", "Granos y abarrotes", 18, 8, 5200, 500, 15),
    ("P010", "Café molido 250 g", "Granos y abarrotes", 9, 10, 9800, 180, 26),
    # Lácteos y huevos
    ("P011", "Leche entera bolsa 900 ml", "Lácteos y huevos", 5, 20, 4300, 4, 120),
    ("P012", "Yogur 1 L", "Lácteos y huevos", 10, 8, 7200, 6, 24),
    ("P013", "Queso campesino 500 g", "Lácteos y huevos", 6, 5, 12500, 5, 10),
    ("P014", "Huevos AA cubeta x30", "Lácteos y huevos", 14, 6, 18500, 20, 35),
    ("P015", "Mantequilla 125 g", "Lácteos y huevos", 7, 4, 3900, 3, 0),
    ("P016", "Kumis 1 L", "Lácteos y huevos", 4, 6, 6800, 15, 20),
    # Bebidas
    ("P017", "Gaseosa 1,5 L", "Bebidas", 24, 12, 5500, 150, 90),
    ("P018", "Agua botella 600 ml", "Bebidas", 48, 24, 2000, 400, 110),
    ("P019", "Jugo en caja 1 L", "Bebidas", 16, 8, 4200, 90, 40),
    ("P020", "Cerveza lata 330 ml", "Bebidas", 36, 24, 3200, 200, 70),
    ("P021", "Bebida energizante 250 ml", "Bebidas", 5, 6, 4500, 5, 0),
    ("P022", "Té frío botella 500 ml", "Bebidas", 12, 6, 3000, 60, 0),
    # Snacks y dulces
    ("P023", "Papas fritas 100 g", "Snacks y dulces", 20, 10, 3500, 75, 55),
    ("P024", "Galletas de sal paquete", "Snacks y dulces", 30, 10, 2500, 120, 48),
    ("P025", "Chocolatina", "Snacks y dulces", 40, 15, 1800, 180, 95),
    ("P026", "Chicles paquete", "Snacks y dulces", 3, 10, 1000, 400, 60),
    ("P027", "Maní salado 80 g", "Snacks y dulces", 15, 6, 2000, 3, 0),
    ("P028", "Dulces surtidos bolsa", "Snacks y dulces", 25, 10, 3000, 200, 0),
    # Aseo del hogar
    ("P029", "Detergente en polvo 1 kg", "Aseo del hogar", 14, 6, 9800, None, 30),
    ("P030", "Jabón de loza barra", "Aseo del hogar", 22, 10, 2800, None, 50),
    ("P031", "Cloro 1 L", "Aseo del hogar", 4, 8, 3600, None, 25),
    ("P032", "Papel higiénico x4", "Aseo del hogar", 18, 10, 6500, None, 40),
    ("P033", "Esponja lavaplatos", "Aseo del hogar", 30, 10, 1200, None, 0),
    # Aseo personal
    ("P034", "Jabón de baño", "Aseo personal", 26, 12, 2400, None, 55),
    ("P035", "Crema dental 75 ml", "Aseo personal", 15, 8, 5800, None, 35),
    ("P036", "Champú sachet", "Aseo personal", 60, 30, 900, None, 150),
    ("P037", "Toallas higiénicas x10", "Aseo personal", 7, 8, 5500, None, 14),
    # Papelería
    ("P038", "Cuaderno cuadriculado", "Papelería", 20, 8, 4500, None, 30),
    ("P039", "Lápiz", "Papelería", 50, 20, 800, None, 70),
    ("P040", "Borrador", "Papelería", 3, 10, 600, None, 15),
    ("P041", "Resma de papel carta", "Papelería", 6, 3, 16500, None, 0),
    ("P042", "Pegante en barra", "Papelería", 12, 5, 2800, None, 8),
]

ENCABEZADO = ["codigo", "nombre", "categoria", "stock", "stock_minimo",
              "precio", "vencimiento", "ventas_mensuales"]


def generar(hoy, ruta="datos_tienda.csv"):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(ENCABEZADO)
        for cod, nom, cat, stock, minimo, precio, dias, ventas in PRODUCTOS:
            venc = (hoy + timedelta(days=dias)).isoformat() if dias is not None else ""
            w.writerow([cod, nom, cat, stock, minimo, precio, venc, ventas])
    print(f"Archivo '{ruta}' creado con {len(PRODUCTOS)} productos (fecha base: {hoy}).")


if __name__ == "__main__":
    hoy = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    generar(hoy)
