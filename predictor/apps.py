from django.apps import AppConfig


class PredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictor'
    
    def ready(self):
        # Import signals to register them
        # Import signals to register them
        import predictor.signals
        
        # Clear module-level caches on startup to ensure fresh data
        # This fixes issues on Render where old caches might persist
        try:
            import predictor.analytics
            if hasattr(predictor.analytics, '_data_cache'):
                predictor.analytics._data_cache = {}
            if hasattr(predictor.analytics, '_team_categories_cache'):
                predictor.analytics._team_categories_cache = None
        except ImportError:
            pass
