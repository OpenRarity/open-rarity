import { scoreCollection } from './scorer/index.js';
const sample = {tokens: [
 {token_id:'1',traits:[{trait_type:'Shape',value:'Circle'},{trait_type:'Color',value:'Plum'}]},
 {token_id:'2',traits:[{trait_type:'Shape',value:'Circle'},{trait_type:'Color',value:'Sand'}]},
 {token_id:'3',traits:[{trait_type:'Shape',value:'Star'},{trait_type:'Color',value:'Plum'}]},
 {token_id:'4',traits:[{trait_type:'Shape',value:'Circle'},{trait_type:'Color',value:'Plum'}]}
]};
const input = document.querySelector('#collection');
const status = document.querySelector('#status');
const body = document.querySelector('#results');
function run() {
 body.replaceChildren(); document.querySelector('#count').textContent = 'No results';
 try {
  if (input.value.length > 500000) throw Error('Please use a smaller JSON file (under 500 KB).');
  const data = JSON.parse(input.value);
  if (!Array.isArray(data?.tokens) || data.tokens.length > 1000) throw Error('Provide a tokens array with at most 1,000 items.');
  for (const token of data.tokens) {
   if (!token || typeof token.token_id !== 'string' || !token.token_id || !Array.isArray(token.traits) || token.traits.length > 100) throw Error('Each token needs a string token_id and at most 100 traits.');
   for (const trait of token.traits) if (!trait || typeof trait.trait_type !== 'string' || typeof trait.value !== 'string') throw Error('This preview accepts string trait names and values.');
  }
  const results = scoreCollection(data);
  for (const result of results) {
   const row = document.createElement('tr');
   for (const value of [result.rank, result.token_id, result.score.toFixed(6), result.unique_trait_count]) {
    const cell = document.createElement('td'); cell.textContent = String(value); row.append(cell);
   }
   body.append(row);
  }
  document.querySelector('#count').textContent = `${results.length} tokens`;
  status.textContent = results.length ? 'Calculation complete.' : 'Add tokens to calculate rarity.';
  status.className = '';
 } catch (error) { status.textContent = error.message; status.className = 'error'; }
}
function reset() { input.value = JSON.stringify(sample, null, 2); run(); }
document.querySelector('#score').addEventListener('click', run);
document.querySelector('#reset').addEventListener('click', reset);
reset();
