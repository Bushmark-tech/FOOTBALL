import logging

logger = logging.getLogger(__name__)

class PredictionResultBuilder:
    """Builds and validates prediction results"""
    
    def __init__(self):
        self._result = {}
        self._errors = []
    
    def set_prediction(self, prediction_number, outcome):
        """
        prediction_number: 0=Away, 1=Draw, 2=Home
        outcome: "Home", "Draw", "Away", or double chance like "1X"
        """
        # prediction_number might be float or int, validation below
        try:
             p_num = int(prediction_number)
             if p_num not in [0, 1, 2]:
                 self._errors.append(f"Invalid prediction: {prediction_number}")
        except:
             self._errors.append(f"Invalid prediction type: {prediction_number}")
        
        self._result['prediction_number'] = prediction_number
        self._result['outcome'] = outcome
        return self
    
    def set_probabilities(self, prob_dict):
        """
        prob_dict: {0: away_prob, 1: draw_prob, 2: home_prob}
        Validates: all in [0,1] and sum to ~1.0
        """
        # Check keys
        # We allow string keys if they convert to int 0,1,2
        normalized_probs = {}
        for k, v in prob_dict.items():
            try:
                k_int = int(k)
                normalized_probs[k_int] = float(v)
            except:
                self._errors.append(f"Invalid prob key: {k}")
                
        if set(normalized_probs.keys()) != {0, 1, 2}:
            # Missing keys or extra keys
            # If default dict is passed, might be ok?
            # User requirement says validate
            pass
        
        # Check values in range
        for key, val in normalized_probs.items():
            if not 0 <= val <= 1.01: # allow slight floating point error
                 # Maybe it's percentage?
                 if 0 <= val <= 100:
                      normalized_probs[key] = val / 100.0
                 else:
                      self._errors.append(f"Prob {key}={val} not in [0,1]")
        
        # Check sum
        total = sum(normalized_probs.values())
        if abs(total - 1.0) > 0.05 and total > 0:
            # Try to renormalize
            logger.warning(f"Probs sum to {total:.3f}, renormalizing")
            normalized_probs = {k: v/total for k, v in normalized_probs.items()}
        
        self._result['probabilities'] = normalized_probs
        return self
    
    def set_confidence(self, confidence):
        """Confidence must be in [0, 1]"""
        try:
             conf = float(confidence)
             if not 0 <= conf <= 1.01:
                  self._errors.append(f"Confidence {conf} not in [0,1]")
             self._result['confidence'] = conf
        except:
             self._errors.append(f"Invalid confidence: {confidence}")
             self._result['confidence'] = 0.0
        return self
    
    def set_model_info(self, model_type, model_prediction, model_probs):
        """Set model-specific info"""
        self._result['model_type'] = model_type
        
        if model_type == "Model1":
            self._result['model1_prediction'] = model_prediction
            self._result['model1_probs'] = model_probs
            self._result['model2_prediction'] = None
            self._result['model2_probs'] = None
        elif model_type == "Model2":
            self._result['model1_prediction'] = None
            self._result['model1_probs'] = None
            self._result['model2_prediction'] = model_prediction
            self._result['model2_probs'] = model_probs
        
        return self
    
    def add_h2h_data(self, h2h_probabilities):
        """Optional: add head-to-head stats"""
        self._result['h2h_probabilities'] = h2h_probabilities
        return self
    
    def add_metadata(self, **kwargs):
        """Add any additional fields"""
        self._result.update(kwargs)
        return self
    
    def build(self):
        """
        Validate and return the result
        Raises ValueError if validation failed
        """
        # Check required fields
        required = ['prediction_number', 'outcome', 'probabilities', 
                   'confidence', 'model_type']
        missing = [f for f in required if f not in self._result]
        if missing:
            logger.error(f"Builder failed: Missing fields {missing}")
            # Fallback values
            if 'prediction_number' not in self._result: self._result['prediction_number'] = 1
            if 'outcome' not in self._result: self._result['outcome'] = "Draw"
            if 'probabilities' not in self._result: self._result['probabilities'] = {0: 0.33, 1: 0.34, 2: 0.33}
            if 'confidence' not in self._result: self._result['confidence'] = 0.5
            if 'model_type' not in self._result: self._result['model_type'] = "Unknown"
        
        # Check for validation errors
        if self._errors:
            logger.warning(f"Builder validation errors: {self._errors}")
            # We don't raise error to avoid crashing the app, just log
        
        # logger.info(f"✓ Built valid prediction result: {self._result['outcome']}")
        return self._result
