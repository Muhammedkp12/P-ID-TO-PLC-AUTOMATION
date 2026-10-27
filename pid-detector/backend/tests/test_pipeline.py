import json
from pathlib import Path

from app.services import audit_service as a
from app.services.codegen_service import generate_st
from app.services.ocr_service import normalize_tag
from app.services.verify_service import verify_st


def test_normalize():
    assert normalize_tag("FIC-1O1") == "FIC-101"
    assert normalize_tag("PT2O3") == "PT203"
    assert normalize_tag("LT") == "LT"
    assert normalize_tag("PSV") == "PSV"
    assert normalize_tag("D-1O8") == "D-108"


def test_codegen_verify():
    dets = [{"class": "x", "tag": t} for t in
            ["FIC-101", "PT-203", "TIC-9", "FCV-101", "V-2", "P-14", "D-108", "LT"]]
    dets.append({"class": "y"})
    code, w = generate_st(dets)
    r = verify_st(code)
    assert r["ok"], r["errors"]


def test_verify_catches_errors():
    bad = "PROGRAM X\nVAR\n A : BOOL;\nEND_VAR\nA := B;\nIF A THEN A := TRUE;\nEND_PROGRAM"
    r = verify_st(bad)
    assert not r["ok"]


def test_chain(tmp_path):
    p = tmp_path / "log.jsonl"
    for i in range(3):
        a.append_record("kaizz", "generate_plc", a.sha256_text(str(i)),
                        ["PT-1"], a.sha256_text("code"), path=p)
    assert a.verify_chain(p)["valid"]
    lines = p.read_text().splitlines()
    rec = json.loads(lines[1]); rec["tags"] = ["HACKED"]
    lines[1] = json.dumps(rec, sort_keys=True)
    p.write_text("\n".join(lines) + "\n")
    r = a.verify_chain(p)
    assert not r["valid"] and r["broken_at"] == 1
    # deleting a record is also caught
    lines = lines[:1] + lines[2:]
    p.write_text("\n".join(lines) + "\n")
    assert not a.verify_chain(p)["valid"]
