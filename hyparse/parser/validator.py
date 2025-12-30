"""Validation utilities for .hy3 file format.

This module provides checksum validation and other format validation
functions for HyTek .hy3 swim meet result files.
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class ChecksumValidator:
    """Validates checksums for .hy3 file lines."""

    @staticmethod
    def calculate_checksum(line: str) -> str:
        """Calculates the checksum for a given line.

        The checksum algorithm:
        1. Remove the last 2 characters (the checksum itself)
        2. Sum odd-positioned characters (0-indexed) * 2
        3. Sum even-positioned characters (0-indexed) * 1
        4. Divide total by 21, add 205
        5. Take last 2 digits (reversed order)

        Args:
            line: The line from the .hy3 file (including the last two checksum characters).

        Returns:
            The calculated two-digit checksum as a string.

        Example:
            >>> validator = ChecksumValidator()
            >>> checksum = validator.calculate_checksum("A102                    44")
            >>> print(checksum)
            '44'
        """
        # Strip the last 2 characters which contain the existing checksum
        content = line[:-2]
        chars = list(content)
        ord_chars = [ord(char) for char in chars]

        # Separate odd and even positioned characters (0-indexed)
        odd = []
        even = []
        for i in range(len(chars)):
            if i % 2:  # Odd index (1, 3, 5, ...)
                odd.append(ord_chars[i])
            else:  # Even index (0, 2, 4, ...)
                even.append(ord_chars[i])

        # Calculate weighted sums
        odd_sum = sum(2 * num for num in odd)
        even_sum = sum(even)

        # Apply checksum formula
        sum_val = odd_sum + even_sum
        result = sum_val // 21
        sum2 = result + 205

        # Extract last 2 digits (in reverse order)
        checksum1 = str(sum2)[-1]  # Last digit
        checksum2 = str(sum2)[-2]  # Second-to-last digit
        checksum = checksum1 + checksum2  # Concatenate in correct order

        return checksum

    @staticmethod
    def validate_line(line: str, line_num: int = None) -> Tuple[bool, str]:
        """Validates a single line's checksum.

        Args:
            line: The line to validate.
            line_num: Optional line number for error reporting.

        Returns:
            Tuple of (is_valid, error_message).
            If valid, error_message is empty string.
        """
        if len(line) < 2:
            return False, f"Line too short (length {len(line)})"

        calculated = ChecksumValidator.calculate_checksum(line)
        actual = line[-2:]

        if calculated != actual:
            line_ref = f"Line {line_num}: " if line_num else ""
            return (
                False,
                f"{line_ref}Checksum mismatch. Expected '{calculated}', got '{actual}'",
            )

        return True, ""

    @staticmethod
    def validate_lines(
        lines: List[str],
    ) -> Tuple[bool, List[Tuple[int, str, str]]]:
        """Validates checksums for all lines.

        Args:
            lines: List of lines from the .hy3 file.

        Returns:
            Tuple of (all_valid, errors) where:
            - all_valid: True if all lines pass validation
            - errors: List of (line_num, line_content, error_message) tuples
        """
        errors = []
        all_valid = True

        for i, line in enumerate(lines):
            is_valid, error_msg = ChecksumValidator.validate_line(line, i + 1)
            if not is_valid:
                errors.append((i + 1, line, error_msg))
                all_valid = False

        if not all_valid:
            logger.warning(
                f"Checksum validation failed for {len(errors)} line(s) out of {len(lines)}"
            )

        return all_valid, errors


def validate_file_structure(lines: List[str]) -> Tuple[bool, List[str]]:
    """Validates the structural requirements of a .hy3 file.

    Checks for:
    - File has at least one line
    - First line is A1 (file header)
    - Has at least one B1 line (meet info)

    Args:
        lines: List of lines from the .hy3 file.

    Returns:
        Tuple of (is_valid, error_messages).
    """
    errors = []

    if not lines:
        errors.append("File is empty")
        return False, errors

    # Check for A1 header
    if len(lines[0]) >= 2 and lines[0][:2] != "A1":
        errors.append("File must start with A1 (file header) line")

    # Check for B1 meet info
    has_b1 = any(len(line) >= 2 and line[:2] == "B1" for line in lines)
    if not has_b1:
        errors.append("File must contain at least one B1 (meet info) line")

    if errors:
        logger.error(f"File structure validation failed: {'; '.join(errors)}")
        return False, errors

    return True, []
