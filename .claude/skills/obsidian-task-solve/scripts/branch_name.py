#!/usr/bin/env python3
"""Nombre de rama determinista para una tarea de ObsidianRPG (CLAUDE.md sección 5).

Por qué existe: evita que el modelo "razone" el slug (acentos, mayúsculas, largo) en
cada corrida — un cálculo determinista no debería gastar tokens de razonamiento.

Uso:
  branch_name.py --tipo Bug --id 12 --titulo "El esquema no cubre objetos compartidos"
  -> fix/TSK-12-el-esquema-no-cubre-objetos-compartidos
"""
import argparse
import re
import sys
import unicodedata

MAX_SLUG_LEN = 40


def slugify(text: str, max_len: int = MAX_SLUG_LEN) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text[:max_len].rstrip("-")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tipo", required=True, help='Campo "tipo" del frontmatter de la tarea')
    parser.add_argument("--id", required=True, type=int, help='Campo "id" del frontmatter (TSK-<id>)')
    parser.add_argument("--titulo", required=True, help='Campo "titulo" del frontmatter')
    args = parser.parse_args()

    if not args.titulo.strip():
        print("El título no puede estar vacío.", file=sys.stderr)
        sys.exit(1)

    prefix = "fix" if args.tipo == "Bug" else "feature"
    slug = slugify(args.titulo)
    if not slug:
        print("El título no produjo un slug válido (¿solo símbolos?).", file=sys.stderr)
        sys.exit(1)
    print(f"{prefix}/TSK-{args.id}-{slug}")


if __name__ == "__main__":
    main()
