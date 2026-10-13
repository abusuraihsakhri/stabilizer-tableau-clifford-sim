import {simulateCircuit} from './simulator.mjs';

const $=id=>document.getElementById(id);
const examples={
  bell:{n:2,text:'H 0\nCX 0 1\nM 0\nM 1'},
  ghz:{n:3,text:'H 0\nCX 0 1\nCX 1 2\nM 0\nM 1\nM 2'},
  phase:{n:1,text:'H 0\nS 0\nSDG 0\nH 0\nM 0'},
  error:{n:3,text:'# Encode a three-qubit repetition state\nX 0\nCX 0 1\nCX 0 2\n# Single-bit flip\nX 1\nM 0\nM 1\nM 2'}
};
let last=null;

function showError(message) {
  $('status').textContent=message;
  $('status').className='resultState error';
  for (const id of ['out-qubits','out-operations','out-measurements']) $(id).textContent='—';
  for (const id of ['measurements','stabilizers','expectations']) $(id).textContent='No result.';
  $('copy').disabled=$('save').disabled=true;
  last=null;
}
function simulate() {
  try {
    const n=Number($('qubits').value),seed=Number($('seed').value);
    if (!$('qubits').value.trim() || !$('seed').value.trim()) throw Error('Qubit count and seed are required.');
    last=simulateCircuit(n,$('circuit').value,seed);
    $('status').textContent='Simulation completed locally. No data was transmitted.';
    $('status').className='resultState success';
    $('out-qubits').textContent=last.qubits;
    $('out-operations').textContent=last.operations;
    $('out-measurements').textContent=last.measurements.length;
    $('measurements').textContent=last.measurements.length?
      last.measurements.map((m,i)=>'#'+(i+1)+' · q'+m.qubit+' → '+m.outcome+' ('+(m.random?'sampled':'determined')+')').join('\n'):
      'No measurements in circuit.';
    $('stabilizers').textContent=last.stabilizers.map((s,i)=>'g'+i+' = '+s).join('\n');
    $('expectations').textContent=last.expectations_z.map((v,i)=>'⟨Z'+i+'⟩ = '+v).join('\n');
    $('copy').disabled=$('save').disabled=false;
  } catch(err) { showError(err instanceof Error ? err.message : 'Unexpected simulation error'); }
}
function loadExample() {
  const e=examples[$('example').value];
  if (!e) return;
  $('qubits').value=e.n;
  $('seed').value=0;
  $('circuit').value=e.text;
  simulate();
}
function json(){return JSON.stringify(last,null,2)+'\n';}
$('run').addEventListener('click',simulate);
$('reset').addEventListener('click',loadExample);
$('example').addEventListener('change',loadExample);
$('copy').addEventListener('click',async()=>{
  if(!last)return;
  try{
    await navigator.clipboard.writeText(json());
    $('status').textContent='JSON copied to clipboard.';
  }catch{
    $('status').textContent='Clipboard unavailable. Use Export JSON instead.';
  }
});
$('save').addEventListener('click',()=>{
  if(!last)return;
  const url=URL.createObjectURL(new Blob([json()],{type:'application/json'}));
  const anchor=document.createElement('a');
  anchor.href=url;anchor.download='stabilizer-result.json';
  document.body.appendChild(anchor);anchor.click();anchor.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
});
loadExample();
