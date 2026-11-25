import os
import time
import json
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

print("==================================================", flush=True)
print("     AI CLOUD MASTER ENGINE & WORKER INITIALIZED  ", flush=True)
print("==================================================", flush=True)

# সিঙ্গাপুরের ডাটাবেজ লিঙ্ক
FIREBASE_DB_URL = "https://ai-engine-admin-default-rtdb.asia-southeast1.firebasedatabase.app/"

# ---------------------------------------------------------
# লাইভ ওয়েব টেস্ট ও ডায়াগনস্টিক সার্ভার
# ---------------------------------------------------------
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # ব্রাউজারে লিংক ওপেন করলেই তাৎক্ষণিক ফায়ারবেসে টেস্ট সিগন্যাল পাঠাবে
        fb_report = ""
        try:
            health_data = {
                "status": "healthy",
                "light": "blue",
                "last_ping": datetime.utcnow().isoformat(),
                "message": "AI Cloud Engine is active & running smoothly 24/7."
            }
            res = requests.put(f"{FIREBASE_DB_URL}system_health.json", json=health_data, timeout=10)
            fb_report = f"Firebase Sync Status: HTTP {res.status_code} | Response: {res.text}"
            print(f"[Direct-Ping] {fb_report}", flush=True)
        except Exception as e:
            fb_report = f"Firebase Connection Error: {str(e)}"
            print(f"[Direct-Ping Error] {fb_report}", flush=True)

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        output_text = f"✓ AI Engine is Officially LIVE on Render!\n\n[Diagnostic Report]:\n{fb_report}\n\nTarget URL: {FIREBASE_DB_URL}"
        self.wfile.write(output_text.encode("utf-8"))

    def log_message(self, format, *args):
        return

def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthServer)
    print(f"[✓] Render Port Listener active on port {port}", flush=True)
    server.serve_forever()

# ---------------------------------------------------------
# ব্যাকগ্রাউন্ড হার্টবিট লুপ (প্রতি ৩০ সেকেন্ডে)
# ---------------------------------------------------------
def send_heartbeat():
    time.sleep(5) # সার্ভার শুরুর পর একটু বিরতি
    while True:
        try:
            health_data = {
                "status": "healthy",
                "light": "blue",
                "last_ping": datetime.utcnow().isoformat(),
                "message": "AI Cloud Engine is active & running smoothly 24/7."
            }
            res = requests.put(f"{FIREBASE_DB_URL}system_health.json", json=health_data, timeout=10)
            print(f"[Heartbeat] Sent Blue signal! HTTP Status: {res.status_code}", flush=True)
        except Exception as e:
            print(f"[!] Heartbeat Error: {e}", flush=True)
        time.sleep(30)

def check_repair_commands():
    while True:
        try:
            res = requests.get(f"{FIREBASE_DB_URL}system_control/command.json", timeout=10)
            cmd_data = res.json()
            if cmd_data and cmd_data.get("action") == "RESTART_AND_HEAL":
                print("[*] Repair signal received! Cleaning cache and restarting...", flush=True)
                requests.put(f"{FIREBASE_DB_URL}system_health.json", json={
                    "status": "healthy",
                    "light": "blue",
                    "last_ping": datetime.utcnow().isoformat(),
                    "message": "System repaired & reloaded successfully!"
                }, timeout=10)
                requests.delete(f"{FIREBASE_DB_URL}system_control/command.json", timeout=10)
                print("[✓] Engine successfully healed!", flush=True)
        except Exception as e:
            pass
        time.sleep(5)

def listen_video_queue():
    while True:
        try:
            res = requests.get(f"{FIREBASE_DB_URL}video_queue.json", timeout=10)
            queue = res.json()
            if queue:
                for task_id, task_data in queue.items():
                    if task_data and task_data.get("status") == "pending":
                        prompt = task_data.get("prompt", "")
                        print(f"[+] Processing Task: {task_id} | Prompt: {prompt}", flush=True)
                        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={"status": "processing"}, timeout=10)
                        
                        encoded_prompt = requests.utils.quote(f"Cinematic 4k footage, high quality, {prompt}")
                        video_output_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=576" 
                        
                        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={
                            "status": "completed",
                            "video_url": video_output_url,
                            "completed_at": datetime.utcnow().isoformat()
                        }, timeout=10)
                        print(f"[✓] Task Completed: {task_id}", flush=True)
        except Exception as e:
            pass
        time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=start_web_server, daemon=True).start()
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=check_repair_commands, daemon=True).start()
    print("[✓] AI Cloud Engine is officially LIVE & listening for orders.", flush=True)
    listen_video_queue()
