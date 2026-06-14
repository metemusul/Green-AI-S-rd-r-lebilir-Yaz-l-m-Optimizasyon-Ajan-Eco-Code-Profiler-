<div align="center">

# 🌿 Eco-Code Profiler
### Green AI & Sürdürülebilir Yazılım Optimizasyon Ajanı

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq_API-Llama_3.3-F55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Green Software](https://img.shields.io/badge/Green_Software-Foundation-16a34a?style=for-the-badge&logo=leaflet&logoColor=white)](https://greensoftware.foundation)

*Verimsiz kodu okur, düşünür ve daha yeşil bir geleceğe dönüştürür.*

</div>

---

## 🎯 Proje Amacı

**Eco-Code Profiler**, algoritmik açıdan verimsiz yazılmış Python kodunu otomatik olarak analiz eden, profilleyen ve yapay zeka destekli bir şekilde optimize eden otonom bir CLI aracıdır.

Bu araç, **Green Software Foundation** prensiplerini benimseyerek şu soruya yanıt arar:

> *"Yazılımımızın enerji tüketimini %X azaltırsak, küresel karbon emisyonuna katkımız ne olur?"*

### Çalışma Akışı

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  target_code.py │────▶│ profiler_engine  │────▶│   eco_agent.py  │
│  (O(N²) kötü   │     │  (süre + bellek  │     │  (Groq LLM ile  │
│   algoritma)   │     │   ölçümü)        │     │   optimizasyon) │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                        ┌──────────────────┐     ┌────────▼────────┐
                        │ green_report.md  │◀────│ green_reporter  │
                        │  (CO₂ & enerji  │     │  (karşılaştırma │
                        │   raporu)        │     │   + CO₂ hesap)  │
                        └──────────────────┘     └─────────────────┘
```

---

## 🌍 Çevresel Etki Vizyonu

Yazılım endüstrisi, küresel elektrik tüketiminin yaklaşık **%5-9**'undan sorumludur ve bu oran her yıl büyümektedir. Ancak bu sorunun çözümü büyük ölçüde gözden kaçan bir yerde yatmaktadır: **algoritmik verimsizlik**.

Bir `O(N²)` döngüyü `O(N)` set operasyonuna dönüştürmek, aynı veri merkezini güneş panelleriyle donatmaktan çok daha az maliyetli ve çoğu zaman daha etkilidir. **Eco-Code Profiler**, bu dönüşümü otonom ve ölçeklenebilir bir şekilde gerçekleştirerek:

- 🔋 **CPU döngülerini azaltır** → doğrudan enerji tasarrufu
- 🧠 **Bellek tahsislerini düşürür** → RAM enerji tüketimi azalır
- 🌡️ **CO₂ emisyonunu hesaplar** → gerçek çevresel etki görünür kılar
- 📊 **Raporla belgelendirir** → sürdürülebilirlik kararlarına veri sağlar

> *"En yeşil kod, çalışmayan kodun değil — en verimli şekilde çalışan koddur."*

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Kullanım Amacı |
|-----------|---------------|
| **[LangChain](https://langchain.com)** | LLM orkestrasyonu ve prompt yönetimi |
| **[Groq API](https://groq.com)** | `llama-3.3-70b-versatile` modeliyle hızlı inference |
| **[tracemalloc](https://docs.python.org/3/library/tracemalloc.html)** | Python heap bellek profili |
| **[time.perf_counter](https://docs.python.org/3/library/time.html)** | Yüksek çözünürlüklü süre ölçümü |
| **[python-dotenv](https://pypi.org/project/python-dotenv/)** | Güvenli API anahtar yönetimi |
| **[memory-profiler](https://pypi.org/project/memory-profiler/)** | Satır bazlı bellek analizi |

---

## 📁 Proje Yapısı

```
eco-code-profiler/
│
├── 📄 main.py                  # Ana orkestratör — tüm süreci yönetir
├── 🎯 target_code.py           # Bilerek verimsiz yazılmış O(N²) kod
├── 📊 profiler_engine.py       # Süre ve bellek ölçüm modülü
├── 🤖 eco_agent.py             # LangChain + Groq optimizasyon ajanı
├── 📈 green_reporter.py        # CO₂/enerji hesaplama + rapor üretici
│
├── 📋 requirements.txt         # Python bağımlılıkları
├── 🔐 .env                     # API anahtarları (git'e eklenmez!)
├── 📝 .gitignore               # Git dışlama kuralları
└── 📖 README.md                # Bu dosya
│
│   [Otomatik oluşturulur]
├── ✅ optimized_code.py         # LLM tarafından optimize edilmiş kod
└── 🌿 green_report.md          # Sürdürülebilirlik raporu
```

---

## 🚀 Kurulum ve Kullanım

### Ön Gereksinimler

- Python 3.10 veya üzeri
- Ücretsiz [Groq API](https://console.groq.com) hesabı

### 1. Repoyu Klonla

```bash
git clone https://github.com/yourusername/eco-code-profiler.git
cd eco-code-profiler
```

### 2. Sanal Ortam Oluştur ve Aktif Et

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 4. API Anahtarını Ayarla

```bash
# .env dosyası oluştur
echo GROQ_API_KEY=your_api_key_here > .env
```

> 🔑 Groq API anahtarını [console.groq.com](https://console.groq.com) adresinden ücretsiz alabilirsiniz.

### 5. Çalıştır

```bash
python main.py
```

### Beklenen Çıktı

```
╔══════════════════════════════════════════════════════════════════╗
║          🌿  ECO-CODE PROFILER  —  Green AI v1.0  🌿           ║
╚══════════════════════════════════════════════════════════════════╝

23:10:05 | INFO     | main                 | ADIM 1: Hedef Dosya Kontrolü
23:10:05 | INFO     | main                 | Hedef dosya bulundu → target_code.py
23:10:05 | INFO     | main                 | ADIM 2: Orijinal Kod Profili
...
23:10:12 | INFO     | main                 | 📊 Orijinal: 2.341 s | 3.2 MB
23:10:45 | INFO     | main                 | ✅ Optimizasyon tamamlandı
...
23:10:46 | INFO     | main                 | 📈 Hız artışı: 23.4× daha hızlı
23:10:46 | INFO     | main                 | 🌿 CO₂ azalması: 823.5 gram/1M çağrı
23:10:46 | INFO     | main                 | 📄 green_report.md oluşturuldu
```

---

## 📊 Örnek Rapor Çıktısı

Araç çalıştırıldıktan sonra `green_report.md` şu metrikleri içerir:

| Metrik | Örnek Değer |
|--------|-------------|
| Hız Artışı | **18-25×** daha hızlı |
| Süre Azalması | **%94-96** |
| Bellek Azalması | **%60-80** |
| CO₂ Azalması (1M çağrı) | **~500-1000 gram** |
| Enerji Tasarrufu (1M çağrı) | **~3000-7000 kJ** |

---

## 🔬 Metodoloji

### Enerji Hesabı

```
E [Joule] = P_cpu [Watt] × t [saniye]
```

- **CPU TDP:** 125W (tipik sunucu CPU — Intel Xeon / AMD EPYC)
- **Karbon Yoğunluğu:** 475 g CO₂/kWh (**IEA Global Average 2023**)

### Algoritmik Karmaşıklık İyileştirmeleri

| Fonksiyon | Öncesi | Sonrası |
|-----------|--------|---------|
| Ortak eleman bulma | O(N²) iç içe döngü | O(N) set operasyonu |
| Sıralama | O(N²) Bubble Sort | O(N log N) Timsort |
| İstatistik | O(N²) manuel sıralama | O(N) tek geçiş |
| Tekrar sayımı | O(N²) iç içe döngü | O(N) Counter |

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-optimization`)
3. Commit edin (`git commit -m 'feat: add amazing optimization'`)
4. Push edin (`git push origin feature/amazing-optimization`)
5. Pull Request açın

---

## 📜 Lisans

Bu proje **MIT Lisansı** altında dağıtılmaktadır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

```
MIT License

Copyright (c) 2025 Eco-Code Profiler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<div align="center">

**🌱 Daha iyi kod, daha yeşil dünya.**

*[Green Software Foundation](https://greensoftware.foundation) prensipleri ile geliştirilmiştir.*

</div>
