/* Native editable PowerPoint and matching PDF from one geometry model. */
const fs = require('fs');
const path = require('path');
function dependency(name) {
  try { return require(name); }
  catch {
    if(name==='pdfkit'){
      try{return require(path.join(__dirname,'node_modules/pdfkit/js/pdfkit.js'));}catch{}
    }
    return require('/tmp/asic-pptx-tools-20261019/node_modules/' + name + (name==='pdfkit'?'/js/pdfkit.js':''));
  }
}
const PptxGenJS = dependency('pptxgenjs');
const PDFDocument = dependency('pdfkit');
const base = __dirname;
const project = path.resolve(base, '../../..');
const workspace = path.dirname(project);
const logo = path.join(workspace, 'gira.png');
const content = JSON.parse(fs.readFileSync(path.join(base, 'contenido.json'), 'utf8'));
const audit = JSON.parse(fs.readFileSync(path.join(base, 'auditoria_evidencias.json'), 'utf8'));
const bibliography = fs.readFileSync(path.join(base, 'FUENTES_VERIFICADAS.md'), 'utf8');
const refs = {};
for (const match of bibliography.matchAll(/^### \[(F\d+)\] (.+)\n([\s\S]*?)(?=^### |^## |$(?![\s\S]))/gm)) {
  const urls = [...match[3].matchAll(/<([^>]+)>/g)].map(m => m[1]);
  refs[match[1]] = { title:match[2], urls, text:match[3] };
}
const p = new PptxGenJS();
p.layout = 'LAYOUT_WIDE'; p.lang='es-CO'; p.author='GIRA · revisión de ASIC Area Lab';
p.subject='Pipeline implementado, auditoría de evidencias y límites de la estimación de área';
p.title=content.title; p.company='GIRA';
p.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'es-CO'};
const W=13.333333, H=7.5;
const C={bg:'F5F6F8',ink:'14293B',muted:'526474',teal:'007C83',pale:'E5F3F3',white:'FFFFFF',rule:'D9E2E9',amber:'B36A10',amberPale:'FFF1D9',dark:'112B3C',code:'102331',green:'087E60'};
const visuals=[], pages=[], bounds=[];
let sl, page;
function record(kind, obj) { visuals.push({slide:page,kind,...obj}); }
function check(x,y,w,h,kind) {
  if (![x,y,w,h].every(Number.isFinite) || x<-.01 || y<-.01 || w<0 || h<0 || x+w>W+.01 || y+h>H+.01) throw new Error('Out of slide: '+page+' '+kind+' '+[x,y,w,h]);
  bounds.push({slide:page,kind,x,y,w,h});
}
function text(str,x,y,w,h,size=20,options={}) {
  check(x,y,w,h,'text');
  sl.addText(String(str),{x,y,w,h,fontFace:options.mono?'Courier New':'Arial',fontSize:size,color:C.ink,margin:0,breakLine:false,valign:'top',...options});
  record('text',{str:String(str),x,y,w,h,size,options});
}
function rect(x,y,w,h,fill=C.white,line=C.rule,r=0) {
  check(x,y,w,h,'shape');
  sl.addShape(r?p.ShapeType.roundRect:p.ShapeType.rect,{x,y,w,h,radius:r,rectRadius:r,fill:{color:fill},line:{color:line,width:.65}});
  record('rect',{x,y,w,h,fill,line,r});
}
function line(x1,y1,x2,y2,color=C.teal,width=1.5,arrow=false) {
  check(Math.min(x1,x2),Math.min(y1,y2),Math.abs(x2-x1),Math.abs(y2-y1),'line');
  sl.addShape(p.ShapeType.line,{x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(x2-x1),h:Math.abs(y2-y1),flipV:y2<y1,flipH:x2<x1,line:{color,width,beginArrowType:'none',endArrowType:arrow?'triangle':'none'}});
  record('line',{x1,y1,x2,y2,color,width,arrow});
}
function picture(x,y,w,h) {
  check(x,y,w,h,'image');
  sl.addImage({path:logo,x,y,w,h,altText:'Logo GIRA Robotics and Automation Research Group'});
  record('image',{path:logo,x,y,w,h});
}
function tag(label,x,y,w,fill=C.pale,color=C.teal) {
  rect(x,y,w,.34,fill,fill,.05); text(label,x+.09,y+.06,w-.18,.22,10.4,{bold:true,color});
}
function box(title,body,x,y,w,h,accent=C.teal) {
  rect(x,y,w,h); rect(x,y,.055,h,accent,accent);
  if(h<=2.2){
    text(title,x+.22,y+.17,w-.44,.38,20,{bold:true,color:accent});
    text(body,x+.22,y+.77,w-.44,h-.91,17,{color:C.ink});
    return;
  }
  text(title,x+.22,y+.23,w-.44,.72,22,{bold:true,color:accent});
  text(body,x+.22,y+1.13,w-.44,h-1.34,19,{color:C.ink});
}
function table(headers,rows,x,y,widths,{dense=false,fontSize}={}) {
  const hh=.47, rh=dense?Math.min(.36,3.98/rows.length):Math.min(.75,3.9/rows.length);
  let yy=y;
  for (const [ri,row] of [headers,...rows].entries()) {
    const h=ri===0?hh:rh; let xx=x;
    for (let ci=0;ci<row.length;ci++) {
      const w=widths[ci]; rect(xx,yy,w,h,ri===0?C.ink:ri%2?C.white:'EAF0F5',C.bg);
      const hyperlink=String(row[ci]).startsWith('https://')?{hyperlink:{url:String(row[ci])}}:{};
      text(String(row[ci]),xx+.10,yy+.07,w-.20,h-.10,ri===0?13.5:(fontSize|| (dense?13.5:16)),{color:ri===0?C.white:C.ink,bold:ri===0||ci===0,...hyperlink});
      xx+=w;
    }
    yy+=h;
  }
}
function code(str,x,y,w,h,compact=false) {
  rect(x,y,w,h,C.code,C.code,.1);
  const lines=str.split('\n'), size=compact?12.4:13.6;
  const dy=Math.min(.34,(h-.45)/lines.length);
  lines.forEach((value,i)=>{
    const color=/^\s*#/.test(value)?'E0B76B':/^(ghdl|yosys|iverilog|vvp|read_|hierarchy|synth|dfflibmap|abc|delete|clean|check|write_|tee|RUN|USER|POST)/.test(value)?'80DDD5':'EAF2F7';
    text(value,x+.19,y+.22+i*dy,w-.38,dy,size,{mono:true,color});
  });
}
function node(title,sub,x,y,w=3.7,h=1.35,accent=C.teal) {
  rect(x,y,w,h,C.white,C.rule,.08);
  text(title,x+.18,y+.17,w-.36,.49,title.length>18?18.5:20.5,{bold:true,color:accent,align:'center'});
  if(sub) text(sub,x+.17,y+.72,w-.34,Math.max(.29,h-.80),16.5,{color:C.muted,align:'center'});
}
function footer(s) {
  if(s.takeaway) {
    rect(.63,6.47,12.06,.49,C.pale,C.pale,.05);
    text(s.takeaway,.81,6.58,11.70,.28,15.5,{color:C.teal,bold:true});
  }
  line(.64,7.10,12.68,7.10,C.rule,.7);
  const citations=s.refs.length?s.refs.join(' · '):'Evidencia local';
  let source=citations+(s.local?' | '+s.local:'');
  if(source.length>155) source=source.slice(0,152)+'…';
  text(source,.65,7.19,11.20,.19,8.7,{color:C.muted});
  text(String(page).padStart(2,'0')+' / '+content.slides.length,11.97,7.15,.70,.25,10.5,{color:C.muted,align:'right'});
}
function chart(data,x,y,w,h,{labelWidth=2.8}={}) {
  check(x,y,w,h,'chart');
  sl.addChart(p.ChartType.bar,[{name:'Área de celdas',labels:data.map(d=>d.label),values:data.map(d=>d.value)}],{
    x,y,w,h,barDir:'bar',showLegend:false,showValue:true,showTitle:false,
    chartColors:[C.teal],catAxisLabelFontFace:'Arial',catAxisLabelFontSize:12,
    valAxisLabelFontSize:10,dataLabelFormatCode:'#,##0.000',dataLabelColor:C.ink,dataLabelPosition:'outEnd',
    showCatName:false,showBorder:false,showShadow:false,dataLabelFontSize:12,
    valGridLine:{color:C.rule,width:.5},catAxisLineColor:C.rule,valAxisLineColor:C.rule,
    chartArea:{fill:{color:C.bg},border:{color:C.bg,pt:0}},plotArea:{fill:{color:C.bg},border:{color:C.bg,pt:0}},
    showValue:true,showCatName:false,
  });
  record('chart',{data,x,y,w,h,labelWidth});
}
const f=n=>n.toLocaleString('es-CO',{minimumFractionDigits:3,maximumFractionDigits:3});
for (let i=0;i<content.slides.length;i++) {
  const s=content.slides[i]; page=i+1; sl=p.addSlide();
  sl.background={color:s.type==='cover'?C.dark:C.bg};
  const current=sl;
  pages.push({title:s.title,section:s.section,type:s.type});
  if(s.type==='cover') {
    rect(0,0,.15,H,C.teal,C.teal);
    picture(8.25,.73,3.85,1.666);
    text('GIRA / ASIC AREA LAB',.73,.51,7.2,.32,12,{bold:true,charSpacing:2,color:'93D8D6'});
    text('Del VHDL\nal área ASIC',.73,1.35,7.2,1.65,47,{bold:true,color:C.white});
    text('Qué medimos y qué podemos demostrar',.76,3.25,7.0,1.05,29,{bold:true,color:'9CDCD9'});
    text(s.subtitle,.77,4.54,7.0,.82,22,{color:'CCDAE2'});
    s.chips.forEach((v,k)=>tag(v,.79+k*3.98,5.91,3.73,'23495B','FFFFFF'));
    text('REVISIÓN TÉCNICA · 19 OCTUBRE 2026',.79,6.77,11.7,.31,12,{color:'CCDAE2'});
  } else {
    rect(0,0,.12,H,C.teal,C.teal);
    text(s.section.toUpperCase(),.65,.34,10.35,.26,10.8,{bold:true,color:C.teal,charSpacing:1.5});
    picture(11.30,.24,1.38,.598);
    text(s.title,.65,.88,12.0,1.01,28,{bold:true,color:C.ink});
    if(s.type==='cards') {
      s.cards.forEach((c,k)=>box(c[0],c[1],.68+k*4.08,2.16,3.91,3.84,k===2?C.amber:C.teal));
    } else if(s.type==='table') {
      table(s.headers,s.rows,.75,2.05,s.widths,{dense:s.dense});
    } else if(s.type==='scope') {
      rect(.77,2.10,11.75,.75,C.dark,C.dark,.08);text(s.formula,1.02,2.28,11.25,.44,24,{bold:true,color:C.white,align:'center'});
      text('SE INCLUYE',.96,3.19,5.3,.30,12,{bold:true,color:C.teal,charSpacing:1});
      text('FUERA DEL ALCANCE',7.04,3.19,5.1,.30,12,{bold:true,color:C.amber,charSpacing:1});
      s.left.forEach((v,k)=>{rect(.96,3.79+k*.65,.10,.10,C.teal,C.teal);text(v,1.25,3.69+k*.65,5.3,.4,21);});
      s.right.forEach((v,k)=>{rect(7.04,3.79+k*.65,.10,.10,C.amber,C.amber);text(v,7.33,3.69+k*.65,5.0,.4,21);});
    } else if(s.type==='flow') {
      s.steps.forEach((v,k)=>{
        node(v[0],v[1],.78+k*4.17,2.48,3.42,1.55);
        if(k<2)line(4.20+k*4.17,3.25,4.85+k*4.17,3.25,C.teal,2,true);
      });
      if(s.formula){rect(.83,4.61,11.70,.92,C.white,C.rule,.08);text(s.formula,1.02,4.87,11.32,.49,22,{align:'center',bold:true,color:C.teal});}
      if(s.code)code(s.code,.83,4.51,11.70,1.23,true);
    } else if(s.type==='pipeline') {
      const top=[['01 · Seleccionar','DPU + Liberty'],['02 · Capturar','Fuentes + hashes'],['03 · GHDL RTL','256 esperados'],['04 · Convertir','VHDL → Verilog'],['05 · Yosys','Síntesis + mapeo']];
      const bottom=[['10 · Reportar','JSON / CSV / ZIP'],['09 · Aceptar','O fallar con log'],['08 · Simular','Netlist vs RTL'],['07 · Contar','Área + FF + stat'],['06 · Netlist','Celdas concretas']];
      const xs=[.77,3.28,5.79,8.30,10.81], nw=1.80, nh=1.18, yt=2.38, yb=4.55;
      for(let k=0;k<5;k++){
        for(const [data,y] of [[top,yt],[bottom,yb]]){
          rect(xs[k],y,nw,nh,C.white,C.rule,.06);
          text(data[k][0],xs[k]+.09,y+.18,nw-.18,.34,15.2,{bold:true,color:C.teal,align:'center'});
          text(data[k][1],xs[k]+.09,y+.69,nw-.18,.34,12.3,{color:C.muted,align:'center'});
        }
        if(k<4){line(xs[k]+nw,yt+.59,xs[k+1]-.08,yt+.59,C.teal,1.5,true);line(xs[k+1],yb+.59,xs[k]+nw+.08,yb+.59,C.teal,1.5,true);}
      }
      line(xs[4]+nw/2,yt+nh,xs[4]+nw/2,yb-.07,C.teal,1.5,true);
      line(xs[2]+nw/2,yt+nh,xs[2]+nw/2,yb-.07,C.amber,1.2,true);
      text('Referencia RTL',xs[2]+nw/2+.12,3.90,2.2,.27,11,{color:C.amber,bold:true});
    } else if(s.type==='code') {
      code(s.code,.75,2.10,7.55,4.12,s.compact);
      rect(8.58,2.10,4.0,4.12,C.white,C.rule,.08);
      text('CÓMO INTERPRETARLO',8.83,2.35,3.52,.35,12,{color:C.teal,bold:true,charSpacing:.7});
      text(s.explanation,8.83,3.0,3.48,2.94,17.0);
    } else if(s.type==='architecture') {
      rect(.76,2.03,11.79,3.99,C.white,C.rule,.1);
      node('React + Vite','Selección y visualización',1.01,2.28,3.20,1.18);
      node('FastAPI','HTTP y contratos',5.06,2.28,3.20,1.18);
      node('ExperimentService','Caso de uso + cola',9.11,2.28,3.20,1.18);
      line(4.21,2.87,4.99,2.87,C.teal,1.5,true);line(8.26,2.87,9.04,2.87,C.teal,1.5,true);
      node('Dominio / puertos','ExperimentRepository + SynthesisGateway',3.79,3.86,5.75,1.08);
      line(10.71,3.46,10.71,4.40,C.teal,1.5);line(10.71,4.40,9.58,4.40,C.teal,1.5,true);
      tag('SQLite: estado y reportes',1.09,5.29,4.74);tag('GHDL / Yosys / Icarus: cálculo',7.39,5.29,4.74);
      line(4.65,4.94,3.65,5.26,C.teal,1.2,true);line(8.53,4.94,9.57,5.26,C.teal,1.2,true);
    } else if(s.type==='ledger') {
      const r=JSON.parse(fs.readFileSync(path.join(project,'docs/validation/dpu-matrix-20261018/int8_16/nangate45/report.json'),'utf8'));
      const ff=r.cells.filter(c=>c.category==='flip_flop');
      const chosen=r.cells.filter(c=>c.category==='combinational').sort((a,b)=>b.total_area-a.total_area).slice(0,3);
      const names=new Set([...chosen,...ff].map(c=>c.name));
      const rest=r.cells.filter(c=>!names.has(c.name));
      const rows=[...chosen,...ff].map(c=>[c.name,String(c.count),f(c.unit_area),f(c.total_area)]);
      rows.push(['Otros tipos combinacionales',String(rest.reduce((n,c)=>n+c.count,0)),'Variable',f(rest.reduce((n,c)=>n+c.total_area,0))]);
      rows.push(['TOTAL',String(r.total_cells),'—',f(r.total_area)]);
      table(['Tipo de celda','Cantidad','Área unitaria · µm²','Subtotal · µm²'],rows,.78,2.12,[4.55,1.65,2.55,2.50],{fontSize:16});
    } else if(s.type==='coverage') {
      const ids=['int8_16','int16_32','fxp8_16','fxp16_32','fp8','fp16','fp32','posit8','posit16','posit32','lns16'];
      const techs=['ihp130','nangate45','nangate15'];
      text('DPU / formato',1.0,2.06,3.0,.3,13,{bold:true,color:C.muted});
      techs.forEach((t,k)=>text(t,4.40+k*2.7,2.06,2.4,.3,14,{bold:true,color:C.ink,align:'center'}));
      ids.forEach((id,j)=>{
        const y=2.53+j*.315;text(id,1.03,y+.04,3.0,.23,13.5,{bold:true});
        techs.forEach((t,k)=>{
          const exists=audit.cases.some(r=>r.design_id===id&&r.technology_id===t);
          rect(4.40+k*2.7,y,2.4,.265,exists?C.pale:C.amberPale,exists?C.pale:C.amberPale,.03);
          text(exists?'Documentado':'Pendiente',4.45+k*2.7,y+.025,2.3,.22,11.3,{color:exists?C.green:C.amber,align:'center',bold:true});
        });
      });
    } else if(s.type==='chart') {
      const data=s.chart==='int8'?['ihp130','nangate45','nangate15'].map(t=>{
        const row=audit.cases.find(r=>r.design_id==='int8_16'&&r.technology_id===t);
        return {label:t+' · '+f(row.total_area),value:row.total_area};
      }):audit.cases.filter(r=>r.technology_id==='nangate45').map(r=>({label:r.design_id,value:r.total_area}));
      chart(data,.78,2.08,11.65,4.1,{labelWidth:s.chart==='int8'?3.5:2.0});
      text('Área nominal de celdas · µm²',8.7,6.12,3.6,.22,11,{color:C.muted,align:'right'});
    } else if(s.type==='verdict') {
      rect(.79,2.13,11.77,1.56,C.dark,C.dark,.1);
      text(s.statement,1.10,2.43,11.12,.95,26,{color:C.white,bold:true,align:'center'});
      box('Lo sustentado',s.left,.83,4.03,5.65,2.0,C.teal);
      box('Lo pendiente',s.right,6.85,4.03,5.65,2.0,C.amber);
    } else if(s.type==='references') {
      const rows=s.ids.map(id=>[id,refs[id]?.title||id,refs[id]?.urls[0]||'Ver FUENTES_VERIFICADAS.md']);
      table(['ID','Tema','URL oficial / primaria'],rows,.76,2.08,[.76,4.32,6.20],{fontSize:12.2});
    }
    footer(s);
  }
  let notes=s.notes+'\n\nEVIDENCIA LOCAL\n'+(s.local||'Ver auditoría y código referenciado en la presentación.')+'\n\nFUENTES PRIMARIAS · consulta 19/10/2026\n';
  notes+=s.refs.map(id=>id+' — '+(refs[id]?.title||'')+'\n'+(refs[id]?.urls||[]).join('\n')).join('\n\n');
  current.addNotes(notes);
}

// PDF mirror and independent text-height check; no browser or EDA required.
const doc=new PDFDocument({autoFirstPage:false,size:[960,540],margin:0,compress:true,info:{Title:content.title,Author:'GIRA · ASIC Area Lab',Subject:'Revisión técnica con fuentes y auditoría de evidencia'}});
doc.registerFont('regular','/usr/share/fonts/liberation/LiberationSans-Regular.ttf');
doc.registerFont('bold','/usr/share/fonts/liberation/LiberationSans-Bold.ttf');
doc.registerFont('mono','/usr/share/fonts/liberation/LiberationMono-Regular.ttf');
const pdfPath=path.join(base,'Revision_pipeline_ASIC_GIRA.pdf');
const stream=fs.createWriteStream(pdfPath);doc.pipe(stream);
const overflows=[];
function label(str,x,y,size,options={}){
  doc.font(options.mono?'mono':options.bold?'bold':'regular').fontSize(size).fillColor('#'+(options.color||C.ink));
  doc.text(str,x,y,{width:options.width,align:options.align||'left',lineBreak:false});
}
for(let i=0;i<pages.length;i++){
  doc.addPage({size:[960,540],margin:0});doc.rect(0,0,960,540).fill('#'+(pages[i].type==='cover'?C.dark:C.bg));
  for(const v of visuals.filter(v=>v.slide===i+1)){
    const x=v.x*72,y=v.y*72,w=v.w*72,h=v.h*72;
    if(v.kind==='rect'){
      doc.save().lineWidth(.65).fillColor('#'+v.fill).strokeColor('#'+v.line);
      if(v.r)doc.roundedRect(x,y,w,h,v.r*72);else doc.rect(x,y,w,h);
      doc.fillAndStroke().restore();
    }else if(v.kind==='line'){
      const x1=v.x1*72,y1=v.y1*72,x2=v.x2*72,y2=v.y2*72;
      doc.save().lineWidth(v.width).strokeColor('#'+v.color).moveTo(x1,y1).lineTo(x2,y2).stroke();
      if(v.arrow){const a=Math.atan2(y2-y1,x2-x1),l=7,b=3;doc.moveTo(x2,y2).lineTo(x2-l*Math.cos(a)+b*Math.sin(a),y2-l*Math.sin(a)-b*Math.cos(a)).lineTo(x2-l*Math.cos(a)-b*Math.sin(a),y2-l*Math.sin(a)+b*Math.cos(a)).closePath().fill('#'+v.color);}
      doc.restore();
    }else if(v.kind==='image') doc.image(v.path,x,y,{width:w,height:h});
    else if(v.kind==='text'){
      const o=v.options;doc.save().font(o.mono?'mono':o.bold?'bold':'regular').fontSize(v.size).fillColor('#'+(o.color||C.ink));
      const options={width:w,align:o.align||'left',lineGap:0,paragraphGap:0,characterSpacing:o.charSpacing||0,...(o.hyperlink?{link:o.hyperlink.url}:{})};
      const needed=doc.heightOfString(v.str,options);
      if(needed>h+1.2)overflows.push({slide:i+1,text:v.str,needed_pt:needed,available_pt:h});
      doc.text(v.str,x,y,options);doc.restore();
    }else if(v.kind==='chart'){
      const left=v.labelWidth*72,right=96,top=10,bottom=30,pw=w-left-right,ph=h-top-bottom,max=Math.max(...v.data.map(d=>d.value))*1.06;
      for(let tick=0;tick<=4;tick++){
        const xx=x+left+(tick/4)*pw;
        doc.save().strokeColor('#'+C.rule).lineWidth(.5).moveTo(xx,y+top).lineTo(xx,y+top+ph).stroke().restore();
        label(Math.round(max*tick/4).toLocaleString('es-CO'),xx-30,y+top+ph+10,10,{width:60,align:'center',color:C.muted});
      }
      const rh=ph/v.data.length;
      v.data.forEach((d,j)=>{
        const yy=y+top+j*rh+rh*.2,bar=d.value/max*pw;
        label(d.label,x,yy+rh*.10,v.data.length>5?11.5:14,{width:left-10,align:'right'});
        doc.rect(x+left,yy,bar,rh*.55).fill('#'+C.teal);
        label(f(d.value),x+left+bar+7,yy+rh*.10,v.data.length>5?10.5:13,{width:88,bold:true});
      });
    }
  }
}
doc.end();
const notes=content.slides.map((s,i)=>'## '+String(i+1).padStart(2,'0')+' · '+s.title+'\n\n'+s.notes+'\n\nEvidencia: '+(s.local||'Ver auditoría.')+'\n\n'+s.refs.map(id=>'['+id+'] '+(refs[id]?.title||'')+' — '+(refs[id]?.urls||[]).join(', ')).join('\n')).join('\n\n');
const mainSlides=content.slides.findIndex(s=>s.title.startsWith('Anexo A'));
fs.writeFileSync(path.join(base,'GUION.md'),'# Guion y notas de la presentación\n\n'+content.slides.length+' diapositivas: '+mainSlides+' principales y '+(content.slides.length-mainSlides)+' anexos. Exposición detallada sugerida: 35–45 minutos; usar los anexos para preguntas.\n\n'+notes+'\n');
fs.writeFileSync(path.join(base,'modelo_visual.json'),JSON.stringify({pages,visuals},null,2));
const findings={slides:pages.length,editable_diagrams:true,native_charts:2,logo:'gira.png, original sin modificar',geometry_checks:bounds.length,text_overflow:overflows,pdf_renderer:'PDFKit desde la misma geometría; no se afirma render de PowerPoint/LibreOffice',eda_executed:false};
fs.writeFileSync(path.join(base,'revision_visual.json'),JSON.stringify(findings,null,2));
Promise.all([p.writeFile({fileName:path.join(base,'Revision_pipeline_ASIC_GIRA.pptx')}),new Promise(resolve=>stream.on('finish',resolve))]).then(()=>console.log(JSON.stringify({slides:pages.length,pptx:'Revision_pipeline_ASIC_GIRA.pptx',pdf:'Revision_pipeline_ASIC_GIRA.pdf',overflow:overflows},null,2))).catch(error=>{console.error(error);process.exitCode=1;});
