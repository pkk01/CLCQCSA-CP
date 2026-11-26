"""engine/similarity — cross-language structural plagiarism detection.

Algorithm
---------
1. Parse each snippet with the existing tree-sitter parser (engine.parsing).
   If either tree contains ERROR nodes a SyntaxError is raised immediately.
2. Walk the parse tree in-order and emit a *language-agnostic token sequence*
   by mapping each node type to a category name.  Identifiers, literals,
   comments, punctuation and whitespace are intentionally ignored so the same
   algorithm, control-flow and overall structure registers as "similar" even
   when written in different languages or with renamed variables.
3. Similarity is computed two ways, then averaged:
   * structural_score – difflib.SequenceMatcher ratio on the two token lists.
     Captures order and contiguous runs of matching control-flow tokens.
   * shingle_score    – Jaccard similarity of token 3-grams (shingles).
     Captures local structural patterns regardless of global alignment.
   final_similarity = 0.7 * structural_score + 0.3 * shingle_score, expressed
   as a percentage 0-100.
   The structural component is weighted higher because cross-language comparisons
   share the same control-flow order but naturally differ in n-gram sets (e.g.
   Python range-based for vs Java C-style for produce different shingles despite
   the same algorithmic intent).
4. Verdict thresholds (see THRESHOLDS dict below):
   >= 80  → "plagiarized"
   50–79  → "suspicious"
   <  50  → "not_plagiarized"
5. Edge-case: fewer than MIN_TOKENS tokens in either snippet raises ValueError
   so the API can return 400 rather than a meaningless 100 % for empty inputs.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass

from engine.parsing.grammars import get_language
from tree_sitter import Parser

# ---------------------------------------------------------------------------
# Token-category mapping
# Map node.type → language-agnostic category label.
# Every type absent from this dict is skipped (but its children are still
# walked), so only structural constructs appear in the token sequence.
# ---------------------------------------------------------------------------
NODE_TYPE_TO_TOKEN: dict[str, str] = {
    # Functions / methods
    "function_definition": "FUNC",
    "method_declaration": "FUNC",
    "constructor_declaration": "FUNC",
    # Loops
    "for_statement": "LOOP",
    "enhanced_for_statement": "LOOP",
    "while_statement": "LOOP",
    "do_statement": "LOOP",
    "for_in_statement": "LOOP",
    # Branches
    "if_statement": "BRANCH",
    "elif_clause": "BRANCH",
    "else_clause": "BRANCH",
    "conditional_expression": "BRANCH",
    "switch_expression": "BRANCH",
    "switch_statement": "BRANCH",
    "case_clause": "BRANCH",
    # Returns
    "return_statement": "RETURN",
    # Assignments
    "assignment": "ASSIGN",
    "augmented_assignment": "ASSIGN",
    "assignment_expression": "ASSIGN",
    "local_variable_declaration": "ASSIGN",
    "variable_declarator": "ASSIGN",
    # Calls
    "call": "CALL",
    "method_invocation": "CALL",
    # Binary / boolean expressions
    "binary_operator": "BINOP",
    "binary_expression": "BINOP",
    "boolean_operator": "BINOP",
    "comparison_operator": "BINOP",
    # Exception handling
    "try_statement": "TRY",
    "catch_clause": "TRY",
    "finally_clause": "TRY",
    # Jumps
    "break_statement": "JUMP",
    "continue_statement": "JUMP",
    # Class declarations
    "class_definition": "CLASS",
    "class_declaration": "CLASS",
}

# ---------------------------------------------------------------------------
# Verdict thresholds
# ---------------------------------------------------------------------------
THRESHOLDS = {
    "plagiarized": 80.0,
    "suspicious": 50.0,
}

# Minimum structural tokens needed in each snippet for a valid comparison.
MIN_TOKENS = 5

# n-gram size for the shingle score
NGRAM_N = 3


# ---------------------------------------------------------------------------
# Public result dataclass
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SimilarityResult:
    """Full result of a pairwise plagiarism comparison."""

    similarity: float          # 0-100
    verdict: str               # "plagiarized" | "suspicious" | "not_plagiarized"
    structural_score: float    # 0-1  (SequenceMatcher ratio)
    shingle_score: float       # 0-1  (Jaccard 3-gram similarity)
    tokens_a: int
    tokens_b: int
    matching_ngrams: int
    reason: str


# ---------------------------------------------------------------------------
# Legacy stub interface preserved for Review 1 test compatibility
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SimilarityReport:
    """Legacy wrapper — not used by the new endpoint but kept to avoid import errors."""
    pairs: list[dict[str, object]]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_to_tree(source: str, language: str):
    """Return a tree-sitter Tree for *source* in *language*.

    Raises ValueError for unsupported languages.
    Raises SyntaxError when the parse tree contains ERROR nodes.
    """
    lang = get_language(language)  # raises ValueError for unknown langs
    parser = Parser(lang)
    tree = parser.parse(source.encode("utf-8"))
    if tree.root_node.has_error:
        raise SyntaxError(
            f"Syntax error detected in {language} snippet — "
            "ensure the code is valid before comparing."
        )
    return tree


def _tree_to_tokens(tree) -> list[str]:
    """Walk the parse tree in-order and emit structural tokens.

    Only node types present in NODE_TYPE_TO_TOKEN contribute a token.
    Children of every node are always visited, so skipped nodes are
    transparent — their structural descendants still get emitted.
    """
    tokens: list[str] = []

    def _walk(node) -> None:
        tok = NODE_TYPE_TO_TOKEN.get(node.type)
        if tok:
            tokens.append(tok)
        for child in node.children:
            _walk(child)

    _walk(tree.root_node)
    return tokens


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    """Return all n-grams from *tokens*."""
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _jaccard(a: list[tuple], b: list[tuple]) -> float:
    """Jaccard similarity of two n-gram multisets."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    set_a, set_b = set(a), set(b)
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def _build_reason(tokens_a: list[str], tokens_b: list[str], similarity: float) -> str:
    """Generate a one-line human-readable explanation of the score."""
    if not tokens_a or not tokens_b:
        return "One or both snippets produced no structural tokens."

    # Describe the dominant pattern in the token sequences
    dominant_a = max(set(tokens_a), key=tokens_a.count) if tokens_a else None
    dominant_b = max(set(tokens_b), key=tokens_b.count) if tokens_b else None

    has_loop_a = "LOOP" in tokens_a
    has_loop_b = "LOOP" in tokens_b
    has_branch_a = "BRANCH" in tokens_a
    has_branch_b = "BRANCH" in tokens_b
    has_func_a = "FUNC" in tokens_a
    has_func_b = "FUNC" in tokens_b

    if similarity >= THRESHOLDS["plagiarized"]:
        if has_loop_a and has_loop_b and has_branch_a and has_branch_b:
            return (
                "Same control-flow structure: both contain loops with nested branches "
                "and matching assignment/return patterns."
            )
        if has_func_a and has_func_b and dominant_a == dominant_b:
            return (
                f"Same function structure: both snippets share dominant pattern "
                f"'{dominant_a}' and near-identical token sequences."
            )
        return "Near-identical structural token sequences despite surface-level differences."
    elif similarity >= THRESHOLDS["suspicious"]:
        shared: list[str] = []
        if has_loop_a and has_loop_b:
            shared.append("loops")
        if has_branch_a and has_branch_b:
            shared.append("branches")
        if has_func_a and has_func_b:
            shared.append("function definitions")
        if shared:
            return f"Partially overlapping control-flow: both use {', '.join(shared)}, but overall structure differs."
        return "Moderate structural overlap — some shared patterns but significant differences."
    else:
        if not (has_func_a or has_func_b):
            return "Neither snippet defines functions; control-flow patterns are unrelated."
        return "Different control-flow structure: low overlap in loops, branches, and assignments."


def _verdict(similarity: float) -> str:
    if similarity >= THRESHOLDS["plagiarized"]:
        return "plagiarized"
    if similarity >= THRESHOLDS["suspicious"]:
        return "suspicious"
    return "not_plagiarized"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compare_snippets(
    code_a: str,
    language_a: str,
    code_b: str,
    language_b: str,
) -> SimilarityResult:
    """Compare two code snippets for structural similarity / plagiarism.

    Parameters
    ----------
    code_a, code_b:
        Source code text to compare.
    language_a, language_b:
        Language tags — must be "python" or "java" (case-insensitive match
        against the supported-language list from engine.parsing.grammars).

    Returns
    -------
    SimilarityResult
        Full comparison report with similarity percentage, verdict, and stats.

    Raises
    ------
    ValueError
        * Unsupported language tag.
        * Either snippet produces fewer than MIN_TOKENS structural tokens.
    SyntaxError
        * Either snippet contains a tree-sitter ERROR node.
    """
    language_a = language_a.lower().strip()
    language_b = language_b.lower().strip()

    # 1. Parse — raises SyntaxError on parse errors, ValueError on bad lang
    tree_a = _parse_to_tree(code_a, language_a)
    tree_b = _parse_to_tree(code_b, language_b)

    # 2. Convert to structural token sequences
    tokens_a = _tree_to_tokens(tree_a)
    tokens_b = _tree_to_tokens(tree_b)

    # 3. Edge-case: too short
    if len(tokens_a) < MIN_TOKENS:
        raise ValueError(
            f"Snippet A is too short to compare: produced only {len(tokens_a)} structural "
            f"token(s); need at least {MIN_TOKENS}."
        )
    if len(tokens_b) < MIN_TOKENS:
        raise ValueError(
            f"Snippet B is too short to compare: produced only {len(tokens_b)} structural "
            f"token(s); need at least {MIN_TOKENS}."
        )

    # 4. Structural score (SequenceMatcher on token lists)
    structural_score = difflib.SequenceMatcher(
        None, tokens_a, tokens_b
    ).ratio()

    # 5. Shingle score (Jaccard on 3-grams)
    ngrams_a = _ngrams(tokens_a, NGRAM_N)
    ngrams_b = _ngrams(tokens_b, NGRAM_N)
    shingle_score = _jaccard(ngrams_a, ngrams_b)
    matching_ngrams = len(set(ngrams_a) & set(ngrams_b))

    # 6. Combined similarity
    # Weights: structural=0.7, shingle=0.3.
    # Structural is weighted higher because cross-language comparisons share
    # the same control-flow order but differ in n-gram makeup (e.g. Python
    # range-based for vs Java C-style for produce distinct token sequences
    # despite identical algorithmic intent).
    similarity = round((0.7 * structural_score + 0.3 * shingle_score) * 100, 2)

    verdict = _verdict(similarity)
    reason = _build_reason(tokens_a, tokens_b, similarity)

    return SimilarityResult(
        similarity=similarity,
        verdict=verdict,
        structural_score=round(structural_score, 4),
        shingle_score=round(shingle_score, 4),
        tokens_a=len(tokens_a),
        tokens_b=len(tokens_b),
        matching_ngrams=matching_ngrams,
        reason=reason,
    )
