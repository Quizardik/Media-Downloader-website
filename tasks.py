import os
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
from downloader import download_media

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(REDIS_URL)
q = Queue('downloads', connection=redis_conn)


def enqueue_download(url: str, kind: str = 'video', cookies_text: str = None, max_filesize: str = None):
    """Enqueue a background download job. Returns RQ job id."""
    job = q.enqueue(download_media, url, kind, None, cookies_text, max_filesize, job_timeout=60*60)
    return job.get_id()
