from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn
import os

app = FastAPI()

# React'in bağlanabilmesi için CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def temizle_ve_sayiya_cevir(deger):
    """Metin halindeki sayıları grafiğin anlayacağı float tipine çevirir."""
    if deger is None or deger == "":
        return 0
    try:
        if isinstance(deger, (int, float)):
            return float(deger)
        # "46.930,69" -> "46930.69"
        temiz_deger = str(deger).replace('.', '').replace(',', '.')
        return float(temiz_deger)
    except Exception:
        return 0


@app.get("/enerji-verisi")
def veri_gonder():
    # Veritabanı dosyasının varlığını kontrol et (Dosya yolu hatasını önlemek için)
    db_path = 'Proje3\Backend\energy_data.db'
    if not os.path.exists(db_path):
        print(f"HATA: {db_path} dosyası bulunamadı!")
        return []  # Sayfanın beyaz olmaması için liste dönüyoruz

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Tablonun varlığını ve verileri kontrol et
        cursor.execute("SELECT date, hour, solar_energy_real, wind_energy_real, total_energy FROM fuel_energy_stats")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("Uyarı: Veritabanı bağlantısı başarılı ama tablo boş.")
            return []

        temiz_veri = []
        for row in rows:
            temiz_veri.append({
                "tarih_saat": f"{row['date']} {row['hour']}",
                "gunes": temizle_ve_sayiya_cevir(row['solar_energy_real']),
                "ruzgar": temizle_ve_sayiya_cevir(row['wind_energy_real']),
                "toplam": temizle_ve_sayiya_cevir(row['total_energy'])
            })

        print(f"Başarılı: {len(temiz_veri)} satır veri gönderiliyor.")
        return temiz_veri

    except Exception as e:
        print(f"Backend Hatası: {e}")
        # Kritik: Hata olsa bile sözlük değil liste döndürerek React'in çökmesini engelle
        return []


if __name__ == "__main__":
    # Port 8001 olarak ayarlandı.
    uvicorn.run(app, host="127.0.0.1", port=8001)