"""Static checks on generated IEC 61131-3 Structured Text.

This is not a compiler. It catches the mistakes the generator could make:
unbalanced blocks, undeclared variables, missing semicolons.
"""
import re

KEYWORDS = {
    "IF", "THEN", "ELSE", "ELSIF", "END_IF", "NOT", "AND", "OR", "XOR",
    "TRUE", "FALSE", "LIMIT", "PROGRAM", "END_PROGRAM", "VAR", "END_VAR",
    "BOOL", "REAL", "INT", "TIME", "MOD", "CASE", "OF", "END_CASE",
}


def _strip_comments(code):
    return re.sub(r"\(\*.*?\*\)", "", code, flags=re.S)


def verify_st(code):
    errors, warnings = [], []

    if code.count("(*") != code.count("*)"):
        errors.append("Unbalanced comment markers (* *)")
    body = _strip_comments(code)

    if len(re.findall(r"^\s*PROGRAM\b", body, flags=re.M)) != 1:
        errors.append("Expected exactly one PROGRAM")
    if "END_PROGRAM" not in body:
        errors.append("Missing END_PROGRAM")
    if len(re.findall(r"\bVAR\b", body)) != len(re.findall(r"\bEND_VAR\b", body)):
        errors.append("VAR and END_VAR do not match")
    if len(re.findall(r"\bIF\b", body)) != len(re.findall(r"\bEND_IF\b", body)):
        errors.append("IF and END_IF do not match")
    if body.count("(") != body.count(")"):
        errors.append("Unbalanced parentheses")

    m = re.search(r"\bVAR\b(.*?)\bEND_VAR\b", body, flags=re.S)
    declared = {}
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line:
                continue
            if not line.endswith(";"):
                errors.append(f"Declaration missing semicolon: {line}")
            dm = re.match(r"([A-Za-z_]\w*)\s*:\s*(\w+)", line)
            if not dm:
                errors.append(f"Cannot parse declaration: {line}")
                continue
            if dm.group(1) in declared:
                errors.append(f"Duplicate variable {dm.group(1)}")
            declared[dm.group(1)] = dm.group(2)
    else:
        errors.append("No VAR block found")

    logic = body.split("END_VAR", 1)[-1].replace("END_PROGRAM", "")
    for stmt in [s.strip() for s in logic.split(";") if s.strip()]:
        for ident in re.findall(r"\b[A-Za-z_]\w*\b", stmt):
            if ident.upper() in KEYWORDS or ident in declared:
                continue
            errors.append(f"Undeclared identifier: {ident}")
    tail = logic.strip()
    if tail and not tail.endswith(";"):
        errors.append("Last statement is missing a semicolon")

    if set(declared) <= {"ESTOP"}:
        warnings.append("No tag-derived variables were generated")

    errors = list(dict.fromkeys(errors))
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "variables": len(declared)}
