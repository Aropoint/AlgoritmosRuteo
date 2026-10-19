"""Dibuja el diagrama de la BD a partir del catálogo de PostgreSQL (rúbrica punto 0).

Lee las tablas, columnas, claves primarias y claves foráneas que realmente
existen en la BD, así el diagrama nunca se desalinea de schema.sql.

Uso (dentro del contenedor app, con la BD creada):  python BD/diagrama_bd.py
Salida: BD/diagrama_bd.png (y BD/diagrama_bd.svg)
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz  # noqa: E402

from comun.bd import conectar  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "diagrama_bd"

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

# parametros_pesos no tiene clave foránea: es la tabla de constantes que lee BD/pesos.sql
# para calcular las columnas de riesgo y restricción de `aristas`. Sin esta arista el lector
# la ve suelta y no entiende para qué está. Se dibuja punteada para no confundirla con una FK.
RELACIONES_LOGICAS = [
    ("parametros_pesos", "aristas", "BD/pesos.sql"),
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
    # splines=ortho: tramos rectos con quiebres en ángulo recto, más fáciles de seguir que las curvas.
    # newrank=true es imprescindible para que rank=same funcione entre clusters distintos.
    dot = graphviz.Digraph("bd", graph_attr={"rankdir": "LR", "newrank": "true", "splines": "ortho",
                                             "fontname": "Helvetica", "nodesep": "0.5", "ranksep": "1.6",
                                             "label": "Modelo de datos: ruteo resiliente de UAV",
                                             "labelloc": "t", "fontsize": "18"},
                           node_attr={"shape": "plaintext", "fontname": "Helvetica", "fontsize": "10"},
                           edge_attr={"color": "#555555", "arrowhead": "crow", "arrowtail": "tee", "dir": "both"})
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

    # constraint=false: las FK ya no deciden la posición, solo se dibujan sobre la rejilla.
    # Se unen tabla con tabla y no fila con fila: anclar a un PORT hace que splines=ortho deje de
    # esquivar las cajas y las líneas terminen cruzando por encima de otras tablas. Qué columna es
    # la clave foránea se sigue leyendo en la marca FK de cada fila.
    for tabla, columna, ref, columna_ref in fk:
        dot.edge(ref, tabla, constraint="false")
    for origen, destino, etiqueta in RELACIONES_LOGICAS:
        if origen in columnas and destino in columnas:
            # xlabel y no label: splines=ortho no sabe dibujar etiquetas sobre la arista.
            dot.edge(origen, destino, constraint="false", style="dashed", color="#9ca3af",
                     arrowhead="vee", arrowtail="none", dir="forward",
                     xlabel=etiqueta, fontsize="9", fontcolor="#6b7280")
    return dot


def main() -> None:
    with conectar() as conn:
        columnas, pk, fk = leer_catalogo(conn)
    if not columnas:
        raise SystemExit("La BD no tiene tablas: ejecuta primero BD/crear_bd.py.")
    dot = dibujar(columnas, pk, fk)
    for formato in ("png", "svg"):
        SALIDA.with_suffix(f".{formato}").write_bytes(dot.pipe(format=formato))
    print(f"{len(columnas)} tablas, {len(fk)} claves foráneas -> {SALIDA.with_suffix('.png')}")


if __name__ == "__main__":
    main()
