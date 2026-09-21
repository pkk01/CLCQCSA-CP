from engine.parsing import normalize_tree, parse_source
from engine.parsing.normalize import FileIR, FunctionIR
from engine.quality import complexity_signals, correctness_signals, score_file, style_signals


def test_quality_signals_and_composite_score() -> None:
    file_ir = FileIR(
        language="python",
        loc=10,
        comment_lines=2,
        functions=[
            FunctionIR(
                name="work",
                start_line=1,
                end_line=5,
                branch_count=2,
                loop_count=1,
                max_nesting_depth=4,
                param_count=2,
            )
        ],
    )

    assert complexity_signals(file_ir)["aggregate_cyclomatic_complexity"] == 4
    assert complexity_signals(file_ir)["max_nesting_depth"] == 4
    assert style_signals(file_ir)["comment_density"] == 0.2
    assert correctness_signals(file_ir)["issues"] == []
    assert score_file(file_ir)["composite_score"] == 98.0


def test_invalid_file_receives_syntax_issue() -> None:
    file_ir = FileIR(language="java", loc=1, syntax_valid=False)

    result = score_file(file_ir)

    assert result["composite_score"] == 0.0
    assert result["flags"] == ["syntax_error"]


def test_flags_undefined_java_foreach_iterable() -> None:
    source = """class Demo {
    int total(int[] values) {
        for (int value : missing) {
            return value;
        }
        return 0;
    }
}
"""
    file_ir = normalize_tree(parse_source(source, "java"), source, "java")

    result = correctness_signals(file_ir)

    assert result["issues"] == ["undefined_variable"]
    assert result["undefined_variables"] == {"total": ["missing"]}


def test_parsed_complexity_changes_composite_score() -> None:
    simple_source = "def add(first, second):\n    return first + second\n"
    nested_source = """def search(items):
    for first in items:
        for second in items:
            for third in items:
                for fourth in items:
                    if fourth:
                        return fourth
    return None
"""
    simple = normalize_tree(parse_source(simple_source, "python"), simple_source, "python")
    nested = normalize_tree(parse_source(nested_source, "python"), nested_source, "python")

    simple_score = score_file(simple)["composite_score"]
    nested_score = score_file(nested)["composite_score"]

    assert simple_score == 90.0
    assert nested_score < simple_score


def test_java_report_method_does_not_flag_fields_as_undefined() -> None:
    source = """class Report {
    void generate(int[] data) {
        System.out.println("Starting");
        int sum = 0;
        int max = data[0];
        int min = data[0];
        for (int i = 0; i < data.length; i++) {
            sum += data[i];
            if (data[i] > max) { max = data[i]; }
            if (data[i] < min) { min = data[i]; }
        }
        double avg = (double) sum / data.length;
        System.out.println("Sum: " + sum);
        System.out.println("Max: " + max);
        System.out.println("Min: " + min);
        System.out.println("Avg: " + avg);
        System.out.println("Done");
    }
}
"""
    file_ir = normalize_tree(parse_source(source, "java"), source, "java")

    result = score_file(file_ir)

    assert result["correctness"]["undefined_variables"] == {}
    assert result["composite_score"] == 90.0
