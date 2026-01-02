from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# React'in bağlanabilmesi için CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def formatla(sayi_str):
    try:
        # "46.930,69" -> 46930.69
        return float(sayi_str.replace('.', '').replace(',', '.'))
    except:
        return 0


@app.get("/enerji-verisi")
def veri_gonder():
    with open('energy_data.json', 'r', encoding='utf-8') as f:
        ham_veri = json.load(f)

    temiz_veri = []
    for satir in ham_veri:
        temiz_veri.append({
            "tarih_saat": f"{satir['Date']} {satir['Hour']}",
            "toplam": formatla(satir['Total Energy']),
            "gunes": formatla(satir['Solar Energy']),
            "ruzgar": formatla(satir['Wind Energy'])
        })
    return temiz_veri