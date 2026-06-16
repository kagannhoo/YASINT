# Kaynakça

YASINT, aşağıdaki açık kaynak projeler, kütüphaneler ve harici servisler üzerine inşa edilmiştir. Bu liste, kullanılan kaynaklara atıf ve şeffaflık amacıyla tutulur.

## Proje

| Kaynak | Açıklama | Bağlantı |
|--------|----------|----------|
| **YASINT** | Yet Another Source Intelligence Tool — pasif OSINT kişi analiz platformu | https://github.com/kagannhoo/YASINT |

**Geliştirici:** [kagannhoo](https://github.com/kagannhoo)

---

## OSINT araçları ve modüller

| Araç / Servis | Kullanım alanı | Lisans / erişim | Bağlantı |
|---------------|----------------|-----------------|----------|
| **Maigret** | 3000+ sitede kullanıcı adı taraması | MIT | https://github.com/soxoj/maigret |
| **Holehe** | E-posta kayıt tespiti (120+ site) | GNU GPL-3.0 | https://github.com/megadose/holehe |
| **Sherlock** | Kullanıcı adı araması (yedek / referans) | MIT | https://github.com/sherlock-project/sherlock |
| **DeepFace** | Yüz analizi (yaş, cinsiyet, duygu) | MIT | https://github.com/serengil/deepface |
| **ExifTool** | Fotoğraf EXIF / GPS metadata | Artistic License 2.0 | https://exiftool.org |
| **Nmap** | Port taraması ve ağ keşfi | Nmap Public Source License | https://nmap.org |
| **phonenumbers** | Telefon numarası doğrulama ve coğrafi bilgi | Apache 2.0 | https://github.com/daviddrysdale/python-phonenumbers |
| **python-whois** | WHOIS sorguları | MIT | https://github.com/richardpenman/whois |
| **dnspython** | DNS kayıt sorguları | ISC | https://www.dnspython.org |

---

## Harici API'ler ve web servisleri

| Servis | Kullanım alanı | API anahtarı | Bağlantı |
|--------|----------------|--------------|----------|
| **GitHub API** | Profil, kod arama, kullanıcı keşfi | Gerekmez (rate limit) | https://docs.github.com/en/rest |
| **XposedOrNot** | E-posta veri ihlali kontrolü | Gerekmez | https://xposedornot.com |
| **emailrep.io** | E-posta itibar ve ihlal referansları | Gerekmez | https://emailrep.io |
| **ip-api.com** | IP coğrafi konum (GeoIP) | Gerekmez (ücretsiz katman) | https://ip-api.com |
| **crt.sh** | Sertifika şeffaflığı / alt alan adı keşfi | Gerekmez | https://crt.sh |
| **Gravatar** | E-posta → profil fotoğrafı | Gerekmez | https://gravatar.com |
| **DuckDuckGo** | OSINT dork araması | Gerekmez | https://duckduckgo.com |
| **grep.app** | Açık kaynak kodda arama | Gerekmez | https://grep.app |
| **decapi.me** | Twitch kullanıcı adı doğrulama | Gerekmez | https://decapi.me |
| **Keybase API** | Kullanıcı adı doğrulama | Gerekmez | https://keybase.io |
| **Hacker News Firebase API** | HN kullanıcı doğrulama | Gerekmez | https://github.com/HackerNews/API |
| **Anthropic Claude** | AI profil özeti (opsiyonel) | Kullanıcı anahtarı | https://www.anthropic.com |

### Platform doğrulama API'leri

YASINT, kullanıcı adı taramasında aşağıdaki platformların resmi veya kamuya açık API'lerini kullanır:

GitHub · Reddit · GitLab · Dev.to · Twitch · Steam · Telegram · SoundCloud · Linktree

---

## Altyapı ve framework'ler

### Backend

| Teknoloji | Kullanım | Bağlantı |
|-----------|----------|----------|
| Python 3.11 | Çalışma ortamı | https://www.python.org |
| FastAPI | REST API | https://fastapi.tiangolo.com |
| Celery | Arka plan görev kuyruğu | https://docs.celeryq.dev |
| Redis | Mesaj broker / önbellek | https://redis.io |
| PostgreSQL | Kalıcı veri depolama | https://www.postgresql.org |
| SQLAlchemy | ORM | https://www.sqlalchemy.org |
| Alembic | Veritabanı migration | https://alembic.sqlalchemy.org |
| httpx | HTTP istemcisi | https://www.python-httpx.org |
| ReportLab | PDF rapor üretimi | https://www.reportlab.com |
| Folium | Harita görselleştirme | https://python-visualization.github.io/folium |
| OpenCV (headless) | Görüntü işleme | https://opencv.org |
| Pillow | Görüntü okuma | https://python-pillow.org |
| BeautifulSoup4 | HTML ayrıştırma | https://www.crummy.com/software/BeautifulSoup |
| Geopy | Coğrafi hesaplamalar | https://github.com/geopy/geopy |
| pytest | Test çerçevesi | https://pytest.org |

### Frontend

| Teknoloji | Kullanım | Bağlantı |
|-----------|----------|----------|
| Next.js 14 | Web uygulaması çerçevesi | https://nextjs.org |
| React 18 | UI kütüphanesi | https://react.dev |
| TypeScript | Tip güvenliği | https://www.typescriptlang.org |
| Tailwind CSS | Stil | https://tailwindcss.com |
| Framer Motion | Animasyonlar | https://www.framer.com/motion |
| Leaflet / react-leaflet | Harita bileşenleri | https://leafletjs.com |
| React Flow | Ağ grafiği görselleştirme | https://reactflow.dev |
| Lucide React | İkonlar | https://lucide.dev |

### DevOps

| Teknoloji | Kullanım | Bağlantı |
|-----------|----------|----------|
| Docker | Konteynerizasyon | https://www.docker.com |
| Docker Compose | Çoklu servis orkestrasyonu | https://docs.docker.com/compose |

---

## Atıf notu

Bu projeyi akademik veya teknik bir çalışmada kullanıyorsanız, aşağıdaki biçim önerilir:

```
kagannhoo. (2026). YASINT — Yet Another Source Intelligence Tool [Computer software].
https://github.com/kagannhoo/YASINT
```

Harici servislerin kullanım koşullarına ve rate limitlerine uyun. YASINT yalnızca pasif, açık kaynak istihbarat amaçlı tasarlanmıştır.
