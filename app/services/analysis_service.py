"""Analysis service for leaf and soil analysis."""
import cv2
import numpy as np
from app.ml_models.model_loader import ModelLoader


class AnalysisService:
    """Service for analyzing leaf images and NPK values."""
    
    @staticmethod
    def analyze_leaf_image(image_data):
        """
        Analyze leaf image for BWD score.
        
        Args:
            image_data: Binary image data
            
        Returns:
            dict: Analysis results with score, hue, and confidence
        """
        try:
            bwd_model = ModelLoader.get_model('bwd')
            if bwd_model is None:
                raise RuntimeError("BWD model not loaded")
            
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
            
            # Convert to HSV color space
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create mask for green color (leaves)
            lower_green = np.array([30, 40, 40])
            upper_green = np.array([90, 255, 255])
            mask = cv2.inRange(hsv_image, lower_green, upper_green)
            
            # Check if any green pixels found
            if cv2.countNonZero(mask) == 0:
                return None
            
            # Calculate average hue value
            avg_hue = cv2.mean(hsv_image, mask=mask)[0]
            
            # Predict BWD score
            input_data = np.array([[avg_hue]])
            predicted_score = bwd_model.predict(input_data)[0]
            confidence = np.max(bwd_model.predict_proba(input_data)) * 100
            
            return {
                'bwd_score': int(predicted_score),
                'avg_hue': round(avg_hue, 2),
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            raise RuntimeError(f"Leaf analysis failed: {str(e)}")
    
    @staticmethod
    def analyze_npk_values(n_value, p_value, k_value):
        """
        Analyze NPK values and provide recommendations.
        
        Args:
            n_value: Nitrogen value
            p_value: Phosphorus value
            k_value: Potassium value
            
        Returns:
            dict: Analysis results with recommendations
        """
        analysis = {}
        
        # Nitrogen analysis
        if 100 <= n_value <= 200:
            n_label = "Optimal"
            n_rec = "Nitrogen level is optimal. Maintain current fertilization."
        elif n_value < 100:
            n_label = "Rendah"
            n_rec = "Nitrogen is low. Increase Urea or organic nitrogen sources."
        else:
            n_label = "Berlebih"
            n_rec = "Nitrogen is excessive. Reduce nitrogen fertilizers to prevent lodging."
        
        analysis['Nitrogen (N)'] = {
            'value': n_value,
            'label': n_label,
            'rekomendasi': n_rec
        }
        
        # Phosphorus analysis
        if 20 <= p_value <= 40:
            p_label = "Optimal"
            p_rec = "Phosphorus level is optimal. Important for root and flower development."
        elif p_value < 20:
            p_label = "Rendah"
            p_rec = "Phosphorus is low. Apply SP-36 or rock phosphate."
        else:
            p_label = "Berlebih"
            p_rec = "Phosphorus is excessive. May interfere with micronutrient uptake."
        
        analysis['Fosfor (P)'] = {
            'value': p_value,
            'label': p_label,
            'rekomendasi': p_rec
        }
        
        # Potassium analysis
        if 150 <= k_value <= 250:
            k_label = "Optimal"
            k_rec = "Potassium level is optimal. Important for fruit quality."
        elif k_value < 150:
            k_label = "Rendah"
            k_rec = "Potassium is low. Apply KCL or organic potassium sources."
        else:
            k_label = "Berlebih"
            k_rec = "Potassium is excessive. May cause salt stress."
        
        analysis['Kalium (K)'] = {
            'value': k_value,
            'label': k_label,
            'rekomendasi': k_rec
        }
        
        return analysis
