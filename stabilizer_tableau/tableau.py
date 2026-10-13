"""Binary symplectic Clifford tableau simulator.

Tableau rows represent (-1)^r i^(x.z) X^x Z^z, with destabilizers
followed by stabilizers. Implements Aaronson–Gottesman gate/measurement rules.
"""
from __future__ import annotations

from typing import Any

GATES = {"H": 1, "S": 1, "SDG": 1, "X": 1, "Y": 1, "Z": 1,
         "CX": 2, "CZ": 2, "SWAP": 2, "M": 1}
ALIASES = {"CNOT": "CX", "MEASURE": "M", "S_DAG": "SDG"}
MAX_QUBITS = 64
MAX_OPERATIONS = 10000


def parse_circuit(text: str, qubits: int) -> list[tuple]:
    """Parse newline- or semicolon-delimited gates, using zero-based indices."""
    if type(qubits) is not int or not 1 <= qubits <= MAX_QUBITS:
        raise ValueError(f"qubits must be an integer between 1 and {MAX_QUBITS}")
    if not isinstance(text, str):
        raise ValueError("circuit must be a string")
    if len(text) > 200_000:
        raise ValueError("circuit input is too large")
    operations = []
    for line_no, raw in enumerate(text.replace(";", "\n").splitlines(), 1):
        words = raw.split("#", 1)[0].replace(",", " ").split()
        if not words:
            continue
        gate = ALIASES.get(words[0].upper(), words[0].upper())
        count = GATES.get(gate)
        if count is None:
            raise ValueError(f"line {line_no}: unsupported gate {words[0]!r}")
        if len(words) != count + 1:
            raise ValueError(f"line {line_no}: {gate} requires {count} qubit index/indices")
        try:
            indices = [int(word) for word in words[1:]]
        except ValueError as exc:
            raise ValueError(f"line {line_no}: qubit indices must be integers") from exc
        if any(i < 0 or i >= qubits for i in indices) or len(indices) != len(set(indices)):
            raise ValueError(f"line {line_no}: qubit indices must be distinct and in [0, {qubits - 1}]")
        operations.append((gate, *indices))
        if len(operations) > MAX_OPERATIONS:
            raise ValueError(f"circuit exceeds {MAX_OPERATIONS} operations")
    return operations


class Tableau:
    """Pure-state Clifford simulator with computational-basis Z measurements."""

    def __init__(self, qubits: int, seed: int = 0):
        if type(qubits) is not int or not 1 <= qubits <= MAX_QUBITS:
            raise ValueError(f"qubits must be an integer between 1 and {MAX_QUBITS}")
        if type(seed) is not int or not -(2**31) <= seed < 2**32:
            raise ValueError("seed must be a 32-bit integer")
        self.n = qubits
        self.x = [1 << i for i in range(qubits)] + [0] * qubits
        self.z = [0] * qubits + [1 << i for i in range(qubits)]
        self.r = [0] * (2 * qubits)
        self.seed = seed & 0xFFFFFFFF

    def _sum(self, dest: int, src: int) -> None:
        """Multiply commuting Hermitian Pauli rows: dest := dest * src."""
        phase = 2 * (self.r[dest] + self.r[src])
        for q in range(self.n):
            mask = 1 << q
            a, b = bool(self.x[dest] & mask), bool(self.z[dest] & mask)
            c, d = bool(self.x[src] & mask), bool(self.z[src] & mask)
            if a and b:
                phase += int(d) - int(c)
            elif a:
                phase += int(d) * (2 * int(c) - 1)
            elif b:
                phase += int(c) * (1 - 2 * int(d))
        if phase % 2:
            raise ValueError("attempted to multiply anticommuting tableau rows")
        self.r[dest] = (phase // 2) % 2
        self.x[dest] ^= self.x[src]
        self.z[dest] ^= self.z[src]

    def _randbit(self) -> int:
        self.seed = (1664525 * self.seed + 1013904223) & 0xFFFFFFFF
        return self.seed >> 31

    def apply(self, gate: str, *qs: int) -> None:
        mask = 1 << qs[0]
        if gate == "H":
            for i in range(2 * self.n):
                a, b = bool(self.x[i] & mask), bool(self.z[i] & mask)
                self.r[i] ^= int(a and b)
                if a != b:
                    self.x[i] ^= mask
                    self.z[i] ^= mask
        elif gate in ("S", "SDG"):
            for _ in range(1 if gate == "S" else 3):
                for i in range(2 * self.n):
                    a, b = bool(self.x[i] & mask), bool(self.z[i] & mask)
                    self.r[i] ^= int(a and b)
                    if a:
                        self.z[i] ^= mask
        elif gate in ("X", "Y", "Z"):
            for i in range(2 * self.n):
                a, b = bool(self.x[i] & mask), bool(self.z[i] & mask)
                self.r[i] ^= {"X": int(b), "Y": int(a != b), "Z": int(a)}[gate]
        elif gate == "CX":
            control, target = (1 << q for q in qs)
            for i in range(2 * self.n):
                xa = bool(self.x[i] & control)
                xb = bool(self.x[i] & target)
                za = bool(self.z[i] & control)
                zb = bool(self.z[i] & target)
                self.r[i] ^= int(xa and zb and (xb == za))
                if xa:
                    self.x[i] ^= target
                if zb:
                    self.z[i] ^= control
        elif gate == "CZ":
            self.apply("H", qs[1])
            self.apply("CX", *qs)
            self.apply("H", qs[1])
        elif gate == "SWAP":
            self.apply("CX", *qs)
            self.apply("CX", qs[1], qs[0])
            self.apply("CX", *qs)
        else:
            raise ValueError(f"unsupported unitary gate {gate!r}")

    def expectation_z(self, q: int) -> int:
        """Return -1, 0, or +1 for the expectation of Z_q."""
        mask = 1 << q
        if any(self.x[i] & mask for i in range(self.n, 2 * self.n)):
            return 0
        self.x.append(0)
        self.z.append(0)
        self.r.append(0)
        scratch = 2 * self.n
        try:
            for i in range(self.n):
                if self.x[i] & mask:
                    self._sum(scratch, i + self.n)
            return -1 if self.r[scratch] else 1
        finally:
            self.x.pop()
            self.z.pop()
            self.r.pop()

    def measure(self, q: int) -> tuple[int, bool]:
        """Return (bit, probabilistic), collapsing the stabilizer state."""
        mask = 1 << q
        pivot = next((i for i in range(self.n, 2 * self.n) if self.x[i] & mask), None)
        if pivot is None:
            return int(self.expectation_z(q) == -1), False
        for i in range(2 * self.n):
            if i != pivot and i != pivot - self.n and self.x[i] & mask:
                self._sum(i, pivot)
        self.x[pivot - self.n], self.z[pivot - self.n], self.r[pivot - self.n] = (
            self.x[pivot], self.z[pivot], self.r[pivot]
        )
        outcome = self._randbit()
        self.x[pivot], self.z[pivot], self.r[pivot] = 0, mask, outcome
        return outcome, True

    def stabilizers(self) -> list[str]:
        symbols = "IXZY"  # x + 2*z: I, X, Z, Y
        return [
            ("-" if self.r[i] else "+") + "".join(
                symbols[(1 if self.x[i] & (1 << q) else 0) + (2 if self.z[i] & (1 << q) else 0)]
                for q in range(self.n)
            )
            for i in range(self.n, 2 * self.n)
        ]


def simulate_circuit(qubits: int, circuit: str, seed: int = 0) -> dict[str, Any]:
    """Execute a Clifford circuit and return Z measurements and final stabilizers."""
    ops = parse_circuit(circuit, qubits)
    state = Tableau(qubits, seed)
    measurements = []
    for gate, *indices in ops:
        if gate == "M":
            bit, random = state.measure(indices[0])
            measurements.append({"qubit": indices[0], "outcome": bit, "random": random})
        else:
            state.apply(gate, *indices)
    return {"qubits": qubits, "operations": len(ops), "measurements": measurements,
            "expectations_z": [state.expectation_z(q) for q in range(qubits)],
            "stabilizers": state.stabilizers()}
