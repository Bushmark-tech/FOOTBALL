from abc import ABC, abstractmethod
import logging
from .utils import normalize_team_name, safe_import_numpy

logger = logging.getLogger(__name__)

class TeamMatcher(ABC):
    def __init__(self):
        self.next_matcher = None
    
    def set_next(self, matcher):
        self.next_matcher = matcher
        return matcher
    
    def match(self, team_name, unique_teams, team_mapping=None):
        result = self._try_match(team_name, unique_teams, team_mapping)
        if result is not None:
             # logger.debug(f"Matches found using {self.__class__.__name__}: {result}")
             return result
        if self.next_matcher:
            return self.next_matcher.match(team_name, unique_teams, team_mapping)
        return None
    
    @abstractmethod
    def _try_match(self, team_name, unique_teams, team_mapping):
        pass

class ExactMatcher(TeamMatcher):
    def _try_match(self, team_name, unique_teams, team_mapping):
        if team_name in unique_teams:
            return team_name
        return None

class NormalizedMatcher(TeamMatcher):
    def _try_match(self, team_name, unique_teams, team_mapping):
        team_normalized = normalize_team_name(team_name)
        for team in unique_teams:
            if normalize_team_name(str(team)) == team_normalized:
                return team
        return None

class CaseInsensitiveMatcher(TeamMatcher):
    def _try_match(self, team_name, unique_teams, team_mapping):
        team_lower = str(team_name).lower().strip()
        for team in unique_teams:
            if str(team).lower().strip() == team_lower:
                return team
        return None

class IDMatcher(TeamMatcher):
    def _try_match(self, team_name, unique_teams, team_mapping):
        if not team_mapping:
            return None
            
        # Try to find ID from name
        target_id = team_mapping.get(str(team_name).strip())
        if target_id is None:
             target_id = team_mapping.get(normalize_team_name(team_name))
             
        if target_id is not None:
            # Check if this ID exists in unique_teams
            if len(unique_teams) > 0:
                sample = unique_teams[0]
                np = safe_import_numpy()
                is_numeric = False
                if np:
                    is_numeric = isinstance(sample, (int, float, np.integer, np.floating))
                else:
                    is_numeric = isinstance(sample, (int, float))
                
                if is_numeric:
                    if target_id in unique_teams:
                        return target_id
                else:
                    # Data uses names, but we have an ID from the mapping
                    # Check if any team in data maps to this ID
                    # This is O(N*M) worst case where N is unique teams, M is mapping size, but usually fast enough
                    for team in unique_teams:
                        team_str = str(team).strip()
                        if team_mapping.get(team_str) == target_id:
                            return team
        return None

class PartialMatcher(TeamMatcher):
    def _try_match(self, team_name, unique_teams, team_mapping):
        team_lower = str(team_name).lower().strip()
        for team in unique_teams:
            team_str = str(team).lower().strip()
            if team_lower in team_str or team_str in team_lower:
                return team
        return None

def get_team_matcher_chain():
    """Build and return the chain of responsibility."""
    root = ExactMatcher()
    root.set_next(NormalizedMatcher())\
        .set_next(CaseInsensitiveMatcher())\
        .set_next(IDMatcher())\
        .set_next(PartialMatcher())
    return root
