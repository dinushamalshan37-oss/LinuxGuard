'use strict';

const $ = (id) => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const formatter = new Intl.DateTimeFormat(undefined, {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});

function setText(id, value) { const node=$(id); if(node) node.textContent = String(value); }
function numeric(value) { const n=Number(value); return Number.isFinite(n) ? n : 0; }
function percent(value) { return `${numeric(value).toFixed(1)}%`; }
function shortOS(value) { return String(value || 'Unknown').slice(0, 45); }
function formatUptime(seconds) {
  const s=Math.max(0,Math.floor(numeric(seconds)));
  const days=Math.floor(s/86400), hrs=Math.floor((s%86400)/3600), mins=Math.floor((s%3600)/60);
  return `${days}d ${hrs}h ${mins}m`;
}
function niceTime(seconds){return formatter.format(new Date(numeric(seconds)*1000));}
function setMetric(id, ringId, value) {
  const val=Math.min(100, Math.max(0,numeric(value)));
  const node=$(id); node.textContent='';
  node.append(document.createTextNode(val.toFixed(1)));
  const suffix=document.createElement('small'); suffix.textContent='%'; node.append(suffix);
  $(ringId).style.setProperty('--value',String(val));
}
function markConnection(connected) {
  $('connection-pill').classList.toggle('offline',!connected);
  setText('connection-text',connected ? 'SYSTEM ONLINE' : 'CONNECTION LOST');
}
function renderStatus(data) {
  if (!data || !data.sample) return;
  const s=data.sample, m=data.system||{};
  setMetric('metric-cpu','ring-cpu',s.cpu);
  setMetric('metric-memory','ring-memory',s.memory);
  setMetric('metric-disk','ring-disk',s.disk);
  const score=Number.isFinite(Number(data.score)) ? numeric(data.score) : 0;
  const scoreNode=$('metric-score'); scoreNode.textContent=String(Math.round(score));
  const suffix=document.createElement('small'); suffix.textContent='/100'; scoreNode.append(suffix);
  setText('cpu-note',numeric(s.cpu)>=85?'High processor usage':'Normal utilization');
  setText('memory-note',numeric(s.memory)>=90?'Memory pressure detected':'Memory allocation');
  setText('disk-note',numeric(s.disk)>=90?'Low disk space':'Root filesystem usage');
  const health=score>=85?'OPTIMAL':score>=65?'FAIR':'ATTENTION';
  setText('health-status',health);
  setText('health-note',s.anomaly?'Anomaly signal active':'System monitoring active');
  $('health-status').style.color=score>=85?'#65e7b5':score>=65?'#f5c979':'#f77f94';
  setText('sidebar-host',m.host||'Unknown host');
  setText('info-host',m.host||'--');
  setText('info-os',shortOS(m.os));
  setText('info-kernel',m.kernel||'--');
  setText('info-cores',m.cpu_cores??'--');
  setText('info-uptime',formatUptime(m.uptime_seconds));
  setText('info-network',`${numeric(s.rx_kbs).toFixed(1)} / ${numeric(s.tx_kbs).toFixed(1)} KB/s`);
  renderProcesses(data.processes||[]);
  renderRecommendations(data.recommendations||[]);
}
function renderProcesses(items){
  const tbody=$('process-table'); tbody.replaceChildren();
  if(!items.length){const tr=document.createElement('tr'), td=document.createElement('td');td.colSpan=4;td.className='empty';td.textContent='No visible processes.';tr.append(td);tbody.append(tr);return;}
  for(const process of items){
    const tr=document.createElement('tr');
    const nameTd=document.createElement('td');
    const icon=document.createElement('span'); icon.className='process-avatar';icon.textContent='⌘';
    nameTd.append(icon,document.createTextNode(String(process.name||'unknown')));
    const pid=document.createElement('td');pid.textContent=String(process.pid);
    const cpu=document.createElement('td');const cpuPill=document.createElement('span');cpuPill.className='usage-pill';cpuPill.textContent=percent(process.cpu);cpu.append(cpuPill);
    const memory=document.createElement('td');memory.textContent=percent(process.memory);
    tr.append(nameTd,pid,cpu,memory);tbody.append(tr);
  }
}
function renderRecommendations(items){
  const target=$('recommendations');target.replaceChildren();
  items.slice(0,4).forEach((item,index)=>{
    const outer=document.createElement('div');outer.className='recommendation';
    const num=document.createElement('span');num.className='insight-index';num.textContent=String(index+1).padStart(2,'0');
    const paragraph=document.createElement('p');paragraph.textContent=String(item);
    outer.append(num,paragraph);target.append(outer);
  });
}
function makeLine(x1,y1,x2,y2){
  const line=document.createElementNS(svgNS,'line');
  for(const [k,v] of Object.entries({x1,y1,x2,y2,stroke:'#28384e','stroke-width':1,'stroke-dasharray':'3 7'}))line.setAttribute(k,String(v));
  return line;
}
function pointsFor(rows,key){
  return rows.map((r,i)=>{
    const x=(i/(Math.max(1,rows.length-1)))*820;
    const y=240-Math.max(0,Math.min(100,numeric(r[key])))*2.4;
    return [x.toFixed(2),y.toFixed(2)];
  });
}
function renderHistory(samples){
  const rows=(samples||[]).slice(-60);
  const grid=$('chart-grid');grid.replaceChildren();
  [0,60,120,180,240].forEach(y=>grid.append(makeLine(0,y,820,y)));
  for(const key of ['cpu','memory']){
    const coords=pointsFor(rows,key);
    $(key+'-line').setAttribute('points',coords.map(p=>p.join(',')).join(' '));
    if(key==='cpu')$('cpu-area').setAttribute('d',coords.length?'M '+coords.map(p=>p.join(' ')).join(' L ')+' L 820 240 L 0 240 Z':'');
  }
  setText('chart-range',rows.length?`${rows.length} readings • latest ${niceTime(rows[rows.length-1].ts)}`:'Waiting for telemetry samples');
  setText('chart-peak',rows.length?`CPU peak: ${Math.max(...rows.map(s=>numeric(s.cpu))).toFixed(1)}%`:'CPU peak: --');
}
function renderAlerts(alerts){
  const target=$('alerts-list');target.replaceChildren();
  if(!alerts?.length){const empty=document.createElement('div');empty.className='empty-state';empty.textContent='No anomaly events recorded. All clear so far.';target.append(empty);return;}
  for(const item of alerts.slice(0,6)){
    const outer=document.createElement('div');outer.className='alert-item '+(item.severity==='critical'?'critical':'warning');
    const icon=document.createElement('span');icon.className='alert-icon';icon.textContent=item.severity==='critical'?'!':'⚑';
    const body=document.createElement('div');body.className='alert-body';
    const title=document.createElement('div');title.className='alert-title';title.textContent=item.title;
    const desc=document.createElement('div');desc.className='alert-detail';desc.textContent=item.detail;
    const time=document.createElement('span');time.className='alert-time';time.textContent=niceTime(item.ts);
    body.append(title,desc);outer.append(icon,body,time);target.append(outer);
  }
}
async function fetchJSON(path, options){
  const response=await fetch(path,{cache:'no-store',...options});
  if(!response.ok)throw new Error(`HTTP ${response.status} on ${path}`);
  return response.json();
}
let refreshBusy=false;
async function refresh(){
  if(refreshBusy)return;
  refreshBusy=true;
  try{
    const [status,history,events]=await Promise.all([fetchJSON('/api/status'),fetchJSON('/api/history?limit=60'),fetchJSON('/api/alerts')]);
    renderStatus(status);renderHistory(history.samples);renderAlerts(events.alerts);
    markConnection(true);
  }catch(error){console.warn('LinuxGuard refresh failed:',error);markConnection(false);}
  finally{refreshBusy=false;}
}
async function runScan(){
  const button=$('run-scan');button.disabled=true;button.textContent='Scanning...';
  try{
    const result=await fetchJSON('/api/security-scan',{method:'POST'});
    setText('ssh-failures',result.ssh_failures_last_hour===null?'N/A':result.ssh_failures_last_hour);
    setText('ssh-note',result.ssh_note);
    setText('all-listeners',result.all_interface_count);
    setText('ports-note',result.port_access_limited?'Some ports may be hidden by permissions':`${(result.listeners||[]).length} listener(s) visible`);
    const list=$('scan-findings');list.replaceChildren();
    for(const finding of result.findings||[]){const li=document.createElement('li');li.textContent=finding;list.append(li);}
    await refresh();
  }catch(error){
    const list=$('scan-findings');list.replaceChildren();const li=document.createElement('li');li.textContent=`Scan failed: ${error.message}`;list.append(li);
  }finally{button.disabled=false;button.textContent='↻ Run scan';}
}
function updateClock(){setText('clock-label',new Intl.DateTimeFormat(undefined,{weekday:'short',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date()));}
function init(){
  updateClock();setInterval(updateClock,30000);
  $('run-scan').addEventListener('click',runScan);
  document.querySelectorAll('.nav-link').forEach(link=>link.addEventListener('click',()=>{
    document.querySelectorAll('.nav-link').forEach(item=>item.classList.remove('active'));
    link.classList.add('active');
  }));
  refresh();setInterval(refresh,5000);
}
window.addEventListener('DOMContentLoaded',init);
