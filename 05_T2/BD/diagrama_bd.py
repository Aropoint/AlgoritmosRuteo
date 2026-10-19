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


def dibujar(columnas, pk, fk) -> graphviz.Digraph:
    dot = graphviz.Digraph("bd", graph_attr={"rankdir": "LR", "fontname": "Helvetica", "nodesep": "0.4",
                                             "ranksep": "1.1", "label": "Modelo de datos: ruteo resiliente de UAV",
                                             "labelloc": "t", "fontsize": "18"},
                           node_attr={"shape": "plaintext", "fontname": "Helvetica", "fontsize": "10"},
                           edge_attr={"color": "#555555", "arrowhead": "crow", "arrowtail": "tee", "dir": "both"})
    con_fk = {(t, c) for t, c, _, _ in fk}
    por_grupo: dict[int, list[str]] = {}
    for tabla in columnas:
        por_grupo.setdefault(_grupo(tabla), []).append(tabla)
    for i, tablas in sorted(por_grupo.items()):
        titulo, color, _ = GRUPOS[i]
        with dot.subgraph(name=f"cluster_{i}") as sub:
            sub.attr(label=titulo, style="rounded,filled", color="#999999", fillcolor=color)
            for tabla in sorted(tablas):
                filas = [f'<TR><TD COLSPAN="2" BGCOLOR="#1f2937"><FONT COLOR="white"><B>{tabla}</B></FONT></TD></TR>']
                for columna, tipo, no_nulo in columnas[tabla]:
                    marcas = ("PK " if columna in pk.get(tabla, ()) else "") + ("FK " if (tabla, columna) in con_fk else "")
                    nombre = f"<B>{html.escape(columna)}</B>" if marcas.startswith("PK") else html.escape(columna)
                    tipo_txt = html.escape(tipo) + ("" if no_nulo else " ?")
                    filas.append(f'<TR><TD ALIGN="LEFT" PORT="{columna}">{marcas}{nombre}</TD>'
                                 f'<TD ALIGN="LEFT"><FONT COLOR="#555555">{tipo_txt}</FONT></TD></TR>')
                etiqueta = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="white">' + "".join(filas) + "</TABLE>>"
                sub.node(tabla, label=etiqueta)
    for tabla, columna, ref, columna_ref in fk:
        dot.edge(f"{ref}:{columna_ref}", f"{tabla}:{columna}")
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
