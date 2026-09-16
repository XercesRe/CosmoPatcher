import frida
import time
import os
import sys

PROCESS = "COSMOTE Connect 3G.exe"
JS_FILE = os.path.join(os.path.dirname(__file__), "wifi_bridge.js")

print("[+] Starting COSMOTE Wi-Fi bridge")
print("[+] Target:", PROCESS)

try:
    session = frida.attach(PROCESS)
except Exception as e:
    print("[-] Could not attach:", e)
    sys.exit(1)

print("[+] Attached to COSMOTE Connect")

if not os.path.exists(JS_FILE):
    print("[-] Missing:", JS_FILE)
    session.detach()
    sys.exit(1)

with open(JS_FILE, "r", encoding="utf-8") as f:
    source = f.read()

def on_message(message, data):
    if message["type"] == "send":
        print("[BRIDGE]", message["payload"])
    elif message["type"] == "error":
        print("[BRIDGE ERROR]")
        print(message.get("stack", message))

script = session.create_script(source)
script.on("message", on_message)
script.load()

print("[+] Wi-Fi bridge injected")
print("[+] COSMOTE's modem/network path can now be intercepted")
print("[+] Windows Wi-Fi remains the real Internet connection")
print("[+] Press Connect / Redial in COSMOTE Connect")
print("[+] Ctrl+C to stop")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[+] Stopping bridge")
    script.unload()
    session.detach()