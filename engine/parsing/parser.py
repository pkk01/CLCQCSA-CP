from tree_sitter import Parser, Tree

from engine.parsing.grammars import get_language


def parse_source(source: str, language: str) -> Tree:
    """Parse source text with the grammar for ``language``."""
    parser = Parser(get_language(language))
    return parser.parse(source.encode("utf-8"))
