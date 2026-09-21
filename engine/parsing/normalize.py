from dataclasses import dataclass, field

from tree_sitter import Node, Tree


@dataclass(frozen=True)
class FunctionIR:
    name: str
    start_line: int
    end_line: int
    branch_count: int
    loop_count: int
    max_nesting_depth: int
    param_count: int
    declared_names: tuple[str, ...] = ()
    used_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class FileIR:
    language: str
    loc: int
    functions: list[FunctionIR] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    comment_lines: int = 0
    syntax_valid: bool = True


_FUNCTION_TYPES = {"python": {"function_definition"}, "java": {"method_declaration"}}
_BRANCH_TYPES = {"if_statement", "elif_clause", "conditional_expression", "switch_expression", "switch_label"}
_LOOP_TYPES = {"for_statement", "enhanced_for_statement", "while_statement", "do_statement", "for_in_statement"}
_COMMENT_TYPES = {"comment", "line_comment", "block_comment"}
_IMPORT_TYPES = {"import_statement", "import_declaration", "import_from_statement"}
_PYTHON_BUILTINS = {"abs", "all", "any", "bool", "dict", "enumerate", "float", "int", "len", "list", "max", "min", "print", "range", "set", "str", "sum", "tuple"}


def normalize_tree(tree: Tree, source: str, language: str) -> FileIR:
    """Convert a parsed tree into the language-neutral parsing IR."""
    root = tree.root_node
    functions = [
        _normalize_function(node, language)
        for node in _walk(root)
        if node.type in _FUNCTION_TYPES[language]
    ]
    imports = [
        _node_text(node, source)
        for node in _walk(root)
        if node.type in _IMPORT_TYPES
    ]
    comment_lines = sum(
        node.end_point[0] - node.start_point[0] + 1
        for node in _walk(root)
        if node.type in _COMMENT_TYPES
    )
    return FileIR(
        language=language,
        loc=len(source.splitlines()),
        functions=functions,
        imports=imports,
        comment_lines=comment_lines,
        syntax_valid=not root.has_error,
    )


def _normalize_function(node: Node, language: str) -> FunctionIR:
    descendants = list(_walk(node))
    branch_count = sum(item.type in _BRANCH_TYPES for item in descendants)
    loop_count = sum(item.type in _LOOP_TYPES for item in descendants)
    nesting_depth = _max_control_depth(node, 0)
    name_node = node.child_by_field_name("name")
    parameters = node.child_by_field_name("parameters")
    name = name_node.text.decode("utf-8") if name_node else "<anonymous>"
    param_count = _count_parameters(parameters, language)
    declared_names, used_names = _collect_names(node, language, name)
    return FunctionIR(
        name=name,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        branch_count=branch_count,
        loop_count=loop_count,
        max_nesting_depth=nesting_depth,
        param_count=param_count,
        declared_names=declared_names,
        used_names=used_names,
    )


def _collect_names(node: Node, language: str, function_name: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    identifiers = [
        item.text.decode("utf-8")
        for item in _walk(node)
        if item.type == "identifier" and _is_variable_use(item, language)
    ]
    declared = {function_name}
    parameters = node.child_by_field_name("parameters")
    if parameters is not None:
        for parameter in _walk(parameters):
            name_node = parameter.child_by_field_name("name")
            if name_node is not None and parameter.type in {"formal_parameter", "typed_parameter", "default_parameter"}:
                declared.add(name_node.text.decode("utf-8"))
            elif language == "python" and parameter.type == "identifier":
                declared.add(parameter.text.decode("utf-8"))
    for item in _walk(node):
        if item.type in {"variable_declarator", "assignment"}:
            name_node = item.child_by_field_name("name") or item.child_by_field_name("left")
            if name_node is not None and name_node.type == "identifier":
                declared.add(name_node.text.decode("utf-8"))
        if language == "java" and item.type == "enhanced_for_statement":
            name_node = item.child_by_field_name("name")
            if name_node is not None:
                declared.add(name_node.text.decode("utf-8"))
        if language == "python" and item.type in {"for_statement", "for_in_statement"}:
            name_node = item.child_by_field_name("left")
            if name_node is not None:
                declared.update(
                    child.text.decode("utf-8")
                    for child in _walk(name_node)
                    if child.type == "identifier"
                )
    used = tuple(dict.fromkeys(name for name in identifiers if name not in declared))
    return tuple(sorted(declared - {function_name})), used


def _is_variable_use(node: Node, language: str) -> bool:
    name = node.text.decode("utf-8")
    if language == "python" and name in _PYTHON_BUILTINS:
        return False
    if language == "java" and node.parent is not None:
        if node.parent.type == "field_access":
            object_node = node.parent.child_by_field_name("object")
            field_node = node.parent.child_by_field_name("field")
            if field_node is not None and field_node.start_byte == node.start_byte:
                return False
            if object_node is not None and object_node.start_byte == node.start_byte and name[:1].isupper():
                return False
        if node.parent.type == "method_invocation":
            method_node = node.parent.child_by_field_name("name")
            if method_node is not None and method_node.start_byte == node.start_byte:
                return False
    if node.parent is not None and node.parent.type in {"call", "attribute", "method_invocation"}:
        return False
    return True


def _max_control_depth(node: Node, parent_depth: int) -> int:
    control = node.type in _BRANCH_TYPES or node.type in _LOOP_TYPES
    current_depth = parent_depth + int(control)
    child_depths = [_max_control_depth(child, current_depth) for child in node.children]
    return max([current_depth, *child_depths])


def _count_parameters(parameters: Node | None, language: str) -> int:
    if parameters is None:
        return 0
    if language == "python":
        return sum(
            child.type in {"identifier", "default_parameter", "typed_parameter", "list_splat_pattern", "dictionary_splat_pattern"}
            for child in parameters.named_children
        )
    return sum(child.type in {"formal_parameter", "spread_parameter", "receiver_parameter"} for child in parameters.named_children)


def _walk(node: Node) -> list[Node]:
    result = [node]
    for child in node.children:
        result.extend(_walk(child))
    return result


def _node_text(node: Node, source: str) -> str:
    lines = source.splitlines(keepends=True)
    return "".join(lines[node.start_point[0] : node.end_point[0] + 1]).strip()
