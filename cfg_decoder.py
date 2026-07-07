"""Decode CoD hashed dvar config files (config*.cfg) for the editor.

Two hashed formats exist; only the values are plaintext, the dvar names are hashed:
  * IW9  (MWII 2022):  seta #x<hex>  "value"   -- names ARE recoverable: the hash is the
                        64-bit FNV-1a dvar hash; we look it up in dvar_hashes.txt.
  * IW8  (MW 2019):    setcl <dec>   "value"   -- 32-bit ids, NOT in our dump, so these
                        stay id-only (values still readable).

Requires dvar_hashes.txt (0x<hash>u64 => "name") in the same folder for name lookup.
"""
import os, re

_DUMP = None

def _load_dump():
    global _DUMP
    if _DUMP is None:
        _DUMP = {}
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dvar_hashes.txt")
        if os.path.exists(p):
            for line in open(p, encoding="latin1"):
                m = re.search(r"0x([0-9A-Fa-f]+)u64\s*=>\s*\"([^\"]+)\"", line)
                if m:
                    _DUMP[int(m.group(1), 16) & 0xFFFFFFFFFFFFFFFF] = m.group(2)
    return _DUMP

def decode_cfg(path):
    """Return (rows, stats). rows: {key, value, named, fmt}."""
    dump = _load_dump()
    text = open(path, encoding="latin1").read()
    rows = []
    named = 0
    for h, v in re.findall(r'seta\s+#x([0-9a-fA-F]+)\s+"([^"]*)"', text):     # IW9
        nm = dump.get(int(h, 16) & 0xFFFFFFFFFFFFFFFF)
        rows.append({"key": nm or ("#x" + h), "value": v, "named": bool(nm), "fmt": "seta"})
        if nm:
            named += 1
    for i, v in re.findall(r'setcl\s+(\d+)\s+"([^"]*)"', text):               # IW8
        rows.append({"key": "id:" + i, "value": v, "named": False, "fmt": "setcl"})
    rows.sort(key=lambda r: (not r["named"], r["key"].lower()))
    return rows, {"total": len(rows), "named": named}

def find_cfgs():
    """Find config*.cfg dvar files across all CoD titles (scoped to player folders)."""
    home = os.path.expanduser("~")
    docs = os.path.join(home, "Documents")
    lad = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
    bases = []
    for parent, prefix in ((docs, "Call of Duty"), (os.path.join(lad, "Activision"), "Call of Duty")):
        if os.path.isdir(parent):
            for d in os.listdir(parent):
                if d.startswith(prefix):
                    bases.append(os.path.join(parent, d, "players"))
    found = []
    for players in bases:
        if not os.path.isdir(players):
            continue
        for base, _dirs, files in os.walk(players):
            for f in files:
                if f.lower().endswith(".cfg") and f.lower().startswith("config"):
                    found.append(os.path.join(base, f))
    return found

if __name__ == "__main__":
    import sys
    paths = sys.argv[1:] or find_cfgs()
    for p in paths:
        rows, st = decode_cfg(p)
        print(f"\n=== {os.path.basename(p)}  ({st['named']}/{st['total']} named) ===")
        for r in rows[:18]:
            print(f"  {r['key']:36s} = {r['value']}")
