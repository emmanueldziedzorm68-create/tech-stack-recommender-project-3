// Real Chromium checks and screenshots, using its local debugging protocol.
const {spawn} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');
const browser = process.env.AUDIT_BROWSER || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const out = path.resolve('evidence'); fs.mkdirSync(out,{recursive:true});
const child = spawn(browser, ['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
    '--remote-debugging-port=9333','--user-data-dir='+path.resolve('.browser-audit'),'about:blank'],
    {windowsHide:true,stdio:'ignore'});
let socket; let launchError;
const deadline=setTimeout(()=>{console.error('Browser audit timed out.');child.kill();process.exit(1);},30000);
child.on('error', e => {launchError = e;});
const pause = ms => new Promise(r=>setTimeout(r,ms));
(async()=>{
    let targets;
    for(let i=0;i<60;i++) {
        if(launchError) throw launchError;
        try {targets=await (await fetch('http://127.0.0.1:9333/json')).json();break;} catch {await pause(250);}
    }
    if(!targets)throw Error('Browser debugging endpoint did not start.');
    console.log('Browser endpoint ready.');
    socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
    await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
    console.log('Browser debugging connected.');
    let id=0; const pending=new Map();const errors=[];
    socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);if(m.error)p.reject(Error(m.error.message));else p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params);};
    function call(method,params={}){return new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>{pending.delete(n);reject(Error('Timed out: '+method));},8000);pending.set(n,{resolve:value=>{clearTimeout(timer);resolve(value);},reject:error=>{clearTimeout(timer);reject(error);}});socket.send(JSON.stringify({id:n,method,params}));});}
    async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
    async function screenshot(name){const m=await call('Page.getLayoutMetrics');const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:m.cssContentSize.width,height:m.cssContentSize.height,scale:1}});fs.writeFileSync(path.join(out,name),Buffer.from(r.data,'base64'));}
    async function submit(skills,goals=''){await evaluate(`document.querySelector('#skills').value=${JSON.stringify(skills)};document.querySelector('#goals').value=${JSON.stringify(goals)};document.querySelector('#submit').click();`);}
    await call('Runtime.enable');await call('Page.enable');
    await call('Emulation.setDeviceMetricsOverride',{width:1365,height:1000,deviceScaleFactor:1,mobile:false});
    await call('Page.navigate',{url:pathToFileURL(path.resolve('index.html')).href});
    for(let i=0;i<40;i++){if(await evaluate(`!!document.querySelector('#vocabulary') && document.querySelector('#vocabulary').textContent.includes('python')`))break;await pause(100);}
    assert(await evaluate(`document.querySelector('#vocabulary').textContent.includes('python')`));
    await submit('HTML, CSS, React');
    assert.equal(await evaluate(`document.querySelectorAll('.card').length`),3);
    assert.equal(await evaluate(`document.querySelector('.card h3').textContent`),'Full Stack Developer');
    await screenshot('01-web-desktop.png');
    await submit('Python, Cloud Computing, Automation','Machine Learning');
    assert.match(await evaluate(`document.querySelector('#status').textContent`),/career-goal/);
    await screenshot('02-career-goals.png');
    await submit('Python');assert.match(await evaluate(`document.querySelector('#status').textContent`),/at least three/);
    await submit('Python, cloud, cloud computing');assert.match(await evaluate(`document.querySelector('#status').textContent`),/at least three/);
    await submit('pottery, baking, knitting');assert.match(await evaluate(`document.querySelector('#status').textContent`),/No matching roles/);
    await screenshot('03-no-matches.png');
    await submit('Python, pottery, baking');assert.match(await evaluate(`document.querySelector('#status').textContent`),/Fewer than three/);
    await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
    await submit('HTML, CSS, React');
    assert(await evaluate(`document.documentElement.scrollWidth <= window.innerWidth`));
    await screenshot('04-web-mobile.png');
    assert.equal(errors.length,0);
    const summary={browser:await call('Browser.getVersion'),checks:['standalone file loads catalogue','web skills return three roles','career goals affect profile','insufficient input rejected','duplicate aliases rejected','unknown inputs show no-match guidance','partial vocabulary warning','mobile width has no horizontal overflow','no JavaScript runtime exceptions'],screenshots:fs.readdirSync(out).filter(n=>n.endsWith('.png'))};
    fs.writeFileSync(path.join(out,'browser-checks.json'),JSON.stringify(summary,null,2));
    console.log(JSON.stringify(summary,null,2));
    await call('Browser.close');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(deadline);if(socket)socket.close();child.kill();});
