# 🛒 PricePulse

Compare grocery prices across **Blinkit**, **Zepto**, **Instamart**, and **BigBasket** with real-time price tracking, analytics, price history, and smart savings.

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Django](https://img.shields.io/badge/Django-6-092E20?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

---

# 🌐 Live Demo

🚀 Frontend: https://pricepulse.vercel.app *(Coming Soon)*

🔗 Backend API: https://pricepulse.onrender.com *(Coming Soon)*

---

# ✨ Features

🛒 Compare grocery prices across multiple providers

⚡ Multi-provider architecture (Blinkit, Zepto, Instamart, BigBasket)

📈 Price history tracking

💰 Smart savings calculation

📊 Analytics dashboard

❤️ Wishlist

🔔 Price drop alerts

🔍 Intelligent product search

⚙️ Hybrid provider fallback

🐳 Docker support

---

# 🏗️ Architecture

```text
                React + Vite
                      │
                 REST API
                      │
            Django REST Framework
                      │
               Price Service
                      │
             Provider Manager
        ┌────────┬────────┬────────┬────────┐
        │        │        │        │
    Blinkit   Zepto  Instamart BigBasket
                      │
                 PostgreSQL
                      │
               Redis + Celery
```

---

# 📊 Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | React, Vite, React Query |
| Backend | Django, Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis |
| Background Jobs | Celery |
| Containerization | Docker |
| Automation | Playwright |
| Authentication | JWT |

---

# 📂 Project Structure

```text
pricepulse/

├── backend/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── catalog/
│   │   ├── pricing/
│   │   └── notifications/
│   └── config/
│
├── frontend1/
│   └── frontend/
│
├── docs/
│
├── docker-compose.yml
│
└── README.md
```

---

# 🚀 Quick Start

Clone

```bash
git clone https://github.com/<username>/PricePulse.git

cd PricePulse
```

Run

```bash
docker compose up --build
```

Frontend

```
http://localhost:5173
```

Backend

```
http://localhost:8000
```

---

# 🛍️ Supported Providers

| Provider | Status |
|----------|--------|
| Blinkit | ✅ |
| Zepto | ✅ |
| Instamart | ✅ |
| BigBasket | ✅ |
| Hybrid Fallback | ✅ |

---

# 📈 Highlights

- Multi-provider normalization
- Provider caching
- Background price collection
- Concurrent provider fetching
- Price analytics
- Historical price tracking
- JWT Authentication
- Dockerized development

---

# 🚀 Deployment

Frontend → Vercel

Backend → Render

Database → Neon PostgreSQL

Redis → Upstash Redis

---

# 🔮 Future Improvements

- Amazon Fresh integration
- Flipkart Minutes integration
- GTIN-based matching
- AI-powered recommendations
- Smarter price predictions

---

# 📄 License

MIT License © 2026 PricePulse

If you found this project useful, consider giving it a ⭐