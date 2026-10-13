"""Regression tests for the actual binary-symplectic Clifford simulator."""
import pytest

from stabilizer_tableau.tableau import Tableau, parse_circuit, simulate_circuit
from stabilizer_tableau.cli import main


def test_zero_state_and_pauli_flips():
    assert simulate_circuit(2, "")["stabilizers"] == ["+ZI", "+IZ"]
    assert simulate_circuit(2, "X 0")["expectations_z"] == [-1, 1]
    assert simulate_circuit(2, "Y 0")["expectations_z"] == [-1, 1]
    assert simulate_circuit(1, "X 0; M 0; M 0")["measurements"] == [
        {"qubit": 0, "outcome": 1, "random": False},
        {"qubit": 0, "outcome": 1, "random": False},
    ]


def test_bell_pair_and_correlated_collapse():
    bell = simulate_circuit(2, "H 0; CX 0 1")
    assert bell["stabilizers"] == ["+XX", "+ZZ"]
    assert bell["expectations_z"] == [0, 0]
    for seed in (0, 1, 7, 128, 999):
        result = simulate_circuit(2, "H 0; CNOT 0 1; MEASURE 0; M 1", seed)
        a, b = result["measurements"]
        assert a["random"] is True and b["random"] is False
        assert a["outcome"] == b["outcome"]
        assert result["expectations_z"] == [1 - 2 * a["outcome"]] * 2
        assert result == simulate_circuit(2, "H 0; CNOT 0 1; MEASURE 0; M 1", seed)


def test_phase_and_inverse_gates():
    assert simulate_circuit(1, "H 0; S 0")["stabilizers"] == ["+Y"]
    assert simulate_circuit(1, "H 0; S 0; SDG 0")["stabilizers"] == ["+X"]
    assert simulate_circuit(1, "H 0; S 0; M 0")["measurements"][0]["random"] is True
    assert simulate_circuit(2, "H 0; CZ 0 1; H 0")["expectations_z"] == [1, 1]
    assert simulate_circuit(2, "X 0; SWAP 0 1")["expectations_z"] == [1, -1]


def test_measurements_on_y_state_and_repeated_measurement():
    for seed in (0, 1, 3, 17):
        r = simulate_circuit(1, "H 0; S 0; M 0; M 0", seed)
        assert r["measurements"][1]["random"] is False
        assert r["measurements"][0]["outcome"] == r["measurements"][1]["outcome"]


@pytest.mark.parametrize("gate", ["H", "S", "SDG", "X", "Y", "Z"])
def test_single_qubit_unitary_inverses(gate):
    inverse = "SDG" if gate == "S" else "S" if gate == "SDG" else gate
    assert simulate_circuit(1, f"{gate} 0; {inverse} 0")["expectations_z"] == [1]


@pytest.mark.parametrize("text,n", [
    ("T 0", 2), ("H", 2), ("CX 0 0", 2),
    ("H -1", 2), ("S 2", 2), ("H 0.5", 2),
    ("H 0 1", 2), ("H 0", 0), ("H 0", 65),
    ("H 0\n" * 10001, 1),
])
def test_reject_invalid_circuits(text, n):
    with pytest.raises(ValueError):
        simulate_circuit(n, text)


def test_cli_simulation_and_failures(capsys):
    assert main(["simulate", "--qubits", "2", "--gates", "H 0; CX 0 1"]) == 0
    assert '"+XX"' in capsys.readouterr().out
    assert main(["simulate", "--qubits", "2", "--gates", "T 0"]) == 2
    assert "unsupported gate" in capsys.readouterr().err


def test_api_endpoints():
    from agents.api import CircuitRequest, api_simulate
    from stabilizer_tableau.server import create_app
    assert api_simulate(CircuitRequest(qubits=2, circuit="H 0; CX 0 1"))["stabilizers"] == ["+XX", "+ZZ"]
    assert any(route.path == "/api/simulate" for route in create_app().routes)


def test_tableau_z_expectation_is_nondestructive():
    t = Tableau(2, seed=5)
    t.apply("H", 0)
    t.apply("CX", 0, 1)
    before = t.stabilizers()
    for _ in range(5):
        assert [t.expectation_z(q) for q in range(2)] == [0, 0]
    assert t.stabilizers() == before
