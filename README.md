# 🩺 API Health Prober

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

Serverlar, mikroservislar va tashqi REST API larning uzluksiz ishlashini (uptime), kechikishini (latency percentiles p50/p95/p99) va SSL sertifikatlari tugash muddatini parallel sinovdan o'tkazuvchi asinxron sintetik monitoring CLI vositasi va Python kutubxonasi.

---

## 🌟 Imkoniyatlari

- **Yuqori tezlikdagi Asinxron Tekshiruv:** O'nlab yoki yuzlab endpointlarni bir vaqtda parallel so'rov orqali zudlik bilan tekshiradi.
- **Kechikish Statistikasi:** Har bir so'rov vaqtini o'lchaydi hamda p50, p95 latentlik foizlarini hisoblaydi.
- **SSL/TLS Sertifikat Tugashini Aniqlash:** HTTPS domenlarning sertifikati tugashiga necha kun qolganini avtomatik ko'rsatadi.
- **Tana (Body) Assertion:** Javob ichida kerakli kalit so'z (`{"status": "ok"}`) mavjudligini tasdiqlaydi.
- **CI/CD Integratsiyasi:** Xatolik aniqlanganda `exit code 1` qaytaradi, bu esa avtomatlashtirilgan pipeline'larda xatoliklarni to'xtatishga yordam beradi.
- **Zero-Dependency:** Tashqi paketlar talab etilmaydi.

---

## 🚀 O'rnatish

```bash
git clone https://github.com/afzalbek-dev/api-health-prober.git
cd api-health-prober
pip install .
```

---

## 💻 CLI Foydalanish

### 1. Bitta URL ni tekshirish
```bash
api-health-prober --url https://api.github.com
```

### 2. Konfiguratsiya fayli orqali tekshirish
`endpoints.json`:
```json
[
  {
    "name": "Auth Service",
    "url": "https://auth.example.com/health",
    "expected_status": 200,
    "keyword_assertion": "ok",
    "check_ssl": true
  },
  {
    "name": "Payment Gateway",
    "url": "https://payment.example.com/ping",
    "expected_status": 200
  }
]
```

Tekshiruvni ishga tushirish:
```bash
api-health-prober --config endpoints.json --concurrency 5
```

Chiqish namunasi:
```text
=======================================================
📊 API HEALTH PROBE REPORT
=======================================================
✅ [Auth Service] https://auth.example.com/health -> 142.5ms (HTTP 200, SSL: 68d)
✅ [Payment Gateway] https://payment.example.com/ping -> 89.2ms (HTTP 200, SSL: 120d)
-------------------------------------------------------
Total: 2 | Healthy: 2 | Unhealthy: 0
Latency Percentiles: p50=89.2ms, p95=142.5ms
=======================================================
```

---

## 🧪 Testlash

```bash
python3 -m unittest discover tests -v
```

---

## 📄 Litsenziya

MIT License. Muallif: [Afzalbek](https://github.com/afzalbek-dev).
