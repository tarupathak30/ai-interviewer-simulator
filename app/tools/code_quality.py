import ast
import re


def analyze_code_quality(code: str) -> dict:
    """
    Analyze code quality: PEP 8, naming, docstrings, readability.
    Returns a quality score and list of issues.
    """
    issues = []
    suggestions = []
    score = 100

    lines = code.splitlines()

    # --- PEP 8 Checks ---

    for i, line in enumerate(lines, 1):
        # Line too long (PEP 8: max 79 chars)
        if len(line) > 79:
            issues.append(f"Line {i}: Line too long ({len(line)} chars, max 79)")
            score -= 2

        # Trailing whitespace
        if line.rstrip('\n') != line.rstrip():
            issues.append(f"Line {i}: Trailing whitespace")
            score -= 1

        # Tabs instead of spaces
        if '\t' in line:
            issues.append(f"Line {i}: Tab used instead of spaces")
            score -= 2

        # Missing space after comma
        if re.search(r',\S', line) and not re.search(r',["\']', line):
            issues.append(f"Line {i}: Missing space after comma")
            score -= 1

        # No space around operators (basic check)
        if re.search(r'\w=[^=\s]', line) and '==' not in line and '!=' not in line \
                and '>=' not in line and '<=' not in line and 'def ' not in line \
                and 'lambda' not in line:
            issues.append(f"Line {i}: Missing spaces around assignment operator")
            score -= 1

    # --- AST-based Checks ---
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "quality_score": 0,
            "issues": [f"Syntax error: {e}"],
            "suggestions": [],
            "has_docstrings": False,
            "naming_issues": [],
            "pep8_violations": len(issues),
        }

    naming_issues = []
    has_docstrings = False
    function_count = 0
    documented_count = 0

    for node in ast.walk(tree):

        # Check function naming (should be snake_case)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_count += 1
            if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and node.name != '__init__':
                naming_issues.append(f"Function '{node.name}' should be snake_case")
                score -= 3

            # Check for docstring
            if (ast.get_docstring(node)):
                documented_count += 1

        # Check class naming (should be PascalCase)
        if isinstance(node, ast.ClassDef):
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                naming_issues.append(f"Class '{node.name}' should be PascalCase")
                score -= 3

        # Check variable naming (should not be single char except loop vars)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if len(node.id) == 1 and node.id not in ('i', 'j', 'k', 'n', 'm', 'x', 'y', 'z', '_'):
                naming_issues.append(f"Variable '{node.id}' — consider a more descriptive name")
                score -= 1

    # Docstring coverage
    if function_count > 0:
        coverage = documented_count / function_count
        has_docstrings = coverage > 0
        if coverage == 0:
            issues.append("No docstrings found — add docstrings to functions")
            suggestions.append("Add docstrings explaining what each function does, its args, and return value")
            score -= 5
        elif coverage < 1.0:
            issues.append(f"Partial docstring coverage ({documented_count}/{function_count} functions)")
            score -= 2

    # Empty except blocks
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                issues.append("Empty except block found — avoid silencing errors")
                score -= 5

    # Magic numbers
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if node.value not in (0, 1, -1, 2, True, False):
                suggestions.append(f"Magic number {node.value} — consider using a named constant")

    # Build suggestions
    if naming_issues:
        suggestions.extend(naming_issues)
    if not has_docstrings and function_count > 0:
        suggestions.append("Add docstrings to improve code documentation")

    # Cap score
    score = max(0, min(100, score))

    return {
        "quality_score": score,
        "issues": issues[:10],           # cap at 10 issues
        "suggestions": suggestions[:5],  # cap at 5 suggestions
        "has_docstrings": has_docstrings,
        "naming_issues": naming_issues,
        "pep8_violations": len([i for i in issues if "Line" in i]),
    }