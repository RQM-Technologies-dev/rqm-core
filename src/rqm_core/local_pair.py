"""Paired local :math:`SU(2) \times SU(2)` quaternion coordinates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from rqm_core.quaternion import Quaternion


@dataclass(frozen=True)
class QuaternionSU2Pair:
    """Two local unit-quaternion factors in Qiskit little-endian order.

    ``q0`` acts on the lower-index/Qiskit qubit 0 and ``q1`` acts on qubit 1.
    Matrix reconstruction therefore uses ``kron(q1, q0)``.
    """

    q0: Quaternion
    q1: Quaternion

    def __post_init__(self) -> None:
        if not isinstance(self.q0, Quaternion) or not isinstance(self.q1, Quaternion):
            raise TypeError("q0 and q1 must be Quaternion instances")
        if not self.q0.is_unit(atol=1e-12) or not self.q1.is_unit(atol=1e-12):
            raise ValueError("q0 and q1 must be unit quaternions")

    @classmethod
    def identity(cls) -> "QuaternionSU2Pair":
        """Return the paired identity."""
        return cls(Quaternion.identity(), Quaternion.identity())

    @property
    def numeric_payload_bytes(self) -> int:
        """Return the packed float64 payload size, excluding Python overhead."""
        return 8 * 8

    def compose_after(self, earlier: "QuaternionSU2Pair") -> "QuaternionSU2Pair":
        """Return ``self`` applied after ``earlier``.

        Sequential matrix application is ``U_self @ U_earlier``.  Hamilton
        products use the same order componentwise.
        """
        if not isinstance(earlier, QuaternionSU2Pair):
            raise TypeError("earlier must be a QuaternionSU2Pair")
        return QuaternionSU2Pair(
            (self.q0 * earlier.q0).normalize(),
            (self.q1 * earlier.q1).normalize(),
        )

    def inverse(self) -> "QuaternionSU2Pair":
        """Return the componentwise inverse pair."""
        return QuaternionSU2Pair(self.q0.inverse(), self.q1.inverse())

    def canonicalize(self) -> "QuaternionSU2Pair":
        """Return componentwise canonical representatives."""
        return QuaternionSU2Pair(self.q0.canonicalize(), self.q1.canonicalize())

    def to_unitary(self) -> NDArray[np.complex128]:
        """Reconstruct ``kron(q1, q0)`` in computational-basis order."""
        return np.asarray(
            np.kron(self.q1.to_su2_matrix(), self.q0.to_su2_matrix()),
            dtype=np.complex128,
        )

