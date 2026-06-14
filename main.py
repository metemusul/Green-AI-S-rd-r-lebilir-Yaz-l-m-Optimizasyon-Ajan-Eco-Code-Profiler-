from __future__ import annotations
"""
main.py
=======
Eco-Code Profiler -- Ana Orkestrator

Surec akisi:
  1. Logging yapilandirmasi
  2. Hedef kodu profille (orijinal, verimsiz)
  3. EcoAgent ile LLM optimizasyonu
  4. Optimize kodu kaydet
  5. Optimize kodu profille
  6. Performans karsilastirmasi yap
  7. Green Report uret

Kullanim:
  python main.py
"""
import os
import sys

# Windows konsolunda UTF-8 zorla
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # Python < 3.7 fallback
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import logging
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging yapilandirmasi
# ---------------------------------------------------------------------------
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
)
DATE_FORMAT = "%H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    """Uygulama genelinde logging yapılandır."""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Harici kütüphane loglarını kısıtla
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Proje modülleri
# ---------------------------------------------------------------------------
from eco_agent import EcoAgent
from green_reporter import compare_performance, generate_report
from profiler_engine import profile_code, profile_code_string

logger = logging.getLogger("main")

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).parent.resolve()
TARGET_FILE = PROJECT_DIR / "target_code.py"
OPTIMIZED_FILE = PROJECT_DIR / "optimized_code.py"
REPORT_FILE = PROJECT_DIR / "green_report.md"

BANNER = """
+==================================================================+
|       [*]  ECO-CODE PROFILER  --  Green AI v1.0  [*]           |
|       Surdurulebilir Yazilim Optimizasyon Ajani                  |
|       Model: llama-3.3-70b-versatile  via  Groq API             |
+==================================================================+
"""

SEPARATOR = "-" * 68


# ---------------------------------------------------------------------------
# Yardımcı — adım başlığı yazdırıcı
# ---------------------------------------------------------------------------
def _step(number: int, title: str) -> None:
    logger.info("")
    logger.info(SEPARATOR)
    logger.info("ADIM %d: %s", number, title)
    logger.info(SEPARATOR)


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main() -> int:
    """
    Eco-Code Profiler'ı uçtan uca çalıştır.

    Returns
    -------
    int
        0 → başarı, 1 → hata
    """
    setup_logging()
    print(BANNER)
    wall_start = time.perf_counter()

    # ------------------------------------------------------------------ #
    # ADIM 1 — Hedef dosya kontrolü
    # ------------------------------------------------------------------ #
    _step(1, "Hedef Dosya Kontrolü")

    if not TARGET_FILE.exists():
        logger.error("Hedef dosya bulunamadı: %s", TARGET_FILE)
        return 1

    logger.info("Hedef dosya bulundu → %s", TARGET_FILE.name)
    source_code = TARGET_FILE.read_text(encoding="utf-8")
    logger.info("Kaynak kod yüklendi — %d satır, %d karakter",
                source_code.count("\n"), len(source_code))

    # ------------------------------------------------------------------ #
    # ADIM 2 — Orijinal kod profili
    # ------------------------------------------------------------------ #
    _step(2, "Orijinal Kod Profili (Verimsiz Algoritma)")

    logger.info("Profiling baslatiliyor -- lutfen bekleyin...")
    original_profile = profile_code(TARGET_FILE, func_name="run_wasteful_algorithms")

    if not original_profile.is_successful:
        logger.error("Orijinal profil basarisiz: %s", original_profile.error)
        return 1

    logger.info("[PROFIL] Orijinal Profil Sonuclari:")
    for line in original_profile.summary().splitlines():
        logger.info("   %s", line)

    # ------------------------------------------------------------------ #
    # ADIM 3 — LLM Optimizasyonu
    # ------------------------------------------------------------------ #
    _step(3, "LLM Optimizasyonu (Groq / llama-3.3-70b-versatile)")

    try:
        agent = EcoAgent()
        optimized_code = agent.optimize_code(source_code)
    except EnvironmentError as exc:
        logger.error("API yapilandirma hatasi: %s", exc)
        logger.error("Lutfen .env dosyasinda GROQ_API_KEY degerini ayarlayin.")
        return 1
    except RuntimeError as exc:
        logger.error("LLM optimizasyon hatasi: %s", exc)
        return 1

    logger.info("[OK] Optimizasyon basarili -- %d karakter uretildi.", len(optimized_code))

    # ------------------------------------------------------------------ #
    # ADIM 4 — Optimize kodu kaydet
    # ------------------------------------------------------------------ #
    _step(4, "Optimize Kodu Kaydetme")

    saved_path = agent.save_optimized_code(optimized_code, output_path=OPTIMIZED_FILE)
    logger.info("Optimize kod kaydedildi -> %s", saved_path.name)

    # Ilk 10 satiri onizle
    preview_lines = optimized_code.strip().splitlines()[:10]
    logger.info("Kod onizleme (ilk 10 satir):")
    for i, line in enumerate(preview_lines, 1):
        logger.info("  %3d | %s", i, line)

    # ------------------------------------------------------------------ #
    # ADIM 5 — Optimize kod profili
    # ------------------------------------------------------------------ #
    _step(5, "Optimize Kod Profili")

    logger.info("Optimize kod profiling baslatiliyor...")
    optimized_profile = profile_code_string(
        source_code=optimized_code,
        func_name="run_optimized_algorithms",
        tmp_filename=str(OPTIMIZED_FILE),
    )

    if not optimized_profile.is_successful:
        logger.warning(
            "Optimize profil basarisiz: %s -- manuel olcum kullaniliyor.",
            optimized_profile.error,
        )
        # Fallback -- dogrudan dosyadan profil al
        optimized_profile = profile_code(OPTIMIZED_FILE, func_name="run_optimized_algorithms")

    logger.info("[PROFIL] Optimize Profil Sonuclari:")
    for line in optimized_profile.summary().splitlines():
        logger.info("   %s", line)

    # ------------------------------------------------------------------ #
    # ADIM 6 — Performans karşılaştırması
    # ------------------------------------------------------------------ #
    _step(6, "Performans Karşılaştırması & Enerji Hesabı")

    comparison = compare_performance(original_profile, optimized_profile)

    logger.info("[RAPOR] Karsilastirma Ozeti:")
    logger.info("   Hiz artisi     : %.2fx daha hizli", comparison.speedup_ratio)
    logger.info("   Sure azalmasi  : %.1f%%", comparison.time_reduction_pct)
    logger.info("   Bellek azalmasi: %.1f%%", comparison.memory_reduction_pct)
    logger.info(
        "   Enerji tasarrufu (1M cagri): %s Joule",
        f"{comparison.energy_saved_joules:,.0f}",
    )
    logger.info(
        "   CO2 azalmasi (1M cagri): %.2f gram",
        comparison.co2_saved_grams,
    )

    # ------------------------------------------------------------------ #
    # ADIM 7 — Green Report üretimi
    # ------------------------------------------------------------------ #
    _step(7, "Green Sustainability Report Üretimi")

    report_path = generate_report(
        comparison=comparison,
        old_code_path=TARGET_FILE.name,
        new_code_path=OPTIMIZED_FILE.name,
        output_path=str(REPORT_FILE),
        optimized_code_snippet=optimized_code,
    )

    logger.info("[OK] Rapor basariyla olusturuldu -> %s", report_path.name)

    # ------------------------------------------------------------------ #
    # Genel özet
    # ------------------------------------------------------------------ #
    wall_elapsed = time.perf_counter() - wall_start
    logger.info("")
    logger.info("=" * 68)
    logger.info("[BITTI] ECO-CODE PROFILER TAMAMLANDI")
    logger.info("=" * 68)
    logger.info("   Toplam sure         : %.2f saniye", wall_elapsed)
    logger.info("   Uretilen dosyalar   :")
    logger.info("     * %s", OPTIMIZED_FILE.name)
    logger.info("     * %s", REPORT_FILE.name)
    logger.info("")
    logger.info("   [YESIL] Sonuc: Bu optimizasyon 1 milyon cagrida")
    logger.info("      %.2f gram CO2 emisyonunu engeller.", comparison.co2_saved_grams)
    logger.info(
        "      (%s Joule enerji tasarrufu)", f"{comparison.energy_saved_joules:,.0f}"
    )
    logger.info("=" * 68)

    return 0


# ---------------------------------------------------------------------------
# Giriş noktası
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
