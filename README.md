# YASINT

**Y**et **A**nother **S**ource **I**ntelligence **T**ool — pasif OSINT tabanlı kişi analiz platformu. Kullanıcı elindeki verileri (fotoğraf, kullanıcı adı, IP, e-posta, telefon) sisteme girer; sistem bu verileri otomatik analiz eder ve dijital ayak izi raporu üretir.

## Özellikler

- **EXIF Analizi** — GPS, cihaz bilgisi, çekim zamanı
- **Yüz Analizi** — DeepFace ile yaş, cinsiyet, duygu tahmini
- **Kullanıcı Adı Taraması** — Maigret + API doğrulamalı platform taraması
- **IP Analizi** — GeoIP, WHOIS, Nmap port taraması (ücretsiz)
- **E-posta** — Holehe kayıt tespiti, Gravatar
- **Veri İhlali** — XposedOrNot + emailrep.io (ücretsiz, API anahtarı yok)
- **Domain / Paste / Dork** — crt.sh, GitHub, DuckDuckGo
- **Kimlik Dosyası** — Tüm bulguların birleşik özeti
- **Canlı Güncelleme** — WebSocket ile modül durumu
- **PDF/JSON Rapor** — İndirilebilir analiz raporları

## Teknoloji

| Katman | Teknolojiler |
|--------|-------------|
| Backend | Python 3.11, FastAPI, Celery, Redis, PostgreSQL |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| OSINT | Maigret, Holehe, Nmap, DeepFace, ExifTool |

## Hızlı Başlangıç (Docker)

```bash
git clone https://github.com/kagannhoo/YASINT.git
cd YASINT

cp .env.example .env
docker-compose up -d --build

# Frontend: http://localhost:3000
# API:       http://localhost:8000/docs
```

## Ortam Değişkenleri

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/osint_db
REDIS_URL=redis://localhost:6379/0
NMAP_PATH=nmap
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000
```

Ücretli API anahtarı gerekmez. Tüm ihlal ve itibar kontrolleri ücretsiz kaynaklarla çalışır.

## Test

```bash
cd backend
pytest tests/ -v
```

## Yasal Uyarı

Bu platform yalnızca yasal ve etik amaçlarla, açık kaynaklardan elde edilebilen bilgilerin analizi için tasarlanmıştır. KVKK, GDPR ve yerel yasalara uygun kullanım kullanıcının sorumluluğundadır.

## Lisans

MIT
