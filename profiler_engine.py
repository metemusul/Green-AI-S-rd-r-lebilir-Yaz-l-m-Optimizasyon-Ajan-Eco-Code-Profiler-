"""
profiler_engine.py
==================
Hedef Python kodunun çalışma süresi ve bellek tüketimini ölçen modül.

Araçlar:
  - time.perf_counter() → yüksek çözünürlüklü süre ölçümü
  - tracemalloc         → Python nesnelerinin anlık bellek kullanımı

Notlar:
  - subprocess ile izole çalıştırma (ana süreç kirlenmez)
  - ProfileResult dataclass ile temiz API
"""

from __future__ import annotations

import importlib.util
import logging
import subprocess
import sys
import time
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Veri Sınıfları
# ---------------------------------------------------------------------------
@dataclass
class ProfileResult:
    """Tek bir profil ölçümünün sonuçlarını taşır."""

    filepath: str
    elapsed_seconds: float
    peak_memory_mb: float
    current_memory_mb: float
    return_value: Any = field(default=None, repr=False)
    error: str | None = None

    # --- Türetilmiş özellikler ------------------------------------------- #
    @property
    def elapsed_ms(self) -> float:
        return self.elapsed_seconds * 1_000

    @property
    def is_successful(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        status = "✅ Başarılı" if self.is_successful else f"❌ Hata: {self.error}"
        return (
            f"Dosya          : {self.filepath}\n"
            f"Durum          : {status}\n"
            f"Süre           : {self.elapsed_ms:.1f} ms  ({self.elapsed_seconds:.4f} s)\n"
            f"Peak Bellek    : {self.peak_memory_mb:.3f} MB\n"
            f"Anlık Bellek   : {self.current_memory_mb:.3f} MB"
        )


# ---------------------------------------------------------------------------
# Yardımcı — dinamik modül yükleyici
# ---------------------------------------------------------------------------
def _load_module_from_path(filepath: str | Path):
    """Bir .py dosyasını dinamik olarak modül olarak yükle."""
    path = Path(filepath).resolve()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Modül yüklenemedi: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


# ---------------------------------------------------------------------------
# Ana Profiler Fonksiyonu
# ---------------------------------------------------------------------------
def profile_code(filepath: str | Path, func_name: str = "run_wasteful_algorithms") -> ProfileResult:
    """
    Verilen Python dosyasındaki ``func_name`` fonksiyonunu çalıştır ve
    performans metriklerini ölç.

    Parameters
    ----------
    filepath:
        Profillenecek .py dosyasının yolu.
    func_name:
        Dosya içindeki çalıştırılacak fonksiyon adı.

    Returns
    -------
    ProfileResult
        Süre ve bellek ölçümlerini içeren sonuç nesnesi.
    """
    path = Path(filepath).resolve()
    logger.info("Profiling başlıyor → %s::%s()", path.name, func_name)

    return_value = None
    error = None

    # tracemalloc başlat
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    start_time = time.perf_counter()

    try:
        module = _load_module_from_path(path)
        target_func = getattr(module, func_name, None)

        if target_func is None:
            raise AttributeError(
                f"'{func_name}' fonksiyonu '{path.name}' içinde bulunamadı."
            )

        return_value = target_func()
        logger.info("Fonksiyon başarıyla tamamlandı.")

    except Exception as exc:
        error = str(exc)
        logger.error("Profiling hatası: %s", exc, exc_info=True)

    finally:
        elapsed = time.perf_counter() - start_time
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    peak_mb = peak_mem / (1024 ** 2)
    current_mb = current_mem / (1024 ** 2)

    result = ProfileResult(
        filepath=str(path),
        elapsed_seconds=elapsed,
        peak_memory_mb=peak_mb,
        current_memory_mb=current_mb,
        return_value=return_value,
        error=error,
    )

    logger.info(
        "Profiling tamamlandı — Süre: %.3f s | Peak bellek: %.3f MB",
        elapsed,
        peak_mb,
    )
    return result


# ---------------------------------------------------------------------------
# Geçici dosya profili (optimize edilmiş kod için string → dosya)
# ---------------------------------------------------------------------------
def profile_code_string(
    source_code: str,
    func_name: str = "run_optimized_algorithms",
    tmp_filename: str = "optimized_code.py",
) -> ProfileResult:
    """
    Verilen kaynak kodu string'ini geçici bir dosyaya yaz ve profille.

    Parameters
    ----------
    source_code:
        Profillenecek Python kaynak kodu.
    func_name:
        Çalıştırılacak fonksiyon adı.
    tmp_filename:
        Geçici dosyanın adı (proje dizinine yazılır).
    """
    tmp_path = Path(tmp_filename).resolve()
    logger.info("Optimize kod geçici dosyaya yazılıyor → %s", tmp_path)

    try:
        tmp_path.write_text(source_code, encoding="utf-8")
    except OSError as exc:
        logger.error("Geçici dosya yazılamadı: %s", exc)
        return ProfileResult(
            filepath=str(tmp_path),
            elapsed_seconds=0.0,
            peak_memory_mb=0.0,
            current_memory_mb=0.0,
            error=str(exc),
        )

    return profile_code(tmp_path, func_name=func_name)


# ---------------------------------------------------------------------------
# Subprocess tabanlı izole profil (opsiyonel — daha temiz ölçüm)
# ---------------------------------------------------------------------------
def profile_subprocess(filepath: str | Path) -> dict:
    """
    Dosyayı ayrı bir subprocess'te çalıştırıp süresini ölç.
    Bellek ölçümü subprocess'e erişilemediği için approximation kullanır.

    Returns
    -------
    dict
        ``elapsed_seconds`` ve ``returncode`` anahtarlarını içerir.
    """
    path = Path(filepath).resolve()
    logger.info("Subprocess profiling başlıyor → %s", path.name)

    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        elapsed = time.perf_counter() - t0
        logger.info(
            "Subprocess tamamlandı — kod: %d | süre: %.3f s",
            result.returncode,
            elapsed,
        )
        return {
            "elapsed_seconds": elapsed,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        logger.error("Subprocess timeout! (%.1f s)", elapsed)
        return {"elapsed_seconds": elapsed, "returncode": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as exc:
        logger.error("Subprocess hatası: %s", exc)
        return {"elapsed_seconds": 0.0, "returncode": -1, "stdout": "", "stderr": str(exc)}
