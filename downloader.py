import os
import uuid
import json
import subprocess
from typing import Optional
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import redis

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
try:
    redis_client = redis.from_url(REDIS_URL)
except Exception:
    redis_client = None

DEFAULT_MAX_FILESIZE = os.getenv('MAX_FILESIZE', None)  # e.g. '50M' or None


def _safe_title(info):
    return info.get('title', 'download')


def _make_outtmpl(ext_template='%(title)s.%(ext)s'):
    return os.path.join(DOWNLOAD_DIR, ext_template)


def download_media(url: str, kind: str = 'video', job_id: Optional[str] = None, cookies_text: Optional[str] = None, max_filesize: Optional[str] = None, use_redis: bool = True) -> str:
    """
    Download media via yt-dlp. kind: 'video' or 'audio'.
    Reports progress to Redis key `progress:{job_id}` as JSON with keys: status, downloaded_bytes, total_bytes, percent.
    Stores final filepath to Redis key `result:{job_id}`.
    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    outtmpl = _make_outtmpl('%(title)s.%(ext)s')
    opts = {
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'socket_timeout': 60,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        'age_limit': None,
    }

    if kind == 'video':
        opts.update({'format': 'bestvideo+bestaudio/best'})
    else:
        opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]})

    # apply max filesize if provided
    if max_filesize is None:
        max_filesize = DEFAULT_MAX_FILESIZE
    if max_filesize:
        opts['max_filesize'] = max_filesize

    # handle cookies: if cookies_text provided, write to a temporary file and pass cookiefile
    cookiefile = None
    if cookies_text and cookies_text.strip():
        cookiefile = os.path.join(DOWNLOAD_DIR, f'cookies-{job_id}.txt')
        # Ensure cookies text is properly formatted (each line is a cookie entry)
        # Remove any BOM or extra whitespace at start/end
        cookies_clean = cookies_text.strip()
        if not cookies_clean.startswith('# Netscape HTTP Cookie File'):
            # If it doesn't look like a Netscape cookie file, just write it as-is
            pass
        with open(cookiefile, 'w', encoding='utf-8') as f:
            f.write(cookies_clean)
        opts['cookiefile'] = cookiefile
        print(f'[INFO] Using cookies file: {cookiefile}', flush=True)

    def _progress_hook(d):
        try:
            key = f'progress:{job_id}'
            if d.get('status') == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes') or 0
                total_bytes = d.get('total_bytes') or d.get('estimated_bytes') or 0
                percent = None
                if total_bytes:
                    try:
                        percent = round(downloaded_bytes / total_bytes * 100, 2)
                    except Exception:
                        percent = None
                payload = {
                    'status': 'downloading',
                    'downloaded_bytes': downloaded_bytes,
                    'total_bytes': total_bytes,
                    'percent': percent,
                }
                if use_redis and redis_client:
                    try:
                        redis_client.set(key, json.dumps(payload))
                    except Exception:
                        pass
            elif d.get('status') == 'finished':
                # finalizing
                payload = {'status': 'processing'}
                if use_redis and redis_client:
                    try:
                        redis_client.set(f'progress:{job_id}', json.dumps(payload))
                    except Exception:
                        pass
        except Exception:
            pass

    opts['progress_hooks'] = [_progress_hook]

    try:
        # For YouTube videos, try to extract cookies from browser
        if 'youtube' in url or 'youtu.be' in url:
            try:
                with YoutubeDL({'cookies_from_browser': ('chrome',)}) as temp_ydl:
                    # This will extract cookies if available
                    pass
            except Exception:
                pass  # If cookie extraction fails, continue without them
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        raise RuntimeError(f'yt-dlp failed: {str(e)}') from e

    # For audio with FFmpegExtractAudio, the actual file may have a different extension
    # Try to find the real file: if audio, look for .mp3; otherwise use prepare_filename result
    if kind == 'audio' and not os.path.exists(filename):
        # Try common audio extensions
        base_name = os.path.splitext(filename)[0]
        for ext in ['.mp3', '.m4a', '.wav', '.aac', '.opus']:
            alt_path = base_name + ext
            if os.path.exists(alt_path):
                filename = alt_path
                break
        else:
            # If still not found, list directory and find most recent file with audio extension
            try:
                audio_exts = {'.mp3', '.m4a', '.wav', '.aac', '.opus', '.flac', '.ogg'}
                files = [
                    os.path.join(DOWNLOAD_DIR, f) 
                    for f in os.listdir(DOWNLOAD_DIR) 
                    if os.path.splitext(f)[1].lower() in audio_exts
                ]
                if files:
                    filename = max(files, key=os.path.getctime)
            except Exception:
                pass

    if not os.path.exists(filename):
        raise RuntimeError(f'Download completed but file not found at {filename}. Expected downloads in {DOWNLOAD_DIR}')

    # cleanup cookiefile
    if cookiefile and os.path.exists(cookiefile):
        try:
            os.remove(cookiefile)
        except Exception:
            pass

    # write result key (if Redis available and enabled)
    if use_redis and redis_client:
        try:
            redis_client.set(f'result:{job_id}', filename)
            redis_client.set(f'progress:{job_id}', json.dumps({'status': 'finished'}))
        except Exception:
            pass
    return filename
