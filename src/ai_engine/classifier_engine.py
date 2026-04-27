import joblib
import os
from src.ai_engine.mapping import get_levels # La función de traducción cs.AI -> Nivel 1/2

class PaperClassifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), 'model_v1.joblib')
        self.model = joblib.load(model_path) if os.path.exists(model_path) else None

    def predict(self, text):
        if not self.model: return "Unknown", "Unknown", 0.0
        
        raw_tag = self.model.predict([text])[0]
        probs = self.model.predict_proba([text])
        confidence = max(probs[0])
        
        # Obtenemos los dos niveles
        cat, subcat = get_levels(raw_tag)
        return cat, subcat, round(float(confidence), 2)

classifier = PaperClassifier()