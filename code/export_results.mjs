// Optional XLSX packaging. Numerical reproduction only requires solve.py.
// Requires @oai/artifact-tool 2.8.58+ in the Codex primary Node runtime.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const root = process.env.DRYING_SUPPORT_ROOT || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root,'results');
const which = Number(process.argv[2]);
const wb = Workbook.create();
async function csv(name) {
  const lines=(await fs.readFile(path.join(out,name),'utf8')).trim().split(/\r?\n/);
  return lines.slice(1).map(l=>l.split(',').map(v=>v==='nan'?null:Number(v)));
}
async function sheet(name,file,surface=false,radius=false) {
  const s=wb.worksheets.add(name), rows=await csv(file);
  const heads=radius ? ['时间/s','半径/cm'] :
    ['时间\\到药材中心的距离',...Array.from({length:surface?20:21},(_,i)=>i/10),...(surface?['药材表面']:[])];
  const width=heads.length, height=rows.length+1;
  s.getRangeByIndexes(0,0,1,width).values=[heads];
  for(let i=0;i<rows.length;i+=2000) {
    const block=rows.slice(i,i+2000).map(r=>r.map((v,j)=>j===0||v===null?v:Math.round(v*1e4)/1e4));
    s.getRangeByIndexes(i+1,0,block.length,width).values=block;
  }
  const used=s.getRangeByIndexes(0,0,height,width);
  used.format.font={name:'Droid Sans Fallback',size:10};
  used.format.rowHeight=19;
  used.format.columnWidth=12;
  used.format.verticalAlignment='center';
  s.getRangeByIndexes(0,0,height,1).format.columnWidth=34;
  s.getRangeByIndexes(0,0,1,width).format={fill:'#E8ECF1',font:{bold:true,color:'#111827'},rowHeight:30,horizontalAlignment:'center'};
  s.getRangeByIndexes(1,1,rows.length,width-1).setNumberFormat('0.0000');
  s.getRangeByIndexes(1,0,rows.length,1).setNumberFormat('0');
  s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(1);
  s.showGridLines=true;
}
if(which===1||which===2) {
  await sheet('温度',`result${which}_T.csv`);
  await sheet('水分浓度',`result${which}_C.csv`);
} else {
  await sheet('Sheet1',`result${which}_C.csv`,which===4);
  if(which===4) await sheet('表面位置','radius_output.csv',false,true);
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:`'${which<=2?'温度':'Sheet1'}'!A1:D4`,tableMaxRows:4,tableMaxCols:4,maxChars:1000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:5},maxChars:1000})).ndjson);
await fs.mkdir(path.join(root,'previews'),{recursive:true});
for(let i=0;i<(which<=2||which===4?2:1);i++) {
  const s=wb.worksheets.getItemAt(i);
  const png=await wb.render({sheetName:s.name,range:which===4&&i===1?'A1:B8':'A1:G8',scale:1.5,format:'png'});
  await fs.writeFile(path.join(root,'previews',`result${which}_${i}.png`),new Uint8Array(await png.arrayBuffer()));
}
await fs.mkdir(path.join(out,'workbooks'),{recursive:true});
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'workbooks',`result${which}.xlsx`));
console.log(`Exported result${which}.xlsx`);
