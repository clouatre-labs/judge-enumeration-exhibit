"""Exact 3x3 linear system solver over rationals.

Gauss-Jordan elimination using fractions.Fraction so all intermediate
values are exact. Returns None when a zero pivot is encountered
(singular system); never raises on singular input.
"""

from fractions import Fraction


def solve3x3(a, b):
    """Solve a 3x3 linear system a @ x = b exactly.

    Args:
        a: 3x3 list of lists of Fraction-compatible numbers.
        b: length-3 list of Fraction-compatible numbers.

    Returns:
        List of three Fraction unknowns, or None if the system is
        singular (zero pivot at any elimination step).
    """
    m = [[Fraction(v) for v in row] for row in a]
    rhs = [Fraction(v) for v in b]

    n = 3
    for col in range(n):
        # Find a pivot row with a nonzero entry in this column.
        pivot_row = None
        for row in range(col, n):
            if m[row][col] != 0:
                pivot_row = row
                break
        if pivot_row is None:
            return None
        if pivot_row != col:
            m[col], m[pivot_row] = m[pivot_row], m[col]
            rhs[col], rhs[pivot_row] = rhs[pivot_row], rhs[col]
        pivot = m[col][col]
        # Eliminate below the pivot.
        for row in range(col + 1, n):
            factor = m[row][col] / pivot
            if factor == 0:
                continue
            for k in range(col, n):
                m[row][k] -= factor * m[col][k]
            rhs[row] -= factor * rhs[col]

    # Back substitution.
    x = [Fraction(0)] * n
    for row in range(n - 1, -1, -1):
        acc = rhs[row]
        for k in range(row + 1, n):
            acc -= m[row][k] * x[k]
        x[row] = acc / m[row][row]
    return x
