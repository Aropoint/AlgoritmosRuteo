"""Dibuja el diagrama de la BD a partir del catálogo de PostgreSQL (rúbrica punto 0).

Lee las tablas, columnas, claves primarias y claves foráneas que realmente
existen en la BD, así el diagrama nunca se desalinea de schema.sql.

Uso (dentro del contenedor app, con la BD creada):  python BD/diagrama_bd.py
Salida: BD/diagrama_bd.png (y BD/diagrama_bd.svg)
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz  # noqa: E402

from comun.bd import conectar  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "diagrama_bd"

# Trazado ortogonal. graphviz no sabe hacerlo respetando el anclaje por fila (ver dibujar()), así
# que las rutas se calculan aquí y se sustituyen en el SVG que él genera. Medidas en puntos, que a
# la escala 1:1 de la salida equivalen a píxeles.
MARGEN_GRUPO = 12.0       # distancia mínima entre una línea vertical y el borde de un grupo de color
SEPARACION_LINEAS = 8.0   # distancia entre carriles paralelos dentro de un mismo corredor
FLECHA_LARGO = 7.5
FLECHA_ANCHO = 3.0

GRUPOS = [  # (título, color, prefijo o nombres)
    ("Infraestructura", "#dbeafe", ("nodos", "aristas", "mision")),
    ("Metadata", "#dcfce7", ("meta_",)),
    ("Amenazas", "#fee2e2", ("amz_",)),
    ("Resultados", "#fef9c3", ("rutas", "evaluaciones")),
    ("Soporte", "#f3f4f6", ("fuentes", "parametros_pesos")),
]

# Disposición en rejilla: una lista por columna (de izquierda a derecha) con los grupos
# apilados de arriba a abajo. Sin esto, dot encadena los grupos por sus claves foráneas y
# el diagrama sale como una sola tira vertical, imposible de proyectar.
COLUMNAS = [
    ["Resultados"],
    ["Infraestructura"],
    ["Amenazas", "Soporte"],
    ["Metadata"],
]

# Título con una línea de leyenda, para que la lámina se entienda sin explicarla de viva voz.
LEYENDA = (
    '<<FONT POINT-SIZE="18"><B>Modelo de datos: ruteo resiliente de UAV</B></FONT><BR/><BR/>'
    '<FONT POINT-SIZE="11" COLOR="#374151">Cada flecha sale de la columna referenciada y apunta a '
    'la columna que es clave foránea.<BR/>'
    '<FONT COLOR="#9ca3af"><B>La punteada es una relación lógica, sin clave foránea.</B></FONT>'
    '</FONT>>'
)

# parametros_pesos no tiene clave foránea: es la tabla de constantes que lee BD/pesos.sql
# para calcular las columnas de riesgo y restricción de `aristas`. Sin esta arista el lector
# la ve suelta y no entiende para qué está. Se dibuja punteada para no confundirla con una FK.
RELACIONES_LOGICAS = [  # (tabla, columna, tabla_ref, columna_ref)
    ("aristas", "riesgo", "parametros_pesos", "valor"),
]


def _grupo(tabla: str) -> int:
    for i, (_, _, claves) in enumerate(GRUPOS):
        if any(tabla == c or (c.endswith("_") and tabla.startswith(c)) for c in claves):
            return i
    return len(GRUPOS) - 1


def leer_catalogo(conn):
    columnas: dict[str, list[tuple[str, str, bool]]] = {}
    for tabla, columna, tipo, no_nulo in conn.execute(
        """SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod), a.attnotnull
           FROM pg_class c
           JOIN pg_namespace n ON n.oid = c.relnamespace
           JOIN pg_attribute a ON a.attrelid = c.oid
           WHERE n.nspname = 'public' AND c.relkind = 'r' AND a.attnum > 0 AND NOT a.attisdropped
             AND c.relname <> 'spatial_ref_sys'
           ORDER BY c.relname, a.attnum"""
    ):
        columnas.setdefault(tabla, []).append((columna, tipo, no_nulo))
    pk: dict[str, set[str]] = {}
    fk: list[tuple[str, str, str, str]] = []  # (tabla, columna, tabla_ref, columna_ref)
    for tabla, tipo, cols, ref, cols_ref in conn.execute(
        """SELECT con.conrelid::regclass::text, con.contype,
                  ARRAY(SELECT a.attname FROM unnest(con.conkey) k JOIN pg_attribute a
                        ON a.attrelid = con.conrelid AND a.attnum = k),
                  con.confrelid::regclass::text,
                  ARRAY(SELECT a.attname FROM unnest(con.confkey) k JOIN pg_attribute a
                        ON a.attrelid = con.confrelid AND a.attnum = k)
           FROM pg_constraint con
           WHERE con.connamespace = 'public'::regnamespace AND con.contype IN ('p', 'f')"""
    ):
        if tipo == "p":
            pk.setdefault(tabla, set()).update(cols)
        else:
            fk.extend((tabla, c, ref, cr) for c, cr in zip(cols, cols_ref))
    return columnas, pk, fk


def _nodo_tabla(sub, tabla: str, columnas, pk, con_fk) -> None:
    filas = [f'<TR><TD COLSPAN="2" BGCOLOR="#1f2937"><FONT COLOR="white"><B>{tabla}</B></FONT></TD></TR>']
    for columna, tipo, no_nulo in columnas[tabla]:
        marcas = ("PK " if columna in pk.get(tabla, ()) else "") + ("FK " if (tabla, columna) in con_fk else "")
        nombre = f"<B>{html.escape(columna)}</B>" if marcas.startswith("PK") else html.escape(columna)
        tipo_txt = html.escape(tipo) + ("" if no_nulo else " ?")
        filas.append(f'<TR><TD ALIGN="LEFT" PORT="{columna}">{marcas}{nombre}</TD>'
                     f'<TD ALIGN="LEFT"><FONT COLOR="#555555">{tipo_txt}</FONT></TD></TR>')
    etiqueta = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="white">' + "".join(filas) + "</TABLE>>"
    sub.node(tabla, label=etiqueta)


def dibujar(columnas, pk, fk) -> graphviz.Digraph:
    # splines=polyline: tramos rectos trazados por el espacio libre entre las cajas. Usa el mismo
    # cálculo de camino que las curvas (busca un pasillo vacío y lo recorre), pero lo dibuja con
    # segmentos en vez de bézier, y respeta el anclaje a la fila exacta.
    #
    # No se usa splines=ortho, que daría quiebres en ángulo recto: su router no sabe salir de un
    # PORT, que es un punto en el costado de una caja a media altura, y termina trazando segmentos
    # por encima de las tablas vecinas. Manhattan y anclaje por fila son incompatibles en graphviz.
    #
    # newrank=true es imprescindible para que rank=same funcione entre clusters distintos.
    dot = graphviz.Digraph("bd", graph_attr={"rankdir": "LR", "newrank": "true", "splines": "polyline",
                                             "fontname": "Helvetica", "nodesep": "0.5", "ranksep": "1.6",
                                             "label": LEYENDA, "labelloc": "t", "fontsize": "18"},
                           node_attr={"shape": "plaintext", "fontname": "Helvetica", "fontsize": "10"},
                           # Punta simple en vez de pie de gallo + marca de «uno»: esos dos símbolos
                           # se dibujan justo donde la línea toca la caja y emborronan la fila a la
                           # que está anclada, que es lo que de verdad interesa leer.
                           edge_attr={"color": "#555555", "arrowhead": "vee", "arrowsize": "0.8",
                                      "dir": "forward"})
    con_fk = {(t, c) for t, c, _, _ in fk}
    por_titulo: dict[str, list[str]] = {}
    for tabla in columnas:
        por_titulo.setdefault(GRUPOS[_grupo(tabla)][0], []).append(tabla)
    indice = {titulo: i for i, (titulo, _, _) in enumerate(GRUPOS)}

    # Los clusters se declaran en el orden de COLUMNAS: dentro de una misma columna, ese orden
    # es el que dot usa para apilarlos de arriba a abajo.
    for col in COLUMNAS:
        for titulo in col:
            tablas = sorted(por_titulo.get(titulo, []))
            if not tablas:
                continue
            i = indice[titulo]
            with dot.subgraph(name=f"cluster_{i}") as sub:
                sub.attr(label=titulo, style="rounded,filled", color="#999999", fillcolor=GRUPOS[i][1])
                for tabla in tablas:
                    _nodo_tabla(sub, tabla, columnas, pk, con_fk)

    # Cada columna es un rank, y una cadena invisible fija su orden de izquierda a derecha.
    representantes = []
    for col in COLUMNAS:
        tablas_col = [t for titulo in col for t in sorted(por_titulo.get(titulo, []))]
        if not tablas_col:
            continue
        with dot.subgraph() as mismo:
            mismo.attr(rank="same")
            for tabla in tablas_col:
                mismo.node(tabla)
        representantes.append(tablas_col[0])
    for origen, destino in zip(representantes, representantes[1:]):
        dot.edge(origen, destino, style="invis")

    # Una línea por clave foránea, anclada a la fila exacta en ambos extremos (PORT): se lee de qué
    # columna sale y a cuál llega sin necesidad de etiquetas.
    # constraint=false: las FK ya no deciden la posición, solo se dibujan sobre la rejilla.
    # El id identifica cada arista en el SVG para poder reemplazar su trazado por el ortogonal.
    for i, (tabla, columna, ref, columna_ref) in enumerate(fk):
        dot.edge(f"{ref}:{columna_ref}", f"{tabla}:{columna}", constraint="false", id=f"rel{i}")
    for j, (tabla, columna, ref, columna_ref) in enumerate(relaciones_logicas(columnas)):
        dot.edge(f"{ref}:{columna_ref}", f"{tabla}:{columna}", constraint="false", style="dashed",
                 color="#9ca3af", arrowhead="vee", arrowtail="none", dir="forward", id=f"log{j}")
    return dot


def relaciones_logicas(columnas) -> list[tuple[str, str, str, str]]:
    """Las de RELACIONES_LOGICAS cuyas dos tablas existen realmente en la BD."""
    return [r for r in RELACIONES_LOGICAS if r[0] in columnas and r[2] in columnas]


# ---------------------------------------------------------------------------
# Trazado ortogonal propio
# ---------------------------------------------------------------------------

def _filas_nodo(obj: dict) -> list[float]:
    """Centro vertical de cada fila de datos de una tabla, en orden.

    Se toma de los contornos de celda que graphviz deja en `_ldraw_`, que son la geometría real
    de la tabla HTML. No se usan los extremos que graphviz calcula para la arista: cuando decide
    sacarla por arriba o por abajo de la caja, ese punto no está en la fila sino en el borde, y
    además a veces invierte el orden de los dos extremos.
    """
    rangos = set()
    for op in obj.get("_ldraw_", []):
        if op.get("op") == "p":  # contorno de celda (los rellenos usan "P")
            ys = [p[1] for p in op["points"]]
            rangos.add((round(min(ys), 1), round(max(ys), 1)))
    ordenados = sorted(rangos, key=lambda r: -r[1])
    return [(a + b) / 2 for a, b in ordenados[1:]]  # el primero es la cabecera con el nombre


def _geometria(js: dict) -> tuple[dict[str, tuple], dict[str, list[float]], list[tuple], tuple]:
    limites = tuple(float(v) for v in js["bb"].split(","))
    cajas_nodo: dict[str, tuple] = {}
    filas_nodo: dict[str, list[float]] = {}
    cajas_grupo: list[tuple] = []
    for obj in js.get("objects", []):
        nombre = obj.get("name", "")
        if nombre.startswith("cluster"):
            if "bb" in obj:
                cajas_grupo.append(tuple(float(v) for v in obj["bb"].split(",")))
        elif "pos" in obj and "width" in obj:
            cx, cy = (float(v) for v in obj["pos"].split(","))
            mitad_ancho = float(obj["width"]) * 36.0   # pulgadas -> puntos, dividido en dos
            mitad_alto = float(obj["height"]) * 36.0
            cajas_nodo[nombre] = (cx - mitad_ancho, cy - mitad_alto, cx + mitad_ancho, cy + mitad_alto)
            filas_nodo[nombre] = _filas_nodo(obj)
    return cajas_nodo, filas_nodo, cajas_grupo, limites


def _canales(cajas_grupo: list[tuple], limites: tuple) -> list[tuple[float, float]]:
    """Pasillos verticales entre columnas: el espacio en blanco que dejan los grupos de color.

    Se calculan una sola vez sobre todo el lienzo, no por arista. Tomar el hueco libre para el
    tramo de alturas de cada arista daba intervalos enormes (media lámina) cuando las dos tablas
    estaban a la misma altura, y el carril terminaba trazado lejísimos de ambas.
    """
    franjas: list[list[float]] = []
    for x1, _, x2, _ in sorted(cajas_grupo, key=lambda g: g[0]):
        if franjas and x1 <= franjas[-1][1]:
            franjas[-1][1] = max(franjas[-1][1], x2)
        else:
            franjas.append([x1, x2])
    canales, x = [], limites[0] - 40
    for x1, x2 in franjas:
        if x1 - x >= 2 * MARGEN_GRUPO:
            canales.append((x, x1))
        x = x2
    if limites[2] + 40 - x >= 2 * MARGEN_GRUPO:
        canales.append((x, limites[2] + 40))
    return canales


def _choca_horizontal(xa: float, xb: float, y: float, cajas_grupo: list[tuple], permitidos: set[int]) -> bool:
    """¿El tramo horizontal atraviesa algún grupo que no sea el de salida o el de llegada?"""
    izq, der = min(xa, xb), max(xa, xb)
    for i, (gx1, gy1, gx2, gy2) in enumerate(cajas_grupo):
        if i in permitidos:
            continue
        if gy1 <= y <= gy2 and not (der <= gx1 or izq >= gx2):
            return True
    return False


def _grupo_de(caja: tuple, cajas_grupo: list[tuple]) -> int | None:
    cx, cy = (caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2
    for i, (gx1, gy1, gx2, gy2) in enumerate(cajas_grupo):
        if gx1 <= cx <= gx2 and gy1 <= cy <= gy2:
            return i
    return None


def rutas_ortogonales(js: dict, columnas, fk) -> dict[str, list[tuple[float, float]]]:
    """Ruta en ángulo recto para cada arista: sale en horizontal de la fila, baja o sube por una
    franja de espacio en blanco y entra en horizontal a la fila de destino.

    Las aristas que comparten franja se reparten en carriles separados entre sí, para que los
    tramos verticales no se superpongan y se lean como una sola línea.
    """
    cajas_nodo, filas_nodo, cajas_grupo, limites = _geometria(js)
    canales = _canales(cajas_grupo, limites)
    if not canales:
        return {}

    def _y_fila(tabla: str, columna: str) -> float | None:
        indices = [i for i, (c, _, _) in enumerate(columnas[tabla]) if c == columna]
        filas = filas_nodo.get(tabla, [])
        if not indices or len(filas) != len(columnas[tabla]):
            caja = cajas_nodo.get(tabla)
            return None if caja is None else (caja[1] + caja[3]) / 2
        return filas[indices[0]]

    enlaces = [(f"rel{i}", r) for i, r in enumerate(fk)]
    enlaces += [(f"log{j}", r) for j, r in enumerate(relaciones_logicas(columnas))]

    candidatas = []
    for ident, (destino, col_destino, origen, col_origen) in enlaces:
        if origen not in cajas_nodo or destino not in cajas_nodo:
            continue
        sy, ey = _y_fila(origen, col_origen), _y_fila(destino, col_destino)
        if sy is None or ey is None:
            continue
        caja_o, caja_d = cajas_nodo[origen], cajas_nodo[destino]
        objetivo = ((caja_o[0] + caja_o[2]) / 2 + (caja_d[0] + caja_d[2]) / 2) / 2
        permitidos = {g for g in (_grupo_de(caja_o, cajas_grupo), _grupo_de(caja_d, cajas_grupo))
                      if g is not None}
        # El canal más cercano al punto medio de las dos tablas, descartando los que obligarían a
        # cruzar un grupo ajeno para llegar hasta él.
        elegido = None
        for x1, x2 in sorted(canales, key=lambda c: abs((c[0] + c[1]) / 2 - objetivo)):
            x = min(max(objetivo, x1 + MARGEN_GRUPO), x2 - MARGEN_GRUPO)
            if (not _choca_horizontal(caja_o[0], x, sy, cajas_grupo, permitidos)
                    and not _choca_horizontal(caja_d[0], x, ey, cajas_grupo, permitidos)):
                elegido = (x1, x2)
                break
        if elegido is None:
            continue
        candidatas.append({"id": ident, "caja_o": caja_o, "caja_d": caja_d,
                           "sy": sy, "ey": ey, "canal": elegido, "objetivo": objetivo})

    # Carriles: dentro de un canal, una x distinta por arista. Si el canal no da para la
    # separación pedida se reparte el ancho disponible, que es preferible a solaparlas.
    por_canal: dict[tuple, list[dict]] = {}
    for c in candidatas:
        por_canal.setdefault(c["canal"], []).append(c)

    rutas: dict[str, list[tuple[float, float]]] = {}
    for (x1, x2), grupo in por_canal.items():
        grupo.sort(key=lambda c: (c["ey"], c["sy"]))
        n = len(grupo)
        util = (x2 - x1) - 2 * MARGEN_GRUPO
        separacion = SEPARACION_LINEAS if n < 2 else min(SEPARACION_LINEAS, util / (n - 1))
        centro = min(max(grupo[0]["objetivo"], x1 + MARGEN_GRUPO + util / 2), x2 - MARGEN_GRUPO - util / 2)
        for i, c in enumerate(grupo):
            carril = centro + (i - (n - 1) / 2) * separacion
            caja_o, caja_d = c["caja_o"], c["caja_d"]
            ax = caja_o[0] if carril < (caja_o[0] + caja_o[2]) / 2 else caja_o[2]
            bx = caja_d[0] if carril < (caja_d[0] + caja_d[2]) / 2 else caja_d[2]
            puntos = [(ax, c["sy"]), (carril, c["sy"]), (carril, c["ey"]), (bx, c["ey"])]
            limpios = [p for j, p in enumerate(puntos) if j == 0 or p != puntos[j - 1]]
            rutas[c["id"]] = limpios
    return rutas


def _flecha(puntos: list[tuple[float, float]]) -> str:
    """Punta triangular en el extremo, apuntando en el sentido del último tramo (horizontal)."""
    (px, _), (ex, ey) = puntos[-2], puntos[-1]
    sentido = 1.0 if ex >= px else -1.0
    base = ex - sentido * FLECHA_LARGO
    return (f"{base:.2f},{-ey + FLECHA_ANCHO:.2f} {ex:.2f},{-ey:.2f} "
            f"{base:.2f},{-ey - FLECHA_ANCHO:.2f}")


def svg_con_rutas(svg: str, rutas: dict[str, list[tuple[float, float]]]) -> str:
    """Sustituye el trazado de cada arista del SVG de graphviz por su ruta ortogonal."""
    for ident, puntos in rutas.items():
        bloque = re.search(r'(<g id="%s"[^>]*>)(.*?)(</g>)' % re.escape(ident), svg, re.S)
        if not bloque:
            continue
        camino = "M" + " L".join(f"{x:.2f},{-y:.2f}" for x, y in puntos)
        contenido = re.sub(r'(<path[^>]*\sd=")[^"]*(")', lambda m: m.group(1) + camino + m.group(2),
                           bloque.group(2), count=1)
        contenido = re.sub(r'(<polygon[^>]*\spoints=")[^"]*(")',
                           lambda m: m.group(1) + _flecha(puntos) + m.group(2), contenido, count=1)
        svg = svg[:bloque.start(2)] + contenido + svg[bloque.end(2):]
    return svg


def main() -> None:
    with conectar() as conn:
        columnas, pk, fk = leer_catalogo(conn)
    if not columnas:
        raise SystemExit("La BD no tiene tablas: ejecuta primero BD/crear_bd.py.")
    dot = dibujar(columnas, pk, fk)

    # Dos salidas del mismo trazado: el SVG, que se modifica, y el JSON con la geometría
    # (cajas de las tablas, de los grupos y anclajes de cada arista) para calcular las rutas.
    svg = svg_con_rutas(dot.pipe(format="svg").decode("utf-8"),
                        rutas_ortogonales(json.loads(dot.pipe(format="json")), columnas, fk))
    svg_destino = SALIDA.with_suffix(".svg")
    svg_destino.write_text(svg, encoding="utf-8")

    # El PNG se rasteriza desde ese SVG: graphviz no puede generarlo porque las rutas ya no son
    # suyas. rsvg-convert viene en la imagen (ver Dockerfile).
    png_destino = SALIDA.with_suffix(".png")
    subprocess.run(["rsvg-convert", "-f", "png", "-o", str(png_destino), str(svg_destino)], check=True)
    print(f"{len(columnas)} tablas, {len(fk)} claves foráneas -> {png_destino}")


if __name__ == "__main__":
    main()
