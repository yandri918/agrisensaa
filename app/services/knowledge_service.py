"""Knowledge service for agricultural information."""
from app.utils.data_loader import DataLoader
from app.services.recommendation_service import RecommendationService


class KnowledgeService:
    """Service for agricultural knowledge base."""
    
    @staticmethod
    def get_crop_knowledge(commodity):
        """Get knowledge base for specific crop."""
        knowledge_base = DataLoader.get_knowledge_base()
        return knowledge_base.get(commodity)
    
    @staticmethod
    def get_commodity_guide(commodity):
        """Get comprehensive guide for commodity."""
        guides = {
            'cabai': {
                "name": "Cabai (Capsicum sp.)",
                "icon": "🌶️",
                "description": "Cabai adalah komoditas hortikultura bernilai ekonomi tinggi.",
                "sop": {
                    "1. Persiapan Lahan": [
                        "Buat bedengan tinggi 30-40 cm untuk drainase optimal.",
                        "Ukur pH tanah. Jika < 6.0, aplikasikan Dolomit 1.5-2 ton/ha.",
                        "Berikan pupuk organik 15-20 ton/ha.",
                        "Tutup dengan mulsa plastik perak-hitam."
                    ],
                    "2. Persemaian": [
                        "Gunakan media semai steril (tanah:kompos:arang sekam = 1:1:1).",
                        "Bibit siap pindah tanam setelah 4-5 helai daun sejati."
                    ],
                    "3. Pemeliharaan": [
                        "Pemupukan susulan sistem kocor setiap 7-10 hari.",
                        "Fase Vegetatif: NPK tinggi N (25-7-7).",
                        "Fase Generatif: NPK seimbang (16-16-16)."
                    ]
                },
                "business_analysis": {
                    "title": "Analisis Usaha Tani Cabai per 1000 m²",
                    "assumptions": {
                        "Luas_Lahan": "1000 m²",
                        "Populasi_Tanaman": "4000 tanaman"
                    },
                    "costs": [
                        {"item": "Benih Unggul", "amount": "40 gram", "cost": 200000},
                        {"item": "Pupuk Kandang", "amount": "1.5 ton", "cost": 1500000},
                        {"item": "Pupuk Anorganik", "amount": "Paket lengkap", "cost": 800000},
                        {"item": "Mulsa Plastik", "amount": "1 roll", "cost": 500000},
                        {"item": "Pestisida", "amount": "Paket lengkap", "cost": 1000000},
                        {"item": "Tenaga Kerja", "amount": "5 bulan", "cost": 5000000}
                    ],
                    "yield_potential": [
                        {"scenario": "Konservatif", "total_yield_kg": 3000},
                        {"scenario": "Optimal", "total_yield_kg": 6000}
                    ],
                    "revenue_scenarios": [
                        {"price_level": "Harga Rendah", "price_per_kg": 8000},
                        {"price_level": "Harga Normal", "price_per_kg": 15000},
                        {"price_level": "Harga Tinggi", "price_per_kg": 25000}
                    ]
                }
            },
            'padi': {
                "name": "Padi (Oryza sativa)",
                "icon": "🌾",
                "description": "Padi adalah tanaman pangan utama Indonesia yang menjadi sumber karbohidrat utama.",
                "sop": {
                    "1. Persiapan Lahan": [
                        "Bajak dan garu sawah hingga rata.",
                        "Atur ketinggian air 5-10 cm.",
                        "Aplikasikan pupuk dasar: Urea 100 kg/ha, SP-36 75 kg/ha, KCl 50 kg/ha.",
                        "Biarkan lahan tergenang 3-5 hari sebelum tanam."
                    ],
                    "2. Penanaman": [
                        "Gunakan bibit umur 18-25 hari.",
                        "Tanam 2-3 bibit per lubang dengan jarak 25x25 cm.",
                        "Kedalaman tanam 2-3 cm."
                    ],
                    "3. Pemeliharaan": [
                        "Pemupukan susulan I (21 HST): Urea 100 kg/ha.",
                        "Pemupukan susulan II (42 HST): Urea 50 kg/ha + KCl 50 kg/ha.",
                        "Pengairan: Macak-macak saat pembungaan, kering 2 minggu sebelum panen."
                    ]
                },
                "business_analysis": {
                    "title": "Analisis Usaha Tani Padi per 1 Hektar",
                    "assumptions": {
                        "Luas_Lahan": "1 hektar (10,000 m²)",
                        "Populasi_Tanaman": "160,000 rumpun"
                    },
                    "costs": [
                        {"item": "Benih Bersertifikat", "amount": "25 kg", "cost": 500000},
                        {"item": "Pupuk Anorganik", "amount": "Urea 250kg, SP-36 150kg, KCl 100kg", "cost": 2000000},
                        {"item": "Pestisida", "amount": "Paket lengkap", "cost": 800000},
                        {"item": "Tenaga Kerja", "amount": "4 bulan", "cost": 4000000},
                        {"item": "Sewa Traktor", "amount": "2x pengolahan", "cost": 1500000}
                    ],
                    "yield_potential": [
                        {"scenario": "Konservatif", "total_yield_kg": 4500},
                        {"scenario": "Optimal", "total_yield_kg": 7000}
                    ],
                    "revenue_scenarios": [
                        {"price_level": "Harga Rendah", "price_per_kg": 4000},
                        {"price_level": "Harga Normal", "price_per_kg": 5500},
                        {"price_level": "Harga Tinggi", "price_per_kg": 7000}
                    ]
                }
            },
            'jagung': {
                "name": "Jagung (Zea mays)",
                "icon": "🌽",
                "description": "Jagung adalah tanaman pangan alternatif dan pakan ternak yang penting.",
                "sop": {
                    "1. Persiapan Lahan": [
                        "Olah tanah sedalam 20-30 cm.",
                        "Buat bedengan lebar 70-80 cm, tinggi 20-30 cm.",
                        "Aplikasikan pupuk kandang 2-3 ton/ha.",
                        "pH optimal 5.5-7.0."
                    ],
                    "2. Penanaman": [
                        "Jarak tanam 75x25 cm atau 70x30 cm.",
                        "Tanam 1-2 biji per lubang, kedalaman 3-5 cm.",
                        "Aplikasikan pupuk dasar: Urea 100 kg/ha, SP-36 100 kg/ha, KCl 75 kg/ha."
                    ],
                    "3. Pemeliharaan": [
                        "Pemupukan susulan I (21 HST): Urea 150 kg/ha.",
                        "Pemupukan susulan II (42 HST): Urea 100 kg/ha + KCl 75 kg/ha.",
                        "Penyiangan 2-3 kali selama masa tanam."
                    ]
                },
                "business_analysis": {
                    "title": "Analisis Usaha Tani Jagung per 1 Hektar",
                    "assumptions": {
                        "Luas_Lahan": "1 hektar (10,000 m²)",
                        "Populasi_Tanaman": "53,000 tanaman"
                    },
                    "costs": [
                        {"item": "Benih Hibrida", "amount": "20 kg", "cost": 1200000},
                        {"item": "Pupuk Kandang", "amount": "2 ton", "cost": 1000000},
                        {"item": "Pupuk Anorganik", "amount": "Urea 350kg, SP-36 100kg, KCl 150kg", "cost": 1800000},
                        {"item": "Pestisida", "amount": "Paket lengkap", "cost": 600000},
                        {"item": "Tenaga Kerja", "amount": "3.5 bulan", "cost": 3500000}
                    ],
                    "yield_potential": [
                        {"scenario": "Konservatif", "total_yield_kg": 5000},
                        {"scenario": "Optimal", "total_yield_kg": 8000}
                    ],
                    "revenue_scenarios": [
                        {"price_level": "Harga Rendah", "price_per_kg": 4000},
                        {"price_level": "Harga Normal", "price_per_kg": 5000},
                        {"price_level": "Harga Tinggi", "price_per_kg": 6500}
                    ]
                }
            }
        }
        
        return guides.get(commodity)
    
    @staticmethod
    def get_ph_knowledge():
        """Get pH knowledge base."""
        return {
            "title": "Ilmu Fundamental pH Tanah",
            "icon": "🧪",
            "sections": {
                "Definisi": {
                    "title": "Apa itu pH?",
                    "content": [
                        "pH mengukur tingkat keasaman/kebasaan tanah (skala 0-14).",
                        "pH 7 = netral, < 7 = asam, > 7 = basa.",
                        "pH adalah 'Master Variable' yang mengontrol ketersediaan hara."
                    ]
                },
                "Tanah Asam": {
                    "title": "Masalah pH < 6.0",
                    "content": [
                        "Fosfor (P) terikat oleh Aluminium dan Besi.",
                        "Kekurangan Kalsium dan Magnesium.",
                        "Keracunan Aluminium pada akar.",
                        "Solusi: Aplikasi Dolomit atau Kalsit."
                    ]
                },
                "Tanah Basa": {
                    "title": "Masalah pH > 7.2",
                    "content": [
                        "Unsur mikro (Fe, Mn, Zn) tidak larut.",
                        "Fosfor terikat oleh Kalsium.",
                        "Gejala: Klorosis pada daun muda.",
                        "Solusi: Aplikasi Sulfur atau bahan organik."
                    ]
                }
            }
        }
    
    @staticmethod
    def get_diagnostic_tree():
        """Get plant disease diagnostic tree."""
        return {
            "start": {
                "question": "Di bagian mana gejala utama muncul?",
                "options": {
                    "daun": {
                        "question": "Gejala spesifik di daun?",
                        "options": {
                            "keriting_kecil": {
                                "question": "Ada serangga kecil di balik daun?",
                                "options": {
                                    "ya": "DIAGNOSIS: Thrips. REKOMENDASI: Semprot Abamektin.",
                                    "tidak": "DIAGNOSIS: Tungau atau kekurangan Ca."
                                }
                            },
                            "bercak_coklat": "DIAGNOSIS: Antraknosa. REKOMENDASI: Fungisida Mankozeb.",
                            "menguning": "DIAGNOSIS: Kekurangan Nitrogen atau unsur mikro."
                        }
                    },
                    "buah": {
                        "question": "Gejala di buah?",
                        "options": {
                            "busuk_berair": "DIAGNOSIS: Antraknosa atau Phytophthora.",
                            "ada_lubang": "DIAGNOSIS: Lalat Buah. REKOMENDASI: Perangkap petrogenol."
                        }
                    },
                    "batang": {
                        "question": "Gejala di batang?",
                        "options": {
                            "layu_mendadak": "DIAGNOSIS: Layu Fusarium/Bakteri. REKOMENDASI: Cabut tanaman terinfeksi.",
                            "kerdil": "DIAGNOSIS: Virus. REKOMENDASI: Kendalikan vektor (kutu kebul)."
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def get_fertilizer_data():
        """Get fertilizer composition data."""
        return DataLoader.get_fertilizer_data()
    
    @staticmethod
    def get_spraying_strategy(pest: str):
        """Bridge method for legacy route: return spraying strategy from RecommendationService."""
        return RecommendationService.get_spraying_recommendation(pest)
