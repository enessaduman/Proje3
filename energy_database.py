import sqlite3
import pandas as pd
import json
import os


class EnergyDatabase:
    def __init__(self, db_name="energy_data.db"):
        self.db_name = db_name
        self.setup_db()

    def setup_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # RE-RUN DESTEĞİ: Tablo varsa hata vermez
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS fuel_energy_stats
                       (
                           id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                           date                    TEXT,
                           hour                    TEXT,
                           city                    TEXT,
                           solar_radiation         REAL,
                           wind_speed              REAL,
                           solar_energy_real       REAL,
                           solar_energy_calculated REAL,
                           wind_energy_real        REAL,
                           wind_energy_calculated  REAL,
                           total_energy            REAL
                       )
                       ''')
        # HIZLI SORGULAMA: Index kriteri
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_time ON fuel_energy_stats (date, hour)')
        conn.commit()
        conn.close()
        print(f"Database setup successful: {self.db_name} is ready.")

    def store_json_to_sql(self, json_file_path):
        if not os.path.exists(json_file_path):
            print(f"Error: {json_file_path} not found!")
            return

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            df = pd.DataFrame(data)

            # --- KRİTİK EŞLEŞTİRME BURASI ---
            # Scrapy'den gelen (Sol taraf) -> SQL'deki isimlere (Sağ taraf) çevriliyor
            name_mapping = {
                "Date": "date",
                "Hour": "hour",
                "Total Energy": "total_energy",
                "Solar Energy": "solar_energy_real",
                "Wind Energy": "wind_energy_real"
            }
            df = df.rename(columns=name_mapping)

            # SQL tablosunda olan ama Scrapy'de olmayan kolonları (city vb.) boş olarak ekle
            all_columns = ['date', 'hour', 'city', 'solar_radiation', 'wind_speed',
                           'solar_energy_real', 'solar_energy_calculated',
                           'wind_energy_real', 'wind_energy_calculated', 'total_energy']

            for col in all_columns:
                if col not in df.columns:
                    df[col] = None

            # Sadece tablomuzda olan kolonları seçiyoruz
            df = df[all_columns]

            conn = sqlite3.connect(self.db_name)
            # RE-RUN: if_exists='append' sayesinde veriler üst üste eklenir
            df.to_sql('fuel_energy_stats', conn, if_exists='append', index=False)
            conn.commit()
            conn.close()

            print(f"Başarılı: {len(df)} satır SQL'e aktarıldı.")

        except Exception as e:
            print(f"Data storage error: {e}")


if __name__ == "__main__":
    db = EnergyDatabase()
    # Scrapy kodun "energy_data.json" oluşturduğu için ismi güncelledim
    db.store_json_to_sql('energy_data.json')