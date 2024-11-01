from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
import requests
import time
from logger import logger
import threading
from datetime import datetime
from notifications import send_sms_bulk
from artsist import get_artist_from_acrcloud

# Flask app setup
app = Flask(__name__)

# Control flags
MONITORING_ACTIVE = False  # Global flag to control API monitoring
LOG_REGULAR_CALLBACKS = False  # Control regular song logger

# Email configuration
SMTP_SERVER = 'mail.its-4-u.com'
SMTP_PORT = 465
EMAIL_ADDRESS = 'test@its-4-u.com'
EMAIL_PASSWORD = '#Test#myEmail2024'
TO_EMAIL = 'ammaralee.005@gmail.com'
NUMBER = '+447770982600'

# Bearer token for API authentication
bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI3IiwianRpIjoiNTJhZDUzNTIzMmExMTRmYmI3YTdjZTRmOGRmNDA1NTA3YzRiMzUxZGU0MTNkMmZkMmQzMTczMzRkYWM1MDJmYmYyOTgzYjg0MGQzZGY5MDYiLCJpYXQiOjE3MjM1NDY3NTYuMzU1MDAyLCJuYmYiOjE3MjM1NDY3NTYuMzU1MDA0LCJleHAiOjIwMzkwNzk1NTYuMzIxNjExLCJzdWIiOiIxODQ4MDQiLCJzY29wZXMiOlsiKiIsIndyaXRlLWFsbCIsInJlYWQtYWxsIl19.JH4UjF2XVKlXVwTxWcW6Ia6vUDI6TtgUhKpCLutgrPZ1cxWZZ2Ta-japzaMFC1cVKVXTn36FyQNaok9yAEqOhAwVlfkSFnByW5A6VD2H-rtc70u7oI2EK6LYyY6jpwtk_bjp68RtRLwY6u4B4oLuXwjOP-VQp7qm5oIksmSd4ZnPRzEubb1IiYXPtpaSY2aWr4h10r1S6ibYNmgS0FbrD5ahwMqzjzQvPq2LUext3Vyi0E_D1wrzbpl0ZaYi_sMpVP052K2S1WbPvw7Jzgkzl0RogaifrqQ-Zyy0sV7AuGGo-syrcWgRpz2oscBkJZu6fcPLe5D1s8daMFiUslODrfA16rUgYUxPXcrSHYwwwgYAtRpV5VCwdMN-yFau0DG9wl2ZEm0x089x7iZ_QTSHVQGlCTqV50yASrXtazQfM2a1WRd5P446O1k7faaOE_Yqs9yc8RXOS-Z1_AfV2cXKHnckWtdUjSii2iCKPrk85i_oI278Bj-HacPe_LNsTPZQihq2GyaeQCSN3GW3LRAIEthbHGlq7woFQ1jPzFEr2w4tWTyF6a8PtkXpnsMW_WIOSqH-4RQeMnsNK5MIpOlVo3pp3ZPimWe5miAEb-2zbxBjo4AXUZ4LPtxtHbH3EFmyW7xFv-lRIT9zjjg4Cpsy8vBuUpKqILeMkZkHmmSRiic"

# API URL for live artist data
live_data_api_url = "https://api-v2.acrcloud.com/api/bm-bd-projects/3165/channels/293484/realtime_results"

# State variables
last_artist = None
processing_alarm = False
waiting_for_api_check = False

@app.route('/pause', methods=['POST'])
def pause_monitoring():
    """Pause API monitoring"""
    global MONITORING_ACTIVE
    MONITORING_ACTIVE = False
    logger.info("🛑 Monitoring paused")
    return jsonify({"status": "success", "message": "Monitoring paused"}), 200

@app.route('/resume', methods=['POST'])
def resume_monitoring():
    """Resume API monitoring"""
    global MONITORING_ACTIVE
    MONITORING_ACTIVE = True
    logger.info("▶️ Monitoring resumed")
    return jsonify({"status": "success", "message": "Monitoring resumed"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    """Get current monitoring status"""
    status = "Active" if MONITORING_ACTIVE else "Paused"
    return jsonify({
        "status": "success",
        "monitoring": status,
        "logger_callbacks": LOG_REGULAR_CALLBACKS
    }), 200

def send_email(artist_name):
    """Send email with artist notification"""
    try:
        message = f"Get Ready To Win - Show Me The Money test - The artist is ({artist_name}) enter now. Text the word MONEY and the NAME OF THE ARTIST to 82122"
        
        msg = MIMEText(message)
        msg['Subject'] = f"2WIN ALERTS 🔔🔔🔔: {artist_name}"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
            
        logger.info("🔔 [ALARM] Email sent successfully for artist: %s", artist_name)
        return True
    except Exception as e:
        logger.error("🔔 [ALARM] Failed to send email: %s", str(e))
        return False

def fetch_live_data():
    """Fetch live data with improved error handling"""
    if not MONITORING_ACTIVE:
        logger.info("🛑 Monitoring is paused - skipping API call")
        return None

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    try:
        logger.info("🔔 [ALARM] Fetching live artist data...")
        response = requests.get(live_data_api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            live_data = response.json()
            logger.info("🔔 [ALARM] API Response:")
            logger.info(live_data)
            return live_data
            
        elif response.status_code == 401:
            logger.error("🔔 [ALARM] Authentication failed. Check bearer token.")
            return None
            
        elif response.status_code == 429:
            logger.warning("🔔 [ALARM] Rate limit exceeded. Waiting...")
            time.sleep(60)
            return None
            
        else:
            logger.error("🔔 [ALARM] API error. Status code: %s", response.status_code)
            return None
            
    except Exception as e:
        logger.error("🔔 [ALARM] Error fetching live data: %s", str(e))
        return None

def get_artist_name(live_data):
    """Extract artist name with improved error handling"""
    try:
        if not live_data or 'data' not in live_data:
            logger.info("🔔 [ALARM] No data in API response")
            return None
            
        metadata = live_data['data'].get('metadata', {})
        music_data = metadata.get('music', [{}])[0] if metadata.get('music') else {}
        
        if not music_data or 'artists' not in music_data:
            logger.info("🔔 [ALARM] No music playing (could be advert/news)")
            return None
        
        artists = music_data.get('artists', [])
        if not artists:
            logger.info("🔔 [ALARM] No artists found in music data")
            return None
        
        # Get all artist names
        artist_names = [artist['name'] for artist in artists if 'name' in artist]
        if not artist_names:
            logger.info("🔔 [ALARM] No valid artist names found")
            return None
        
        # Join multiple artists with ' & '
        artist_name = ' & '.join(artist_names)
        artist_name = artist_name.strip()
        
        logger.info("🔔 [ALARM] Found artist: %s", artist_name)
        return artist_name

    except Exception as e:
        logger.error("🔔 [ALARM] Error extracting artist: %s", str(e))
        return None

def process_alarm():
    """Process alarm and check for artists"""
    global last_artist, processing_alarm, waiting_for_api_check
    
    if not MONITORING_ACTIVE:
        logger.info("🛑 Monitoring is paused - skipping alarm processing")
        return

    processing_alarm = True
    waiting_for_api_check = True
    
    logger.info("🔔 [ALARM] Starting alarm processing...")
    logger.info("🔔 [ALARM] Waiting 30 seconds before checking for artist...")
    time.sleep(30)
    
    waiting_for_api_check = False
    check_count = 0
    max_checks = 6
    
    while MONITORING_ACTIVE and processing_alarm and check_count < max_checks:
        logger.info("🔔 [ALARM] Performing check %d of %d", check_count + 1, max_checks)
        live_data = fetch_live_data()
        
        if live_data:
            artist_name = get_artist_from_acrcloud(live_data)
            if artist_name:
                if artist_name != last_artist:
                    logger.info("🔔 [ALARM] New artist detected: %s", artist_name)
                    if send_email(artist_name) and send_sms_bulk(phone_numbers=[NUMBER],artist_name=artist_name):
                        last_artist = artist_name
                        logger.info("🔔 [ALARM] Successfully processed artist: %s", artist_name)
                        break
                else:
                    logger.info("🔔 [ALARM] Same artist still playing: %s", artist_name)
                    break
        
        check_count += 1
        if check_count < max_checks and MONITORING_ACTIVE:
            logger.info("🔔 [ALARM] Waiting 20 seconds before next check...")
            time.sleep(20)
    
    processing_alarm = False
    logger.info("🔔 [ALARM] Alarm processing complete")

@app.route('/callback', methods=['POST'])
def handle_callback():
    """Handle ACRCloud callback"""
    global processing_alarm, waiting_for_api_check
    
    if not MONITORING_ACTIVE:
        return jsonify({"status": "success", "message": "Monitoring is paused"}), 200
    
    try:
        data = request.json
        
        # Check if this is an alarm trigger
        if (data and "data" in data and 
            "metadata" in data["data"] and 
            "custom_files" in data["data"]["metadata"]):
            
            for file_info in data["data"]["metadata"]["custom_files"]:
                alarm_id = file_info.get("alarm_id")
                
                if alarm_id in ["Alarm 1", "Alarm 2", "Alarm 3", "Alarm 4", "Alarm 5"]:
                    logger.info("🔔 [ALARM] Received alarm trigger: %s", alarm_id)
                    
                    if not processing_alarm and not waiting_for_api_check:
                        thread = threading.Thread(target=process_alarm)
                        thread.daemon = True
                        thread.start()
                        logger.info("🔔 [ALARM] Started processing thread for alarm: %s", alarm_id)
                    else:
                        logger.info("🔔 [ALARM] Skipping alarm - already processing")
                    return jsonify({"status": "success"}), 200
        
        # Only log regular callbacks if flag is True
        if LOG_REGULAR_CALLBACKS:
            if (data and "data" in data and 
                "metadata" in data["data"] and 
                "music" in data["data"]["metadata"] and 
                data["data"]["metadata"]["music"]):
                
                music_data = data["data"]["metadata"]["music"][0]
                if "artists" in music_data:
                    artists = [artist["name"] for artist in music_data["artists"]]
                    logger.info("[INFO] Current song playing: %s", " & ".join(artists))
                    
    except Exception as e:
        logger.error("[ERROR] Error processing callback: %s", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    logger.info("Starting Artist Monitor System")
    logger.info("Monitoring Status: Active")
    logger.info("Regular Callback logger: %s", "Enabled" if LOG_REGULAR_CALLBACKS else "Disabled")
    logger.info("Monitoring for Alarms: 1, 2, 3, 4, 5")
    app.run(host='0.0.0.0', port=8080)