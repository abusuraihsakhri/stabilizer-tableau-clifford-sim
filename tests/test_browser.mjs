import test from 'node:test';
import assert from 'node:assert/strict';
import {simulateCircuit, parseCircuit, Tableau} from '../web/simulator.mjs';

test('initial zero state and X flip', () => {
  assert.deepEqual(simulateCircuit(2,'' ).stabilizers,['+ZI','+IZ']);
  assert.deepEqual(simulateCircuit(2,'X 0').expectations_z,[-1,1]);
});

test('Bell pair generators and correlated measurements', () => {
  const bell=simulateCircuit(2,'H 0; CX 0 1');
  assert.deepEqual(bell.stabilizers,['+XX','+ZZ']);
  assert.deepEqual(bell.expectations_z,[0,0]);
  for (const seed of [0,1,7,123,999]) {
    const a=simulateCircuit(2,'H 0; CNOT 0 1; M 0; M 1',seed);
    assert.equal(a.measurements[0].random,true);
    assert.equal(a.measurements[1].random,false);
    assert.equal(a.measurements[0].outcome,a.measurements[1].outcome);
    assert.deepEqual(a,simulateCircuit(2,'H 0; CNOT 0 1; M 0; M 1',seed));
  }
});

test('S, S-dagger and Y Pauli signs', () => {
  assert.deepEqual(simulateCircuit(1,'H 0; S 0').stabilizers,['+Y']);
  assert.deepEqual(simulateCircuit(1,'H 0; S 0; SDG 0').stabilizers,['+X']);
  assert.deepEqual(simulateCircuit(1,'Y 0').expectations_z,[-1]);
});

test('swap and collapse on Y state', () => {
  assert.deepEqual(simulateCircuit(2,'X 0; SWAP 0 1').expectations_z,[1,-1]);
  for (const seed of [0,7,255]) {
    const m=simulateCircuit(1,'H 0; S 0; M 0; M 0',seed).measurements;
    assert.equal(m[0].outcome,m[1].outcome);
    assert.equal(m[1].random,false);
  }
});

test('reject malformed and out-of-range input', () => {
  for (const [text,n] of [['T 0',1],['H 2',2],['CX 0 0',2],['H 0.3',2],['CX 0',2],['H 0',0],['H 0',25]]) {
    assert.throws(()=>parseCircuit(text,n));
  }
});

test('expectations do not collapse the tableau', () => {
  const t=new Tableau(2);
  t.apply('H',0);t.apply('CX',0,1);
  const prev=t.stabilizers();
  assert.equal(t.expectationZ(0),0);
  assert.equal(t.expectationZ(1),0);
  assert.deepEqual(t.stabilizers(),prev);
});
