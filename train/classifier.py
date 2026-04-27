import joblib
import os
import numpy as np

class PaperClassifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), 'model_v1.joblib')
        if os.path.exists(model_path):
            data = joblib.load(model_path)
            self.model = data['model']
            self.mapping = data['mapping'] # Diccionario de códigos a nombres
        else:
            self.model = None

    def classify_for_user(self, text, user_interests_codes):
        """
        text: Contenido del PDF
        user_interests_codes: Lista de códigos que el usuario eligió (ej: ['cs.LG', 'cs.CV'])
        """
        if not self.model or not user_interests_codes:
            return "Sin Clasificar", 0.0

        # 1. Obtener probabilidades para TODAS las categorías que conoce el modelo
        probs = self.model.predict_proba([text])[0]
        classes = self.model.classes_ # Lista de todos los códigos (cs.LG, cs.CV, etc.)

        # 2. Filtrar solo las que le interesan al usuario
        filtered_probs = []
        for i, code in enumerate(classes):
            if code in user_interests_codes:
                filtered_probs.append((code, probs[i]))
        
        if not filtered_probs:
            return "No coincide con tus intereses", 0.0

        # 3. Encontrar la mejor categoría entre las permitidas
        best_code, confidence = max(filtered_probs, key=lambda x: x[1])
        
        # 4. Traducir código a nombre y separar en niveles
        full_name = self.mapping.get(best_code, best_code)
        
        # El nivel 1 suele ser la parte antes del punto en el código
        nivel_1_code = best_code.split('.')[0]
        
        return {
            "categoria_principal": nivel_1_code, # ej: cs
            "subcategoria": full_name,           # ej: Machine Learning
            "confianza": round(float(confidence), 2)
        }

# Instancia global
classifier = PaperClassifier()



if __name__ == '__main__':
    pc = PaperClassifier()
    text = '''
    Title: "Optimization of Deep Residual Networks for Real-time Image Segmentation"

    Abstract: In this paper, we propose a novel approach to improve the efficiency of convolutional neural networks in resource-constrained environments. By leveraging sparse matrix multiplications and quantized weights, our model achieves a 40% reduction in latency without significant loss in accuracy. We evaluate our method on the ImageNet dataset and demonstrate superior performance compared to traditional stochastic gradient descent baselines. Our findings suggest that structural pruning is essential for deploying large-scale models on edge devices.
    '''
    text = '''
The art of losing isn’t hard to master;
so many things seem filled with the intent
to be lost that their loss is no disaster.

Lose something every day. Accept the fluster
of lost door keys, the hour badly spent.
The art of losing isn’t hard to master.

Then practice losing farther, losing faster:
places, and names, and where it was you meant
to travel. None of these will bring disaster.
    '''
    print(pc.classify_for_user(text, ['cs.LG', 'cs.CV', 'cs.CL', 'cs.AI', 'stat.ML']))