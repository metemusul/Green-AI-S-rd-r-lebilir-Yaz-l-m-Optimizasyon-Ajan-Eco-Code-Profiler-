"""
target_code.py
==============
BILEREK VERIMSIZ YAZILMIS KOD — Eco-Code Profiler kurban dosyası.

Bu dosya, algoritmik açıdan son derece savurgan teknikler içermektedir:
  - O(N²) iç içe döngüler
  - Gereksiz bellek kopyalamaları
  - Verimsiz bubble sort
  - Tekrarlı hesaplamalar

Bu kodun ÜRETIMDE KULLANILMASI AMAÇLANMAMAKTADIR.
"""

import time
import random


# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
DATA_SIZE = 8_000          # Yeterince büyük — 1-2 sn sürmesini sağlar
SEARCH_SIZE = 4_000        # Ortak eleman arama için


# ---------------------------------------------------------------------------
# O(N²) — İç içe döngü ile ortak eleman bulma
# ---------------------------------------------------------------------------
def find_common_elements(list_a: list, list_b: list) -> list:
    """
    İki liste arasındaki ortak elemanları bul.

    KÖTÜ YAKLASIM: Her eleman için tüm listeyi tarar → O(N²).
    DOGRU YAKLASIM: set kesisimi → O(N).
    """
    common = []
    for item_a in list_a:            # N iterasyon
        for item_b in list_b:        # N iterasyon → toplam N*N
            if item_a == item_b:
                common.append(item_a)
                break
    return common


# ---------------------------------------------------------------------------
# O(N²) — Bubble Sort implementasyonu
# ---------------------------------------------------------------------------
def bubble_sort(arr: list) -> list:
    """
    Listeyi kabarcık sıralaması ile sırala.

    KÖTÜ YAKLASIM: O(N²) zaman, yerinde sıralama ama çok yavaş.
    DOGRU YAKLASIM: Timsort (Python built-in sorted) → O(N log N).
    """
    data = arr[:]                    # gereksiz kopya #1
    n = len(data)
    for i in range(n):               # Dış döngü: N kez
        swapped = False
        for j in range(0, n - i - 1):  # İç döngü: ~N kez
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
        if not swapped:
            break
    return data


# ---------------------------------------------------------------------------
# O(N²) — Gereksiz tekrarlı liste kopyaları ile istatistik hesaplama
# ---------------------------------------------------------------------------
def calculate_statistics(data: list) -> dict:
    """
    Bir listedeki temel istatistikleri hesapla.

    KÖTÜ YAKLASIM:
      - Her adımda yeni liste kopyası oluşturur
      - Ortalama için gereksiz döngü
      - Varyans için çift geçiş
    """
    # Gereksiz kopya — orijinal data değiştirilmiyor zaten
    working_data = list(data)          # kopya #1
    sorted_data = list(working_data)   # kopya #2

    # O(N) toplama — manuel döngüyle
    total = 0
    for val in working_data:           # 1. geçiş
        total += val
    mean = total / len(working_data)

    # Varyans hesabı — tekrar tüm listeyi dola
    variance_sum = 0
    for val in working_data:           # 2. geçiş (tekrar)
        diff = val - mean
        variance_sum += diff * diff
    variance = variance_sum / len(working_data)

    # Manuel sıralama (bubble sort!) — sorted() kullanmak yerine
    n = len(sorted_data)
    for i in range(n):
        for j in range(0, n - i - 1):  # O(N²) iç içe!
            if sorted_data[j] > sorted_data[j + 1]:
                sorted_data[j], sorted_data[j + 1] = (
                    sorted_data[j + 1], sorted_data[j]
                )

    # Medyan
    mid = len(sorted_data) // 2
    if len(sorted_data) % 2 == 0:
        median = (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        median = sorted_data[mid]

    return {
        "mean": mean,
        "variance": variance,
        "median": median,
        "min": sorted_data[0],
        "max": sorted_data[-1],
    }


# ---------------------------------------------------------------------------
# O(N²) — Tekrarlayan elemanların sayısını say (Counter kullanmadan)
# ---------------------------------------------------------------------------
def count_duplicates(data: list) -> dict:
    """
    Listede her elemanın kaç kez geçtiğini say.

    KÖTÜ YAKLASIM: Her eleman için tüm listeyi tarar → O(N²).
    DOGRU YAKLASIM: collections.Counter → O(N).
    """
    counts = {}
    for i in range(len(data)):         # Dış döngü
        count = 0
        for j in range(len(data)):     # İç döngü — N*N
            if data[i] == data[j]:
                count += 1
        counts[data[i]] = count
    return counts


# ---------------------------------------------------------------------------
# Ana çalışma bloğu
# ---------------------------------------------------------------------------
def run_wasteful_algorithms() -> dict:
    """Tüm verimsiz algoritmaları sırayla çalıştır ve sonuçları döndür."""
    random.seed(42)

    # Veri setleri
    list_a = random.sample(range(DATA_SIZE * 2), DATA_SIZE)
    list_b = random.sample(range(DATA_SIZE * 2), SEARCH_SIZE)
    small_data = [random.randint(1, 500) for _ in range(2_000)]
    sort_data = random.sample(range(DATA_SIZE), DATA_SIZE // 2)

    results = {}

    # 1. Ortak eleman bulma
    t0 = time.perf_counter()
    common = find_common_elements(list_a, list_b)
    results["common_elements_time"] = time.perf_counter() - t0
    results["common_count"] = len(common)

    # 2. Bubble Sort
    t0 = time.perf_counter()
    sorted_arr = bubble_sort(sort_data)
    results["bubble_sort_time"] = time.perf_counter() - t0
    results["sorted_length"] = len(sorted_arr)

    # 3. İstatistik hesaplama
    t0 = time.perf_counter()
    stats = calculate_statistics(small_data)
    results["statistics_time"] = time.perf_counter() - t0
    results["stats"] = stats

    # 4. Tekrar sayımı
    t0 = time.perf_counter()
    dup_sample = [random.randint(1, 50) for _ in range(500)]
    dupes = count_duplicates(dup_sample)
    results["duplicates_time"] = time.perf_counter() - t0
    results["unique_values"] = len(dupes)

    return results


if __name__ == "__main__":
    start = time.perf_counter()
    output = run_wasteful_algorithms()
    elapsed = time.perf_counter() - start

    print(f"\n[target_code] Toplam çalışma süresi: {elapsed:.3f} saniye")
    print(f"  Ortak eleman sayısı  : {output['common_count']}")
    print(f"  Sıralanan eleman     : {output['sorted_length']}")
    print(f"  İstatistik (medyan)  : {output['stats']['median']:.2f}")
    print(f"  Benzersiz değer sayısı: {output['unique_values']}")
