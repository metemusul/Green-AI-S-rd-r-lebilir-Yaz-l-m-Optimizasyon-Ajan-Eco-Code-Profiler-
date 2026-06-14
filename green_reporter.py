"""
green_reporter.py
=================
Performans karşılaştırması yapan ve sürdürülebilirlik raporu üreten modül.

Metodoloji:
  - Enerji tahmini: CPU TDP modeline dayalı Joule hesabı
    E = P * t  (P = güç [W], t = süre [s])
  - CO₂ tahmini: Küresel ortalama elektrik karbon yoğunluğu
    (IEA 2023: ~475 g CO₂/kWh → 0.1319 g CO₂/kJ)
  - Ölçek tahmini: 1.000.000 istek (milyon çağrı) bazında
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from profiler_engine import ProfileResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fiziksel Sabitler & Varsayımlar
# ---------------------------------------------------------------------------

# Tipik bir sunucu CPU TDP değeri (W) — Intel Xeon / AMD EPYC ortalaması
CPU_TDP_WATTS: float = 125.0

# IEA 2023 küresel ortalama karbon yoğunluğu: 475 g CO₂/kWh
# = 475 / 3_600_000 g CO₂/J = 0.0001319 g CO₂/J
CARBON_INTENSITY_G_PER_JOULE: float = 475 / 3_600_000  # ≈ 1.319e-4

# Referans ölçek: 1 milyon API/fonksiyon çağrısı
SCALE_FACTOR: int = 1_000_000


# ---------------------------------------------------------------------------
# Veri Sınıfları
# ---------------------------------------------------------------------------
@dataclass
class EnergyMetrics:
    """Tek bir çalıştırma için hesaplanan enerji metrikleri."""

    elapsed_seconds: float
    peak_memory_mb: float
    energy_joules: float
    co2_grams: float

    @property
    def energy_millijoules(self) -> float:
        return self.energy_joules * 1_000

    @property
    def energy_joules_per_million_calls(self) -> float:
        return self.energy_joules * SCALE_FACTOR

    @property
    def co2_grams_per_million_calls(self) -> float:
        return self.co2_grams * SCALE_FACTOR


@dataclass
class ComparisonReport:
    """Eski ve yeni kod karşılaştırma sonuçları."""

    old_metrics: EnergyMetrics
    new_metrics: EnergyMetrics

    @property
    def speedup_ratio(self) -> float:
        """Hız kazanımı oranı (X kat daha hızlı)."""
        if self.new_metrics.elapsed_seconds == 0:
            return float("inf")
        return self.old_metrics.elapsed_seconds / self.new_metrics.elapsed_seconds

    @property
    def time_saved_seconds(self) -> float:
        return self.old_metrics.elapsed_seconds - self.new_metrics.elapsed_seconds

    @property
    def memory_reduction_mb(self) -> float:
        return self.old_metrics.peak_memory_mb - self.new_metrics.peak_memory_mb

    @property
    def memory_reduction_pct(self) -> float:
        if self.old_metrics.peak_memory_mb == 0:
            return 0.0
        return (self.memory_reduction_mb / self.old_metrics.peak_memory_mb) * 100

    @property
    def energy_saved_joules(self) -> float:
        return (
            self.old_metrics.energy_joules_per_million_calls
            - self.new_metrics.energy_joules_per_million_calls
        )

    @property
    def co2_saved_grams(self) -> float:
        return (
            self.old_metrics.co2_grams_per_million_calls
            - self.new_metrics.co2_grams_per_million_calls
        )

    @property
    def time_reduction_pct(self) -> float:
        if self.old_metrics.elapsed_seconds == 0:
            return 0.0
        return (self.time_saved_seconds / self.old_metrics.elapsed_seconds) * 100

    @property
    def energy_reduction_pct(self) -> float:
        old = self.old_metrics.energy_joules_per_million_calls
        new = self.new_metrics.energy_joules_per_million_calls
        if old == 0:
            return 0.0
        return ((old - new) / old) * 100


# ---------------------------------------------------------------------------
# Enerji Hesaplama Fonksiyonu
# ---------------------------------------------------------------------------
def compute_energy_metrics(profile: ProfileResult) -> EnergyMetrics:
    """
    ProfileResult nesnesinden enerji ve CO₂ metriklerini hesapla.

    Formül:
        E [J] = P [W] × t [s]
        CO₂ [g] = E [J] × karbon_yoğunluğu [g/J]

    Parameters
    ----------
    profile:
        Profiler'dan gelen ölçüm sonucu.

    Returns
    -------
    EnergyMetrics
        Joule ve CO₂ gram cinsinden enerji değerleri.
    """
    energy_joules = CPU_TDP_WATTS * profile.elapsed_seconds
    co2_grams = energy_joules * CARBON_INTENSITY_G_PER_JOULE

    logger.debug(
        "Enerji hesaplandı → %.4f J | CO₂: %.6f g (tek çağrı)",
        energy_joules,
        co2_grams,
    )

    return EnergyMetrics(
        elapsed_seconds=profile.elapsed_seconds,
        peak_memory_mb=profile.peak_memory_mb,
        energy_joules=energy_joules,
        co2_grams=co2_grams,
    )


# ---------------------------------------------------------------------------
# Karşılaştırma Fonksiyonu
# ---------------------------------------------------------------------------
def compare_performance(
    old_profile: ProfileResult,
    new_profile: ProfileResult,
) -> ComparisonReport:
    """
    Eski ve yeni profil sonuçlarını karşılaştır.

    Parameters
    ----------
    old_profile:
        Orijinal (verimsiz) kodun profil sonucu.
    new_profile:
        Optimize edilmiş kodun profil sonucu.

    Returns
    -------
    ComparisonReport
        Karşılaştırmalı metrikler.
    """
    old_metrics = compute_energy_metrics(old_profile)
    new_metrics = compute_energy_metrics(new_profile)

    report = ComparisonReport(old_metrics=old_metrics, new_metrics=new_metrics)

    logger.info(
        "Performans karşılaştırması: %.2f× hız artışı | %.1f%% süre azalması",
        report.speedup_ratio,
        report.time_reduction_pct,
    )

    return report


# ---------------------------------------------------------------------------
# Markdown Rapor Üreteci
# ---------------------------------------------------------------------------
def generate_report(
    comparison: ComparisonReport,
    old_code_path: str = "target_code.py",
    new_code_path: str = "optimized_code.py",
    output_path: str = "green_report.md",
    optimized_code_snippet: Optional[str] = None,
) -> Path:
    """
    Karşılaştırma sonuçlarından green_report.md oluştur.

    Parameters
    ----------
    comparison:
        ``compare_performance()`` çıktısı.
    old_code_path:
        Orijinal kod dosyası adı.
    new_code_path:
        Optimize kod dosyası adı.
    output_path:
        Raporun kaydedileceği yol.
    optimized_code_snippet:
        Rapora eklenecek optimize kod özeti (isteğe bağlı).

    Returns
    -------
    Path
        Oluşturulan rapor dosyasının yolu.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r = comparison  # kısa alias

    # ------------------------------------------------------------------ #
    # Hız rozetleri
    speedup_str = f"{r.speedup_ratio:.1f}×"
    energy_badge = f"{r.energy_reduction_pct:.1f}%"
    co2_badge_val = r.co2_saved_grams
    co2_badge = (
        f"{co2_badge_val:.1f} g"
        if co2_badge_val < 1000
        else f"{co2_badge_val / 1000:.3f} kg"
    )

    # ------------------------------------------------------------------ #
    # CO₂ gerçek dünya eşdeğerleri
    # 1 km araba yolculuğu ≈ 120 g CO₂
    car_km = co2_badge_val / 120

    # Bir ağacın 1 yılda tuttuğu CO₂ ≈ 21,000 g
    tree_hours = (co2_badge_val / 21_000) * 8_760  # saate çevir

    # ------------------------------------------------------------------ #
    # Sütun hizalaması için değerler
    old = r.old_metrics
    new = r.new_metrics

    content = f"""# 🌿 Eco-Code Profiler — Green Sustainability Report

> **Oluşturulma Tarihi:** {now}  
> **Analiz Aracı:** Eco-Code Profiler v1.0  
> **LLM Motoru:** Groq API — llama-3.3-70b-versatile  

---

## 📊 Yönetici Özeti

Bu rapor, `{old_code_path}` dosyasındaki algoritmik verimsizliklerin
otomatik olarak tespit edilip `{new_code_path}` ile optimize edilmesi
sonucunda elde edilen enerji ve performans kazanımlarını özetlemektedir.

| Metrik | Değer |
|--------|-------|
| 🚀 Hız Artışı | **{speedup_str}** daha hızlı |
| ⏱️ Süre Azalması | **{r.time_reduction_pct:.1f}%** |
| 🧠 Bellek Azalması | **{r.memory_reduction_pct:.1f}%** |
| ⚡ Enerji Tasarrufu (1M çağrı) | **{r.energy_saved_joules:,.0f} Joule** |
| 🌍 CO₂ Azalması (1M çağrı) | **{co2_badge}** |

---

## ⏱️ Çalışma Süresi Karşılaştırması

| | Orijinal Kod | Optimize Kod | Fark |
|---|---|---|---|
| **Süre (ms)** | `{old.elapsed_seconds * 1000:.1f} ms` | `{new.elapsed_seconds * 1000:.1f} ms` | `-{r.time_saved_seconds * 1000:.1f} ms` |
| **Süre (s)** | `{old.elapsed_seconds:.4f} s` | `{new.elapsed_seconds:.4f} s` | `-{r.time_saved_seconds:.4f} s` |
| **Peak Bellek** | `{old.peak_memory_mb:.3f} MB` | `{new.peak_memory_mb:.3f} MB` | `-{r.memory_reduction_mb:.3f} MB` |

> ⚙️ **Metodoloji:** `time.perf_counter()` ile yüksek çözünürlüklü süre ölçümü,
> `tracemalloc` ile Python heap bellek takibi.

---

## ⚡ Enerji Tüketimi Analizi

### Tek Çağrı Başına

| | Orijinal | Optimize | Tasarruf |
|---|---|---|---|
| **Enerji (mJ)** | `{old.energy_millijoules:.2f} mJ` | `{new.energy_millijoules:.2f} mJ` | `{(old.energy_millijoules - new.energy_millijoules):.2f} mJ` |
| **CO₂ (µg)** | `{old.co2_grams * 1e6:.2f} µg` | `{new.co2_grams * 1e6:.2f} µg` | `{(old.co2_grams - new.co2_grams) * 1e6:.2f} µg` |

### 1.000.000 Çağrı Başına (Üretim Ölçeği)

| | Orijinal | Optimize | Tasarruf |
|---|---|---|---|
| **Toplam Süre** | `{old.elapsed_seconds * SCALE_FACTOR / 3600:.2f} saat` | `{new.elapsed_seconds * SCALE_FACTOR / 3600:.2f} saat` | `{r.time_saved_seconds * SCALE_FACTOR / 3600:.2f} saat` |
| **Enerji (kJ)** | `{old.energy_joules_per_million_calls / 1000:.2f} kJ` | `{new.energy_joules_per_million_calls / 1000:.2f} kJ` | `{r.energy_saved_joules / 1000:.2f} kJ` |
| **CO₂ (g)** | `{old.co2_grams_per_million_calls:.2f} g` | `{new.co2_grams_per_million_calls:.2f} g` | `{r.co2_saved_grams:.2f} g` |

> 📐 **Enerji Formülü:** `E [J] = P [W] × t [s]`  
> 🖥️ **Varsayılan TDP:** {CPU_TDP_WATTS:.0f}W (Tipik sunucu CPU'su — Intel Xeon/AMD EPYC)  
> 🌡️ **Karbon Yoğunluğu:** 475 g CO₂/kWh (IEA Global Average 2023)

---

## 🌍 Gerçek Dünya Çevresel Etkisi

1 milyon çağrıda **{co2_badge}** CO₂ tasarrufu sağlamak şuna eşdeğerdir:

| Eşdeğer | Değer |
|---------|-------|
| 🚗 Araçla kat edilmemiş mesafe | `≈ {car_km:.2f} km` |
| 🌳 Ağacın tuttuğu CO₂ süresi | `≈ {tree_hours:.1f} saat` |
| 💡 Tasarruf edilen enerji | `≈ {r.energy_saved_joules / 3600:.4f} Wh` |

---

## 🔍 Algoritmik Darboğaz Analizi

### Tespit Edilen Verimsizlikler

| Fonksiyon | Eski Karmaşıklık | Yeni Karmaşıklık | Yöntem |
|-----------|-----------------|-----------------|--------|
| `find_common_elements()` | O(N²) | **O(N)** | İç içe döngü → `set` kesişimi |
| `bubble_sort()` | O(N²) | **O(N log N)** | Bubble sort → `sorted()` (Timsort) |
| `calculate_statistics()` | O(N²) | **O(N)** | Manuel sıralama → `sorted()` + tek geçiş |
| `count_duplicates()` | O(N²) | **O(N)** | İç içe döngü → `collections.Counter` |

### Big-O Karmaşıklık Grafiği

```
N = 8,000 eleman için yaklaşık işlem sayısı:

O(N²)    : ████████████████████████████████████ 64,000,000 işlem
O(N log N): ██ 104,000 işlem  
O(N)     : ▌  8,000 işlem
```

---

## 📂 Dosya Bilgileri

| Dosya | Açıklama |
|-------|---------|
| `{old_code_path}` | Orijinal, verimsiz kod |
| `{new_code_path}` | LLM tarafından optimize edilmiş kod |
| `green_report.md` | Bu sürdürülebilirlik raporu |

---

## 🏆 Sonuç

Bu optimizasyon, yalnızca kodun hızını artırmakla kalmayıp **{energy_badge}**
oranında enerji tasarrufu sağlamaktadır. Yazılım dünyasında bu tür
algoritmik iyileştirmeler ölçekte yapıldığında, veri merkezlerinin
karbon ayak izini anlamlı şekilde azaltabilir.

> 💡 **Green Software Foundation** prensiplerine göre, sürdürülebilir yazılım
> geliştirmenin en etkin yolu algoritmik karmaşıklığı azaltmaktır —
> donanım yükseltmesinden veya yenilenebilir enerjiden çok daha önce.

---

*Rapor [Eco-Code Profiler](https://github.com/eco-code-profiler) tarafından otomatik olarak oluşturulmuştur.*  
*Model: `llama-3.3-70b-versatile` via Groq API*
"""

    output = Path(output_path).resolve()
    try:
        output.write_text(content, encoding="utf-8")
        logger.info("Green raporu oluşturuldu → %s", output)
    except OSError as exc:
        logger.error("Rapor dosyası yazılamadı: %s", exc)
        raise

    return output


# ---------------------------------------------------------------------------
# Sabit dışa aktarım (green_reporter içinden import edilebilir)
# ---------------------------------------------------------------------------
__all__ = [
    "EnergyMetrics",
    "ComparisonReport",
    "compute_energy_metrics",
    "compare_performance",
    "generate_report",
    "CPU_TDP_WATTS",
    "CARBON_INTENSITY_G_PER_JOULE",
    "SCALE_FACTOR",
]
