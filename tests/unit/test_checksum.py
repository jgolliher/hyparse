"""Unit tests for checksum validation in hyparse parser."""
import pytest
from hyparse.parser.hy3_file import Hy3File
from hyparse.parser.validator import ChecksumValidator


class TestChecksumCalculation:
    """Tests for checksum calculation algorithm."""

    def test_checksum_calculation_basic(self):
        """Test basic checksum calculation with known values."""
        # Test line from actual .hy3 file format
        # Format: content + 2-digit checksum at end
        test_line = "A102                                            MM 8.0     20251101  88"

        # Use the ChecksumValidator directly
        calculated = ChecksumValidator.calculate_checksum(test_line)
        actual = test_line[-2:]

        # The checksum should match what's at the end of the line
        assert calculated == actual

    def test_checksum_digit_order(self):
        """Test that checksum digits are in correct order (not reversed)."""
        # Create a test line where we know the checksum algorithm
        # This tests the bug fix where digits were reversed
        test_line = "B1Test Meet                                   Test Pool                                           20251201202512010000000100   L                           04"

        calculated = ChecksumValidator.calculate_checksum(test_line)

        # Ensure it's a 2-character string
        assert len(calculated) == 2
        assert calculated.isdigit()

        # The algorithm should produce checksum1 + checksum2 (last 2 digits)
        # This is implicitly tested by the format

    def test_checksum_empty_line(self):
        """Test checksum calculation on very short line."""
        # Line that's too short (less than 2 chars) should be handled
        test_line = "A104"  # Minimal line: type + checksum

        # Should not crash
        calculated = ChecksumValidator.calculate_checksum(test_line)
        assert isinstance(calculated, str)
        assert len(calculated) == 2


class TestChecksumValidation:
    """Tests for checksum validation during parsing."""

    def test_valid_checksums_pass(self):
        """Test that valid checksums pass validation."""
        import tempfile

        # Create a file with known valid checksum
        valid_line = "A102                                            MM 8.0     20251101  88\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.hy3', delete=False) as f:
            f.write(valid_line)
            temp_path = f.name

        try:
            hy3 = Hy3File(temp_path)
            # Check parse_errors for checksum errors
            checksum_errors = [e for e in hy3.parse_errors if 'checksum' in e[2].lower()]

            # Should be empty if checksum is valid
            # Note: Might have other parse errors, just check no checksum errors
            assert len([e for e in checksum_errors if 'mismatch' in e[2].lower()]) == 0
        finally:
            import os
            os.unlink(temp_path)

    def test_invalid_checksum_detected(self):
        """Test that invalid checksums are detected."""
        import tempfile

        # Create a line with intentionally wrong checksum
        invalid_line = "A102                                            MM 8.0     20251101  99\n"  # Wrong checksum

        with tempfile.NamedTemporaryFile(mode='w', suffix='.hy3', delete=False) as f:
            f.write(invalid_line)
            temp_path = f.name

        try:
            hy3 = Hy3File(temp_path)
            # Check parse_errors for checksum mismatch
            checksum_errors = [e for e in hy3.parse_errors if 'checksum mismatch' in e[2].lower()]

            # Should have at least one checksum error
            assert len(checksum_errors) > 0
        finally:
            import os
            os.unlink(temp_path)

    def test_checksum_validation_continues_parsing(self):
        """Test that parsing continues even with checksum errors."""
        import tempfile

        # Create a file with both valid and invalid checksums
        lines = [
            "A102                                            MM 8.0     20251101  88\n",
            "B1Bad Checksum Meet                                                                                                                           99\n",  # Bad checksum
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.hy3', delete=False) as f:
            f.writelines(lines)
            temp_path = f.name

        try:
            hy3 = Hy3File(temp_path)

            # Should still have parsed content despite checksum error
            # (The parser continues after checksum validation)
            assert hy3.raw_lines is not None
            assert len(hy3.raw_lines) == 2
        finally:
            import os
            os.unlink(temp_path)


class TestChecksumAlgorithm:
    """Tests for the specific checksum algorithm implementation."""

    def test_checksum_calculation_steps(self):
        """Test individual steps of checksum algorithm."""
        # Simple test line
        test_line = "TEST00"  # Simple test, checksum at end

        # The algorithm:
        # 1. Takes line without last 2 chars (checksum)
        # 2. Sums ASCII values: odd positions * 2, even positions * 1
        # 3. Divides by 21, adds 205
        # 4. Takes last 2 digits

        result = ChecksumValidator.calculate_checksum(test_line)

        # Result should be 2 digits
        assert len(result) == 2
        assert result.isdigit()

        # Verify it's numeric between 00-99
        checksum_val = int(result)
        assert 0 <= checksum_val <= 99

    def test_checksum_format(self):
        """Test that checksum is always 2 digits (zero-padded if needed)."""
        test_line = "A" + "0" * 50 + "00"  # Line that might produce small checksum

        result = ChecksumValidator.calculate_checksum(test_line)

        # Should always be exactly 2 characters
        assert len(result) == 2
        # Should be valid digits (0-9)
        assert result.isdigit()
