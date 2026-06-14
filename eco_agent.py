"""
eco_agent.py
============
LangChain + Groq (llama-3.3-70b-versatile) kullanan Eco-Code Optimizer ajanı.

Sorumluluklar:
  - Kaynak kodu okuyup algoritmik darboğazları tespit etmek
  - O(N²) → O(N) / O(N log N) dönüşüm gerçekleştirmek
  - Optimize edilmiş, çalışabilir Python kodu üretmek
  - API hatalarını düzgün yönetmek
"""

from __future__ import annotations

import logging
import os
import re
import textwrap
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 4096
TEMPERATURE = 0.1       # Düşük sıcaklık → deterministik, güvenilir kod çıktısı

# ---------------------------------------------------------------------------
# System Prompt — LLM'e rol ve kısıtlar tanımlanır
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = textwrap.dedent("""
    Sen kıdemli bir Green Software & Performans Optimizasyon Mühendisisin.
    Görevin: verilen Python kodundaki algoritmik verimsizlikleri tespit etmek
    ve bunları optimal, enerji-verimli alternatiflerle değiştirmek.

    KURALLARIN:
    1. Yalnızca Python standart kütüphanesi kullan (collections, itertools vb.).
    2. Orijinal fonksiyon isimlerini koru; sadece içerik değiştir.
    3. Ana çalışma fonksiyonu mutlaka "run_optimized_algorithms" olarak adlandırılsın.
    4. Her optimize edilmiş fonksiyona kısa bir docstring ekle.
    5. PEP8 standardına tam uy.
    6. Yanıtın SADECE çalışabilir Python kodu olsun — başka hiçbir şey yok.
    7. ```python ... ``` bloğu içinde yaz.
    8. İmport ifadelerini dosyanın en üstüne koy.
    9. Orijinal kodun mantığını (aynı veri boyutu, aynı işlemler) koru.
""").strip()

# ---------------------------------------------------------------------------
# Kullanıcı Prompt Template
# ---------------------------------------------------------------------------
USER_PROMPT_TEMPLATE = textwrap.dedent("""
    Aşağıdaki Python kodu algoritmik açıdan verimsizdir.
    Bu kodu analiz et ve tam olarak optimize edilmiş bir versiyonunu yaz.

    Optimizasyon hedefleri:
    - find_common_elements: O(N²) iç içe döngü → set kesişimi O(N)
    - bubble_sort: O(N²) → Python built-in sorted() O(N log N)
    - calculate_statistics: gereksiz kopya + O(N²) iç sıralama → numpy-free O(N)
    - count_duplicates: O(N²) → collections.Counter O(N)
    - Gereksiz liste kopyalarını kaldır
    - Bellek tahsislerini minimize et

    ORIJINAL KOD:
    ```python
    {source_code}
    ```

    Şimdi optimize edilmiş, enerji-verimli versiyonu yaz:
""").strip()


# ---------------------------------------------------------------------------
# Yardımcı — kod bloğunu ayıkla
# ---------------------------------------------------------------------------
def _extract_code_block(text: str) -> str:
    """
    LLM yanıtından ```python ... ``` bloğunu çıkar.
    Blok bulunamazsa ham metni döndür.
    """
    pattern = r"```(?:python)?\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: tırnak işaretleri olmadan döndür
    logger.warning("Kod bloğu işaretleyicisi bulunamadı, ham metin kullanılıyor.")
    return text.strip()


# ---------------------------------------------------------------------------
# Ana Ajan Sınıfı
# ---------------------------------------------------------------------------
class EcoAgent:
    """
    Groq LLM tabanlı kod optimizasyon ajanı.

    Kullanım:
        agent = EcoAgent()
        optimized = agent.optimize_code(source_code)
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self._api_key:
            raise EnvironmentError(
                "GROQ_API_KEY bulunamadı. "
                "Lütfen .env dosyasını oluşturun veya ortam değişkenini ayarlayın."
            )

        logger.info("EcoAgent başlatılıyor — model: %s", GROQ_MODEL)
        self._llm = ChatGroq(
            api_key=self._api_key,
            model=GROQ_MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        logger.info("Groq LLM bağlantısı kuruldu ✅")

    # ---------------------------------------------------------------------- #
    def optimize_code(self, source_code: str) -> str:
        """
        Verilen Python kaynak kodunu LLM ile optimize et.

        Parameters
        ----------
        source_code:
            Optimize edilecek Python kodu (ham string).

        Returns
        -------
        str
            Optimize edilmiş, çalıştırılabilir Python kodu.

        Raises
        ------
        RuntimeError
            API çağrısı başarısız olduğunda.
        """
        logger.info("LLM optimizasyonu başlatılıyor...")
        logger.info("Kaynak kod boyutu: %d karakter", len(source_code))

        user_message = USER_PROMPT_TEMPLATE.format(source_code=source_code)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        try:
            logger.info("Groq API'ye istek gönderiliyor...")
            response = self._llm.invoke(messages)
            raw_output = response.content
            logger.info(
                "Groq API yanıtı alındı — %d karakter", len(raw_output)
            )

        except Exception as exc:
            logger.error("Groq API hatası: %s", exc, exc_info=True)
            raise RuntimeError(f"LLM optimizasyon başarısız: {exc}") from exc

        # Kod bloğunu ayıkla
        optimized_code = _extract_code_block(raw_output)

        # Temel doğrulama — en az bazı Python anahtar kelimeleri olmalı
        if len(optimized_code) < 100:
            logger.warning(
                "Optimize kod çok kısa (%d karakter). LLM yanıtı beklenmedik olabilir.",
                len(optimized_code),
            )

        logger.info(
            "Optimizasyon tamamlandı ✅ — %d karakter kod üretildi.",
            len(optimized_code),
        )
        return optimized_code

    # ---------------------------------------------------------------------- #
    def optimize_file(self, filepath: str | Path) -> str:
        """
        Bir .py dosyasını oku ve optimize et.

        Parameters
        ----------
        filepath:
            Optimize edilecek dosyanın yolu.

        Returns
        -------
        str
            Optimize edilmiş kaynak kodu.
        """
        path = Path(filepath).resolve()
        logger.info("Dosya okunuyor → %s", path.name)

        try:
            source_code = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Dosya okunamadı: %s", exc)
            raise

        return self.optimize_code(source_code)

    # ---------------------------------------------------------------------- #
    def save_optimized_code(
        self,
        optimized_code: str,
        output_path: str | Path = "optimized_code.py",
    ) -> Path:
        """
        Optimize edilmiş kodu bir dosyaya kaydet.

        Parameters
        ----------
        optimized_code:
            Kaydedilecek Python kodu.
        output_path:
            Hedef dosya yolu.

        Returns
        -------
        Path
            Kaydedilen dosyanın tam yolu.
        """
        path = Path(output_path).resolve()
        try:
            path.write_text(optimized_code, encoding="utf-8")
            logger.info("Optimize kod kaydedildi → %s", path)
        except OSError as exc:
            logger.error("Dosya kaydedilemedi: %s", exc)
            raise
        return path
