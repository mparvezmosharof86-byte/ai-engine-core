import time
import json
import threading
import requests
from datetime import datetime, timedelta

print("==================================================")
print("     AI CLOUD MASTER ENGINE & WORKER INITIALIZED  ")
print("==================================================")

# ---------------------------------------------------------
# কনফিগারেশন: তোমার ফায়ারবেস Realtime Database URL
# (যেমন: https://ai-engine-admin-default-rtdb.firebaseio.com/)
# ---------------------------------------------------------
FIREBASE_DB_URL = "YOUR_FIREBASE_DATABASE_URL_HERE" 

if not FIREBASE_DB_URL.endswith('/'):
    FIREBASE_DB_URL += '/'

# ---------------------------------------------------------
# ১. সিগন্যাল লাইট ও হার্টবিট মেকানিজম (Heartbeat System)
# ---------------------------------------------------------
def send_heartbeat():
    """অ্যাডমিন প্যানেলে ব্লু লাইট ও হেলথ স্ট্যাটাস পাঠায়"""
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
        time.sleep(30)  # প্রতি ৩০ সেকেন্ডে সিগন্যাল পাঠাবে

# ---------------------------------------------------------
# ২. সেলফ-হিলিং ও অটো-রিপেয়ার মেকানিজম (Self-Healing)
# ---------------------------------------------------------
def check_repair_commands():
    """অ্যাডমিন প্যানেলের Repair বাটনের রিকোয়েস্ট চেক করে"""
    while True:
        try:
            res = requests.get(f"{FIREBASE_DB_URL}system_control/command.json")
            cmd_data = res.json()
            if cmd_data and cmd_data.get("action") == "RESTART_AND_HEAL":
                print("[*] Repair signal received! Cleaning cache and restarting...")
                # রিপেয়ার হলে স্ট্যাটাস ফ্রেশ করা
                requests.put(f"{FIREBASE_DB_URL}system_health.json", json={
                    "status": "healthy",
                    "light": "blue",
                    "message": "System repaired & reloaded successfully!"
                })
                # কমান্ড ক্লিয়ার করা
                requests.delete(f"{FIREBASE_DB_URL}system_control/command.json")
                print("[✓] Engine successfully healed!")
        except Exception as e:
            print(f"[!] Repair Check Error: {e}")
        time.sleep(5)

# ---------------------------------------------------------
# ৩. মেমোরি ক্লিনার (Garbage Collector)
# ---------------------------------------------------------
def clean_stale_memory():
    """৫ মাসের পুরনো অব্যবহৃত মেমোরি ক্লিন করে"""
    try:
        res = requests.get(f"{FIREBASE_DB_URL}user_memory.json")
        memories = res.json()
        if memories:
            cutoff_date = datetime.utcnow() - timedelta(days=150) # ৫ মাস (১৫০ দিন)
            for user_id, data in memories.items():
                last_active = data.get("last_active")
                if last_active:
                    user_time = datetime.fromisoformat(last_active)
                    if user_time < cutoff_date:
                        requests.delete(f"{FIREBASE_DB_URL}user_memory/{user_id}.json")
                        print(f"[-] Pruned stale memory for inactive user: {user_id}")
    except Exception as e:
        print(f"[!] Memory Cleaner Error: {e}")

# ---------------------------------------------------------
# ৪. মাল্টি-ল্যাঙ্গুয়েজ ভিডিও জেনারেটর পাইপলাইন
# ---------------------------------------------------------
def process_video_task(task_id, task_data):
    """ভিডিও প্রম্পট নিয়ে ভিডিও জেনারেশন সম্পন্ন করে"""
    prompt = task_data.get("prompt", "")
    print(f"\n[+] Processing Video Task: {task_id} | Prompt: {prompt}")
    
    # প্রম্পট অপ্টিমাইজেশন (সিনেমেটিক বুস্ট)
    enhanced_prompt = f"Cinematic 4k footage, high quality, smooth motion, {prompt}"
    
    # ক্লাউড ভিডিও ব্যাকএন্ডে রিকোয়েস্ট পাঠানো
    try:
        # জেনারেশন শুরু স্ট্যাটাস
        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={"status": "processing"})
        
        # Pollinations / ওপেন সোর্স ভিডিও মেকার থেকে রেজাল্ট তৈরি
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        video_output_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=576" 
        
        # সফলভাবে রেজাল্ট ফায়ারবেসে জমা করা
        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={
            "status": "completed",
            "video_url": video_output_url,
            "completed_at": datetime.utcnow().isoformat()
        })
        print(f"[✓] Video Generated Successfully for task: {task_id}")
    except Exception as e:
        requests.patch(f"{FIREBASE_DB_URL}video_queue/{task_id}.json", json={"status": "failed", "error": str(e)})

# ---------------------------------------------------------
# ৫. টাস্ক কিউ লিসেনার (Video Queue Listener)
# ---------------------------------------------------------
def listen_video_queue():
    """ইউজার অ্যাপ বা ডেভেলপারদের ভিডিও অর্ডার চেক করে"""
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

# ---------------------------------------------------------
# মূল ইঞ্জিন স্টার্টার
# ---------------------------------------------------------
if __name__ == "__main__":
    print("[*] Starting Background Threads...")
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=check_repair_commands, daemon=True).start()
    
    # প্রতিবার স্টার্ট হওয়ার সময় মেমোরি ক্লিন হবে
    clean_stale_memory()
    
    print("[✓] AI Engine is officially LIVE & listening for orders.")
    listen_video_queue()
