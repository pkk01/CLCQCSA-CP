from engine.parsing.normalize import FileIR


def correctness_signals(file_ir: FileIR) -> dict[str, object]:
    """Report syntax and basic undefined-name checks from the normalized IR.

    A name is considered undefined when it is used inside a function but is not
    present in that function's parameters or local declarations. This is a
    deliberately conservative static check, not a full compiler/type checker.
    """
    issues = [] if file_ir.syntax_valid else ["syntax_error"]
    undefined_by_function = {}
    for function in file_ir.functions:
        declared = set(function.declared_names)
        undefined = sorted(set(function.used_names) - declared)
        if undefined:
            undefined_by_function[function.name] = undefined
    if undefined_by_function:
        issues.append("undefined_variable")
    return {
        "syntax_valid": file_ir.syntax_valid,
        "issues": issues,
        "undefined_variables": undefined_by_function,
    }
