# 🎬 Media Downloader

A beautiful, modern web application for downloading videos and audio from 1000+ platforms instantly.

**Supported platforms:** YouTube, TikTok, Instagram, VK, SoundCloud, Spotify, Pinterest, and many more via `yt-dlp`.

## ✨ Features

- 🎨 **Modern Dark UI** — Beautiful glassmorphism design with smooth animations
- ⚡ **Instant Downloads** — Synchronous download with real-time progress
- 🎯 **Multi-Platform Support** — Auto-detect or manually select platform (YouTube, TikTok, Instagram, VK, SoundCloud, Spotify, Pinterest, etc.)
- 🎬 **Video & Audio** — Download as video or convert to MP3
- 📱 **Responsive Design** — Works perfectly on desktop, tablet, and mobile
- 🐳 **Docker Ready** — One-command deployment with Docker Compose
- 🔒 **No Redis Required** — Synchronous mode works without external dependencies

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended) — https://www.docker.com/products/docker-desktop/
- OR Python 3.10+, FFmpeg, and Redis (for local development)

### Deploy with Docker Compose (Recommended)

```bash
git clone <your-repo-url>
cd 232
docker compose up --build -d
```

Then open **http://localhost:5000** in your browser.

### Local Development (without Docker)

```bash
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe web_app.py
```

Visit **http://localhost:8080**.

## 📋 Requirements

- **Python 3.10+**
- **FFmpeg** (for audio conversion) — Install and add to PATH
- **Redis** (optional, for background jobs)

## 🛠️ Project Structure

```
232/
├── web_app.py           # Flask web application
├── downloader.py        # yt-dlp wrapper with error handling
├── tasks.py             # RQ task definitions (optional)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image
├── docker-compose.yml   # Multi-service orchestration
├── Procfile             # Heroku deployment config
├── .env.example         # Environment template
└── README.md            # This file
```

## 🐳 Docker Compose Services

- **web** — Flask app + gunicorn on port 5000
- **redis** — Cache & job queue (port 6379)
- **worker** — RQ background worker (optional for future async jobs)

## 📦 Dependencies

- `Flask==2.3.2` — Web framework
- `yt-dlp` — Media downloader
- `redis>=4.5.0` — Cache/queue backend
- `rq>=1.11.1` — Job queue
- `gunicorn==21.2.0` — Production server

## 🌐 Deployment

### Heroku

```bash
heroku create <app-name>
heroku addons:create heroku-redis:mini
git push heroku main
heroku open
```

### VPS / Self-Hosted

1. Install Docker & Docker Compose
2. Clone repository
3. Configure `.env` (Redis URL, port, max file size)
4. Run `docker compose up --build -d`
5. Set up Nginx reverse proxy (optional)
6. Enable HTTPS with Let's Encrypt (recommended)

### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
REDIS_URL=redis://localhost:6379/0
MAX_FILESIZE=100M
PORT=5000
```

## 🎨 Design Highlights

- **Glassmorphism** — Modern frosted glass effect
- **Gradient Typography** — Cyan-to-purple text gradients
- **Smooth Animations** — Floating logo, pulsing spinner, wave button effects
- **Dark Theme** — Eye-friendly night mode
- **Responsive Layout** — Mobile-first design

## ⚠️ Legal Notice

This tool is provided for **lawful purposes only**. Ensure you:
- Have permission to download the content
- Respect platform terms of service
- Follow copyright laws in your jurisdiction
- Use only for personal, non-commercial purposes where applicable

## 🔧 Troubleshooting

### Port already in use
Change port in `docker-compose.yml` (e.g., `3000:8080`) or `.env` file.

### FFmpeg not found
- **Windows:** Download from https://ffmpeg.org/download.html and add to PATH
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### Download fails
- Check that the URL is valid and the platform is supported
- Some platforms require authentication (cookies/login)
- Very large files may timeout (increase timeout in `downloader.py`)

## 📈 Future Enhancements

- [ ] Background job queue with progress tracking
- [ ] Download history / favorites
- [ ] Batch downloads
- [ ] S3 / cloud storage integration
- [ ] User authentication & accounts
- [ ] Admin panel
- [ ] API endpoints for programmatic access

## 📝 License

MIT License — Feel free to use, modify, and distribute.

## 🤝 Contributing

Issues and pull requests are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues, questions, or feedback, open an issue on GitHub.

---

**Made with ❤️ using Flask, yt-dlp, and Docker**
