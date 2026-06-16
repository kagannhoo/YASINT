"""Kullanıcı adı varyantları üretir — yazım farkları, ayırıcılar."""


def generate_variants(username: str) -> list[str]:
    clean = username.strip().lstrip("@").lower()
    if not clean:
        return []

    variants: set[str] = {clean}

    # Ayırıcı varyantları
    for sep in ("", "_", ".", "-"):
        if sep in clean:
            variants.add(clean.replace(sep, ""))
        else:
            for i in range(1, len(clean)):
                variants.add(clean[:i] + sep + clean[i:])

    # Tekrar eden harf (kagannhoo ↔ kaganhoo)
    for i in range(len(clean) - 1):
        if clean[i] == clean[i + 1]:
            variants.add(clean[:i] + clean[i + 1:])
        else:
            variants.add(clean[: i + 1] + clean[i] + clean[i:])

    # Sayı eki varyantları
    for suffix in ("1", "01", "123", "official", "real"):
        variants.add(clean + suffix)
        if clean.endswith(suffix):
            variants.add(clean[: -len(suffix)])

    # Türkçe isim varyantları (kagan ↔ kağan ascii)
    tr_map = {"ğ": "g", "ü": "u", "ş": "s", "ı": "i", "ö": "o", "ç": "c"}
    ascii_ver = clean
    for tr, en in tr_map.items():
        ascii_ver = ascii_ver.replace(tr, en)
    variants.add(ascii_ver)

    variants.discard("")
    return sorted(variants)[:8]
