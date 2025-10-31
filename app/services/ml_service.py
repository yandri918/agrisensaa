import joblib
import os
import pandas as pd
import numpy as np
import threading  # <-- PERBAIKAN: Impor 'threading' ditambahkan di sini
from werkzeug.utils import secure_filename
import cv2
from inference_sdk import InferenceHTTPClient
import uuid

# --- MANAJEMEN MODEL ---
_model_cache = {}
_model_lock = threading.Lock() # Sekarang 'threading' sudah terdefinisi

MODEL_PATHS = {
    'bwd': 'bwd_model.pkl',
    'recommendation': 'recommendation_model.pkl',
    'crop_recommendation': 'crop_recommendation_model.pkl',
    'yield_prediction': 'yield_prediction_model.pkl',
    'advanced_yield': 'advanced_yield_model.pkl',
    'shap_explainer': 'shap_explainer.pkl',
    'success_model': 'success_model.pkl'
}

def get_model(model_name):
    """Memuat model sesuai permintaan dan menyimpannya di cache."""
    with _model_lock:
        if model_name not in _model_cache:
            # Mengasumsikan file model ada di folder root, di luar folder 'app'
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', MODEL_PATHS.get(model_name))
            if path and os.path.exists(path):
                _model_cache[model_name] = joblib.load(path)
            else:
                _model_cache[model_name] = None
        return _model_cache[model_name]

# --- MANAJEMEN DATASET ---
def get_dataset_path(filename):
    # Mengasumsikan file dataset ada di folder root, di luar folder 'app'
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', filename)

class MLService:
    """
    Berisi semua logika bisnis untuk fungsionalitas Machine Learning.
    Ini dipanggil oleh file routes/ml.py.
    """

    @staticmethod
    def recommend_crop(data):
        crop_model = get_model('crop_recommendation')
        if crop_model is None: raise RuntimeError("Model Rekomendasi Tanaman tidak bisa dimuat.")
        
        # Nama fitur harus sama persis dengan saat pelatihan
        features = [
            float(data.get('n_value', 0)),
            float(data.get('p_value', 0)),
            float(data.get('k_value', 0)),
            float(data.get('temperature', 0)),
            float(data.get('humidity', 0)),
            float(data.get('ph', 0)),
            float(data.get('rainfall', 0))
        ]
        input_data = np.array([features])
        prediction = crop_model.predict(input_data)[0]
        return prediction.capitalize()

    @staticmethod
    def predict_yield(data):
        yield_model = get_model('yield_prediction')
        if yield_model is None: raise RuntimeError("Model Prediksi Panen tidak bisa dimuat.")
        
        # Nama fitur harus sama persis dengan saat pelatihan
        features = [
            float(data.get('nitrogen', 0)),
            float(data.get('phosphorus', 0)),
            float(data.get('potassium', 0)),
            float(data.get('temperature', 0)),
            float(data.get('rainfall', 0)),
            float(data.get('ph', 0))
        ]
        input_data = np.array([features])
        prediction = yield_model.predict(input_data)[0]
        return round(float(prediction) / 1000, 2) # Konversi dari kg/ha ke ton/ha

    @staticmethod
    def predict_yield_advanced(data):
        advanced_model = get_model('advanced_yield')
        explainer = get_model('shap_explainer')
        if advanced_model is None or explainer is None:
            raise RuntimeError("Model Prediksi Panen Lanjutan atau SHAP explainer tidak bisa dimuat.")
        
        feature_names = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Rainfall', 'pH']
        features = [float(data.get(name.lower(), 0)) for name in feature_names]
        input_data = pd.DataFrame([features], columns=feature_names)
        
        prediction = advanced_model.predict(input_data)[0]
        importances = advanced_model.feature_importances_
        feature_importance_dict = sorted(zip(feature_names, [float(i) for i in importances]), key=lambda x: x[1], reverse=True)
        shap_values = explainer.shap_values(input_data)
        shap_dict = {name: round(float(val), 2) for name, val in zip(feature_names, shap_values[0])}
        
        return {
            'predicted_yield_ton_ha': round(float(prediction) / 1000, 2),
            'feature_importances': feature_importance_dict,
            'shap_values': shap_dict,
            'base_value': round(float(explainer.expected_value) / 1000, 2)
        }

    @staticmethod
    def calculate_fertilizer_bags(nutrient_needed, nutrient_amount_kg, fertilizer_type):
        from app.services.knowledge_service import KnowledgeService
        FERTILIZER_DATA = KnowledgeService.get_fertilizer_data()
        
        fert_data = FERTILIZER_DATA.get(fertilizer_type)
        if not fert_data:
            return None
            
        nutrient_percentage = fert_data["content"].get(nutrient_needed, 0)
        if nutrient_percentage == 0:
            return None
            
        required_fertilizer_kg = nutrient_amount_kg / nutrient_percentage
        return {
            'required_kg': round(required_fertilizer_kg, 2),
            'fertilizer_name': fert_data["name"],
            'nutrient_needed': nutrient_needed,
            'nutrient_amount_kg': nutrient_amount_kg
        }

    @staticmethod
    def generate_yield_plan(target_yield_ton_ha):
        dataset_path = get_dataset_path('EDA_500.csv')
        if not os.path.exists(dataset_path):
            raise RuntimeError("Dataset EDA_500.csv tidak ditemukan.")
        
        df = pd.read_csv(dataset_path)
        df['Yield'] = pd.to_numeric(df['Yield'], errors='coerce')
        df.dropna(subset=['Yield'], inplace=True)
        
        target_yield_kg = target_yield_ton_ha * 1000
        best_match_row = df.iloc[(df['Yield'] - target_yield_kg).abs().argsort()[:1]]
        
        if best_match_row.empty:
            return None

        result = best_match_row.iloc[0]
        plan = {
            "Nitrogen (kg/ha)": round(float(result['Nitrogen']), 2),
            "Phosphorus (kg/ha)": round(float(result['Phosphorus']), 2),
            "Potassium (kg/ha)": round(float(result['Potassium']), 2),
            "Temperature (°C)": round(float(result['Temperature']), 2),
            "Rainfall (mm)": round(float(result['Rainfall']), 2),
            "pH Tanah": round(float(result['pH']), 2),
            "Hasil Panen Aktual dari Data": f"{round(float(result['Yield'])/1000, 2)} ton/ha"
        }
        return plan

    @staticmethod
    def predict_success(data):
        success_model = get_model('success_model')
        if success_model is None: 
            raise RuntimeError("Model Prediksi Keberhasilan tidak dimuat.")
        
        features = [
            float(data.get('nitrogen', 0)),
            float(data.get('phosphorus', 0)),
            float(data.get('potassium', 0)),
            float(data.get('temperature', 0)),
            float(data.get('rainfall', 0)),
            float(data.get('ph', 0))
        ]
        input_data = np.array([features])
        
        prediction = success_model.predict(input_data)[0]
        probability = success_model.predict_proba(input_data)[0]
        
        status = "Berhasil" if prediction == 1 else "Berisiko Tinggi"
        prob_percent = round(probability[1] * 100, 2)
        
        return {
            'status': status,
            'probability_of_success': prob_percent
        }

