"""Linear algebra helpers used throughout rqm_core."""

import numpy as np
from numpy.typing import NDArray


def normalize_vector(v: NDArray[np.floating]) -> NDArray[np.float64]:
    """Return a unit vector in the direction of *v*.

    Args:
        v: Non-zero real-valued array.

    Returns:
        Unit vector with the same direction as *v*.

    Raises:
        ValueError: If *v* is the zero vector.
    """
    n = np.linalg.norm(v)
    if n == 0.0:
        raise ValueError("Cannot normalize a zero vector.")
    return np.asarray(v, dtype=np.float64) / float(n)


def matrix_trace(m: NDArray[np.complexfloating]) -> complex:
    """Return the trace of square matrix *m*.

    Args:
        m: Square matrix.

    Returns:
        Sum of diagonal elements.
    """
    return complex(np.trace(m))


def matrix_determinant(m: NDArray[np.complexfloating]) -> complex:
    """Return the determinant of square matrix *m*.

    Args:
        m: Square matrix.

    Returns:
        Determinant of *m*.
    """
    return complex(np.linalg.det(m))


def is_unitary(m: NDArray[np.complexfloating], *, atol: float = 1e-9) -> bool:
    """Return ``True`` if *m* is a unitary matrix (``m† m ≈ I``).

    Args:
        m: Square complex matrix.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when *m* is unitary within *atol*.
    """
    n = m.shape[0]
    identity = np.eye(n, dtype=np.complex128)
    product = m.conj().T @ m
    return bool(np.allclose(product, identity, atol=atol, rtol=0.0))
