from engine.parsing.normalize import FileIR
from engine.quality.complexity import complexity_signals
from engine.quality.correctness import correctness_signals
from engine.quality.style import style_signals


def score_file(file_ir: FileIR) -> dict[str, object]:
    """Return a 0-100 composite score from simple documented signal weights.

    The score starts with 50 syntax points, 25 complexity points, 15 nesting
    points, and up to 10 comment-density points. Complexity loses one point
    per unit above 10, nesting loses two points per level above 3, long
    functions lose 0.5 points per line above 20, and each undefined variable
    loses 30 points. These penalties make the score respond to real IR signals.
    """
    complexity = complexity_signals(file_ir)
    correctness = correctness_signals(file_ir)
    style = style_signals(file_ir)
    if not correctness["syntax_valid"]:
        return {
            "composite_score": 0.0,
            "complexity": complexity,
            "correctness": correctness,
            "style": style,
            "flags": list(correctness["issues"]),
        }
    complexity_penalty = max(0, int(complexity["aggregate_cyclomatic_complexity"]) - 10)
    nesting_penalty = max(0, int(complexity["max_nesting_depth"]) - 3) * 2
    syntax_points = 50.0
    complexity_points = max(0.0, 25.0 - complexity_penalty)
    nesting_points = max(0.0, 15.0 - nesting_penalty)
    comment_points = min(10.0, float(style["comment_density"]) * 50)
    length_penalty = sum(
        max(0, int(function["length_lines"]) - 20) * 0.5
        for function in style["functions"]
    )
    undefined_count = sum(
        len(names) for names in correctness["undefined_variables"].values()
    )
    correctness_penalty = undefined_count * 30.0
    score = round(max(0.0, min(100.0, syntax_points + complexity_points + nesting_points + comment_points - length_penalty - correctness_penalty)), 1)
    flags = list(correctness["issues"])
    if int(complexity["max_nesting_depth"]) > 3:
        flags.append("deep_nesting")
    for function in style["functions"]:
        if function["long_function"]:
            flags.append(f"long_function:{function['name']}")
    return {
        "composite_score": score,
        "complexity": complexity,
        "correctness": correctness,
        "style": style,
        "flags": flags,
    }
