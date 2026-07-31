#!/usr/bin/env python3
"""
  NEP TUNNEL  ·  Roblox Local Test :O
  ────────────────────────────────────────────────────────
  Host mode   → launches Studio server, writes SESSION_INFO.txt,
                copies join command to clipboard.
  Join mode   → UDP proxy (localhost → remote) then Studio client.

  Platforms: Windows · macOS · Linux (Vinegar / Flatpak)

  Requirements:
      pip install pillow customtkinter
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
import socket, threading, time, subprocess, uuid, math, random, atexit
import platform, os, glob, shutil, json
from io import BytesIO
import urllib.request
import tkinter.font as tkfont

# ═══════════════════════════════════════════════════════════════════
#  PLATFORM / DPI
# ═══════════════════════════════════════════════════════════════════
_SYS = platform.system()

if _SYS == 'Windows':
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('nep.tunnel.app')
    except Exception:
        try: windll.user32.SetProcessDPIAware()
        except Exception: pass

# ═══════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
USER_ID     = '<ur user id here>'
STATIC_PORT = '55555'
TUNNEL_ADDR = '<[Address:Port] here>'

import sys
PROXY_PORT  = 55555
BG_IMG_URL  = 'https://gaming-cdn.com/img/products/1756/pcover/1756.jpg?v=1649173756'
LOGO_URL    = 'https://i.imgur.com/68Bdv5u_d.webp?maxwidth=760&fidelity=grand'

if getattr(sys, 'frozen', False):
    _SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(_SCRIPT_DIR, 'nep_config.json')
LOG_FILE    = os.path.join(_SCRIPT_DIR, 'SESSION_INFO.txt')

BUNDLED_MAPS = []
def _init_bundled_assets():
    global BUNDLED_MAPS
    bundled = ['MapsforNepfile.rbxm', 'CleanedAnimsNepFile.rbxm']
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        source_dir = sys._MEIPASS
    else:
        source_dir = os.path.dirname(os.path.abspath(__file__))
    
    assets_dir = os.path.join(_SCRIPT_DIR, 'bundled_assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    for f in bundled:
        src = os.path.join(source_dir, f)
        dst = os.path.join(assets_dir, f)
        if os.path.isfile(src):
            try:
                if not os.path.isfile(dst) or os.path.getsize(src) != os.path.getsize(dst):
                    shutil.copy2(src, dst)
                BUNDLED_MAPS.append(dst)
            except Exception:
                pass

_init_bundled_assets()

def load_config() -> dict:
    defaults = {'uid': USER_ID, 'port': STATIC_PORT,
                'addr': TUNNEL_ADDR, 'studio': '', 'map': '',
                'saved_maps': []}
    try:
        with open(CONFIG_FILE, 'r') as f:
            defaults.update(json.load(f))
    except Exception:
        pass
        
    # Inject bundled maps so they are always available
    for p in BUNDLED_MAPS:
        if p not in defaults['saved_maps']:
            defaults['saved_maps'].insert(0, p)
            
    return defaults

def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════════════════════
BG     = '#08040f'
CARD   = '#130b22'
CARD2  = '#1c1035'
BORD   = '#3a1a68'
ACC    = '#8b5cf6'
GLOW   = '#c4b5fd'
MOON_C = '#f5f0ff'
TEXT   = '#f0e6ff'
MUTE   = '#8b7aaa'
OK     = '#10b981'
ERR    = '#ef4444'
WARN   = '#f59e0b'
BLUE   = '#6366f1'
TEAL   = '#14b8a6'

# ═══════════════════════════════════════════════════════════════════
#  WINDOW GEOMETRY
# ═══════════════════════════════════════════════════════════════════
W, H     = 720, 660
MIN_W    = 580
MIN_H    = 520
BANNER_H = 140
SBAR_H   = 34

# ═══════════════════════════════════════════════════════════════════
#  FONTS
# ═══════════════════════════════════════════════════════════════════
_FF = ('Segoe UI'      if _SYS == 'Windows'
       else 'Helvetica Neue' if _SYS == 'Darwin'
       else 'DejaVu Sans')
_FM = ('Consolas'      if _SYS == 'Windows'
       else 'Menlo'    if _SYS == 'Darwin'
       else 'DejaVu Sans Mono')

FT = (_FF, 22, 'bold')
FH = (_FF, 15, 'bold')
FL = (_FF, 13, 'bold')
FB = (_FF, 12)
FS = (_FF, 10)
FC = (_FM, 10)

# ═══════════════════════════════════════════════════════════════════
#  PROXY STATE
# ═══════════════════════════════════════════════════════════════════
_prx_running = threading.Event()
_prx_stopped = threading.Event()
_prx_socks: list = []
_prx_lock   = threading.Lock()
_prx_thread = None

# ═══════════════════════════════════════════════════════════════════
#  COLOUR HELPERS
# ═══════════════════════════════════════════════════════════════════
def hex_lerp(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    ar, ag, ab = int(a[1:3],16), int(a[3:5],16), int(a[5:7],16)
    br, bg, bb = int(b[1:3],16), int(b[3:5],16), int(b[5:7],16)
    return (f'#{int(ar+(br-ar)*t):02x}'
            f'{int(ag+(bg-ag)*t):02x}'
            f'{int(ab+(bb-ab)*t):02x}')

def ts() -> str:       return time.strftime('%H:%M:%S')
def gen_guid() -> str: return str(uuid.uuid4()).upper()

# ═══════════════════════════════════════════════════════════════════
#  BACKGROUND / LOGO
# ═══════════════════════════════════════════════════════════════════
_bg_raw:   Image.Image | None = None
_logo_raw: Image.Image | None = None

def fetch_bg() -> None:
    global _bg_raw
    try:
        req = urllib.request.Request(BG_IMG_URL, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as r:
            _bg_raw = Image.open(BytesIO(r.read())).convert('RGB')
    except Exception:
        _bg_raw = None

def fetch_logo() -> None:
    global _logo_raw
    try:
        req = urllib.request.Request(LOGO_URL, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as r:
            img = Image.open(BytesIO(r.read())).convert('RGBA')
        s = min(img.size)
        img = img.crop(((img.width-s)//2,(img.height-s)//2,
                         (img.width+s)//2,(img.height+s)//2)).resize((256,256),Image.LANCZOS)
        mask = Image.new('L',(256,256),0)
        ImageDraw.Draw(mask).ellipse([0,0,255,255],fill=255)
        img.putalpha(mask)
        _logo_raw = img
    except Exception:
        _logo_raw = None

def make_bg(w: int, h: int) -> ImageTk.PhotoImage:
    w, h = max(1,w), max(1,h)
    if _bg_raw is not None:
        iw,ih = _bg_raw.size
        sc = max(w/iw, h/ih)
        nw,nh = max(1,int(iw*sc)), max(1,int(ih*sc))
        img = _bg_raw.resize((nw,nh),Image.LANCZOS)
        img = img.crop(((nw-w)//2,(nh-h)//2,(nw+w)//2,(nh+h)//2))
    else:
        img = Image.new('RGB',(w,h),(8,4,15))
    base = img.convert('RGBA')
    base = Image.alpha_composite(base, Image.new('RGBA',(w,h),(5,2,10,210)))
    base = Image.alpha_composite(base, Image.new('RGBA',(w,h),(65,20,120,45)))
    return ImageTk.PhotoImage(base.convert('RGB'))

# ═══════════════════════════════════════════════════════════════════
#  STUDIO DETECTION
# ═══════════════════════════════════════════════════════════════════
VINEGAR = '__VINEGAR__'

def get_studio_path() -> str:
    if _SYS == 'Windows':
        base = os.environ.get('LOCALAPPDATA','')
        pat  = os.path.join(base,'Roblox','Versions','*','RobloxStudioBeta.exe')
        hits = sorted(glob.glob(pat))
        if hits: return hits[-1]
        alt = os.path.join(base,'Roblox','RobloxStudioBeta.exe')
        return alt if os.path.exists(alt) else ''
    elif _SYS == 'Darwin':
        for p in ['/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio',
                  os.path.expanduser('~/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio')]:
            if os.path.exists(p): return p
        return ''
    elif _SYS == 'Linux':
        if shutil.which('flatpak'):
            try:
                r = subprocess.run(['flatpak','info','org.vinegarhq.Vinegar'],
                                   capture_output=True, timeout=5)
                if r.returncode == 0: return VINEGAR
            except Exception: pass
        return ''
    return ''

def _build_cmd(studio: str, args: list) -> list:
    if studio == VINEGAR:
        return ['flatpak','run','org.vinegarhq.Vinegar','studio','--'] + args
    return [studio] + args

def launch_server(studio, port, uid, pg, tg):
    subprocess.Popen(_build_cmd(studio,[
        '-task','StartServer','-placeId','0','-universeId','0','-placeVersion','1',
        '-port',port,'-creatorId',uid,'-creatorType','1',
        '-numTestServerPlayersUponStartup','1','-userid',uid,
        '-parentSessionGuid',pg,'-playTestSessionGuid',tg,'-instanceId','StudioServer',
    ]))

def launch_client(studio, server, port, pg, tg, inst='StudioPlayer_0'):
    subprocess.Popen(_build_cmd(studio,[
        '-task','StartClient','-placeId','0','-universeId','0','-placeVersion','1',
        '-server',server,'-port',str(port),
        '-parentSessionGuid',pg,'-playTestSessionGuid',tg,'-instanceId',inst,
    ]))

# ═══════════════════════════════════════════════════════════════════
#  MAP INJECTION  (rbxl  — copies into Studio runtime cache)
# ═══════════════════════════════════════════════════════════════════
def get_runtime_server_place() -> str:
    if _SYS == 'Windows':
        base = os.environ.get('LOCALAPPDATA', '')
        return os.path.join(base, 'Roblox', 'server.rbxl')
    elif _SYS == 'Darwin':
        return os.path.expanduser('~/Library/Application Support/Roblox/server.rbxl')
    elif _SYS == 'Linux':
        return os.path.expanduser('~/.var/app/org.vinegarhq.Vinegar/data/Roblox/server.rbxl')
    return ''

def inject_map(map_path: str) -> bool:
    if not map_path or not os.path.exists(map_path):
        return False
    target = get_runtime_server_place()
    if not target:
        return False
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target):
            try: os.remove(target)
            except Exception: pass
        shutil.copyfile(map_path, target)
        return True
    except Exception as e:
        print(f"[map] Failed to inject: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════
#  RBXM BRIDGE SERVER  (inline — no separate file needed)
#  Plugin polls GET /poll → {"status":"ready","name":...,"staging_dir":...}
#  Launcher POSTs {"path":...} to /queue to stage a file
# ═══════════════════════════════════════════════════════════════════
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer as _HTTPServer

BRIDGE_PORT    = 7878
_STAGING_DIR   = os.path.join(tempfile.gettempdir(), 'rbxm_bridge')
os.makedirs(_STAGING_DIR, exist_ok=True)

_bridge_pending: str | None = None   # staged filename or None
_bridge_lock    = threading.Lock()
_bridge_server: _HTTPServer | None = None
_bridge_running = False

class _BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass  # silence

    def _json(self, code: int, obj: dict):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        global _bridge_pending
        if self.path == '/poll':
            with _bridge_lock:
                if _bridge_pending is None:
                    self._json(200, {'status': 'idle'})
                else:
                    self._json(200, {
                        'status': 'ready',
                        'name': _bridge_pending,
                        'staging_dir': _STAGING_DIR,
                    })
        elif self.path == '/download':
            with _bridge_lock:
                fname = _bridge_pending
            if fname is None:
                self._json(404, {'error': 'no file pending'})
                return
            fpath = os.path.join(_STAGING_DIR, fname)
            if not os.path.isfile(fpath):
                self._json(404, {'error': 'staged file missing'})
                return
            try:
                with open(fpath, 'rb') as fh:
                    data = fh.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self._json(500, {'error': str(e)})
        else:
            self._json(404, {'error': 'not found'})

    def do_POST(self):
        global _bridge_pending
        length = int(self.headers.get('Content-Length', 0))
        body   = json.loads(self.rfile.read(length))

        if self.path == '/queue':
            src = body.get('path', '')
            if not os.path.isfile(src):
                self._json(400, {'error': f'file not found: {src}'}); return
            dst = os.path.join(_STAGING_DIR, os.path.basename(src))
            shutil.copy2(src, dst)
            with _bridge_lock:
                _bridge_pending = os.path.basename(dst)
            self._json(200, {'status': 'queued', 'staged': dst})

        elif self.path == '/clear':
            with _bridge_lock:
                _bridge_pending = None
            self._json(200, {'status': 'cleared'})
        else:
            self._json(404, {'error': 'not found'})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def _start_bridge():
    global _bridge_server, _bridge_running
    if _bridge_running: return True
    try:
        _bridge_server = _HTTPServer(('127.0.0.1', BRIDGE_PORT), _BridgeHandler)
        t = threading.Thread(target=_bridge_server.serve_forever, daemon=True)
        t.start()
        _bridge_running = True
        return True
    except OSError:
        return False   # port already in use (maybe from a previous run)

def _queue_rbxm(path: str) -> tuple[bool, str]:
    """Copy rbxm to staging dir and set it as pending. Returns (ok, message)."""
    if not os.path.isfile(path):
        return False, 'File not found'
    _start_bridge()
    dst = os.path.join(_STAGING_DIR, os.path.basename(path))
    try:
        shutil.copy2(path, dst)
    except Exception as e:
        return False, str(e)
    with _bridge_lock:
        global _bridge_pending
        _bridge_pending = os.path.basename(dst)
    return True, os.path.basename(dst)

# ═══════════════════════════════════════════════════════════════════
#  SESSION LOG
# ═══════════════════════════════════════════════════════════════════
def write_session_log(pg,tg,tunnel_addr,port,uid) -> str:
    host,dp = (tunnel_addr.rsplit(':',1) if ':' in tunnel_addr
               else (tunnel_addr, port))
    win_cmd = (f'powershell -ExecutionPolicy Bypass -Command "'
               f'$p = Get-ChildItem -Path $env:LOCALAPPDATA\\Roblox\\Versions '
               f'-Filter RobloxStudioBeta.exe -Recurse | Select-Object -First 1 '
               f'-ExpandProperty FullName; Start-Process -FilePath $p -ArgumentList '
               f'\'-task StartClient -placeId 0 -universeId 0 -placeVersion 0 '
               f'-server {host} -port {dp} -parentSessionGuid {pg} '
               f'-playTestSessionGuid {tg} -instanceId StudioPlayer_0\'"')
    mac_cmd = (f'"/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio" '
               f'-task StartClient -placeId 0 -universeId 0 -placeVersion 0 '
               f'-server {host} -port {dp} -parentSessionGuid {pg} '
               f'-playTestSessionGuid {tg} -instanceId StudioPlayer_0')
    lin_cmd = (f'flatpak run org.vinegarhq.Vinegar studio -- '
               f'-task StartClient -placeId 0 -universeId 0 -placeVersion 0 '
               f'-server {host} -port {dp} -parentSessionGuid {pg} '
               f'-playTestSessionGuid {tg} -instanceId StudioPlayer_0')
    lines = ['╔'+'═'*56+'╗','║  NEP TUNNEL  ·  ROBLOX STUDIO SESSION LOG            ║',
             '╚'+'═'*56+'╝',f'Date       : {time.strftime("%Y-%m-%d %H:%M:%S")}',
             f'User ID    : {uid}',f'Address    : {tunnel_addr}',
             f'Server Local Port: {port}','','── WINDOWS (Command Prompt) ──',win_cmd,'',
             '── MAC (Terminal) ──',mac_cmd,'','── LINUX / VINEGAR ──',lin_cmd,'','═'*58]
    try:
        with open(LOG_FILE,'w',encoding='utf-8') as fh: fh.write('\n'.join(lines))
    except Exception: pass
    return win_cmd

# ═══════════════════════════════════════════════════════════════════
#  UDP PROXY
# ═══════════════════════════════════════════════════════════════════
def start_proxy(dst_host: str, dst_port: int) -> bool:
    global _prx_thread
    if _prx_running.is_set(): stop_proxy()
    _prx_running.set(); _prx_stopped.clear()

    def _relay(rs, ls, ca):
        while _prx_running.is_set():
            try:
                d,_ = rs.recvfrom(65536); ls.sendto(d,ca)
            except socket.timeout: continue
            except OSError: break
        try: rs.close()
        except Exception: pass

    def worker():
        try:
            ip = socket.gethostbyname(dst_host)
            s  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', PROXY_PORT)); s.settimeout(1.0)
            with _prx_lock: _prx_socks.append(s)
            _prx_stopped.set(); sess: dict = {}
            while _prx_running.is_set():
                try: data, addr = s.recvfrom(65536)
                except socket.timeout: continue
                except OSError: break
                if addr not in sess:
                    r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    r.settimeout(1.0)
                    with _prx_lock: _prx_socks.append(r)
                    sess[addr] = r
                    threading.Thread(target=_relay,args=(r,s,addr),daemon=True).start()
                try: sess[addr].sendto(data,(ip,dst_port))
                except Exception: pass
        except Exception as e: print(f'[proxy] {e}')
        finally:
            with _prx_lock:
                for sk in list(_prx_socks):
                    try: sk.close()
                    except Exception: pass
            _prx_socks.clear(); _prx_stopped.set()

    _prx_thread = threading.Thread(target=worker, daemon=True)
    _prx_thread.start()
    return _prx_stopped.wait(timeout=3.0)

def stop_proxy(wait: bool = True):
    if not _prx_running.is_set(): return
    _prx_running.clear()
    with _prx_lock:
        for s in list(_prx_socks):
            try: s.close()
            except Exception: pass
    if _prx_thread and _prx_thread.is_alive() and wait:
        _prx_stopped.wait(timeout=2.0)

atexit.register(lambda: stop_proxy(wait=False))

# ═══════════════════════════════════════════════════════════════════
#  TUNNEL WARM-UP
# ═══════════════════════════════════════════════════════════════════
WARM_PACKETS  = 8
WARM_INTERVAL = 0.10

def warm_tunnel(proxy_port: int, packets: int = WARM_PACKETS,
                interval: float = WARM_INTERVAL) -> int:
    sent = 0
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.3)
        for _ in range(packets):
            if not _prx_running.is_set(): break
            payload = bytes([0xFF,0x00]) + os.urandom(random.randint(6,20))
            try: sock.sendto(payload,('127.0.0.1',proxy_port)); sent += 1
            except OSError: break
            time.sleep(interval)
    except Exception: pass
    finally:
        if sock:
            try: sock.close()
            except Exception: pass
    return sent

# ═══════════════════════════════════════════════════════════════════
#  ECHO TEST PROTOCOL
# ═══════════════════════════════════════════════════════════════════
ECHO_REQ  = b'NEP_TEST\x00'
ECHO_RESP = b'NEP_ECHO\x00'

class EchoServer:
    def __init__(self):
        self._sock:   socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop    = threading.Event()
        self.port: int = 0
        self.echoed: int = 0
        self.clients: set = set()
        self.log_fn = None

    def start(self, port: int, log_fn=None) -> bool:
        self._stop.clear()
        self.port    = port
        self.echoed  = 0
        self.clients = set()
        self.log_fn  = log_fn
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind(('0.0.0.0', port))
            self._sock.settimeout(0.5)
        except OSError as e:
            if self.log_fn:
                self.log_fn(f'✗ Could not bind to port {port}.', 'err')
                self.log_fn('  Is Roblox Studio already running? Close it and try again.', 'err')
                self.log_fn(f'  OS Error: {e}', 'dim')
            return False
        except Exception as e:
            if self.log_fn:
                self.log_fn(f'✗ Unexpected error binding port: {e}', 'err')
            return False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._stop.set()
        if self._sock:
            try: self._sock.close()
            except Exception: pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._sock = None

    def running(self) -> bool:
        return not self._stop.is_set() and self._thread is not None and self._thread.is_alive()

    def _run(self):
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(512)
            except socket.timeout:
                continue
            except OSError:
                break
            if data.startswith(ECHO_REQ):
                nonce = data[len(ECHO_REQ):]
                try:
                    self._sock.sendto(ECHO_RESP + nonce, addr)
                    self.echoed += 1
                    self.clients.add(addr[0])
                except OSError:
                    pass

_echo_server = EchoServer()


def run_echo_test(log_fn, tunnel_host: str, tunnel_port: int, max_successes: int = 3, timeout: float = 10.0):
    log_fn('─── Echo Round-Trip Test ───', 'info')
    log_fn(f'Target: {tunnel_host}:{tunnel_port}', 'dim')
    log_fn('Sending probes directly to tunnel (bypassing local proxy)...', 'warn')
    log_fn('Note: Tunnels can take a few seconds to "wake up". Please wait...', 'dim')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    sent = {}; received = 0; rtts = []
    start_time = time.perf_counter()
    probe_interval = 0.4; next_probe_time = start_time; icmp_reject = False
    while time.perf_counter() - start_time < timeout and received < max_successes:
        now = time.perf_counter()
        if now >= next_probe_time:
            nonce = os.urandom(8)
            try:
                sock.sendto(ECHO_REQ + nonce, (tunnel_host, tunnel_port))
                sent[nonce] = now; next_probe_time = now + probe_interval
            except Exception as e:
                log_fn(f'✗ Send error: {e}', 'err'); break
        try:
            data, _ = sock.recvfrom(512)
            if data.startswith(ECHO_RESP):
                n = data[len(ECHO_RESP):]
                if n in sent:
                    rtt = (time.perf_counter() - sent[n]) * 1000
                    rtts.append(rtt); received += 1
                    if received == 1:
                        log_fn(f'✓ First echo received! ({rtt:.0f} ms) Tunnel is waking up...', 'ok')
                    elif received == 2:
                        log_fn(f'✓ Second echo received. Connection stabilizing...', 'ok')
        except socket.timeout: pass
        except ConnectionResetError:
            log_fn('✗ ICMP Port Unreachable. Tunnel endpoint is actively rejecting.', 'err')
            icmp_reject = True; break
    try: sock.close()
    except Exception: pass
    log_fn('───────────────────────', 'dim')
    if received >= max_successes:
        avg = sum(rtts) / len(rtts)
        mn, mx = min(rtts), max(rtts)
        log_fn(f'✓ SUCCESS: {received} echoes received. Tunnel is LIVE and stable.', 'ok')
        log_fn(f'  RTT: avg {avg:.0f} ms | min {mn:.0f} ms | max {mx:.0f} ms', 'ok')
        log_fn('  You can now safely start your session.', 'info')
    elif received > 0:
        avg = sum(rtts) / len(rtts)
        log_fn(f'△ PARTIAL: {received}/{max_successes} echoes. Tunnel is unstable.', 'warn')
        log_fn(f'  RTT: avg {avg:.0f} ms', 'warn')
        log_fn('  You might experience lag or disconnects in-game.', 'warn')
    elif icmp_reject:
        log_fn('✗ FAILED: Tunnel port is closed or host firewall is blocking it.', 'err')
    else:
        log_fn('✗ FAILED: No echoes received within timeout.', 'err')
        log_fn('  Possible causes:', 'dim')
        log_fn('  1. Host has not started the Echo Server yet.', 'dim')
        log_fn('  2. Tunnel is down or misconfigured.', 'dim')
        log_fn('  3. Host firewall is blocking the tunnel agent.', 'dim')


TEST_PROBE_COUNT   = 5
TEST_PROBE_TIMEOUT = 2.5

def _icmp_ping(host: str) -> tuple:
    try:
        if _SYS == 'Windows':
            cmd = ['ping','-n','1','-w','2000', host]
        else:
            cmd = ['ping','-c','1','-W','2', host]
        t0 = time.perf_counter()
        r  = subprocess.run(cmd, capture_output=True, timeout=6)
        rtt = (time.perf_counter() - t0) * 1000
        return r.returncode == 0, rtt
    except Exception:
        return False, -1


def run_connectivity_test(host: str, port: int, log_fn,
                          is_host_side: bool = False,
                          local_server_port: int = 0):
    log_fn('─── Connectivity Test ───', 'info')
    log_fn('  (For full tunnel verification, use Echo Test)', 'dim')
    passed, warned, failed = 0, 0, 0
    log_fn(f'[1/4]  Resolving  {host} …', 'warn')
    try:
        ip = socket.gethostbyname(host)
        log_fn(f'  ✓  DNS OK   {host} → {ip}', 'ok')
        log_fn(f'       (this only means the hostname exists — not that your tunnel is active)', 'dim')
        passed += 1
    except socket.gaierror as e:
        log_fn(f'  ✗  DNS FAILED — {e}', 'err'); failed += 1
        _ct_summary(log_fn, passed, warned, failed)
        log_fn('───────────────────────', 'dim'); return
    log_fn(f'[2/4]  ICMP ping → {ip} …', 'warn')
    alive, ping_rtt = _icmp_ping(ip)
    if alive:
        log_fn(f'  ✓  Relay server is reachable  (ping ≈ {ping_rtt:.0f} ms)', 'ok')
        log_fn(f'       (this proves the relay IP is up — not that your tunnel is forwarding)', 'dim')
        passed += 1
    else:
        log_fn(f'  ✗  ICMP ping failed — {ip} unreachable', 'err')
        log_fn(f'    → Tunnel address may be wrong, or relay is offline', 'err')
        log_fn(f'    → (Some relays block ICMP — continue to check UDP)', 'warn')
        warned += 1
    if is_host_side:
        lp = local_server_port or port
        log_fn(f'[3/4]  Checking local Studio port {lp} …', 'warn')
        pb = None
        try:
            pb = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            pb.settimeout(0.5)
            pb.sendto(b'\xff\x00\x00', ('127.0.0.1', lp))
            try: pb.recvfrom(64)
            except socket.timeout: pass
            log_fn(f'  ✓  Port {lp} accepts UDP (no ICMP reject)', 'ok'); passed += 1
        except ConnectionResetError:
            log_fn(f'  ✗  Port {lp} ICMP unreachable — Studio not running or OS firewall blocking it', 'err'); failed += 1
        except OSError as e:
            log_fn(f'  △  Port check inconclusive — {e}', 'warn'); warned += 1
        finally:
            if pb:
                try: pb.close()
                except Exception: pass
    else:
        log_fn(f'[3/4]  Checking local proxy on 127.0.0.1:{PROXY_PORT} …', 'warn')
        if _prx_running.is_set():
            log_fn(f'  ✓  Proxy active on port {PROXY_PORT}', 'ok'); passed += 1
        else:
            log_fn(f'  ✗  Proxy is NOT running — Connect first', 'err'); failed += 1
    target_ip   = ip         if is_host_side else '127.0.0.1'
    target_port = port       if is_host_side else PROXY_PORT
    log_fn(f'[4/4]  UDP probe burst → {target_ip}:{target_port} ({TEST_PROBE_COUNT} packets) …', 'warn')
    sent_ok, icmp_err = 0, False; pb2 = None
    try:
        pb2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pb2.settimeout(0.35)
        for i in range(TEST_PROBE_COUNT):
            payload = bytes([0xFF,0x00,0xAA,i&0xFF]) + os.urandom(12)
            try: pb2.sendto(payload,(target_ip,target_port)); sent_ok += 1
            except OSError: break
            try: pb2.recvfrom(64)
            except socket.timeout: pass
            except ConnectionResetError: icmp_err = True; break
            time.sleep(0.1)
    except Exception: pass
    finally:
        if pb2:
            try: pb2.close()
            except Exception: pass
    if icmp_err:
        log_fn(f'  ✗  ICMP Port Unreachable — port {target_port} is actively closed', 'err'); failed += 1
    elif sent_ok == TEST_PROBE_COUNT:
        log_fn(f'  ✓  {sent_ok}/{TEST_PROBE_COUNT} probes sent, no ICMP errors', 'ok')
        log_fn(f'  △  No reply expected here — use Echo Test to confirm end-to-end path', 'dim'); passed += 1
    else:
        log_fn(f'  ✗  Only {sent_ok}/{TEST_PROBE_COUNT} probes sent', 'err'); failed += 1
    _ct_summary(log_fn, passed, warned, failed)
    log_fn('───────────────────────', 'dim')

def _ct_summary(log_fn, passed, warned, failed):
    if failed:   verdict, tag = 'ISSUES DETECTED', 'err'
    elif warned: verdict, tag = 'PARTIALLY OK — check warnings', 'warn'
    else:        verdict, tag = 'ALL CLEAR', 'ok'
    log_fn(f'Result: {verdict}  ({passed} passed · {warned} warnings · {failed} failed)', tag)


# ═══════════════════════════════════════════════════════════════════
#  WIDGET HELPERS
# ═══════════════════════════════════════════════════════════════════
ctk.set_appearance_mode('dark')

def _parent_bg(parent) -> str:
    try: return str(parent.cget('bg'))
    except Exception:
        try: return str(parent.cget('fg_color'))
        except Exception: return BG

def styled_entry(parent, text: str='', width: int=260) -> ctk.CTkEntry:
    e = ctk.CTkEntry(parent, fg_color=CARD2, text_color=TEXT, font=FB,
                     width=width, corner_radius=8, border_color=BORD, border_width=1)
    if text: e.insert(0, text)
    return e

def card_frame(parent, padx: int=20, pady: int=16) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12,
                        border_color=BORD, border_width=1)

def log_box(parent, height: int=8) -> scrolledtext.ScrolledText:
    t = scrolledtext.ScrolledText(
        parent, bg='#060210', fg='#b39ddb', font=FC,
        insertbackground=GLOW, relief='flat', height=height, wrap='word',
        highlightthickness=1, highlightbackground=BORD, state='disabled')
    for tag, col in [('ok',OK),('err',ERR),('warn',WARN),('info',GLOW),('dim',MUTE)]:
        t.tag_config(tag, foreground=col)
    return t

def log_append(widget, msg: str, tag: str=''):
    def _do():
        try:
            if not widget.winfo_exists(): return
        except Exception: return
        widget.config(state='normal')
        widget.insert(tk.END, f'[{ts()}]  ', 'dim')
        widget.insert(tk.END, msg+'\n', tag)
        widget.see(tk.END)
        widget.config(state='disabled')
    widget.after(0, _do)

def divider(parent):
    tk.Frame(parent, bg=BORD, height=1).pack(fill='x', padx=20, pady=8)

# ═══════════════════════════════════════════════════════════════════
#  ICON FACTORY
# ═══════════════════════════════════════════════════════════════════
_icon_cache: dict = {}

def _make_icon(name: str, size: int=16, fg: str='#f0e6ff') -> ctk.CTkImage:
    key = (name, size, fg)
    if key in _icon_cache: return _icon_cache[key]
    s2 = size*2; r_,g_,b_ = int(fg[1:3],16),int(fg[3:5],16),int(fg[5:7],16)
    c = (r_,g_,b_,255)
    img = Image.new('RGBA',(s2,s2),(r_,g_,b_,0)); d = ImageDraw.Draw(img); m = s2
    if name == 'host':
        d.rectangle([m*2//8,m*3//8,m*6//8,m*7//8],outline=c,width=max(2,m//10))
        d.line([m//2,m*1//8,m//2,m*5//8],fill=c,width=max(2,m//10))
        d.polygon([(m*3//8,m*3//8),(m//2,m*1//8),(m*5//8,m*3//8)],fill=c)
    elif name == 'join':
        d.arc([m*1//8,m*2//8,m//2,m*6//8],90,270,fill=c,width=max(2,m//8))
        d.arc([m//2,m*2//8,m*7//8,m*6//8],270,90,fill=c,width=max(2,m//8))
        d.line([m*3//8,m//2,m*5//8,m//2],fill=c,width=max(2,m//10))
    elif name == 'play':
        d.polygon([(m*2//8,m*1//8),(m*7//8,m//2),(m*2//8,m*7//8)],fill=c)
    elif name == 'back':
        d.polygon([(m*6//8,m*2//8),(m*2//8,m//2),(m*6//8,m*6//8)],fill=c)
    elif name == 'stop':
        w = max(3,m//6)
        d.line([m*2//8,m*2//8,m*6//8,m*6//8],fill=c,width=w)
        d.line([m*6//8,m*2//8,m*2//8,m*6//8],fill=c,width=w)
    elif name == 'folder':
        d.rectangle([m*1//8,m*3//8,m*7//8,m*7//8],outline=c,width=max(2,m//10))
        d.rectangle([m*1//8,m*2//8,m*4//8,m*3//8],fill=c)
    elif name == 'test':
        bw = max(2,m//6)
        d.rectangle([m*1//8,m*5//8,m*1//8+bw,m*7//8],fill=c)
        d.rectangle([m*3//8,m*3//8,m*3//8+bw,m*7//8],fill=c)
        d.rectangle([m*5//8,m*1//8,m*5//8+bw,m*7//8],fill=c)
    elif name == 'echo':
        hw = max(2, m//8)
        d.polygon([(m*5//8,m*3//8),(m*7//8,m//2),(m*5//8,m*5//8)],fill=c)
        d.line([m*2//8,m//2,m*7//8,m//2],fill=c,width=hw)
        d.polygon([(m*3//8,m*2//8),(m*1//8,m//2),(m*3//8,m*6//8)],outline=c,width=hw)
    elif name == 'map':
        # Stylised map/grid icon: outer border + cross lines
        bw = max(2, m//10)
        d.rectangle([m*1//8, m*1//8, m*7//8, m*7//8], outline=c, width=bw)
        d.line([m//2, m*1//8, m//2, m*7//8], fill=c, width=bw)
        d.line([m*1//8, m//2, m*7//8, m//2], fill=c, width=bw)
        # Pin dot at top-right quadrant
        pr = max(2, m//8)
        px, py = m*5//8, m*3//8
        d.ellipse([px-pr, py-pr, px+pr, py+pr], fill=c)
    elif name == 'send':
        # Arrow pointing right-up (send/inject)
        hw = max(2, m//8)
        d.polygon([(m*2//8, m*6//8), (m*7//8, m*2//8), (m*6//8, m*7//8)], fill=c)
        d.polygon([(m*2//8, m*6//8), (m*7//8, m*2//8), (m*2//8, m*1//8)], fill=c)
    elif name == 'trash':
        bw = max(2, m//10)
        d.rectangle([m*2//8, m*3//8, m*6//8, m*7//8], outline=c, width=bw)
        d.line([m*1//8, m*3//8, m*7//8, m*3//8], fill=c, width=bw)
        d.line([m*3//8, m*2//8, m*5//8, m*2//8], fill=c, width=bw)
        d.line([m*3//8, m*5//8, m*3//8, m*6//8], fill=c, width=max(1, bw-1))
        d.line([m*5//8, m*5//8, m*5//8, m*6//8], fill=c, width=max(1, bw-1))
    img_sm = img.resize((size,size),Image.LANCZOS)
    ctkimg = ctk.CTkImage(light_image=img_sm, dark_image=img_sm, size=(size,size))
    _icon_cache[key] = ctkimg
    return ctkimg

def icon_btn(parent, text, icon_name, color, command, padx=18, pady=8, icon_size=20):
    icon = _make_icon(icon_name, icon_size, TEXT)
    return ctk.CTkButton(parent, text=text, image=icon, compound='left',
                         fg_color=color, hover_color=hex_lerp(color,'#ffffff',0.18),
                         text_color=TEXT, font=FL, corner_radius=12,
                         bg_color=_parent_bg(parent), command=command)

def draw_moon(canvas,cx,cy,r,bg_fill=BG):
    gids = []
    for i in range(4,0,-1):
        gr=r+i*7; gids.append(canvas.create_oval(cx-gr,cy-gr,cx+gr,cy+gr,fill='',outline=ACC,width=1))
    canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=MOON_C,outline=GLOW,width=1)
    so,sr=int(r*0.56),int(r*1.07)
    canvas.create_oval(cx+so-sr,cy-sr,cx+so+sr,cy+sr,fill=bg_fill,outline=bg_fill)
    for dx,dy,cr in [(-0.10,-0.21,0.09),(-0.32,0.13,0.065),(-0.06,0.28,0.055)]:
        canvas.create_oval(cx+dx*r*2-cr*r,cy+dy*r*2-cr*r,cx+dx*r*2+cr*r,cy+dy*r*2+cr*r,fill='#ece4ff',outline='')
    hx,hy,hr=cx-r*0.28,cy-r*0.33,r*0.13
    canvas.create_oval(hx-hr,hy-hr,hx+hr,hy+hr,fill='white',outline='')
    return gids

def animate_glow(canvas,gids,phase):
    if not canvas.winfo_exists(): return
    phase[0]+=0.038
    for i,gid in enumerate(gids):
        t=(math.sin(phase[0]+i*0.9)+1)/2; t*=max(0,0.55-i*0.12)
        try: canvas.itemconfig(gid,outline=hex_lerp(BG,ACC,t))
        except tk.TclError: return
    canvas.after(55,lambda: animate_glow(canvas,gids,phase))

# ═══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Nep Tunnel'); self.geometry(f'{W}x{H}')
        self.minsize(MIN_W,MIN_H); self.configure(bg=BG)
        self.protocol('WM_DELETE_WINDOW', self._quit)
        self.studio=''; self._page=None; self._sliding=False
        self._first_nav=True; self._bg_photo=None; self._banner_photo=None
        self._last_size=(0,0)

        self._cv=tk.Canvas(self,bg=BG,highlightthickness=0); self._cv.pack(fill='both',expand=True)
        self._bg_iid     = self._cv.create_image(0,0,anchor='nw',tags='bg')
        self._banner_iid = self._cv.create_image(0,0,anchor='nw',tags='bannerbg')
        self._rule_id    = self._cv.create_line(0,BANNER_H-1,W,BANNER_H-1,fill=BORD,width=1,tags='banner')
        self._cont=tk.Frame(self._cv,bg=BG); self._cont.pack_propagate(False)
        self._cont_wid=self._cv.create_window(0,BANNER_H,anchor='nw',window=self._cont,width=W,height=H-BANNER_H-SBAR_H)
        self._sbar=tk.Frame(self._cv,bg=CARD2)
        self._sbar_wid=self._cv.create_window(0,H-SBAR_H,anchor='nw',window=self._sbar,width=W,height=SBAR_H)
        self._status_var=tk.StringVar(value='Starting…')
        self._status_lbl=tk.Label(self._sbar,textvariable=self._status_var,bg=CARD2,fg=MUTE,font=FS,padx=14)
        self._status_lbl.pack(side='left',pady=9)
        self._redraw_banner(W)
        self.bind('<Configure>',self._on_configure)
        threading.Thread(target=self._async_boot,daemon=True).start()

    def _async_boot(self):
        fetch_bg(); fetch_logo()
        _start_bridge()   # start bridge server in background
        self.after(0,self._on_bg_loaded)

    def _on_bg_loaded(self):
        self.update_idletasks()
        w,h=self.winfo_width(),self.winfo_height()
        if w<10: w,h=W,H
        photo=make_bg(w,h); self._cv.itemconfig(self._bg_iid,image=photo); self._bg_photo=photo
        self._redraw_banner(w)
        if _logo_raw is not None:
            self._logo_photo=ImageTk.PhotoImage(_logo_raw); self.iconphoto(True,self._logo_photo)
        self._boot()

    def _on_configure(self,event):
        if event.widget is not self: return
        w,h=event.width,event.height
        if (w,h)==self._last_size: return
        self._last_size=(w,h)
        photo=make_bg(w,h); self._cv.itemconfig(self._bg_iid,image=photo); self._bg_photo=photo
        self._cv.coords(self._rule_id,0,BANNER_H-1,w,BANNER_H-1)
        self._redraw_banner(w)
        cont_h=max(1,h-BANNER_H-SBAR_H)
        self._cv.itemconfig(self._cont_wid,width=w,height=cont_h); self._cont.config(width=w,height=cont_h)
        self._cv.coords(self._sbar_wid,0,h-SBAR_H); self._cv.itemconfig(self._sbar_wid,width=w); self._sbar.config(width=w)
        if self._page and self._page.winfo_exists():
            self._page.place(x=0,y=0,width=w,height=cont_h)

    def _redraw_banner(self,w):
        self._cv.delete('bannertext')
        if _bg_raw is not None:
            iw,ih=_bg_raw.size; sc=max(w/iw,BANNER_H/ih)
            nw,nh=max(1,int(iw*sc)),max(1,int(ih*sc))
            bimg=_bg_raw.resize((nw,nh),Image.LANCZOS)
            x0=(nw-w)//2; y0=(nh-BANNER_H)//2
            bimg=bimg.crop((x0,y0,x0+w,y0+BANNER_H))
            ov=Image.new('RGBA',(w,BANNER_H),(8,4,15,140))
            bimg=Image.alpha_composite(bimg.convert('RGBA'),ov)
            gr=Image.new('RGBA',(w,BANNER_H),(0,0,0,0)); gd=ImageDraw.Draw(gr)
            for yi in range(BANNER_H-20,BANNER_H):
                a=int(180*((yi-(BANNER_H-20))/20)); gd.line([(0,yi),(w,yi)],fill=(8,4,15,a))
            bimg=Image.alpha_composite(bimg,gr)
            self._banner_photo=ImageTk.PhotoImage(bimg.convert('RGB'))
            self._cv.itemconfig(self._banner_iid,image=self._banner_photo)
        self._cv.create_text(24,BANNER_H//2-14,text='NEP TUNNEL',fill=TEXT,font=(_FF,17,'bold'),anchor='w',tags='bannertext')
        self._cv.create_text(26,BANNER_H//2+8,text='Roblox Studio  ·  Local Test',fill=MUTE,font=(_FF,9),anchor='w',tags='bannertext')
        self._cv.create_text(w-16,BANNER_H-12,text='v2.3',fill=MUTE,font=(_FF,8),anchor='e',tags='bannertext')
        self._cv.tag_raise(self._cont_wid); self._cv.tag_raise(self._sbar_wid)

    def _set_status(self,msg,col=MUTE):
        self.after(0,lambda:(self._status_var.set(msg),self._status_lbl.config(fg=col)))

    def _go(self,builder,direction='left'):
        if self._sliding: return
        cw=self._cont.winfo_width() or W; ch=self._cont.winfo_height() or (H-BANNER_H-SBAR_H)
        new=tk.Frame(self._cont,bg=BG,width=cw,height=ch); builder(new); old=self._page
        if self._first_nav or old is None:
            self._first_nav=False
            if old: old.destroy()
            new.place(x=0,y=0,width=cw,height=ch); self._page=new; return
        self._sliding=True; start_x=cw if direction=='left' else -cw
        new.place(x=start_x,y=0,width=cw,height=ch)
        FRAMES,TOTAL_MS=22,260
        def ease(t): return 1-(1-t)**4
        def step(i):
            t=ease(i/FRAMES); nx=int(start_x*(1-t)); ox=int((-start_x)*t)
            new.place(x=nx,y=0)
            if old: old.place(x=ox,y=0)
            if i<FRAMES: self.after(TOTAL_MS//FRAMES,lambda:step(i+1))
            else:
                if old: old.destroy()
                new.place(x=0,y=0); self._page=new; self._sliding=False
        step(0)

    def _quit(self):
        _echo_server.stop(); stop_proxy(wait=False); self.destroy()

    # ══ BOOT ═══════════════════════════════════════════════════
    def _boot(self):
        self._set_status('Locating Roblox Studio…')
        def build(f):
            f.configure(bg=BG); wrap=tk.Frame(f,bg=BG); wrap.place(relx=0.5,rely=0.5,anchor='center')
            mc=tk.Canvas(wrap,width=96,height=96,bg=BG,highlightthickness=0); mc.pack(pady=(0,10))
            phase=[0.0]; gids=[]; cx,cy,r=48,48,30
            for i in range(4,0,-1):
                gr=r+i*6; gids.append(mc.create_oval(cx-gr,cy-gr,cx+gr,cy+gr,fill='',outline=ACC,width=1))
            mc.create_oval(cx-r,cy-r,cx+r,cy+r,fill=MOON_C,outline=GLOW,width=1)
            so,sr=int(r*0.55),int(r*1.07); mc.create_oval(cx+so-sr,cy-sr,cx+so+sr,cy+sr,fill=BG,outline=BG)
            for dx,dy,cr in [(-0.10,-0.21,0.09),(-0.32,0.13,0.065),(-0.06,0.28,0.055)]:
                mc.create_oval(cx+dx*r*2-cr*r,cy+dy*r*2-cr*r,cx+dx*r*2+cr*r,cy+dy*r*2+cr*r,fill='#ece4ff',outline='')
            mc.create_oval(cx-r*0.28-r*0.13,cy-r*0.33-r*0.13,cx-r*0.28+r*0.13,cy-r*0.33+r*0.13,fill='white',outline='')
            animate_glow(mc,gids,phase)
            tk.Label(wrap,text='NEP TUNNEL',font=FT,bg=BG,fg=TEXT).pack()
            tk.Label(wrap,text='Locating Roblox Studio…',font=FB,bg=BG,fg=MUTE).pack(pady=4)
            spin=tk.Label(wrap,text='●  ○  ○',font=(_FF,9),bg=BG,fg=ACC); spin.pack(pady=2)
            frames=['●  ○  ○','○  ●  ○','○  ○  ●','○  ●  ○']; idx=[0]
            def tick():
                if not spin.winfo_exists(): return
                spin.config(text=frames[idx[0]%4]); idx[0]+=1; spin.after(280,tick)
            tick()
        p=tk.Frame(self._cont,bg=BG); p.place(x=0,y=0,relwidth=1,relheight=1); self._page=p; build(p)
        threading.Thread(target=lambda:self.after(0,lambda:self._on_studio(get_studio_path())),daemon=True).start()

    def _on_studio(self,path):
        self.studio=path
        if path==VINEGAR: self._set_status('Studio found  ·  Vinegar (Flatpak) — Linux',OK)
        elif path:
            short=(path[:52]+'…') if len(path)>55 else path; self._set_status(f'Studio found  ·  {short}',OK)
        else:
            saved=load_config().get('studio','')
            if saved and os.path.exists(saved):
                self.studio=saved; short=(saved[:52]+'…') if len(saved)>55 else saved
                self._set_status(f'Studio loaded from config  ·  {short}',OK)
            else:
                self._set_status(f'Studio not found on {_SYS} — use Browse to locate it',ERR)
        self._go_menu()

    # ══ MAIN MENU ══════════════════════════════════════════════
    def _go_menu(self,direction='left'):
        stop_proxy(); _echo_server.stop()
        def build(f):
            f.configure(bg=BG); tk.Frame(f,bg=BG,height=20).pack()
            card=card_frame(f); card.pack(padx=28,pady=(0,12))
            ctk.CTkLabel(card,text='What do you want to do?',font=FH,text_color=TEXT).pack(pady=(10,2),padx=14)
            ctk.CTkLabel(card,text='Host or join a session via tunnel',font=FB,text_color=MUTE).pack(pady=(0,14),padx=14)
            row=ctk.CTkFrame(card,fg_color='transparent'); row.pack(pady=(0,10),padx=14)
            ctk.CTkButton(row,text='  HOST SESSION  ',image=_make_icon('host',18,TEXT),compound='left',
                fg_color=ACC,hover_color=hex_lerp(ACC,'#ffffff',0.18),text_color=TEXT,font=FL,corner_radius=8,
                bg_color=CARD,command=self._go_host_config).pack(side='left',padx=8)
            ctk.CTkButton(row,text='  JOIN SESSION  ',image=_make_icon('join',18,TEXT),compound='left',
                fg_color=BLUE,hover_color=hex_lerp(BLUE,'#ffffff',0.18),text_color=TEXT,font=FL,corner_radius=8,
                bg_color=CARD,command=self._go_join_config).pack(side='left',padx=8)
            # second row — echo test + rbxm importer
            row2=ctk.CTkFrame(card,fg_color='transparent'); row2.pack(pady=(0,18),padx=14)
            ctk.CTkButton(row2,text='  ECHO TEST  ',image=_make_icon('echo',18,TEXT),compound='left',
                fg_color=TEAL,hover_color=hex_lerp(TEAL,'#ffffff',0.18),text_color=TEXT,font=FL,corner_radius=8,
                bg_color=CARD,command=self._go_echo_test).pack(side='left',padx=8)
            ctk.CTkButton(row2,text='  RBXM IMPORTER  ',image=_make_icon('map',18,TEXT),compound='left',
                fg_color='#7c3aed',hover_color=hex_lerp('#7c3aed','#ffffff',0.18),text_color=TEXT,font=FL,corner_radius=8,
                bg_color=CARD,command=self._go_maps).pack(side='left',padx=8)
            divider(f)
            info=tk.Frame(f,bg=BG); info.pack(fill='x',padx=30)
            sr=tk.Frame(info,bg=BG); sr.pack(anchor='w',pady=1)
            tk.Label(sr,text='Studio: ',font=FL,bg=BG,fg=MUTE).pack(side='left')
            short=(self.studio[:42]+'…') if len(self.studio)>45 else (self.studio or 'Not found')
            slbl=tk.Label(sr,text=short,font=FB,bg=BG,fg=GLOW if self.studio else ERR); slbl.pack(side='left')
            def _browse():
                p=filedialog.askopenfilename(title='Select RobloxStudioBeta.exe',
                    filetypes=[('Executable','*.exe'),('All files','*.*')],
                    initialdir=os.path.dirname(self.studio) if self.studio and os.path.exists(self.studio) else None)
                if p:
                    self.studio=p; s=(p[:42]+'…') if len(p)>45 else p
                    slbl.config(text=s,fg=GLOW); self._set_status(f'Studio set  ·  {s}',OK)
            icon_btn(sr,' Browse','folder',CARD2,_browse,padx=8,pady=2,icon_size=16).pack(side='left',padx=(8,0))
            cfg=load_config()
            for label,val in [('Tunnel Address',cfg['addr']),('Server Local Port',cfg['port']),
                               ('User ID',cfg['uid']),('Proxy Port',str(PROXY_PORT)),('Platform',_SYS)]:
                r=tk.Frame(info,bg=BG); r.pack(anchor='w',pady=1)
                tk.Label(r,text=f'{label}: ',font=FL,bg=BG,fg=MUTE).pack(side='left')
                tk.Label(r,text=val,font=FB,bg=BG,fg=GLOW).pack(side='left')
            # Bridge server status
            br=tk.Frame(info,bg=BG); br.pack(anchor='w',pady=1)
            tk.Label(br,text='Studio Bridge: ',font=FL,bg=BG,fg=MUTE).pack(side='left')
            bridge_lbl=tk.Label(br,text=f'● port {BRIDGE_PORT}' if _bridge_running else '✗ failed to start',
                                font=FB,bg=BG,fg=OK if _bridge_running else ERR)
            bridge_lbl.pack(side='left')
        self._go(build,direction)

    # ══ RBXM IMPORTER ══════════════════════════════════════════
    def _go_maps(self):
        cfg = load_config()
        # saved_maps is a list of absolute paths
        saved_maps: list[str] = cfg.get('saved_maps', [])
        # Filter out paths that no longer exist but keep them greyed (we'll mark missing)

        def build(f):
            f.configure(bg=BG)
            tk.Frame(f, bg=BG, height=4).pack()
            tk.Label(f, text='RBXM IMPORTER', font=FH, bg=BG, fg=TEXT).pack()
            tk.Label(f, text='Pick .rbxm files and send them to Studio via the bridge plugin',
                     font=FB, bg=BG, fg=MUTE).pack(pady=(2, 4))

            # ── Top controls ──────────────────────────────────
            top = tk.Frame(f, bg=BG)
            top.pack(fill='x', padx=20, pady=(0, 6))

            status_var = tk.StringVar(value='')
            status_lbl = tk.Label(top, textvariable=status_var, bg=BG, font=FS,
                                  fg=OK, anchor='w')
            status_lbl.pack(side='right', padx=4)

            def set_map_status(msg, col=OK):
                status_var.set(msg)
                status_lbl.config(fg=col)

            # ── File list frame (scrollable, fixed height) ──
            list_outer = tk.Frame(f, bg=CARD, bd=0, highlightthickness=1,
                                  highlightbackground=BORD, height=180)
            list_outer.pack(fill='x', padx=20, pady=(0, 4))
            list_outer.pack_propagate(False)

            list_canvas = tk.Canvas(list_outer, bg=CARD, highlightthickness=0, bd=0)
            scrollbar   = tk.Scrollbar(list_outer, orient='vertical',
                                       command=list_canvas.yview)
            list_canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            list_canvas.pack(side='left', fill='both', expand=True)

            inner = tk.Frame(list_canvas, bg=CARD)
            inner_win = list_canvas.create_window((0, 0), window=inner, anchor='nw')

            def _on_inner_resize(event):
                list_canvas.configure(scrollregion=list_canvas.bbox('all'))
                list_canvas.itemconfig(inner_win, width=list_canvas.winfo_width())
            inner.bind('<Configure>', _on_inner_resize)
            list_canvas.bind('<Configure>', lambda e: list_canvas.itemconfig(inner_win, width=e.width))

            # ── Render the list ───────────────────────────────
            def refresh_list():
                for w in inner.winfo_children():
                    w.destroy()

                if not saved_maps:
                    tk.Label(inner, text='No files saved yet.  Click  + Add .rbxm  to get started.',
                             font=FB, bg=CARD, fg=MUTE).pack(pady=24)
                    return

                for i, path in enumerate(saved_maps):
                    exists   = os.path.isfile(path)
                    row_bg   = CARD2 if i % 2 == 0 else CARD
                    row      = tk.Frame(inner, bg=row_bg)
                    row.pack(fill='x', padx=0, pady=1)

                    # Left: icon + name + path
                    left = tk.Frame(row, bg=row_bg)
                    left.pack(side='left', fill='x', expand=True, padx=10, pady=6)

                    name = os.path.basename(path)
                    name_col = TEXT if exists else MUTE
                    tk.Label(left, text=f'  {name}', font=FL, bg=row_bg,
                             fg=name_col, anchor='w').pack(anchor='w')

                    short_path = (path[:62] + '…') if len(path) > 65 else path
                    path_col   = MUTE if exists else ERR
                    path_note  = short_path if exists else f'⚠ missing  {short_path}'
                    tk.Label(left, text=path_note, font=FS, bg=row_bg,
                             fg=path_col, anchor='w').pack(anchor='w')

                    # Right: Send + Remove buttons
                    right = tk.Frame(row, bg=row_bg)
                    right.pack(side='right', padx=8, pady=4)

                    def make_send(p):
                        def _send():
                            if not os.path.isfile(p):
                                set_map_status(f'✗  File not found: {os.path.basename(p)}', ERR)
                                return
                            ok, result = _queue_rbxm(p)
                            if ok:
                                set_map_status(
                                    f'✓  "{result}" queued — click ▶ Listen in Studio plugin', OK)
                                self._set_status(f'Map queued: {result}', OK)
                            else:
                                set_map_status(f'✗  {result}', ERR)
                        return _send

                    def make_remove(idx):
                        def _remove():
                            saved_maps.pop(idx)
                            cfg2 = load_config()
                            cfg2['saved_maps'] = saved_maps
                            save_config(cfg2)
                            set_map_status('Removed.', MUTE)
                            refresh_list()
                        return _remove

                    send_state = 'normal' if exists else 'disabled'

                    send_btn = ctk.CTkButton(
                        right, text=' Send to Studio',
                        image=_make_icon('send', 14, TEXT), compound='left',
                        fg_color=ACC, hover_color=hex_lerp(ACC,'#ffffff',0.18),
                        text_color=TEXT, font=FS, corner_radius=8,
                        bg_color=row_bg, width=130, state=send_state,
                        command=make_send(path))
                    send_btn.pack(side='left', padx=(0, 6))

                    ctk.CTkButton(
                        right, text='',
                        image=_make_icon('trash', 14, ERR), compound='left',
                        fg_color=CARD, hover_color=hex_lerp(ERR,'#000000',0.6),
                        text_color=TEXT, font=FS, corner_radius=8,
                        bg_color=row_bg, width=34,
                        command=make_remove(i)).pack(side='left')

            refresh_list()

            # ── Bottom controls ───────────────────────────────
            bottom = tk.Frame(f, bg=BG)
            bottom.pack(pady=(0, 8))

            def add_map():
                paths = filedialog.askopenfilenames(
                    title='Select .rbxm map file(s)',
                    filetypes=[('Roblox Model', '*.rbxm *.rbxmx'),
                               ('All files', '*.*')]
                )
                if not paths:
                    return
                added = 0
                for p in paths:
                    p = os.path.abspath(p)
                    if p not in saved_maps:
                        saved_maps.append(p)
                        added += 1
                if added:
                    cfg2 = load_config()
                    cfg2['saved_maps'] = saved_maps
                    save_config(cfg2)
                    set_map_status(f'Added {added} map(s).', OK)
                    refresh_list()

            icon_btn(bottom, ' Back',     'back',   CARD,    lambda: self._go_menu('right')).pack(side='left', padx=8)
            icon_btn(bottom, ' + Add .rbxm','folder', '#7c3aed', add_map).pack(side='left', padx=8)

            # ── Instructions box ─────────────────────────────
            hint = tk.Frame(f, bg=CARD2, bd=0, highlightthickness=1, highlightbackground=BORD)
            hint.pack(fill='x', padx=20, pady=(0, 4))
            hint_lines = [
                ('HOW IT WORKS', 'info'),
                ('1. Add your .rbxm file(s) above.', 'dim'),
                ('2. In Studio, install RbxmImporter plugin and click  ▶ Listen.', 'dim'),
                ('3. Click  Send to Studio  — the plugin auto-imports it', 'dim'),
            ]
            for txt, tag in hint_lines:
                col = {'info': GLOW, 'dim': MUTE, 'ok': OK}.get(tag, TEXT)
                tk.Label(hint, text=txt, font=FS, bg=CARD2, fg=col, anchor='w').pack(
                    anchor='w', padx=12, pady=(4 if txt.startswith('HOW') else 1, 1))
            tk.Frame(hint, bg=CARD2, height=6).pack()

        self._go(build, 'left')

    # ══ ECHO TEST ══════════════════════════════════════════════
    def _go_echo_test(self):
        cfg=load_config()
        def build(f):
            f.configure(bg=BG); tk.Frame(f,bg=BG,height=8).pack()
            tk.Label(f,text='ECHO TEST',font=FH,bg=BG,fg=TEXT).pack()
            tk.Label(f,text='Verify tunnel connectivity before starting a session',
                     font=FB,bg=BG,fg=MUTE).pack(pady=(2,6))
            fields=tk.Frame(f,bg=BG); fields.pack(fill='x',padx=24,pady=(0,4))
            lr=tk.Frame(fields,bg=BG); lr.pack(side='left',fill='x',expand=True)
            tk.Label(lr,text='Studio Port  (host)',font=FS,bg=BG,fg=MUTE).pack(anchor='w')
            port_e=styled_entry(lr,cfg.get('port','55555'),width=120); port_e.pack(anchor='w',pady=(2,0))
            rr=tk.Frame(fields,bg=BG); rr.pack(side='left',fill='x',expand=True,padx=(16,0))
            tk.Label(rr,text='Tunnel Address  (joiner)',font=FS,bg=BG,fg=MUTE).pack(anchor='w')
            addr_e=styled_entry(rr,cfg.get('addr',''),width=300); addr_e.pack(anchor='w',pady=(2,0))
            logw=log_box(f,height=10); logw.pack(fill='x',padx=18,pady=(4,6))
            ctrls=tk.Frame(f,bg=BG); ctrls.pack()
            icon_btn(ctrls,' Back','back',CARD,
                     lambda:(_echo_server.stop(),self._go_menu('right'))
                     ).pack(side='left',padx=8)
            echo_count_var=tk.StringVar(value='')
            def toggle_echo():
                if _echo_server.running():
                    _echo_server.stop()
                    echo_btn.configure(text='  Host: Start Echo',fg_color=TEAL)
                    echo_count_var.set('')
                    log_append(logw,f'Echo server stopped  ({_echo_server.echoed} total echoed)','dim')
                    self._set_status('Echo server stopped',MUTE)
                else:
                    p=port_e.get().strip()
                    if not p.isdigit():
                        log_append(logw,'Port must be a number','err'); return
                    p=int(p)
                    if _echo_server.start(p, log_fn=lambda m, t='': log_append(logw, m, t)):
                        echo_btn.configure(text='  Host: Stop Echo',fg_color=ERR)
                        log_append(logw,f'✓ Echo server ACTIVE on 0.0.0.0:{p}','ok')
                        log_append(logw,'Waiting for joiner to send probe packets...','warn')
                        self._set_status(f'Echo server listening on port {p}',OK)
                        _poll_echo(logw,echo_count_var)
            echo_btn=icon_btn(ctrls,'  Host: Start Echo','echo',TEAL,toggle_echo,icon_size=16)
            echo_btn.pack(side='left',padx=8)
            tk.Label(ctrls,textvariable=echo_count_var,bg=BG,fg=OK,font=FS).pack(side='left',padx=(0,4))
            def run_join_echo():
                addr=addr_e.get().strip()
                if not addr or ':' not in addr:
                    log_append(logw,'Enter a tunnel address  (host:port)','err'); return
                rh,rp=addr.rsplit(':',1)
                if not rp.isdigit():
                    log_append(logw,'Invalid tunnel port','err'); return
                rp=int(rp)
                def _worker():
                    run_echo_test(lambda m,t='':log_append(logw,m,t), tunnel_host=rh, tunnel_port=rp)
                threading.Thread(target=_worker,daemon=True).start()
            icon_btn(ctrls,'  Join: Run Echo','echo',BLUE,run_join_echo,icon_size=16).pack(side='left',padx=8)
            log_append(logw,'HOW TO USE:','info')
            log_append(logw,'  HOST:   Set port above, press "Host: Start Echo"','ok')
            log_append(logw,'  JOINER: Enter tunnel address above, press "Join: Run Echo"','ok')
            log_append(logw,'','dim')
            log_append(logw,'  This test sends packets directly to the tunnel.','dim')
            log_append(logw,'  It may take 3-5 seconds for the tunnel to "wake up".','dim')
            log_append(logw,'───────────────────────────────────────','dim')
        self._go(build,'left')

    # ══ HOST CONFIG ════════════════════════════════════════════
    def _go_host_config(self):
        def build(f):
            f.configure(bg=BG); tk.Frame(f,bg=BG,height=12).pack()
            tk.Label(f,text='HOST SESSION',font=FH,bg=BG,fg=TEXT).pack()
            tk.Label(f,text='Review config, select map, and launch your server',font=FB,bg=BG,fg=MUTE).pack(pady=(2,10))
            cfg=load_config(); card=card_frame(f); card.pack(fill='x',padx=24); ents={}
            for lbl,val,key in [('User ID',cfg['uid'],'uid'),('Server Local Port',cfg['port'],'port'),
                                 ('Tunnel Address',cfg['addr'],'addr')]:
                r=ctk.CTkFrame(card,fg_color='transparent'); r.pack(fill='x',pady=3,padx=10)
                ctk.CTkLabel(r,text=lbl,font=FL,text_color=MUTE,width=160,anchor='w').pack(side='left')
                e=styled_entry(r,val,width=300); e.pack(side='left',fill='x',expand=True); ents[key]=e
            map_row = ctk.CTkFrame(card, fg_color='transparent')
            map_row.pack(fill='x', pady=3, padx=10)
            ctk.CTkLabel(map_row, text='Map File (Optional)', font=FL, text_color=MUTE, width=160, anchor='w').pack(side='left')
            map_entry = styled_entry(map_row, cfg.get('map', ''), width=220)
            map_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
            def browse_map():
                path = filedialog.askopenfilename(
                    title='Select Roblox Map',
                    filetypes=[('Roblox Place', '*.rbxl *.rbxlx'), ('All files', '*.*')])
                if path:
                    map_entry.delete(0, 'end'); map_entry.insert(0, path)
            icon_btn(map_row, ' Browse', 'folder', CARD2, browse_map, padx=8, pady=2, icon_size=16).pack(side='left')
            def _get(): return ents['uid'].get().strip(), ents['port'].get().strip(), ents['addr'].get().strip(), map_entry.get().strip()
            def do_launch():
                uid, port, addr, map_path = _get()
                if not all([uid, port, addr]): messagebox.showwarning('Missing Fields','All fields are required.'); return
                if not port.isdigit(): messagebox.showwarning('Invalid Port','Port must be a number.'); return
                if not self.studio:
                    messagebox.showerror('Studio Not Found',f'Roblox Studio was not found on {_SYS}.\nPlease ensure Roblox Studio is installed.'); return
                save_config({'uid':uid, 'port':port, 'addr':addr, 'studio':self.studio, 'map':map_path})
                self._go_host_running(uid, port, addr, map_path)
            def do_back():
                uid, port, addr, map_path = _get()
                save_config({'uid':uid, 'port':port, 'addr':addr, 'studio':self.studio, 'map':map_path})
                self._go_menu('right')
            tk.Frame(f,bg=BG,height=14).pack(); row=tk.Frame(f,bg=BG); row.pack()
            icon_btn(row,' Back','back',CARD,do_back).pack(side='left',padx=8)
            icon_btn(row,' Launch Server','play',ACC,do_launch).pack(side='left',padx=8)
        self._go(build,'left')

    # ══ HOST RUNNING ═══════════════════════════════════════════
    def _go_host_running(self, uid, port, addr, map_path=''):
        pg,tg=gen_guid(),gen_guid()
        def build(f):
            f.configure(bg=BG)
            tk.Label(f,text='SERVER CONSOLE',font=FH,bg=BG,fg=TEXT).pack(pady=(8,2))
            logw=log_box(f,height=9); logw.pack(fill='x',padx=18,pady=(4,6))
            ctrls=tk.Frame(f,bg=BG); ctrls.pack()
            join_btn=icon_btn(ctrls,'  JOIN LOCALLY  ','join',WARN,lambda:join_local())
            join_btn.pack(side='left',padx=8); join_btn.configure(state='disabled')
            icon_btn(ctrls,' Stop & Back','stop',ERR,lambda:self._go_menu('right')).pack(side='left',padx=8)
            def run_basic_test():
                h=addr.rsplit(':',1)[0] if ':' in addr else addr
                tp=int(addr.rsplit(':',1)[1]) if ':' in addr else int(port)
                threading.Thread(target=lambda:run_connectivity_test(
                    h,tp,lambda m,t='':log_append(logw,m,t),
                    is_host_side=True,local_server_port=int(port)),daemon=True).start()
            icon_btn(ctrls,' Test','test',CARD2,run_basic_test,icon_size=16).pack(side='left',padx=8)
            def join_local():
                try:
                    launch_client(self.studio,'127.0.0.1',port,pg,tg,'StudioPlayer_Host')
                    log_append(logw,'Local client launched.','info')
                except Exception as e:
                    log_append(logw,f'Launch error: {e}','err')
            def run():
                log_append(logw,f'Parent GUID: {pg}','dim'); log_append(logw,f'Play  GUID : {tg}','dim')
                log_append(logw,f'Port       : {port}'); log_append(logw,f'Address    : {addr}','info')
                if map_path and os.path.exists(map_path):
                    log_append(logw,f'Injecting map: {os.path.basename(map_path)}','warn')
                    if inject_map(map_path):
                        log_append(logw,'✓ Map copied to Roblox runtime cache','ok')
                    else:
                        log_append(logw,'✗ Failed to inject map. Studio might load default cache.','err')
                log_append(logw,'Launching Studio server process…')
                try:
                    launch_server(self.studio,port,uid,pg,tg)
                    log_append(logw,'Server started!  Waiting 5 s for Studio init…','ok')
                    write_session_log(pg,tg,addr,port,uid)
                    time.sleep(5)
                    log_append(logw,'● SERVER IS LIVE','ok')
                    log_append(logw,f'Session info saved → {LOG_FILE}','dim')
                    self.after(0,lambda:(self.clipboard_clear(),self.clipboard_append(addr),
                                         join_btn.configure(state='normal')))
                    self._set_status('● Server live — address in clipboard',OK)
                except Exception as e:
                    log_append(logw,f'ERROR: {e}','err'); self._set_status('Server launch failed',ERR)
            threading.Thread(target=run,daemon=True).start()
        self._go(build,'left')

    # ══ JOIN CONFIG ════════════════════════════════════════════
    def _go_join_config(self):
        def build(f):
            f.configure(bg=BG); tk.Frame(f,bg=BG,height=12).pack()
            tk.Label(f,text='JOIN SESSION',font=FH,bg=BG,fg=TEXT).pack()
            tk.Label(f,text="Enter the host's tunnel address",font=FB,bg=BG,fg=MUTE).pack(pady=(2,12))
            card=card_frame(f); card.pack(fill='x',padx=24)
            ctk.CTkLabel(card,text='Tunnel Address  (host:port)',font=FL,text_color=MUTE).pack(anchor='w',padx=10,pady=(10,0))
            addr_e=styled_entry(card,'',width=400); addr_e.pack(anchor='w',pady=(5,4),padx=10)
            ctk.CTkLabel(card,text=f'Will proxy via  127.0.0.1:{PROXY_PORT}  →  remote address',
                         font=FS,text_color=MUTE).pack(anchor='w',padx=10)
            err_lbl=ctk.CTkLabel(card,text='',font=FS,text_color=ERR); err_lbl.pack(anchor='w',pady=(4,10),padx=10)
            def do_join():
                addr=addr_e.get().strip()
                if not addr or ':' not in addr: err_lbl.configure(text='Format must be  host:port'); return
                rh,rp=addr.rsplit(':',1)
                if not rp.isdigit(): err_lbl.configure(text='Port must be a number'); return
                if not self.studio: messagebox.showerror('Studio Not Found','Roblox Studio was not found.'); return
                err_lbl.configure(text=''); self._go_join_running(rh,int(rp))
            tk.Frame(f,bg=BG,height=14).pack(); row=tk.Frame(f,bg=BG); row.pack()
            icon_btn(row,' Back','back',CARD,lambda:self._go_menu('right')).pack(side='left',padx=8)
            icon_btn(row,' Connect & Launch','join',BLUE,do_join).pack(side='left',padx=8)
        self._go(build,'left')

    # ══ JOIN RUNNING ═══════════════════════════════════════════
    def _go_join_running(self,dst_host,dst_port):
        def build(f):
            f.configure(bg=BG)
            tk.Label(f,text='CONNECTION CONSOLE',font=FH,bg=BG,fg=TEXT).pack(pady=(8,2))
            logw=log_box(f,height=9); logw.pack(fill='x',padx=18,pady=(4,6))
            ctrls=tk.Frame(f,bg=BG); ctrls.pack()
            icon_btn(ctrls,' Disconnect & Back','stop',ERR,lambda:disconnect()).pack(side='left',padx=8)
            def run_basic_test():
                threading.Thread(target=lambda:run_connectivity_test(
                    dst_host,dst_port,lambda m,t='':log_append(logw,m,t),is_host_side=False),daemon=True).start()
            icon_btn(ctrls,' Test','test',CARD2,run_basic_test,icon_size=16).pack(side='left',padx=8)
            def disconnect():
                log_append(logw,'Stopping proxy…','warn'); stop_proxy()
                self._set_status('Disconnected',MUTE); self.after(400,lambda:self._go_menu('right'))
            def run():
                pg,tg=gen_guid(),gen_guid()
                log_append(logw,f'Target     : {dst_host}:{dst_port}','info')
                log_append(logw,f'Local proxy: 127.0.0.1:{PROXY_PORT}')
                log_append(logw,'Starting UDP proxy…')
                ok=start_proxy(dst_host,dst_port)
                if not ok:
                    log_append(logw,f'Failed to bind port {PROXY_PORT}.  Is another session running?','err')
                    self._set_status(f'Proxy failed — port {PROXY_PORT} busy?',ERR); return
                log_append(logw,f'Proxy active on 127.0.0.1:{PROXY_PORT}','ok')
                log_append(logw,f'Warming tunnel ({WARM_PACKETS} probes)…','warn')
                warmed=warm_tunnel(PROXY_PORT)
                if warmed:
                    log_append(logw,f'✓ Tunnel warmed ({warmed}/{WARM_PACKETS} sent)','ok')
                else:
                    log_append(logw,'Warm-up skipped (proxy stopped early)','dim')
                time.sleep(0.25)
                log_append(logw,f'Parent GUID: {pg}','dim'); log_append(logw,f'Play  GUID : {tg}','dim')
                log_append(logw,'Launching Studio client…')
                try:
                    launch_client(self.studio,'127.0.0.1',str(PROXY_PORT),pg,tg,'StudioPlayer_Proxy')
                    log_append(logw,'● CONNECTED — Studio launched','ok')
                    self._set_status('● Connected to session',OK)
                except Exception as e:
                    log_append(logw,f'Studio launch error: {e}','err')
                    stop_proxy(); self._set_status('Studio launch failed',ERR)
            threading.Thread(target=run,daemon=True).start()
        self._go(build,'left')


def _poll_echo(logw, count_var: tk.StringVar):
    if not _echo_server.running(): return
    count_var.set(f'↑{_echo_server.echoed} echoed')
    logw.after(500, lambda: _poll_echo(logw, count_var))


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app = App()
    app.mainloop()