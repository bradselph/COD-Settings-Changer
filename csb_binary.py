"""Binary controller/advanced settings support for the CoD editor.

Reads the MWII 'settings.*.csb' Connected-Storage blob, which holds the controller/
deadzone/aim-assist/movement/interaction settings that are NOT in the plaintext config.

File format (reverse-engineered, 28/28 findings verified):
- 16-byte static header, then value records [float32 LE][0x00][uint32 hash],
  a length-prefixed enum pool [uint32 hash][len][ascii][NUL], and a trailing
  CRC32(file[:-4]) little-endian.  => writes are CRC-safe (see write_float).

The dvar hash is a custom, non-invertible IW-engine FNV variant, so only settings we
have positively identified carry friendly names; the rest are labelled by their raw id.
"""
import os, re, struct, zlib, shutil, datetime

CRC_RESIDUE = 0x2144DF1C  # zlib.crc32(whole self-sealing file)

# hash -> friendly in-game name (identified settings; extend as more are named)
FLOAT_NAMES = {
    0xa4108446: "Mouse Horizontal Sensitivity",
    0xe94d915e: "Look Horizontal Sensitivity (gamepad)",
    0x211c4e99: "Look Vertical Sensitivity (gamepad)",
    0x83680ae9: "Left Stick Min Input (deadzone)",
    0x93d9f49c: "Left Stick Max Input (deadzone)",
    0xf4c4d5b7: "Right Stick Min Input (deadzone)",
    0x8eaf5b13: "Right Stick Max Input (deadzone)",
    0x06e0ad2f: "Aim Response / Aim-Assist strength",
}
ENUM_NAMES = {
    0x30b3622f: "Automatic Sprint behavior",
    0x8e0d45ec: "Interact / Reload behavior",
}

def crc_valid(data: bytes) -> bool:
    return (zlib.crc32(data) & 0xFFFFFFFF) == CRC_RESIDUE

def _float_val(data, h):
    i = data.find(struct.pack("<I", h))
    if i >= 5 and data[i - 1] == 0:
        return i - 5, round(struct.unpack("<f", data[i - 5:i - 1])[0], 4)
    return None, None

def _enum_val(data, h):
    i = data.find(struct.pack("<I", h))
    if i >= 0:
        ln = data[i + 4]
        return i + 5, data[i + 5:i + 5 + ln].split(b"\0")[0].decode("latin1")
    return None, None

def decode(path):
    """Return (rows, crc_ok). rows: {name, hash, value, kind, offset}."""
    data = open(path, "rb").read()
    rows = []
    for h, name in FLOAT_NAMES.items():
        off, v = _float_val(data, h)
        if off is not None:
            rows.append({"name": name, "hash": h, "value": v, "kind": "float", "offset": off})
    for h, name in ENUM_NAMES.items():
        off, v = _enum_val(data, h)
        if off is not None:
            rows.append({"name": name, "hash": h, "value": v, "kind": "enum", "offset": off})
    return rows, crc_valid(data)

def float_range(name):
    """(min, max, decimals, step) input guard for a float setting, by friendly name.
    These are UI guardrails to prevent fat-finger corruption; the field itself is a raw
    float32. Ranges reflect the in-game menus for the identified settings."""
    n = (name or "").lower()
    if "deadzone" in n or "min input" in n or "max input" in n:
        return 0.0, 1.0, 3, 0.01           # stick deadzones are a 0..1 fraction
    if "sensitivity" in n:
        return 0.0, 100.0, 2, 0.5          # mouse/gamepad sens (verified 8.0)
    if "aim" in n:
        return 0.0, 20.0, 3, 0.1           # aim response / aim-assist strength
    return 0.0, 1000.0, 4, 0.1             # unknown float: wide but bounded

def write_floats(path, changes):
    """CRC-safe batch write of float settings. `changes` maps hash -> new value.
    Applies every change, re-seals the CRC once, writes, then re-opens to verify the
    CRC is valid. Returns [(hash, old, new), ...]. Raises on unknown hash or bad seal."""
    data = bytearray(open(path, "rb").read())
    applied = []
    for h, new_val in changes.items():
        off, old = _float_val(data, h)
        if off is None:
            raise KeyError(f"hash {h:#010x} not in {path}")
        data[off:off + 4] = struct.pack("<f", float(new_val))
        applied.append((h, old, round(float(new_val), 4)))
    data[-4:] = struct.pack("<I", zlib.crc32(bytes(data[:-4])) & 0xFFFFFFFF)
    if not crc_valid(bytes(data)):
        raise ValueError("CRC re-seal failed; file not written")
    open(path, "wb").write(bytes(data))
    if not crc_valid(open(path, "rb").read()):
        raise ValueError("post-write CRC verification failed")
    return applied

def write_float(path, h, new_val):
    """CRC-safe write of a single float setting by hash. Returns (old, new)."""
    _, old, new = write_floats(path, {h: new_val})[0]
    return old, new

def backup(path):
    """Copy `path` to a timestamped .bak beside it (metadata preserved). Returns the
    backup path. Called before any binary write so a change is trivially reversible."""
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = f"{path}.{stamp}.bak"
    shutil.copy2(path, dst)
    return dst

def list_backups(path):
    """Backups previously made for `path`, newest first."""
    d = os.path.dirname(path) or "."
    base = os.path.basename(path)
    outs = [os.path.join(d, f) for f in os.listdir(d)
            if f.startswith(base + ".") and f.endswith(".bak")]
    return sorted(outs, reverse=True)

def restore(path, backup_path):
    """Restore `path` from a chosen backup. Verifies the backup's CRC first so we never
    write a corrupt file back over the live save. Returns True on success."""
    data = open(backup_path, "rb").read()
    if not crc_valid(data):
        raise ValueError("backup is not a valid .csb (CRC check failed)")
    shutil.copy2(backup_path, path)
    return True

def find_csb():
    """Locate the real MWII settings.3.pc.cod22.csb in Connected Storage, or None."""
    lad = os.environ.get("LOCALAPPDATA", "")
    pkgs = os.path.join(lad, "Packages")
    if not os.path.isdir(pkgs):
        return None
    for d in os.listdir(pkgs):
        if not d.startswith("38985CA0."):
            continue
        for store in ("wgs", "xgs"):
            root = os.path.join(pkgs, d, "SystemAppData", store)
            if not os.path.isdir(root):
                continue
            for base, _dirs, files in os.walk(root):
                if base.endswith("settings.3.pc.cod22.csb") and "save" in files:
                    return os.path.join(base, "save")
    return None

# ---------------------------------------------------------------------------
# BO7 / cod25 (Treyarch) profile binary: same length-prefixed enum pool as the
# MWII .csb, but a different container (no trailing CRC self-seal). Read-only.
# ---------------------------------------------------------------------------
def find_bo7_profile():
    """Locate BO7's g.p.cod25.1.0.b0 profile binary in Connected Storage, or None."""
    lad = os.environ.get("LOCALAPPDATA", "")
    pkgs = os.path.join(lad, "Packages")
    if not os.path.isdir(pkgs):
        return None
    for d in os.listdir(pkgs):
        if not d.startswith("38985CA0.COREBase"):
            continue
        for store in ("wgs", "xgs"):
            root = os.path.join(pkgs, d, "SystemAppData", store)
            if not os.path.isdir(root):
                continue
            for base, _dirs, files in os.walk(root):
                if base.endswith("g.p.cod25.1.0.b0") and "save" in files:
                    return os.path.join(base, "save")
    return None

def decode_bo7_enums(path):
    """Extract the length-prefixed enum control/movement/interaction values from BO7's
    profile binary. Values are self-descriptive; hash->name mapping is not yet available."""
    data = open(path, "rb").read()
    vals = []
    for m in re.finditer(rb"[a-z][a-z0-9_]{2,}", data):
        o = m.start(); s = m.group().decode("latin1")
        if o >= 1 and data[o - 1] in (len(s), len(s) + 1):
            vals.append((o, s))
    return vals


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else find_csb()
    print("file:", p)
    if p:
        rows, ok = decode(p)
        print(f"CRC valid: {ok}")
        for r in rows:
            print(f"  {r['name']:42s} {r['value']}")
