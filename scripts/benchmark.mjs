import {scoreCollection} from '../typescript/dist/index.js';
const sizes = JSON.parse(process.argv[2] || '[10000,100000]');
const repeats = Number(process.argv[3] || 3);
for (const size of sizes) for (const mode of ['categorical','configured']) {
 const collection = {tokens:Array.from({length:size}, (_,i) => ({token_id:String(i),traits:Array.from({length:8},(_,j)=>({trait_type:`Trait${j}`,value:String(i*(j+1)%(17+j))}))}))};
 const config = mode === 'categorical' ? undefined : {traits:[{trait_type:'Trait0',mode:'higher_is_rarer'}]};
 scoreCollection({tokens:collection.tokens.slice(0,100)},config);
 const seconds = [];
 for (let i=0;i<repeats;i++) {
  const start = performance.now();
  const rows = scoreCollection(collection,config);
  seconds.push((performance.now()-start)/1000);
  if(rows.length!==size) throw new Error('Incomplete results');
 }
 const sorted = [...seconds].sort((a,b)=>a-b), mid = Math.floor(sorted.length/2);
 const median_seconds = sorted.length%2 ? sorted[mid] : (sorted[mid-1]+sorted[mid])/2;
 console.log(JSON.stringify({runtime:'node',version:process.version,tokens:size,traits_per_token:8,mode,seconds,median_seconds}));
}
