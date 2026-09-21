from engine.parsing.normalize import FileIR


def style_signals(file_ir: FileIR) -> dict[str, object]:
    """Compute comment density and long-function style signals.

    Comment density is comment lines divided by LOC; functions over 40 lines
    receive a long-function flag because they are harder to review.
    """
    function_lengths = [
        {
            "name": function.name,
            "length_lines": function.end_line - function.start_line + 1,
            "long_function": function.end_line - function.start_line + 1 > 40,
        }
        for function in file_ir.functions
    ]
    return {
        "comment_density": file_ir.comment_lines / file_ir.loc if file_ir.loc else 0.0,
        "functions": function_lengths,
    }
