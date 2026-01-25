from abc import ABC, abstractmethod

class DataAdapter(ABC):
    @abstractmethod
    def get_home_column(self):
        pass
    
    @abstractmethod
    def get_away_column(self):
        pass
    
    @abstractmethod
    def get_result_column(self):
        pass
    
    @abstractmethod
    def normalize_result(self, result):
        """Convert result to standard format (0=Away, 1=Draw, 2=Home)"""
        pass

class V1DataAdapter(DataAdapter):
    def get_home_column(self):
        return "HomeTeam"
    
    def get_away_column(self):
        return "AwayTeam"
    
    def get_result_column(self):
        return "FTR"
    
    def normalize_result(self, result):
        # v1: H, D, A
        # Also maintain compatibility if numeric
        try:
             res_int = int(result)
             if res_int in [0, 1, 2]: return res_int
        except:
             pass
             
        mapping = {'A': 0, 'D': 1, 'H': 2}
        return mapping.get(str(result).strip(), 1) # Default to Draw if unknown

class V2DataAdapter(DataAdapter):
    def get_home_column(self):
        return "Home"
    
    def get_away_column(self):
        return "Away"
    
    def get_result_column(self):
        return "Res"
    
    def normalize_result(self, result):
        # v2: 0, 1, 2 (numeric)
        try:
            return int(result)
        except:
            # Fallback if string
            mapping = {'A': 0, 'D': 1, 'H': 2}
            return mapping.get(str(result).strip(), 1)

class DataAdapterFactory:
    @staticmethod
    def create(data=None, version_str=None):
        if version_str == 'v2':
             return V2DataAdapter()
        if version_str == 'v1':
             return V1DataAdapter()
             
        if data is not None and hasattr(data, 'columns'):
            if 'Home' in data.columns and 'Away' in data.columns:
                return V2DataAdapter()
            elif 'HomeTeam' in data.columns and 'AwayTeam' in data.columns:
                return V1DataAdapter()
                
        # Fallback based on attrs if available
        if data is not None and hasattr(data, 'attrs') and 'version' in data.attrs:
             if data.attrs['version'] == 'v2':
                 return V2DataAdapter()
             return V1DataAdapter()
             
        return V1DataAdapter() # Default
