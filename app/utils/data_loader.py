"""Data loader utility for loading datasets and knowledge bases."""
import os
import pandas as pd
from flask import current_app


class DataLoader:
    """Utility class for loading data files."""
    
    @staticmethod
    def load_eda_dataset():
        """Load EDA dataset for yield planning."""
        try:
            dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'EDA_500.csv')
            if os.path.exists(dataset_path):
                return pd.read_csv(dataset_path)
            return None
        except Exception as e:
            current_app.logger.error(f"Failed to load EDA dataset: {e}")
            return None
    
    @staticmethod
    def get_fertilizer_data():
        """Get fertilizer composition data."""
        return {
            "urea": {"name": "Urea", "content": {"N": 0.46, "P": 0, "K": 0}},
            "sp36": {"name": "SP-36", "content": {"N": 0, "P": 0.158, "K": 0}},
            "kcl": {"name": "KCL (MOP)", "content": {"N": 0, "P": 0, "K": 0.50}},
            "npk_mutiara": {"name": "NPK Mutiara (16-16-16)", "content": {"N": 0.16, "P": 0.07, "K": 0.13}}
        }
    
    @staticmethod
    def get_knowledge_base():
        """Get agricultural knowledge base."""
        return {
            "padi": {
                "name": "Padi",
                "icon": "🌾",
                "data": {
                    "Persiapan Lahan": [
                        "Olah tanah sempurna: Bajak sedalam 20-25 cm, lalu garu.",
                        "Perbaikan pH: Jika masam (pH < 6), aplikasikan Dolomit 1-2 ton/ha.",
                        "Pupuk Dasar: Berikan kompos 5-10 ton/ha dan SP-36."
                    ],
                    "Persemaian & Penanaman": [
                        "Perlakuan Benih: Rendam benih dalam larutan PGPR.",
                        "Sistem Tanam: Terapkan Jajar Legowo untuk meningkatkan populasi.",
                        "Umur Bibit: Pindahkan bibit pada umur 15-21 HSS."
                    ]
                }
            },
            "cabai": {
                "name": "Cabai",
                "icon": "🌶️",
                "data": {
                    "Persiapan Lahan": [
                        "Buat bedengan tinggi (30-40 cm).",
                        "Pastikan pH di rentang 6.0 - 7.0 dengan Dolomit.",
                        "Gunakan mulsa plastik perak-hitam."
                    ]
                }
            },
            "jagung": {
                "name": "Jagung",
                "icon": "🌽",
                "data": {
                    "Persiapan Lahan": [
                        "Bajak tanah sedalam 15-20 cm.",
                        "Berikan pupuk kandang/kompos sebagai pupuk dasar."
                    ]
                }
            }
        }
    
    @staticmethod
    def get_fertilizer_dosage_db():
        """Get fertilizer dosage database."""
        return {
            "padi": {
                "name": "Padi",
                "anorganik_kg_ha": {"Urea": 225, "SP-36": 125, "KCL": 75},
                "organik_ton_ha": {"Pupuk Kandang Sapi": 10, "Pupuk Kandang Ayam": 5},
                "dolomit_ton_ha_asam": 1.5
            },
            "cabai": {
                "name": "Cabai",
                "anorganik_kg_ha": {"Urea": 150, "SP-36": 250, "KCL": 200},
                "organik_ton_ha": {"Pupuk Kandang Sapi": 15, "Pupuk Kandang Ayam": 10},
                "dolomit_ton_ha_asam": 2.0
            },
            "jagung": {
                "name": "Jagung",
                "anorganik_kg_ha": {"Urea": 250, "SP-36": 125, "KCL": 75},
                "organik_ton_ha": {"Pupuk Kandang Sapi": 10, "Pupuk Kandang Ayam": 7},
                "dolomit_ton_ha_asam": 1.5
            }
        }
