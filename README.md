# Stabilizer Tableau Clifford Sim

Pure-Python binary symplectic stabilizer tableau simulator, with a dependency-free in-browser JavaScript workbench. Legacy telemetry/audit utilities are retained separately and do not implement quantum circuit simulation.

## Features

- Clifford gates: H, S, SDG, X, Y, Z, CX/CNOT, CZ, and SWAP
- Z measurement (M/MEASURE) with state collapse, seeded pseudo-random outcomes, and repeatability
- Final signed Pauli stabilizer generators and single-qubit Z expectation values (−1, 0, +1)
- Newline- or semicolon-separated gate syntax with zero-based qubit indices and # comments
- Limits: Python/API 1–64 qubits, browser 1–24 qubits, at most 10,000 operations

This is **not** a universal quantum simulator: T/non-Clifford gates, general amplitudes, arbitrary initial stabilizer groups, and noise channels are not supported.

## Browser application

The static, responsive workbench is in `stabilizer_tableau/web/`. It calculates locally without any external service, offers examples, error messages, reproducible results, and JSON export. Start a local server from the repository root:

~~~bash
python -m http.server 8000 --directory stabilizer_tableau/web
~~~

Open http://127.0.0.1:8000/. GitHub Pages is configured through `.github/workflows/pages.yml`; the verified live link will be added only once deployment succeeds. Browser-Python/Pyodide is not necessary because the browser simulator uses native JavaScript.

## Python CLI

Python 3.9+; core simulator requires no third-party runtime packages.

~~~bash
python -m pip install -e .
stabilizer-tableau-clifford-sim simulate --qubits 2 --gates "H 0; CX 0 1; M 0; M 1" --seed 7
~~~

Also supported: `python cli.py simulate ...`, or `--circuit-file circuit.txt` to read gate operations from a UTF-8 file.

~~~python
from stabilizer_tableau.tableau import simulate_circuit
result = simulate_circuit(2, "H 0; CX 0 1; M 0; M 1", seed=7)
print(result["measurements"])
print(result["stabilizers"])
~~~

## Optional REST service

~~~bash
python -m pip install -e ".[server]"
python cli.py serve --host 127.0.0.1 --port 8000
~~~

The server hosts the same workbench at `/` and accepts `POST /api/simulate` with JSON such as `{"qubits":2,"circuit":"H 0; CX 0 1","seed":7}`. Invalid circuit specifications return HTTP 422. Both existing API implementations expose this endpoint.

The older `audit`, `batch`, `chat`, and root-CLI `verify-audit` commands remain available. Their threshold-based evaluations, `enrichment.py` modules, and legacy audit endpoints are **not** Clifford simulation.

## Privacy and security

The browser does not upload circuits or results. The local API is unauthenticated; do not publish it to the Internet without independent access controls. Docker Compose binds to `127.0.0.1:8000` by default.

Legacy audit logs use an in-memory HMAC chain. A fresh process-local key is generated unless `AUDIT_SECRET_KEY` is supplied through the environment. The formerly committed Compose key must not be reused: it exists in historical commits. Legacy regex identifier screening is **not** HIPAA-compliant de-identification and should not be relied on for sensitive personal information.

## Tests

~~~bash
python -m pip install -e ".[server,test]"
python -m pytest -q
node --test tests/test_browser.mjs
node --check stabilizer_tableau/web/simulator.mjs
node --check stabilizer_tableau/web/app.mjs
~~~

The CI workflow checks Python 3.10, 3.11, and 3.12, and Node 22. The browser supports modern browsers with JavaScript ES modules, Clipboard API (where permitted), and Blob downloads.

## License

MIT — see [LICENSE](LICENSE).
