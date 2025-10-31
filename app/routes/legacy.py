"""Legacy routes for backward compatibility with old frontend."""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from inference_sdk import InferenceHTTPClient
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService
from app.services.knowledge_service import KnowledgeService
from app.services.market_service import MarketService
from app.services.ml_service import MLService
from app.models.npk_reading import NpkReading
from app import db

legacy_bp = Blueprint('legacy', __name__)

# Initialize services
analysis_service = AnalysisService()
recommendation_service = RecommendationService()
knowledge_service = KnowledgeService()
market_service = MarketService()
ml_service = MLService()

UPLOAD_FOLDER = 'uploads/pdfs'
TEMP_IMAGE_FOLDER = 'uploads/temp_images'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@legacy_bp.route('/analyze', methods=['POST'])
def analyze_bwd_endpoint():
    """Legacy BWD analysis endpoint."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Tidak ada file'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'File tidak dipilih'}), 400
        
        result = analysis_service.analyze_leaf_image(file.read())
        
        if result is None:
            return jsonify({'success': False, 'message': 'Tidak ada objek daun yang terdeteksi'}), 400
        
        return jsonify({
            'success': True,
            'bwd_score': result['bwd_score'],
            'avg_hue_value': result['avg_hue'],
            'confidence_percent': result['confidence']
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error in /analyze: {e}", exc_info=True)
        return jsonify({'error': 'Kesalahan internal saat menganalisis gambar.'}), 500


@legacy_bp.route('/recommendation', methods=['POST'])
def recommendation_endpoint():
    """Legacy fertilizer recommendation endpoint."""
    try:
        data = request.get_json()
        recommendation = recommendation_service.get_fertilizer_recommendation(data)
        return jsonify({'success': True, 'recommendation': recommendation})
    except Exception as e:
        current_app.logger.error(f"Error in /recommendation: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat menghitung rekomendasi.'}), 500


@legacy_bp.route('/analyze-npk', methods=['POST'])
def analyze_npk_endpoint():
    """Legacy NPK analysis endpoint."""
    try:
        data = request.get_json()
        n, p, k = int(data['n_value']), int(data['p_value']), int(data['k_value'])
        
        # Hindari FK error jika tabel users atau user_id=1 tidak tersedia
        user_id = None 
        
        reading = NpkReading(n_value=n, p_value=p, k_value=k, user_id=user_id)
        
        analysis = analysis_service.get_npk_analysis(n, p, k)
        reading.analysis_result = analysis
        
        db.session.add(reading)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in /analyze-npk: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat menyimpan data.'}), 500


@legacy_bp.route('/get-prices', methods=['POST'])
def get_prices_endpoint():
    """Legacy market prices endpoint."""
    try:
        data = request.get_json()
        commodity_id = data.get('commodity')
        price_data = market_service.get_current_prices(commodity_id)
        if not price_data:
            return jsonify({'success': False, 'error': 'Data harga tidak ditemukan'}), 404
        return jsonify({'success': True, 'data': price_data})
    except Exception as e:
        current_app.logger.error(f"Error in /get-prices: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal pada data harga.'}), 500


@legacy_bp.route('/get-knowledge', methods=['POST'])
def get_knowledge_endpoint():
    """Legacy knowledge base endpoint."""
    try:
        data = request.get_json()
        commodity_id = data.get('commodity')
        knowledge_data = knowledge_service.get_crop_knowledge(commodity_id)
        if not knowledge_data:
            return jsonify({'success': False, 'error': 'Informasi tidak ditemukan'}), 404
        return jsonify({'success': True, 'data': knowledge_data})
    except Exception as e:
        current_app.logger.error(f"Error in /get-knowledge: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal pada basis pengetahuan.'}), 500


@legacy_bp.route('/calculate-fertilizer', methods=['POST'])
def calculate_fertilizer_endpoint():
    """Legacy fertilizer calculator endpoint."""
    try:
        data = request.get_json()
        commodity_id = data.get('commodity')
        area_sqm = float(data.get('area_sqm', 0))
        ph_tanah = float(data.get('ph_tanah', 7.0))
        
        if not commodity_id or area_sqm <= 0:
            return jsonify({'success': False, 'error': 'Input tidak valid.'}), 400
            
        dosage_data = recommendation_service.calculate_holistic_fertilizer(commodity_id, area_sqm, ph_tanah)
        
        if not dosage_data:
            return jsonify({'success': False, 'error': 'Data dosis tidak ditemukan.'}), 404
            
        return jsonify({
            'success': True,
            'data': dosage_data['results'],
            'commodity_name': dosage_data['name'],
            'area_sqm': area_sqm
        })
    except Exception as e:
        current_app.logger.error(f"Error in /calculate-fertilizer: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat menghitung.'}), 500


@legacy_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf_endpoint():
    """Legacy PDF upload endpoint."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Tidak ada file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'File tidak dipilih'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'message': f'File {filename} berhasil diunggah.'})
    return jsonify({'success': False, 'error': 'Tipe file tidak diizinkan. Harap unggah PDF.'}), 400


@legacy_bp.route('/get-pdfs', methods=['GET'])
def get_pdfs_endpoint():
    """Legacy get PDFs list endpoint."""
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
        return jsonify({'success': True, 'files': sorted(files)})
    except Exception as e:
        current_app.logger.error(f"Error in /get-pdfs: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Gagal memuat daftar dokumen.'}), 500


@legacy_bp.route('/view-pdf/<path:filename>')
def view_pdf_endpoint(filename):
    """Legacy view PDF endpoint."""
    return send_from_directory(UPLOAD_FOLDER, filename)


@legacy_bp.route('/get-integrated-recommendation', methods=['POST'])
def get_integrated_recommendation_endpoint():
    """Legacy integrated recommendation endpoint."""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'error': 'Payload JSON tidak valid'}), 400
        ketinggian = data.get('ketinggian')
        iklim = data.get('iklim')
        fase = data.get('fase')
        masalah = data.get('masalah')
        recommendation_data = recommendation_service.get_integrated_recommendation(ketinggian, iklim, fase, masalah)
        return jsonify({'success': True, 'data': recommendation_data})
    except Exception as e:
        current_app.logger.error(f"Error in /get-integrated-recommendation: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat memproses rekomendasi.'}), 500


@legacy_bp.route('/get-spraying-recommendation', methods=['POST'])
def get_spraying_recommendation_endpoint():
    """Legacy spraying recommendation endpoint."""
    try:
        data = request.get_json()
        pest = data.get('pest')
        if not pest:
            return jsonify({'success': False, 'error': 'Hama/penyakit tidak dipilih'}), 400
        
        strategy = knowledge_service.get_spraying_strategy(pest)
        if not strategy:
            return jsonify({'success': False, 'error': 'Strategi tidak ditemukan.'}), 404
            
        return jsonify({'success': True, 'data': strategy})
    except Exception as e:
        current_app.logger.error(f"Error in /get-spraying-recommendation: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat memproses rekomendasi.'}), 500


@legacy_bp.route('/get-ticker-prices', methods=['GET'])
def get_ticker_prices_endpoint():
    """Legacy ticker prices endpoint."""
    try:
        ticker_data = market_service.get_ticker_prices()
        return jsonify({'success': True, 'data': ticker_data})
    except Exception as e:
        current_app.logger.error(f"Error in /get-ticker-prices: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Gagal memuat data ticker.'}), 500


@legacy_bp.route('/get-historical-prices', methods=['POST'])
def get_historical_prices_endpoint():
    """Legacy historical prices endpoint."""
    try:
        data = request.get_json()
        commodity_id = data.get('commodity')
        time_range = int(data.get('range', 30))
        if not commodity_id:
            return jsonify({'success': False, 'error': 'Komoditas tidak dipilih'}), 400
        
        historical_data = market_service.get_historical_prices(commodity_id, time_range)
        if historical_data is None:
            return jsonify({'success': False, 'error': 'Data historis tidak ditemukan'}), 404
            
        return jsonify({'success': True, 'labels': historical_data['labels'], 'prices': historical_data['prices']})
    except Exception as e:
        current_app.logger.error(f"Error in /get-historical-prices: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat memuat data historis.'}), 500


@legacy_bp.route('/get-commodity-guide', methods=['POST'])
def get_commodity_guide_endpoint():
    """Legacy commodity guide endpoint."""
    try:
        data = request.get_json()
        commodity = data.get('commodity')
        guide = knowledge_service.get_commodity_guide(commodity)
        if not guide:
            return jsonify({'success': False, 'error': 'Panduan untuk komoditas ini belum tersedia.'}), 404
        return jsonify({'success': True, 'data': guide})
    except Exception as e:
        current_app.logger.error(f"Error in /get-commodity-guide: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat memuat panduan.'}), 500


@legacy_bp.route('/get-ph-info', methods=['GET'])
def get_ph_info_endpoint():
    """Legacy pH knowledge base endpoint."""
    try:
        info = knowledge_service.get_ph_knowledge()
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        current_app.logger.error(f"Error in /get-ph-info: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat memuat informasi pH.'}), 500


@legacy_bp.route('/recommend-crop', methods=['POST'])
def recommend_crop_endpoint():
    """Legacy crop recommendation endpoint."""
    try:
        data = request.get_json()
        prediction = ml_service.recommend_crop(data)
        return jsonify({'success': True, 'recommended_crop': prediction})
    except Exception as e:
        current_app.logger.error(f"Error di /recommend-crop: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat membuat rekomendasi tanaman.'}), 500


@legacy_bp.route('/predict-yield', methods=['POST'])
def predict_yield_endpoint():
    """Legacy yield prediction endpoint."""
    try:
        data = request.get_json()
        prediction = ml_service.predict_yield(data)
        return jsonify({'success': True, 'predicted_yield_ton_ha': prediction})
    except Exception as e:
        current_app.logger.error(f"Error di /predict-yield: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat membuat prediksi panen.'}), 500


@legacy_bp.route('/predict-yield-advanced', methods=['POST'])
def predict_yield_advanced_endpoint():
    """Legacy XAI yield prediction endpoint."""
    try:
        data = request.get_json()
        result = ml_service.predict_yield_advanced(data)
        return jsonify({'success': True, **result})
    except Exception as e:
        current_app.logger.error(f"Error di /predict-yield-advanced: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat membuat prediksi XAI.'}), 500


@legacy_bp.route('/calculate-fertilizer-bags', methods=['POST'])
def calculate_fertilizer_bags_endpoint():
    """Legacy fertilizer conversion endpoint."""
    try:
        data = request.get_json()
        result = ml_service.calculate_fertilizer_bags(
            data['nutrient_needed'],
            float(data['nutrient_amount_kg']),
            data['fertilizer_type']
        )
        if not result:
            return jsonify({'success': False, 'error': 'Kalkulasi gagal. Periksa tipe pupuk dan nutrisi.'}), 400
        return jsonify({'success': True, 'required_fertilizer_kg': result['required_kg'], **data})
    except Exception as e:
        current_app.logger.error(f"Error di /calculate-fertilizer-bags: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat menghitung.'}), 500


@legacy_bp.route('/get-diagnostic-tree', methods=['GET'])
def get_diagnostic_tree_endpoint():
    """Legacy diagnostic tree endpoint."""
    try:
        tree = knowledge_service.get_diagnostic_tree()
        return jsonify({'success': True, 'data': tree})
    except Exception as e:
        current_app.logger.error(f"Error di /get-diagnostic-tree: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat memuat data diagnostik.'}), 500


@legacy_bp.route('/generate-yield-plan', methods=['POST'])
def generate_yield_plan_endpoint():
    """Legacy yield planning endpoint."""
    try:
        data = request.get_json()
        plan = ml_service.generate_yield_plan(float(data.get('target_yield', 0)))
        if not plan:
            return jsonify({'success': False, 'error': 'Tidak ditemukan data yang cocok untuk target panen tersebut.'}), 404
        return jsonify({'success': True, 'plan': plan})
    except Exception as e:
        current_app.logger.error(f"Error di /generate-yield-plan: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat membuat rencana panen.'}), 500


# --- ENDPOINT BARU UNTUK MODUL 20 & 21 ---

@legacy_bp.route('/predict-success', methods=['POST'])
def predict_success_endpoint():
    """Legacy success probability endpoint (Modul 21)."""
    try:
        data = request.get_json()
        result = ml_service.predict_success(data)
        return jsonify({'success': True, **result})
    except Exception as e:
        current_app.logger.error(f"Error di /predict-success: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat membuat analisis risiko.'}), 500


@legacy_bp.route('/analyze-disease-advanced', methods=['POST'])
def analyze_disease_advanced_endpoint():
    """Legacy advanced disease analysis endpoint (Modul 20)."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Tidak ada file yang diunggah.'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Tipe file tidak valid.'}), 400

    temp_path = None
    try:
        filename = secure_filename(f"{uuid.uuid4()}.jpg")
        temp_path = os.path.join(TEMP_IMAGE_FOLDER, filename)
        file.save(temp_path)
        current_app.logger.info(f"File sementara disimpan di: {temp_path}")

        client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=os.environ.get('ROBOFLOW_API_KEY', 'jPdPobkMUhG9yEKohrrP')
        )

        current_app.logger.info("Menjalankan workflow Roboflow...")
        result = client.run_workflow(
            workspace_name="andriyanto39",
            workflow_id="detect-and-classify",
            images={"image": temp_path},
            use_cache=True
        )
        current_app.logger.info("Workflow Roboflow berhasil dijalankan.")
        
        return jsonify({'success': True, 'data': result})

    except Exception as e:
        current_app.logger.error(f"Error di /analyze-disease-advanced: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Kesalahan internal saat berkomunikasi dengan layanan AI.'}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            current_app.logger.info(f"File sementara dihapus: {temp_path}")
