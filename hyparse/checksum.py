"""The 2-digit checksum at the end of every .hy3 line."""


def hy3_checksum(content: str) -> str:
    """Compute the checksum for a line's first 128 characters (everything but the checksum).

    Sum the characters at even indexes plus twice the characters at odd indexes, integer-divide
    by 21, add 205, and return the ones digit followed by the tens digit.
    """
    total = sum(ord(ch) * (2 if i % 2 else 1) for i, ch in enumerate(content))
    value = total // 21 + 205
    return f"{value % 10}{value // 10 % 10}"


def has_valid_checksum(line: str) -> bool:
    return len(line) > 2 and hy3_checksum(line[:-2]) == line[-2:]
