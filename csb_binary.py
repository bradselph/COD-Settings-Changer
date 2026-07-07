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
import os, struct, zlib

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

def write_float(path, h, new_val):
    """CRC-safe write of a float setting by hash. Returns (old, new)."""
    data = bytearray(open(path, "rb").read())
    off, old = _float_val(data, h)
    if off is None:
        raise KeyError(f"hash {h:#010x} not in {path}")
    data[off:off + 4] = struct.pack("<f", float(new_val))
    data[-4:] = struct.pack("<I", zlib.crc32(bytes(data[:-4])) & 0xFFFFFFFF)
    open(path, "wb").write(bytes(data))
    return old, float(new_val)

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

if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else find_csb()
    print("file:", p)
    if p:
        rows, ok = decode(p)
        print(f"CRC valid: {ok}")
        for r in rows:
            print(f"  {r['name']:42s} {r['value']}")
