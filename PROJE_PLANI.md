# Ahmed Body CFD Analizi — Proje Planı

25° slant | ANSYS Fluent | k-ω SST | Lienhart & Becker (2003) doğrulaması

---

## Genel Akış

```
Adım 0: Geometri → Adım 1: Domain → Adım 2: Mesh → Adım 3: Fizik
→ Adım 4: Mesh Independence → Adım 5: Post-processing → Adım 6: Rapor
```

Her adımda: sonucu paylaş → onay → bir sonraki adım.

---

## Adım 0: Hazırlık ve Geometri Edinimi
**Sen yaparsın:**
- GrabCAD veya ResearchGate'ten Ahmed body STL/STEP indir
  - Arama: `Ahmed reference model 25 degree slant STEP site:grabcad.com`
  - Boyut kontrolü: 1044 mm × 389 mm × 273 mm, ground clearance 50 mm, slant 25°
- SpaceClaim/DesignModeler'da aç, yüzey kalitesini kontrol et
- Simetri: yarım model kullanmayı düşün (hesap süresi yarıya iner)

**Claude Code yaptı:**
- Repo yapısı oluşturuldu
- `scripts/y_plus_calculator.py` → first cell height hesabı
- `scripts/mesh_independence.py` → GCI analizi
- `scripts/lienhart_comparison.py` → literatür karşılaştırması

> **Onay noktası:** Temiz geometri ekran görüntüsü yolla

---

## Adım 1: Hesap Domaini Tasarımı
**Boyutlar** (H = 389 mm = araç yüksekliği):

| Yön | Mesafe |
|-----|--------|
| Upstream (inlet → araç ön) | 5H |
| Downstream (araç arka → outlet) | 15H |
| Yan ve üst (araç yüzeyinden) | 5H |

**Sınır koşulları:**

| Yüzey | Tip | Değer |
|-------|-----|-------|
| Inlet | Velocity inlet | U∞ = 40 m/s, TI = 0.2% |
| Outlet | Pressure outlet | 0 Pa gauge |
| Yan / Üst duvarlar | Symmetry | — |
| Zemin | Moving wall | U = 40 m/s (deney koşulu) |
| Araç yüzeyi | No-slip wall | — |

> **Onay noktası:** Domain + named selections ekran görüntüsü yolla

---

## Adım 2: Mesh Stratejisi (Ana öğrenme adımı)
**3 mesh seviyesi — biri bitmeden diğerine geçme:**

| Seviye | Hedef hücre | Global max boyut |
|--------|-------------|------------------|
| Coarse | ~1.5M | 40 mm |
| Medium | ~4M | 20 mm |
| Fine | ~10M | 10 mm |

**Her seviyede ortak kurallar:**
- Inflation layer: min. 5 katman, first cell height ≈ **0.04 mm** (y⁺ < 5 için)
  - Hesap: `python scripts/y_plus_calculator.py` → çıktı: dy ≈ 0.0434 mm for y⁺=5
- Wake bölgesine (araç arkası 5H) refinement body of influence
- Slant yüzeyi ve köşelerde mesh yoğunlaştır

> **Onay noktası:** Her mesh için hücre sayısı + kalite metrikleri (skewness, orthogonality) tablosunu paylaş

---

## Adım 3: Fizik Kurulumu
Her mesh için aynı ayarlar:

```
Solver:           Pressure-based, Steady-state
Turbulence:       k-ω SST (Menter 1994)
Discretization:   Second-order upwind
Pressure-vel:     Coupled
Inlet TI:         0.2%
```

**Convergence kriterleri:**
- Residuals < 10⁻⁵
- Cd monitörü: son 200 iterasyonda ±0.001'den az salınım

> **Onay noktası:** Coarse mesh residual grafiği + Cd convergence grafiği yolla

---

## Adım 4: Mesh Independence Analizi
Her mesh için Cd ve Cl kaydet, sonra:

```bash
python scripts/mesh_independence.py
```

Script otomatik hesaplar:
- Richardson extrapolation → asimptotik Cd
- GCI (Celik et al. 2008 metodolojisi)
- Convergence grafiği (Lienhart referans çizgisiyle)

**Kabul kriteri:** Ardışık iki mesh arası Cd farkı < %2

> **Onay noktası:** Tablo + GCI grafiğini paylaş → Claude Code literatürle karşılaştırır

---

## Adım 5: Post-Processing ve Literatür Karşılaştırması
**Fine mesh'ten elde edilecekler:**
1. Cd, Cl değerleri
2. Velocity contours (orta-dikey düzlem, z=0)
3. Streamlines (wake bölgesi)
4. Wall y⁺ dağılımı
5. Hız profilleri — Lienhart ölçüm lokasyonlarında:
   - x/L = 0.484 / 0.609 / 0.734 / 0.859

**ANSYS'ten export:** Fluent → Plot → XY Plot → CSV olarak kaydet
→ `results/fine/velocity_profile_x0484.csv` formatında

Sonra:
```bash
python scripts/lienhart_comparison.py
```

**Kabul aralıkları:**
- Cd: ±%5 → hedef 0.284–0.314
- Hız profilleri MAE: ±%10

> **Onay noktası:** Cd + hız profili grafikleri yolla → Claude Code anında analiz eder

---

## Adım 6: LaTeX Rapor
Mevcut TeX altyapınla uyumlu. Bölümler:

1. Giriş ve literatür özeti
2. Geometri ve hesap domaini
3. Mesh metodolojisi + independence çalışması
4. Fizik modeli
5. Sonuçlar ve literatür doğrulaması
6. Tartışma ve sonuç

Claude Code: LaTeX şablonu, figür otomasyonu ve tablo üretimi yapar — sen sadece analiz metnini doldurursun.

---

## Referans Değerler — Lienhart & Becker (2003)

| Parametre | Değer |
|-----------|-------|
| Cd | 0.299 ± 0.005 |
| Cl | −0.082 ± 0.008 |
| U∞ | 40 m/s |
| Re | ~2.9 × 10⁶ |
| Slant açısı | 25° |

Kaynak: Lienhart H., Becker S. — *Flow and Turbulence Structure in the Wake of a Simplified Car Model*, SAE 2003-01-0656

---

## Repo Yapısı

```
ahmed-body-cfd/
├── geometry/              # CAD dosyaları (.step, .stl)
├── mesh/                  # Mesh dosyaları ve kalite raporları
├── results/
│   ├── coarse/            # ~1.5M hücre
│   ├── medium/            # ~4M hücre
│   └── fine/              # ~10M hücre
├── scripts/
│   ├── y_plus_calculator.py
│   ├── mesh_independence.py
│   └── lienhart_comparison.py
└── report/
    └── figures/
```
