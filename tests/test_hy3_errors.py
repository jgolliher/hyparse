import pytest

from hyparse import ChecksumError, FileFormatError, read_hy3
from hyparse.checksum import has_valid_checksum, hy3_checksum
from tests.conftest import INVITATIONAL, entry_file


def real_lines():
    return entry_file(INVITATIONAL).read_text(encoding="latin-1").splitlines()


def test_checksum_matches_every_real_line():
    assert all(has_valid_checksum(line) for line in real_lines())


def test_checksum_of_content():
    line = real_lines()[0]
    assert hy3_checksum(line[:-2]) == line[-2:]


def test_bad_checksum_is_an_issue_or_error(write_file):
    lines = real_lines()
    lines[1] = lines[1][:2] + "X" + lines[1][3:]
    path = write_file(lines)
    hy3 = read_hy3(path)
    assert [i.line_number for i in hy3.issues] == [2]
    with pytest.raises(ChecksumError, match="Line 2"):
        read_hy3(path, strict=True)


def test_wrong_line_length_is_reported(write_file):
    lines = real_lines()
    lines[2] = lines[2] + "  "
    assert "expected 130" in read_hy3(write_file(lines)).issues[0].message


def test_orphan_e2_is_reported(write_file):
    lines = [line for line in real_lines() if not line.startswith("E1")]
    lines.insert(5, "E2P                   2  4" + " " * 102 + "00")
    issues = read_hy3(write_file(lines)).issues
    assert any("without a preceding E1" in i.message for i in issues)


def test_not_a_hy3_file(write_file):
    with pytest.raises(FileFormatError, match="A1"):
        read_hy3(write_file(["B1 nope"]))
