from engine.parsing.normalize import FileIR, FunctionIR


def complexity_signals(file_ir: FileIR) -> dict[str, object]:
    """Compute branch-based cyclomatic complexity and nesting signals.

    Each function starts at complexity 1 and adds one for every branch and
    loop. Higher nesting is reported as a review flag by the scorer.
    """
    functions = [
        {
            "name": function.name,
            "cyclomatic_complexity": 1 + function.branch_count + function.loop_count,
            "nesting_depth": function.max_nesting_depth,
        }
        for function in file_ir.functions
    ]
    total_complexity = sum(item["cyclomatic_complexity"] for item in functions)
    return {
        "functions": functions,
        "aggregate_cyclomatic_complexity": total_complexity,
        "max_nesting_depth": max((item["nesting_depth"] for item in functions), default=0),
    }
