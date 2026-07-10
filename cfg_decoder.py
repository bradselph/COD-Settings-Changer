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

# Which Documents/Activision title folders belong to each game. The hashed config*.cfg
# format is IW-engine only (MWII/MWIII); Treyarch titles (BO6/BO7) don't use it, so they
# map to no folders and find_cfgs returns nothing for them.
CFG_TITLE_DIRS = {
    "MW2 2022": ("Call of Duty MWII",),
    "MW3 2023": ("Call of Duty MWIII", "Call of Duty"),
    "BO6 2024": (),
    "BO7 2025": (),
}

def find_cfgs(game=None):
    """Find config*.cfg dvar files, scoped to a specific game's title folder(s).
    game=None keeps the legacy behavior of scanning every CoD title (used by the CLI)."""
    home = os.path.expanduser("~")
    docs = os.path.join(home, "Documents")
    lad = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
    if game is not None:
        allowed = CFG_TITLE_DIRS.get(game)
        if not allowed:                       # Treyarch / unknown -> not applicable
            return []
    else:
        allowed = None
    bases = []
    for parent in (docs, os.path.join(lad, "Activision")):
        if not os.path.isdir(parent):
            continue
        for d in os.listdir(parent):
            if allowed is not None:
                if d not in allowed:          # exact match: 'Call of Duty MWII' != 'Call of Duty MWIII'
                    continue
            elif not d.startswith("Call of Duty"):
                continue
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
