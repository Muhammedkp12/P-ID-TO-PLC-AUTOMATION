import re

EQUIPMENT = {"D", "TK", "CT", "C", "E", "R", "RX", "H", "T"}


def _name(tag, used):
    n = re.sub(r"[^A-Za-z0-9]", "_", tag).strip("_").upper()
    if not n or n[0].isdigit():
        n = "T_" + n
    base, k = n, 2
    while n in used:
        n = f"{base}_{k}"
        k += 1
    used.add(n)
    return n


def _kind(tag):
    m = re.match(r"[A-Z]+", tag.upper())
    p = m.group(0) if m else ""
    if p in EQUIPMENT:
        return "equipment"
    if p == "P":
        return "pump"
    if p.endswith("CV"):
        return "control_valve"
    if len(p) >= 2 and p[-1] in "TE":
        return "analog_in"
    if len(p) >= 2 and p[-1] == "C":
        return "controller"
    if p == "V" or (len(p) >= 2 and p[-1] == "V"):
        return "valve"
    return "other"


def generate_st(detections):
    used, decl, logic, warns = set(), [], [], []
    for i, d in enumerate(detections, 1):
        tag = d.get("tag")
        if not tag:
            warns.append(f"Symbol {i} ({d.get('class')}) has no tag, skipped")
            continue
        n, k = _name(tag, used), _kind(tag)
        if k == "analog_in":
            decl += [f"    {n} : REAL;  (* {tag} analog input *)",
                     f"    {n}_HI : REAL := 80.0;  (* placeholder limit *)",
                     f"    {n}_ALM : BOOL;"]
            logic.append(f"{n}_ALM := {n} > {n}_HI;")
        elif k == "controller":
            decl += [f"    {n}_SP : REAL;", f"    {n}_OUT : REAL;",
                     f"    {n}_AUTO : BOOL;"]
            logic.append(f"(* {tag}: connect PID block, PV and SP to OUT *)")
            logic.append(f"IF NOT {n}_AUTO THEN {n}_OUT := 0.0; END_IF;")
        elif k == "control_valve":
            decl.append(f"    {n}_POS : REAL;  (* {tag} position 0 to 100 *)")
            logic.append(f"{n}_POS := LIMIT(0.0, {n}_POS, 100.0);")
        elif k in ("valve", "pump"):
            decl += [f"    {n}_REQ : BOOL;", f"    {n}_CMD : BOOL;"]
            logic.append(f"{n}_CMD := {n}_REQ AND NOT ESTOP;")
        else:
            logic.append(f"(* {tag}: no I/O generated *)")
    code = ("PROGRAM PID_Auto\nVAR\n    ESTOP : BOOL;\n" + "\n".join(decl) +
            "\nEND_VAR\n\n" + "\n".join(logic) + "\nEND_PROGRAM")
    warns.append("Alarm limits are placeholders. Set them from the data sheet.")
    warns.append("Review by a control engineer is required before use.")
    return code, warns