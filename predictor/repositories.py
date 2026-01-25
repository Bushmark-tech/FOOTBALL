import threading
import os
import logging
import warnings
import sys

# Configure logging
logger = logging.getLogger(__name__)

# Safe pandas import logic
def safe_import_pandas():
    try:
        import pandas as pd
        warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")
        return pd
    except Exception as e:
        logger.error(f"Failed to import pandas: {e}")
        return None

class InMemoryCache:
    """Thread-safe in-memory cache implementation."""
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get(self, key):
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key, value, ttl=None):
        with self._lock:
            self._cache[key] = value
            # Note: TTL not implemented for simplicity in this version
    
    def clear(self):
        with self._lock:
            self._cache.clear()

class FootballDataRepository:
    """
    Repository for accessing football data with caching and thread safety.
    """
    def __init__(self, cache_backend=None):
        self.cache = cache_backend or InMemoryCache()
        self._lock = threading.Lock()
        # Determine paths relative to this file
        # predictor/repositories.py -> predictor/ -> FOOTBALL/ -> data/
        self.base_dir = os.path.dirname(os.path.abspath(__file__)) # predictor/
        self.project_root = os.path.dirname(self.base_dir) # FOOTBALL/
        self.data_dir = os.path.join(self.project_root, 'data')
        
        # Fallback path: lGIC folder (outside project)
        self.lgic_path = os.path.join(os.path.dirname(self.project_root), 'lGIC')

    def _resolve_path(self, filename):
        # 1. Check project data directory
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            return path
            
        # 2. Check lGIC directory
        path_lgic = os.path.join(self.lgic_path, filename)
        if os.path.exists(path_lgic):
            return path_lgic
            
        return None

    def get_dataset(self, dataset_id):
        """
        Get dataset by ID (1 or 2).
        """
        cache_key = f"football_data_{dataset_id}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
             return cached_data

        filename = f"football_data{dataset_id}.csv"
        file_path = self._resolve_path(filename)
        
        if not file_path:
             logger.error(f"Dataset {dataset_id} not found (checked {self.data_dir} and {self.lgic_path})")
             return None

        # Special handling for dataset 2 (Switzerland data check)
        if dataset_id == 2:
            # We already resolved the path, so just load it
            pass

        return self._load_and_cache(file_path, cache_key, encoding='latin-1')

    def get_team_mapping(self):
        """Get team mapping dictionary."""
        cache_key = "team_mapping"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
            
        file_path = self._resolve_path("team_mapping.csv")
        if not file_path:
            logger.warning("team_mapping.csv not found, returning empty mapping")
            return {}
            
        return self._load_mapping_and_cache(file_path, cache_key)

    def _load_and_cache(self, file_path, cache_key, encoding='utf-8'):
        with self._lock:
            # Double check inside lock
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
                
            logger.info(f"Loading data from {file_path}")
            try:
                pd = safe_import_pandas()
                if pd is None: return None
                
                # Load data
                data = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                
                # Post-processing
                if 'Date' in data.columns:
                     data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                
                self.cache.set(cache_key, data)
                return data
            except Exception as e:
                logger.error(f"Error loading data from {file_path}: {e}")
                return None

    def _load_mapping_and_cache(self, file_path, cache_key):
         with self._lock:
            # Double check
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
                
            logger.info(f"Loading mapping from {file_path}")
            try:
                pd = safe_import_pandas()
                if pd is None: return {}
                
                df = pd.read_csv(file_path)
                mapping = {}
                # Handle flexible column names
                name_col = next((c for c in df.columns if c.lower() in ['teamname', 'team_name', 'name', 'team']), None)
                id_col = next((c for c in df.columns if c.lower() in ['teamid', 'team_id', 'id']), None)
                
                if name_col and id_col:
                    for _, row in df.iterrows():
                        mapping[str(row[name_col]).strip()] = row[id_col]
                    logger.info(f"Loaded {len(mapping)} team mappings")
                else:
                    logger.warning(f"Could not find Name/ID columns in mapping file. Columns: {df.columns}")
                
                self.cache.set(cache_key, mapping)
                return mapping
            except Exception as e:
                logger.error(f"Error loading mapping {file_path}: {e}")
                return {}

    def get_team_matches(self, team_name, data, adapter):
        """
        Centralized team query logic.
        """
        if data is None or data.empty:
            return data
            
        home_col = adapter.get_home_column()
        away_col = adapter.get_away_column()
        
        # Convert team name/ID to string for comparison
        team_name_str = str(team_name).strip()
        
        # Single optimized query
        mask = ((data[home_col].astype(str).str.strip() == team_name_str) | 
                (data[away_col].astype(str).str.strip() == team_name_str))
        return data[mask]
    
    def get_h2h_matches(self, home_team, away_team, data, adapter):
        """
        Centralized H2H query.
        Returns tuples of (home_matches, away_matches) where:
        - home_matches: home_team is HOME and away_team is AWAY
        - away_matches: home_team is AWAY and away_team is HOME (reversed fixture)
        """
        if data is None or data.empty:
            pd = safe_import_pandas()
            empty = pd.DataFrame() if pd else None
            return empty, empty

        home_col = adapter.get_home_column()
        away_col = adapter.get_away_column()
        
        # Convert team names/IDs to strings for comparison
        home_team_str = str(home_team).strip()
        away_team_str = str(away_team).strip()
        
        # Direction 1: home is home, away is away
        mask1 = ((data[home_col].astype(str).str.strip() == home_team_str) & 
                 (data[away_col].astype(str).str.strip() == away_team_str))
        
        # Direction 2: reversed (home is away, away is home)
        mask2 = ((data[home_col].astype(str).str.strip() == away_team_str) & 
                 (data[away_col].astype(str).str.strip() == home_team_str))
        
        return data[mask1], data[mask2]
    
    def clear_cache(self):
        """Clear the repository cache."""
        self.cache.clear()

# Singleton instance
_repo_instance = None
_repo_lock = threading.Lock()

def get_repository():
    """Get the singleton repository instance."""
    global _repo_instance
    if _repo_instance is None:
        with _repo_lock:
            if _repo_instance is None:
                try:
                    # Provide an integration point for Django's cache if available
                    # For now just use InMemoryCache
                    _repo_instance = FootballDataRepository()
                except Exception as e:
                    logger.error(f"Error initializing repository: {e}")
                    _repo_instance = FootballDataRepository() # Fallback
    return _repo_instance
