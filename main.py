""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
courses_bot_full.py #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- /start shows numbered batches with Batch ID (copyable) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- choose a number -> bot asks for Course ID (string/hex allowed) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- send Course ID -> bot fetches /classes?populate=full and active list to get PDF #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- builds a flat line TXT (one item per line) containing: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    [Subject] <Full Title> : <link> #𓍯𝙎𝙪𝙟𝙖𝙡⚝
  (class video links and class PDFs both appear as separate lines with same title) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- appends summary at end of TXT #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- sends the txt as a document with summary in caption #𓍯𝙎𝙪𝙟𝙖𝙡⚝
- robust: handles errors, always returns safe values #𓍯𝙎𝙪𝙟𝙖𝙡⚝
""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝

import os #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import tempfile #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import logging #𓍯𝙎𝙪𝙟𝙖𝙡⚝
from pathlib import Path #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import time #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import json #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import requests #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import telebot #𓍯𝙎𝙪𝙟𝙖𝙡⚝
import re #𓍯𝙎𝙪𝙟𝙖𝙡⚝
from flask import Flask #𓍯𝙎𝙪𝙟𝙖𝙡⚝
from telebot.apihelper import ApiTelegramException #𓍯𝙎𝙪𝙟𝙖𝙡⚝

# ---------------- CONFIG ---------------- #𓍯𝙎𝙪𝙟𝙖𝙡⚝
BOT_TOKEN = "8455303530:AAHGZwmyy632cytzZaTbhMoVpeofTo1fEgw" # <-- REPLACE with your Bot token #𓍯𝙎𝙪𝙟𝙖𝙡⚝
BASE_URL = "https://backend.multistreaming.site/api" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
USER_ID_FOR_ACTIVE = "8050673236" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
BASE_HEADERS = { #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
} #𓍯𝙎𝙪𝙟𝙖𝙡⚝
# ---------------------------------------- #𓍯𝙎𝙪𝙟𝙖𝙡⚝

if BOT_TOKEN.startswith("PUT_"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    raise SystemExit("Please set your BOT_TOKEN in the script before running.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

# Simple in-memory user state #𓍯𝙎𝙪𝙟𝙖𝙡⚝
user_state = {}      # chat_id -> "await_batch" / "await_course_id" / None #𓍯𝙎𝙪𝙟𝙖𝙡⚝
user_batches = {}    # chat_id -> list_of_batches (from /courses/active) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
user_selected = {}   # chat_id -> selected batch object #𓍯𝙎𝙪𝙟𝙖𝙡⚝

app = Flask("render_web") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def safe_send(send_func, *args, **kwargs): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return send_func(*args, **kwargs) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception as e: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        print(f"[safe_send error] {e}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return None #𓍯𝙎𝙪𝙟𝙖𝙡⚝



@app.route("/") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def home(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    return "✅ Bot is running on Render!" #𓍯𝙎𝙪𝙟𝙖𝙡⚝

# Logging #𓍯𝙎𝙪𝙟𝙖𝙡⚝
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s") #𓍯𝙎𝙪𝙟𝙖𝙡⚝


# ---------------- Helpers ---------------- #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def safe_json_get(r): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return r.json() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception as e: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.warning("safe_json_get failed: %s", e) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return {} #𓍯𝙎𝙪𝙟𝙖𝙡⚝


def get_active_batches(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    """Return (ok, batches_list). Always safe.""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    url = f"{BASE_URL}/courses/active?userId={USER_ID_FOR_ACTIVE}" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        r = requests.get(url, headers=BASE_HEADERS, timeout=15) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        data = safe_json_get(r) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(data, dict) and data.get("state") == 200 and isinstance(data.get("data"), list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            return True, data["data"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            return True, data["data"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return False, [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception as e: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.exception("get_active_batches error") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return False, [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝


def get_course_classes(course_id): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    """Fetch classes for a course_id using classes?populate=full. Returns (ok, classes_list).""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    url = f"{BASE_URL}/courses/{course_id}/classes?populate=full" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        r = requests.get(url, headers=BASE_HEADERS, timeout=20) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        data = safe_json_get(r) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(data, dict) and data.get("state") == 200 and isinstance(data.get("data"), list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            return True, data["data"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            inner = data["data"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if "classes" in inner and isinstance(inner["classes"], list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                return True, inner["classes"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            return True, data["data"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return False, [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception as e: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.exception("get_course_classes error") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return False, [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝


def find_pdf_from_active(course_id, batches=None): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    """Search active batches list for batchInfoPdfUrl. Return list (may be empty).""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if batches is None: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            ok, batches = get_active_batches() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if not ok: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                return [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        for b in batches: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if str(b.get("id")) == str(course_id) or str(b.get("_id")) == str(course_id): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                pdf = b.get("batchInfoPdfUrl") or b.get("batch_info_pdf") or b.get("pdf") or "" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if not pdf: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    return [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if isinstance(pdf, list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    return [p for p in pdf if p] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if isinstance(pdf, str): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    parts = re.split(r"[\n,;]+", pdf) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    return [p.strip() for p in parts if p.strip()] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝


def _extract_subject_from_title(title, fallback=None): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    """Extract a compact subject token for bracket prefix.""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if "||" in title: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            parts = [p.strip() for p in title.split("||")] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if len(parts) > 1: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                second = parts[1] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if "|" in second: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    return second.split("|")[0].strip() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                return second.strip() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if "|" in title: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            parts = [p.strip() for p in title.split("|")] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for p in parts: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if p and not re.search(r"(?i)class[\s-]*\d+", p): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    return p #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if fallback: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            return fallback #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return "Course" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return fallback or "Course" #𓍯𝙎𝙪𝙟𝙖𝙡⚝


def normalize_video_entries(class_item): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    """Extract primary link, mp4s, and PDFs from class_item.""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    title = ( #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        class_item.get("title") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        or class_item.get("classTitle") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        or class_item.get("name") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        or class_item.get("heading") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        or "Untitled" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    candidate_links = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    direct_keys = [ #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "class_link", "videoLink", "video_link", "video_url", "videoUrl", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "link", "url", "playbackUrl", "playback_url", "streamUrl", "stream_url" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for k in direct_keys: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        v = class_item.get(k) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(v, str) and v: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            candidate_links.append(v) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    m3u8_keys = [ #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "masterPlaylist", "master_playlist", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "hlsLink", "hls_link", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "secureLink", "secure_link", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "m3u8", "m3u8Url", "m3u8_url", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "playlist", "playlistUrl" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for k in m3u8_keys: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        v = class_item.get(k) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(v, str) and v: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            candidate_links.append(v) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    array_keys = ["rawSources", "sources", "recordings", "files", "videoFiles", "videos", "assets"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for k in array_keys: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        arr = class_item.get(k) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(arr, list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for it in arr: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if isinstance(it, str) and it: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    candidate_links.append(it) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                elif isinstance(it, dict): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    for subk in ("url", "file", "src", "mp4", "m3u8"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        vv = it.get(subk) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        if isinstance(vv, str) and vv: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                            candidate_links.append(vv) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    nested_keys = ["playback", "video", "stream", "media"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for nk in nested_keys: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        obj = class_item.get(nk) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(obj, dict): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for subk in ("url", "file", "m3u8", "mp4", "hls", "src"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                vv = obj.get(subk) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if isinstance(vv, str) and vv: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    candidate_links.append(vv) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        elif isinstance(obj, list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for it in obj: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if isinstance(it, str): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    candidate_links.append(it) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                elif isinstance(it, dict): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    for subk in ("url", "file", "src", "mp4", "m3u8"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        vv = it.get(subk) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        if isinstance(vv, str): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                            candidate_links.append(vv) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    for k in ("embed", "iframe", "embedHtml"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        v = class_item.get(k) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(v, str) and "http" in v: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            m = re.search(r"https?://[^\s'\"<>]+", v) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if m: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                candidate_links.append(m.group(0)) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    seen = set() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    clean_candidates = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for u in candidate_links: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if not isinstance(u, str) or not u.strip(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            continue #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        u = u.strip() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if u not in seen: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            seen.add(u) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            clean_candidates.append(u) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    hls_links = [u for u in clean_candidates if "m3u8" in u or "playlist-mpl" in u or "hls" in u.lower()] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    other_links = [u for u in clean_candidates if u not in hls_links] #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    mp4_list = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for u in clean_candidates: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if u.lower().endswith(".mp4") or ".mp4?" in u.lower(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            mp4_list.append(u) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    explicit_mp4 = class_item.get("mp4Recordings") or class_item.get("mp4_recordings") or class_item.get("mp4records") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if isinstance(explicit_mp4, list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        for it in explicit_mp4: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if isinstance(it, str) and it.strip(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if it not in mp4_list: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    mp4_list.append(it.strip()) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            elif isinstance(it, dict): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                for subk in ("url", "file", "mp4"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    vv = it.get(subk) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    if isinstance(vv, str) and vv.strip() and vv not in mp4_list: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        mp4_list.append(vv.strip()) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    mp4_seen = set() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    mp4_clean = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for m in mp4_list: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if m not in mp4_seen: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            mp4_seen.add(m) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            mp4_clean.append(m) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    class_pdfs = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    pdf_keys = ["classPdf", "class_pdf", "pdfs", "materials", "resources", "files"] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for key in pdf_keys: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        arr = class_item.get(key) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(arr, list): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for it in arr: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                if isinstance(it, str) and ".pdf" in it.lower(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    class_pdfs.append(it.strip()) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                elif isinstance(it, dict): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    for subk in ("url", "file", "pdf"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        vv = it.get(subk) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                        if isinstance(vv, str) and ".pdf" in vv.lower(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                            class_pdfs.append(vv.strip()) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    for k in ("pdf", "pdfUrl", "pdf_url", "file"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        v = class_item.get(k) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(v, str) and ".pdf" in v.lower(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            class_pdfs.append(v.strip()) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    pdf_seen = set() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    pdf_clean = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    for p in class_pdfs: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if p not in pdf_seen: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            pdf_seen.add(p) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            pdf_clean.append(p) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    primary_link = "" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if hls_links: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        primary_link = hls_links[0] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    elif other_links: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        primary_link = other_links[0] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    else: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        primary_link = "" #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    include_mp4s = False if primary_link and ("m3u8" in primary_link or "hls" in primary_link.lower() or "playlist-mpl" in primary_link) else True #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    return { #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "title": title, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "class_link": primary_link, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "mp4Recordings": mp4_clean if include_mp4s else [], #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "classPdf": pdf_clean #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    } #𓍯𝙎𝙪𝙟𝙖𝙡⚝


def build_txt_for_course(course_id, course_title=None): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    """Build TXT content and summary for a course.""" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ok, classes = get_course_classes(course_id) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    batches_ok, batches = get_active_batches() #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    if not ok: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return False, "ERROR: Failed to fetch classes for this course.", {} #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    items_to_process = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if isinstance(classes, list) and classes and isinstance(classes[0], dict) and classes[0].get("topicName") and classes[0].get("classes"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for topic_block in classes: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                for cls in topic_block.get("classes", []): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                    items_to_process.append(cls) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        else: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            items_to_process = classes if isinstance(classes, list) else [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        items_to_process = classes if isinstance(classes, list) else [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    lines = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    total_videos = 0 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    total_mp4 = 0 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    total_m3u8 = 0 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    total_youtube = 0 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    total_pdfs = 0 #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    for cls in items_to_process: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        normalized = normalize_video_entries(cls) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        title = normalized.get("title", "Untitled") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        subject = _extract_subject_from_title(title, fallback=(course_title or "Course")) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

        primary = normalized.get("class_link") or "" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if primary: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            lines.append(f"[{subject}] {title} : {primary}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            total_videos += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            u = primary.lower() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if "m3u8" in u or "playlist" in u or "hls" in u: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                total_m3u8 += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            elif "youtube" in u: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                total_youtube += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            else: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                total_mp4 += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        elif normalized.get("mp4Recordings"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            for m in normalized.get("mp4Recordings"): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                lines.append(f"[{subject}] {title} : {m}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                total_videos += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                total_mp4 += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝

        for p in normalized.get("classPdf", []): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            lines.append(f"[{subject}] {title} : {p}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            total_pdfs += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    course_level_pdfs = find_pdf_from_active(course_id, batches if batches_ok else None) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if isinstance(course_level_pdfs, str): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        if course_level_pdfs and course_level_pdfs.lower() != "no pdf": #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            course_level_pdfs = [u.strip() for u in re.split(r"[\n,;]+", course_level_pdfs) if u.strip()] #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        else: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            course_level_pdfs = [] #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    if isinstance(course_level_pdfs, list) and course_level_pdfs: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        subj = course_title or "Course" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        for p in course_level_pdfs: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            lines.append(f"[{subj}] {subj} : {p}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            total_pdfs += 1 #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    txt_content = "\n".join(lines) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    summary_text = ( #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        f"📊 Export Summary:\n" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        f"🔗 Total Links: {len(lines)}\n" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        f"🎬 Videos: {total_videos}\n" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        f"📄 PDFs: {total_pdfs}\n" #𓍯𝙎𝙪𝙟𝙖𝙡
        f"🦅 Owner:@Chouhan143_bot\n" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    txt_content += "\n\n" + summary_text #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    summary_dict = { #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "total_links": len(lines), #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "total_videos": total_videos, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "total_mp4": total_mp4, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "total_m3u8": total_m3u8, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "total_youtube": total_youtube, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "total_pdfs": total_pdfs, #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "summary_text": summary_text #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    } #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    return True, txt_content, summary_dict #𓍯𝙎𝙪𝙟𝙖𝙡⚝


# ---------------- BOT HANDLERS ---------------- #𓍯𝙎𝙪𝙟𝙖𝙡⚝
@bot.message_handler(commands=["start"]) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def handle_start(message): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    chat_id = message.chat.id #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ok, batches = get_active_batches() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if not ok: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.send_message(chat_id, "❌ *Unable to fetch batch list. Try again later.*", parse_mode="Markdown") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    user_batches[chat_id] = {str(b.get("id") or b.get("_id")): b for b in batches} #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    user_state[chat_id] = "await_course_id" #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    msg_lines = [ #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "━━━━━━━━━━━━━━━━━━━━━━━━", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        " *WELCOME TO 𓍯✮⃝mrचौहान✮⃝🚩⚝ bots connect - @Chouhan143_bot * ", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        " *Select your batch from below:* ", #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        "━━━━━━━━━━━━━━━━━━━━━━\n" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    ] #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    for i, b in enumerate(batches, start=1): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        title = b.get("title") or b.get("name") or "Untitled" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bid = b.get("id") or b.get("_id") or "" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        msg_lines.append(f"📌 *{i}. {title}*") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        msg_lines.append(f"   🆔 Batch ID: `{bid}`") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        msg_lines.append("────────────────────────") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    msg_lines.append("\n✨ Send the *Batch ID* to continue.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    msg_lines.append("💡 Tip: Copy the Batch ID above to avoid mistakes!") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    msg_lines.append("[JiON CHENAL](https://t.me/+xhH4HjZavEdiODNl)") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    msg_lines.append("━━━━━━━━━━━━━━━━━━━") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    bot.send_message(chat_id, "\n".join(msg_lines), parse_mode="Markdown") #𓍯𝙎𝙪𝙟𝙖𝙡⚝



@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "await_course_id") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def handle_course_id(message): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    chat_id = message.chat.id #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    batch_id = (message.text or "").strip() #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if not batch_id: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.reply_to(message, "❌ Please send a valid Batch ID (string).") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    selected = user_batches.get(chat_id, {}).get(batch_id) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if not selected: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.reply_to(message, f"❌ Invalid Batch ID: {batch_id}. Make sure it's exact.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    user_selected[chat_id] = selected #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    course_title = selected.get("title") or "Course" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    bot.send_message(chat_id, "⏳ Fetching course data... Please wait.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    ok, txt, summary = build_txt_for_course(batch_id, course_title=course_title) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    if not ok: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.send_message(chat_id, f"❌ Failed to fetch course data for ID: {batch_id}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        return #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    tmp_path = None #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        safe_title = re.sub(r"[^\w\s-]", "", course_title).strip().replace(" ", "_") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        tmp_file_name = f"𓍯✮⃝𝕮𝖍o𝖚𝖍𝖆𝖓{safe_title}.txt" #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        tmp_path = os.path.join(tempfile.gettempdir(), tmp_file_name) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        with open(tmp_path, "w", encoding="utf-8") as tf: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            tf.write(txt) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

        with open(tmp_path, "rb") as doc: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            bot.send_document(chat_id, doc, caption=f"Course export: {course_title}\n\n{summary.get('summary_text','')}") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    except Exception as e: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.exception("Error sending document") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.send_message(chat_id, "❌ Error while preparing/sending file.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    finally: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            if tmp_path and Path(tmp_path).exists(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
                os.remove(tmp_path) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        except Exception: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
            pass #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    user_state[chat_id] = None #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    user_selected.pop(chat_id, None) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    user_batches.pop(chat_id, None) #𓍯𝙎𝙪𝙟𝙖𝙡⚝


@bot.message_handler(func=lambda m: True) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
def fallback(message): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    chat_id = message.chat.id #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    bot.send_message(chat_id, "Use /start to list batches and export a course. If you're in the flow, follow instructions.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝


# ---------------- RUN ---------------- #𓍯𝙎𝙪𝙟𝙖𝙡⚝
from threading import Thread #𓍯𝙎𝙪𝙟𝙖𝙡⚝

if __name__ == "__main__": #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    logging.info("Bot starting...") #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    # Flask को separate thread में चलाओ ताकि Render port detect कर सके #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    def run_flask(): #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        port = int(os.environ.get("PORT", 10000)) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        app.run(host="0.0.0.0", port=port) #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    Thread(target=run_flask, daemon=True).start() #𓍯𝙎𝙪𝙟𝙖𝙡⚝

    # Bot start #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    try: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        bot.infinity_polling(timeout=60, long_polling_timeout=60) #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except KeyboardInterrupt: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.info("Bot stopped by user.") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
    except Exception: #𓍯𝙎𝙪𝙟𝙖𝙡⚝
        logging.exception("Bot crashed") #𓍯𝙎𝙪𝙟𝙖𝙡⚝
