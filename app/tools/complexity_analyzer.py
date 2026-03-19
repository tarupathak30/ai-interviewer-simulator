import ast
import re


def analyze_complexity(code: str) -> dict:
    """
    Analyze time and space complexity of Python code.
    Returns Big O estimates with reasoning.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "reasoning": "Could not parse code due to syntax error.",
            "nested_loops": 0,
            "recursion": False,
        }

    analyzer = _ComplexityVisitor()
    analyzer.visit(tree)

    time_complexity = _estimate_time(analyzer)
    space_complexity = _estimate_space(analyzer)
    reasoning = _build_reasoning(analyzer, time_complexity, space_complexity)

    return {
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "reasoning": reasoning,
        "nested_loops": analyzer.max_loop_depth,
        "recursion": analyzer.has_recursion,
        "sorting": analyzer.has_sorting,
        "hash_structures": analyzer.hash_structure_count,
    }


class _ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.has_recursion = False
        self.has_sorting = False
        self.hash_structure_count = 0
        self.list_appends = 0
        self.current_function = None
        self.function_names = set()
        self.recursive_calls = set()

    def visit_FunctionDef(self, node):
        self.function_names.add(node.name)
        prev = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = prev

    def visit_For(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node):
        # Detect set() and dict() constructor calls
        if isinstance(node.func, ast.Name):
            if node.func.id in ("set", "dict", "defaultdict", "Counter", "OrderedDict"):
                self.hash_structure_count += 1

        # Check sorting
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("sort", "sorted"):
                self.has_sorting = True
        if isinstance(node.func, ast.Name):
            if node.func.id == "sorted":
                self.has_sorting = True
            # Check recursion
            if self.current_function and node.func.id == self.current_function:
                self.has_recursion = True

        # Check list appends inside loops
        if isinstance(node.func, ast.Attribute) and node.func.attr == "append":
            self.list_appends += 1

        self.generic_visit(node)

    def visit_Dict(self, node):
        self.hash_structure_count += 1
        self.generic_visit(node)

    def visit_Set(self, node):
        self.hash_structure_count += 1
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.hash_structure_count += 1
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.hash_structure_count += 1
        self.generic_visit(node)


def _estimate_time(a: _ComplexityVisitor) -> str:
    if a.has_recursion:
        if a.max_loop_depth >= 1:
            return "O(n log n) ~ O(2^n)"
        return "O(2^n) or O(n log n)"  # depends on recursion type

    if a.max_loop_depth == 0:
        return "O(1)"
    elif a.max_loop_depth == 1:
        if a.has_sorting:
            return "O(n log n)"
        return "O(n)"
    elif a.max_loop_depth == 2:
        if a.has_sorting:
            return "O(n² log n)"
        return "O(n²)"
    elif a.max_loop_depth == 3:
        return "O(n³)"
    else:
        return f"O(n^{a.max_loop_depth})"


def _estimate_space(a: _ComplexityVisitor) -> str:
    if a.has_recursion:
        return "O(n)"  # call stack
    if a.hash_structure_count > 0:
        return "O(n)"
    if a.list_appends > 0:
        return "O(n)"
    return "O(1)"


def _build_reasoning(a: _ComplexityVisitor, time: str, space: str) -> str:
    parts = []

    if a.max_loop_depth == 0 and not a.has_recursion:
        parts.append("No loops or recursion detected — constant time operations only.")
    elif a.max_loop_depth == 1:
        parts.append("Single loop detected — linear traversal of input.")
    elif a.max_loop_depth == 2:
        parts.append(f"Nested loops detected (depth {a.max_loop_depth}) — quadratic growth.")
    elif a.max_loop_depth >= 3:
        parts.append(f"Deeply nested loops (depth {a.max_loop_depth}) — polynomial complexity.")

    if a.has_sorting:
        parts.append("Sorting operation found — adds O(n log n) factor.")

    if a.has_recursion:
        parts.append("Recursive calls detected — complexity depends on recurrence relation.")

    if a.hash_structure_count > 0:
        parts.append(f"{a.hash_structure_count} hash structure(s) (dict/set) used — O(1) average lookups but O(n) space.")

    parts.append(f"Estimated time: {time}, space: {space}.")
    return " ".join(parts)