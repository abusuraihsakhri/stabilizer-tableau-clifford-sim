// Pure browser-side binary symplectic tableau, no network or dependencies.
const arity = {H:1,S:1,SDG:1,X:1,Y:1,Z:1,CX:2,CZ:2,SWAP:2,M:1};
const aliases = {CNOT:'CX',MEASURE:'M',S_DAG:'SDG'};
export const MAX_QUBITS = 24;

export function parseCircuit(text, n) {
  if (!Number.isInteger(n) || n < 1 || n > MAX_QUBITS) {
    throw Error('Qubits must be an integer between 1 and ' + MAX_QUBITS);
  }
  if (typeof text !== 'string' || text.length > 200000) throw Error('Invalid or oversized circuit text');
  const ops = [];
  text.replaceAll(';', '\n').split('\n').forEach((raw, idx) => {
    const words = raw.split('#',1)[0].replaceAll(',', ' ').trim().split(/\s+/).filter(Boolean);
    if (!words.length) return;
    const name = words[0].toUpperCase();
    const gate = aliases[name] || name;
    if (!(gate in arity)) throw Error('Line ' + (idx+1) + ': unknown gate ' + words[0]);
    if (words.length !== arity[gate] + 1) throw Error('Line ' + (idx+1) + ': wrong number of qubits for ' + gate);
    const qs = words.slice(1).map(w => {
      if (!/^[+-]?\d+$/.test(w)) throw Error('Line ' + (idx+1) + ': qubit indices must be integers');
      return Number(w);
    });
    if (qs.some(q => !Number.isInteger(q) || q < 0 || q >= n) || new Set(qs).size !== qs.length) {
      throw Error('Line ' + (idx+1) + ': indices must be distinct and within 0..' + (n-1));
    }
    ops.push([gate, ...qs]);
    if (ops.length > 10000) throw Error('Circuit exceeds 10000 operations');
  });
  return ops;
}

export class Tableau {
  constructor(n, seed=0) {
    if (!Number.isInteger(n) || n < 1 || n > MAX_QUBITS) throw Error('Invalid qubit count');
    if (!Number.isInteger(seed) || seed < -2147483648 || seed > 4294967295) throw Error('Seed must be a 32-bit integer');
    this.n = n;
    this.seed = seed >>> 0;
    this.x = Array.from({length: 2*n+1}, () => new Uint8Array(n));
    this.z = Array.from({length: 2*n+1}, () => new Uint8Array(n));
    this.r = new Uint8Array(2*n+1);
    for (let i=0;i<n;i++) { this.x[i][i]=1; this.z[i+n][i]=1; }
  }
  rowSum(dst, src) {
    let phase = 2 * (this.r[dst] + this.r[src]);
    for (let q=0;q<this.n;q++) {
      const a=this.x[dst][q], b=this.z[dst][q], c=this.x[src][q], d=this.z[src][q];
      if (a && b) phase += d-c;
      else if (a) phase += d*(2*c-1);
      else if (b) phase += c*(1-2*d);
    }
    if (phase % 2) throw Error('Anticommuting tableau rows');
    this.r[dst] = ((phase/2 % 2)+2)%2;
    for (let q=0;q<this.n;q++) {
      this.x[dst][q] ^= this.x[src][q];
      this.z[dst][q] ^= this.z[src][q];
    }
  }
  randomBit() {
    this.seed = (Math.imul(1664525, this.seed) + 1013904223) >>> 0;
    return this.seed >>> 31;
  }
  apply(gate, ...qs) {
    const q = qs[0], n=this.n;
    if (gate==='H') {
      for (let i=0;i<2*n;i++) {
        const a=this.x[i][q], b=this.z[i][q];
        this.r[i] ^= a&b;
        if (a!==b) { this.x[i][q]^=1; this.z[i][q]^=1; }
      }
    } else if (gate==='S' || gate==='SDG') {
      for (let turn=0;turn<(gate==='S'?1:3);turn++)
        for (let i=0;i<2*n;i++) {
          const a=this.x[i][q], b=this.z[i][q];
          this.r[i] ^= a&b;
          this.z[i][q] ^= a;
        }
    } else if (gate==='X' || gate==='Y' || gate==='Z') {
      for (let i=0;i<2*n;i++) {
        const a=this.x[i][q],b=this.z[i][q];
        this.r[i] ^= gate==='X'?b:gate==='Y'?(a^b):a;
      }
    } else if (gate==='CX') {
      const a=qs[0],b=qs[1];
      for (let i=0;i<2*n;i++) {
        const xa=this.x[i][a], xb=this.x[i][b], za=this.z[i][a], zb=this.z[i][b];
        this.r[i] ^= xa & zb & (xb===za ? 1 : 0);
        this.x[i][b] ^= xa;
        this.z[i][a] ^= zb;
      }
    } else if (gate==='CZ') {
      this.apply('H',qs[1]); this.apply('CX',...qs); this.apply('H',qs[1]);
    } else if (gate==='SWAP') {
      this.apply('CX',...qs); this.apply('CX',qs[1],qs[0]); this.apply('CX',...qs);
    } else throw Error('Unsupported gate: '+gate);
  }
  expectationZ(q) {
    const n=this.n, scratch=2*n;
    for (let i=n;i<2*n;i++) if (this.x[i][q]) return 0;
    this.x[scratch].fill(0); this.z[scratch].fill(0); this.r[scratch]=0;
    for (let i=0;i<n;i++) if (this.x[i][q]) this.rowSum(scratch,i+n);
    return this.r[scratch] ? -1 : 1;
  }
  measure(q) {
    const n=this.n;
    let pivot=-1;
    for (let i=n;i<2*n;i++) if (this.x[i][q]) { pivot=i; break; }
    if (pivot<0) return {qubit:q,outcome:this.expectationZ(q)===-1?1:0,random:false};
    for (let i=0;i<2*n;i++)
      if (i!==pivot && i!==pivot-n && this.x[i][q]) this.rowSum(i,pivot);
    this.x[pivot-n].set(this.x[pivot]); this.z[pivot-n].set(this.z[pivot]); this.r[pivot-n]=this.r[pivot];
    this.x[pivot].fill(0); this.z[pivot].fill(0); this.z[pivot][q]=1;
    const bit=this.randomBit();
    this.r[pivot]=bit;
    return {qubit:q,outcome:bit,random:true};
  }
  stabilizers() {
    const chars=['I','X','Z','Y'], out=[];
    for (let i=this.n;i<2*this.n;i++) {
      let s=this.r[i]?'-':'+';
      for (let q=0;q<this.n;q++) s+=chars[this.x[i][q]+2*this.z[i][q]];
      out.push(s);
    }
    return out;
  }
}

export function simulateCircuit(n, text, seed=0) {
  const ops=parseCircuit(text,n), tableau=new Tableau(n,seed), measurements=[];
  for (const [gate,...qs] of ops) {
    if (gate==='M') measurements.push(tableau.measure(qs[0]));
    else tableau.apply(gate,...qs);
  }
  return {qubits:n,operations:ops.length,measurements,
    expectations_z:Array.from({length:n},(_,q)=>tableau.expectationZ(q)),
    stabilizers:tableau.stabilizers()};
}
