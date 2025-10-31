"""Recommendation service for fertilizer and crop recommendations."""
import numpy as np
from app.ml_models.model_loader import ModelLoader
from app.utils.data_loader import DataLoader


class RecommendationService:
    """Service for fertilizer and crop recommendations."""
    
    @staticmethod
    def get_fertilizer_recommendation(data):
        """Get fertilizer recommendation based on soil and crop data."""
        model = ModelLoader.get_model('recommendation')
        if model is None:
            raise RuntimeError("Recommendation model not loaded")
        
        ph_tanah = float(data['ph_tanah'])
        
        # pH-based recommendations
        if ph_tanah < 6.0:
            rekomendasi_utama = "Prioritaskan aplikasi Dolomit untuk menaikkan pH."
            peringatan = ["Peringatan: Ketersediaan Fosfor (P) sangat rendah pada pH asam."]
        elif ph_tanah > 7.2:
            rekomendasi_utama = "Pertimbangkan aplikasi Belerang (Sulfur) untuk menurunkan pH."
            peringatan = ["Peringatan: Ketersediaan unsur mikro (Besi, Mangan, Seng) rendah pada pH basa."]
        else:
            rekomendasi_utama = "Kondisi pH tanah optimal. Lanjutkan dengan pemupukan berikut:"
            peringatan = []
        
        # ML-based NPK recommendation
        input_df = np.array([[
            data['ph_tanah'],
            data['skor_bwd'],
            data['kelembaban_tanah'],
            data['umur_tanaman_hari']
        ]])
        
        prediksi_ml = model.predict(input_df)[0]
        
        rekomendasi_pupuk_ml = {
            "Rekomendasi N (kg/ha)": round(float(prediksi_ml[0]), 2),
            "Rekomendasi P (kg/ha)": round(float(prediksi_ml[1]), 2),
            "Rekomendasi K (kg/ha)": round(float(prediksi_ml[2]), 2)
        }
        
        return {
            "rekomendasi_utama": rekomendasi_utama,
            "rekomendasi_pupuk_ml": rekomendasi_pupuk_ml,
            "peringatan_penting": peringatan
        }
    
    @staticmethod
    def calculate_fertilizer_dosage(commodity, area_sqm, ph_tanah):
        """Calculate fertilizer dosage for specific crop and area."""
        dosage_db = DataLoader.get_fertilizer_dosage_db()
        dosage_data = dosage_db.get(commodity)
        
        if not dosage_data:
            return None
        
        area_ha = area_sqm / 10000.0
        results = {"anorganik": {}, "organik": {}, "perbaikan_tanah": {}}
        
        # Calculate anorganic fertilizers
        for fert, dose in dosage_data["anorganik_kg_ha"].items():
            results["anorganik"][fert] = round(dose * area_ha, 2)
        
        # Calculate organic fertilizers
        for fert, dose in dosage_data["organik_ton_ha"].items():
            results["organik"][fert] = round((dose * 1000) * area_ha, 2)
        
        # Calculate dolomite if pH is acidic
        if ph_tanah < 6.0:
            dose_dolomit = dosage_data.get("dolomit_ton_ha_asam", 0)
            results["perbaikan_tanah"]["Dolomit"] = round((dose_dolomit * 1000) * area_ha, 2)
        
        results["commodity_name"] = dosage_data['name']
        results["area_sqm"] = area_sqm
        
        return results
    
    @staticmethod
    def get_integrated_recommendation(ketinggian, iklim, fase, masalah):
        """Get integrated recommendation for bibit, pemupukan, penyemprotan."""
        knowledge_base = {
            "bibit": {
                "dataran_tinggi": "Varietas adaptif suhu sejuk (Stroberi, Kentang, Apel).",
                "dataran_rendah": "Varietas tahan panas (Tomat Hibrida, Padi Sawah).",
                "tropis": "Varietas Day-Neutral (Stroberi Day-Neutral, Pepaya).",
                "subtropis": "Varietas dengan periode dormansi (Jeruk, Anggur)."
            },
            "pemupukan": {
                "vegetatif": "Fokus pada Nitrogen (N) tinggi untuk pertumbuhan daun dan batang.",
                "generatif": "Fokus pada Fosfor (P) dan Kalium (K) untuk bunga dan buah."
            },
            "penyemprotan": {
                "thrips": "Rotasi bahan aktif: Abamektin (Grup 6) → Spinetoram (Grup 5).",
                "antraknosa": "Fungisida Mankozeb (kontak) dirotasi dengan Heksakonazol (sistemik).",
                "default": "Lakukan monitoring rutin dan identifikasi spesifik sebelum penyemprotan."
            }
        }
        
        recommendation = {
            "bibit": knowledge_base["bibit"].get(ketinggian, "Pilih varietas sesuai kondisi."),
            "pemupukan": knowledge_base["pemupukan"].get(fase, "Sesuaikan dengan fase pertumbuhan."),
            "penyemprotan": knowledge_base["penyemprotan"].get(masalah, knowledge_base["penyemprotan"]["default"])
        }
        
        return recommendation
    
    @staticmethod
    def get_spraying_recommendation(pest):
        """Get spraying strategy recommendation."""
        strategy_db = {
            "thrips": {
                "name": "Strategi Pengendalian Thrips",
                "description": "Siklus rotasi 9 minggu untuk mencegah resistensi.",
                "cycles": [
                    {
                        "weeks": "Minggu 1-3",
                        "level": "Level 1: Kontak & Translaminar",
                        "active_ingredient": "Abamektin",
                        "irac_code": "Grup 6",
                        "sop": "Aplikasikan setiap 5-7 hari sekali."
                    },
                    {
                        "weeks": "Minggu 4-6",
                        "level": "Level 2: Sistemik Lokal",
                        "active_ingredient": "Spinetoram atau Spinosad",
                        "irac_code": "Grup 5",
                        "sop": "Aplikasikan setiap 5-7 hari sekali."
                    },
                    {
                        "weeks": "Minggu 7-9",
                        "level": "Level 3: Sistemik Penuh",
                        "active_ingredient": "Imidakloprid atau Tiametoksam",
                        "irac_code": "Grup 4A",
                        "sop": "Aplikasikan setiap 7-10 hari sekali."
                    }
                ]
            }
        }
        
        protocol = {
            "title": "Protokol Penyemprotan Profesional",
            "steps": [
                "Waktu: Pagi (sebelum 09:00) atau sore (setelah 15:00)",
                "Urutan: Air → pH adjuster → Pestisida → Perekat",
                "Gunakan perekat & perata untuk efektivitas maksimal",
                "Kalibrasi alat semprot untuk kabut halus dan merata"
            ]
        }
        
        strategy = strategy_db.get(pest)
        if not strategy:
            return None
        
        return {"strategy": strategy, "protocol": protocol}
