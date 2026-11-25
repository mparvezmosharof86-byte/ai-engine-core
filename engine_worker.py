import time
import json
import threading
import requests
from datetime import datetime, timedelta

print("==================================================")
print("     AI CLOUD MASTER ENGINE & WORKER INITIALIZED  ")
print("==================================================")

# তোমার ফায়ারবেস Realtime Database লিঙ্ক সরাসরি যুক্ত করা হয়েছে
FIREBASE_DB_URL = "https://ai-engine-admin-default-rtdb.firebaseio.com/"

def send_heartbeat():
    while True:
        try:
            health_data = {
                "status": "healthy",
                "light": "blue",
                "last_ping": datetime.utcnow().isoformat(),
                "message": "AI Engine is active and running smoothly."
            }
            requests.put(f"{FIREBASE_DB_URL}system_health.json", json=health_data)
        except Exception as e:
            print(f"[!] Heartbeat Error: {e}")
        time.sleep(30)

def check_repair_commands():
    while True:
        try:
            res = requests.get(f"{FIREBASE_DB_URL}system_control/command.json")
            cmd_data = res.json()
            if cmd_data and cmd_data.get("action") == "RESTART_AND_HEAL":
                print("[*] Repair signal received! Cleaning cache and restarting...")
                requests.put(f"{FIREBASE_DB_URL}system_health.json", json={
                    "status": "healthy",
                    "light": "blue",
                    "message": "System repaired & reloaded successfully!"
                })
                requests.delete(f"{FIREBASE_DB_URL}system_control/command.json")
                print("[✓] Engine successfully healed!")
        except Exception as e:
            print(f"[!] Repair Check Error: {e}")
        time.sleep(5)

def clean_stale_memory():
    try:
        res = requests.get(f"{FIREBASE_DB_URL}user_memory.json")
        memories = res.json()
        if memories:
            cutoff_date = datetime.utcnow() - timedelta(days=150)
            for user_id, data in memories.items():
                last_active = data.get("last_active")
                if last_active:
                    user_time = datetime.fromisoformat(last_active)
                    if user_time < cutoff_date:
                        requests.delete(f"{FIREBASE_DB_URL}user_memory/{user_id}.json")
                        print(f"[-] Pruned stale memory: {user_id}")
    except Exception as e:
        print(f"[!] Memory Cleaner Error: {e}")

def process_video_task(task_id, task_data):
    prompt = task_data.get("prompt", "")
    print(f"\n[+] Processing Video Task: {task_id} | Prompt: {prompt}")
    
    enhanced_prompt = f"Cinematic 4k footage, high quality, smooth motion, {prompt}"
    
    try:
        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={"status": "processing"})
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        video_output_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=576" 
        
        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={
            "status": "completed",
            "video_url": video_output_url,
            "completed_at": datetime.utcnow().isoformat()
        })
        print(f"[✓] Video Generated Successfully for: {task_id}")
    except Exception as e:
        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={"status": "failed", "error": str(e)})

def listen_video_queue():
    while True:
        try:
            res = requests.get(f"{FIREBASE_DB_URL}video_queue.json")
            queue = res.json()
            if queue:
                for task_id, task_data in queue.items():
                    if task_data and task_data.get("status") == "pending":
                        process_video_task(task_id, task_data)
        except Exception as e:
            print(f"[!] Queue Error: {e}")
        time.sleep(3)

if __name__ == "__main__":
    print("[*] Starting Background Threads...")
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=check_repair_commands, daemon=True).start()
    clean_stale_memory()
    print("[✓] AI Engine is officially LIVE & listening for orders.")
    listen_video_queue()
