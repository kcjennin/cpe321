from cryptography.hazmat.primitives import hashes


def string_SHA256(b: bytes):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(b) 
    return digest.finalize().hex()


def short_hash(b: bytes, n: int):
    if not (8 <= n <= 50):
        raise ValueError(f"Invalid hash length {n}, must be in [8, 50]")

    digest = hashes.Hash(hashes.SHA256())
    digest.update(b)
    hashed = digest.finalize()
    return int(bin(int.from_bytes(hashed, "little"))[2:2+n])