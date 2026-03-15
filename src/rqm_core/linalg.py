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


def vector_norm(vec: NDArray[np.floating]) -> float:
    """Return the Euclidean norm of *vec*.

    Args:
        vec: Real or complex-valued array.

    Returns:
        Non-negative Euclidean norm.
    """
    return float(np.linalg.norm(vec))


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


def matrix_dagger(m: NDArray[np.complexfloating]) -> NDArray[np.complex128]:
    """Return the conjugate transpose (Hermitian adjoint) of *m*.

    Args:
        m: Complex matrix.

    Returns:
        ``m†`` – complex conjugate of the transpose.
    """
    return np.asarray(m, dtype=np.complex128).conj().T


def matrix_close(
    a: NDArray[np.complexfloating],
    b: NDArray[np.complexfloating],
    *,
    atol: float = 1e-9,
) -> bool:
    """Return ``True`` if matrices *a* and *b* are element-wise close.

    Args:
        a: First matrix.
        b: Second matrix.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when every element satisfies ``|a_ij - b_ij| ≤ atol``.
    """
    return bool(np.allclose(a, b, atol=atol, rtol=0.0))


def complex_close(a: complex, b: complex, *, atol: float = 1e-9) -> bool:
    """Return ``True`` if *a* and *b* are numerically close.

    Args:
        a: First complex number.
        b: Second complex number.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when ``|a - b| ≤ atol``.
    """
    return abs(a - b) <= atol


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

