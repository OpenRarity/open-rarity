import { explainCollection, parseCollectionJson, parseCreatorRarityConfig } from './scorer/index.js';
const sample = {tokens: [
 {token_id:'1',traits:[{trait_type:'Shape',value:'Circle'},{trait_type:'Color',value:'Plum'}]},
 {token_id:'2',traits:[{trait_type:'Shape',value:'Circle'},{trait_type:'Color',value:'Sand'}]},
 {token_id:'3',traits:[{trait_type:'Shape',value:'Star'},{trait_type:'Color',value:'Plum'}]},
 {token_id:'4',traits:[{trait_type:'Shape',value:'Circle'},{trait_type:'Color',value:'Plum'}]}
]};
const input = document.querySelector('#collection');
const status = document.querySelector('#status');
const body = document.querySelector('#results');
let latestResults = null;
function run() {
 latestResults = null; document.querySelector('#download').disabled = true;
 body.replaceChildren(); document.querySelector('#count').textContent = 'No results';
 try {
  if (input.value.length > 500000) throw Error('Please use a smaller JSON file (under 500 KB).');
  const data = parseCollectionJson(input.value);
  const config = parseCreatorRarityConfig(JSON.parse(input.value));
  if (!Array.isArray(data?.tokens) || data.tokens.length > 1000) throw Error('Provide a tokens array with at most 1,000 items.');
  for (const token of data.tokens) {
   if (!token || typeof token.token_id !== 'string' || !token.token_id || !Array.isArray(token.traits) || token.traits.length > 100) throw Error('Each token needs a string token_id and at most 100 traits.');

  }
  const explained = explainCollection(data, config);
  const results = explained.map(row => row.result);
  const byId = new Map(explained.map(row => [row.result.token_id, row]));
  latestResults = results; document.querySelector('#download').disabled = false;
  for (const result of results) {
   const row = document.createElement('tr');
   for (const value of [result.rank, result.token_id, result.score.toFixed(6), result.unique_trait_count]) {
    const cell = document.createElement('td'); cell.textContent = String(value); row.append(cell);
   }
   const cell = document.createElement('td');
   const details = document.createElement('details');
   const summary = document.createElement('summary'); summary.textContent = 'Explain';
   details.append(summary);
   const explanation = byId.get(result.token_id);
   const list = document.createElement('ul');
   for (const trait of explanation.traits) {
    const item = document.createElement('li');
    const frequency = trait.count === null ? (trait.mode === 'exclude' ? 'excluded' : 'no numeric contribution') : `${trait.count}/${data.tokens.length} tokens${trait.mode === 'higher_is_rarer' ? ' at or above this value' : ''}`;
    item.textContent = `${trait.trait_type}: ${trait.value ?? '(missing)'}; ${frequency}; contributes ${trait.contribution.toFixed(6)}${trait.unique ? '; unique trait' : ''}`;
    list.append(item);
   }
   details.append(list); cell.append(details); row.append(cell);
   body.append(row);
  }
  document.querySelector('#count').textContent = `${results.length} tokens`;
  status.textContent = results.length ? 'Calculation complete.' : 'Add tokens to calculate rarity.';
  status.className = '';
 } catch (error) { status.textContent = error.message; status.className = 'error'; }
}
const numericSample = {tokens:[
 {token_id:'1',traits:[{trait_type:'Level',value:10}]},
 {token_id:'2',traits:[{trait_type:'Level',value:50}]},
 {token_id:'3',traits:[{trait_type:'Level',value:20}]}
],rarity:{trait_count:'exclude',traits:[{trait_type:'Level',mode:'higher_is_rarer'}]}};
function reset() { input.value = JSON.stringify(document.querySelector('#sample').value === 'numeric' ? numericSample : sample, null, 2); run(); }
document.querySelector('#sample').addEventListener('change', reset);
document.querySelector('#copy-install').addEventListener('click', async () => {
 const button = document.querySelector('#copy-install');
 try { await navigator.clipboard.writeText('pip install open-rarity'); button.textContent = 'Copied'; document.querySelector('#copy-status').textContent = 'Install command copied.'; }
 catch { document.querySelector('#copy-status').textContent = 'Select and copy the install command above.'; }
 setTimeout(()=>{button.textContent='Copy';},2000);
});
document.querySelector('#score').addEventListener('click', run);
document.querySelector('#reset').addEventListener('click', reset);
reset();

document.querySelector('#upload').addEventListener('change', async (event) => {
 const file = event.target.files[0]; if (!file) return;
 if (file.size > 500000) { status.textContent = 'Please use a file under 500 KB.'; status.className = 'error'; return; }
 input.value = await file.text(); run();
});
document.querySelector('#download').addEventListener('click', () => {
 if (!latestResults) return;
 const url = URL.createObjectURL(new Blob([JSON.stringify(latestResults, null, 2)], {type:'application/json'}));
 const link = document.createElement('a'); link.href = url; link.download = 'openrarity-results.json'; link.click();
 setTimeout(() => URL.revokeObjectURL(url), 1000);
});
