from engine.parsing import normalize_tree, parse_source


def test_normalizes_python_function_and_file_signals() -> None:
    source = """import os

# total items
def total(items):
    for item in items:
        if item:
            return 1
    return 0
"""

    file_ir = normalize_tree(parse_source(source, "python"), source, "python")

    assert file_ir.language == "python"
    assert file_ir.loc == 8
    assert file_ir.imports == ["import os"]
    assert file_ir.comment_lines == 1
    assert file_ir.syntax_valid is True
    assert len(file_ir.functions) == 1
    function = file_ir.functions[0]
    assert function.name == "total"
    assert function.start_line == 4
    assert function.end_line == 8
    assert function.branch_count == 1
    assert function.loop_count == 1
    assert function.max_nesting_depth == 2
    assert function.param_count == 1


def test_normalizes_java_method_and_import() -> None:
    source = """import java.util.List;
class Demo {
    int total(List<Integer> items) {
        for (int item : items) {
            if (item > 0) return item;
        }
        return 0;
    }
}
"""

    file_ir = normalize_tree(parse_source(source, "java"), source, "java")

    assert file_ir.language == "java"
    assert file_ir.loc == 9
    assert file_ir.imports == ["import java.util.List;"]
    assert file_ir.syntax_valid is True
    function = file_ir.functions[0]
    assert function.name == "total"
    assert function.start_line == 3
    assert function.end_line == 8
    assert function.branch_count == 1
    assert function.loop_count == 1
    assert function.max_nesting_depth == 2
    assert function.param_count == 1


def test_marks_malformed_source_invalid() -> None:
    source = "def broken(:\n    return 1\n"

    file_ir = normalize_tree(parse_source(source, "python"), source, "python")

    assert file_ir.syntax_valid is False


def test_python_parameters_are_declared_names() -> None:
    source = "def add(first, second):\n    return first + second\n"

    file_ir = normalize_tree(parse_source(source, "python"), source, "python")

    assert file_ir.functions[0].declared_names == ("first", "second")
    assert file_ir.functions[0].used_names == ()
