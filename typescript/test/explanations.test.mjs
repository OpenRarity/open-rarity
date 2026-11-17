import assert from 'node:assert/strict';
import test from 'node:test';
import {explainCollection, scoreCollection, parseCollectionJson} from '../dist/index.js';
test('explanations preserve scores and source order', () => {
 const collection = parseCollectionJson('{"tokens":[{"token_id":"1","traits":[{"trait_type":"Level","value":9007199254740993},{"trait_type":"Hide","value":"x"}]},{"token_id":"2","traits":[{"trait_type":"Level","value":"bad"}]}]}');
 const config = {trait_count:'exclude',traits:[{trait_type:'Level',mode:'higher_is_rarer'},{trait_type:'Hide',mode:'exclude'}]};
 const rows = explainCollection(collection, config);
 assert.deepEqual(rows.map(r=>r.result), scoreCollection(collection, config));
 assert.equal(rows[0].source_traits[0].value, '9007199254740993');
 for (const row of rows) {
  assert.ok(Math.abs(row.traits.reduce((sum,t)=>sum+t.contribution,0)-row.result.score)<1e-12);
  assert.equal(row.traits.filter(t=>t.unique).length,row.result.unique_trait_count);
 }
 const invalid = rows.find(r=>r.result.token_id==='2').traits.find(t=>t.trait_type==='Level');
 assert.equal(invalid.probability,null);
 assert.equal(invalid.information,0);
 assert.deepEqual(explainCollection({tokens:[]}),[]);
});
