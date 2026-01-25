"""
Model Accuracy Testing Script
Tests prediction accuracy and identifies areas for improvement
"""

import os
import sys
import django
import logging
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

import pandas as pd
import numpy as np
from predictor.analytics import advanced_predict_match, load_team_mapping
from predictor.views import load_prediction_models

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelAccuracyTester:
    """Test model accuracy and provide improvement recommendations"""
    
    def __init__(self):
        self.model1, self.model2 = load_prediction_models()
        self.team_mapping = load_team_mapping()
        self.results = {
            'total_tests': 0,
            'correct_predictions': 0,
            'correct_outcomes': 0,
            'predictions': [],
            'by_category': {},
            'by_model': {'Model1': {'total': 0, 'correct': 0}, 'Model2': {'total': 0, 'correct': 0}}
        }
        
    def load_test_data(self, dataset_path, sample_size=100):
        """Load recent matches for testing"""
        try:
            df = pd.read_csv(dataset_path)
            logger.info(f"Loaded {len(df)} matches from {dataset_path}")
            
            # Filter for recent matches with complete data
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date'])
                df = df.sort_values('Date', ascending=False)
            
            # Take sample
            df = df.head(sample_size)
            logger.info(f"Testing on {len(df)} recent matches")
            
            return df
        except Exception as e:
            logger.error(f"Error loading test data: {e}")
            return None
    
    def get_actual_outcome(self, row, adapter_version='v1'):
        """Extract actual match outcome from data"""
        try:
            if adapter_version == 'v1':
                result = row.get('FTR', row.get('Res'))
            else:
                result = row.get('Res', row.get('FTR'))
            
            # Map result to outcome
            if pd.isna(result):
                return None
            
            result_str = str(result).upper()
            if result_str in ['H', '2', 'HOME']:
                return 'Home'
            elif result_str in ['A', '0', 'AWAY']:
                return 'Away'
            elif result_str in ['D', '1', 'DRAW']:
                return 'Draw'
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting actual outcome: {e}")
            return None
    
    def test_prediction(self, home_team, away_team, actual_outcome, category='European Leagues'):
        """Test a single prediction"""
        try:
            # Make prediction
            result = advanced_predict_match(
                home_team, 
                away_team, 
                self.model1, 
                self.model2,
                category=category
            )
            
            if not result:
                logger.warning(f"No prediction for {home_team} vs {away_team}")
                return None
            
            predicted_outcome = result.get('outcome')
            model_type = result.get('model_type', 'Unknown')
            confidence = result.get('confidence', 0)
            probabilities = result.get('probabilities', {})
            
            # Check if prediction is correct
            is_correct = predicted_outcome == actual_outcome
            
            # Handle double chance outcomes
            if predicted_outcome in ['1X', 'X2', '12']:
                if predicted_outcome == '1X' and actual_outcome in ['Home', 'Draw']:
                    is_correct = True
                elif predicted_outcome == 'X2' and actual_outcome in ['Draw', 'Away']:
                    is_correct = True
                elif predicted_outcome == '12' and actual_outcome in ['Home', 'Away']:
                    is_correct = True
            
            # Record result
            test_result = {
                'home_team': home_team,
                'away_team': away_team,
                'predicted': predicted_outcome,
                'actual': actual_outcome,
                'correct': is_correct,
                'model': model_type,
                'confidence': confidence,
                'probabilities': probabilities,
                'category': category
            }
            
            self.results['predictions'].append(test_result)
            self.results['total_tests'] += 1
            
            if is_correct:
                self.results['correct_predictions'] += 1
            
            # Track by model
            if model_type in self.results['by_model']:
                self.results['by_model'][model_type]['total'] += 1
                if is_correct:
                    self.results['by_model'][model_type]['correct'] += 1
            
            # Track by category
            if category not in self.results['by_category']:
                self.results['by_category'][category] = {'total': 0, 'correct': 0}
            self.results['by_category'][category]['total'] += 1
            if is_correct:
                self.results['by_category'][category]['correct'] += 1
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error testing prediction for {home_team} vs {away_team}: {e}")
            return None
    
    def run_tests(self, dataset_path, sample_size=100, category='European Leagues'):
        """Run all tests"""
        logger.info(f"\n{'='*60}")
        logger.info(f"STARTING MODEL ACCURACY TESTS")
        logger.info(f"{'='*60}\n")
        
        # Load test data
        df = self.load_test_data(dataset_path, sample_size)
        if df is None or df.empty:
            logger.error("No test data available")
            return
        
        # Determine column names
        home_col = 'HomeTeam' if 'HomeTeam' in df.columns else 'Home'
        away_col = 'AwayTeam' if 'AwayTeam' in df.columns else 'Away'
        adapter_version = 'v1' if 'HomeTeam' in df.columns else 'v2'
        
        # Run tests
        for idx, row in df.iterrows():
            home_team = row.get(home_col)
            away_team = row.get(away_col)
            actual_outcome = self.get_actual_outcome(row, adapter_version)
            
            if pd.isna(home_team) or pd.isna(away_team) or actual_outcome is None:
                continue
            
            logger.info(f"Testing: {home_team} vs {away_team} (Actual: {actual_outcome})")
            self.test_prediction(str(home_team), str(away_team), actual_outcome, category)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive accuracy report"""
        logger.info(f"\n{'='*60}")
        logger.info(f"MODEL ACCURACY REPORT")
        logger.info(f"{'='*60}\n")
        
        if self.results['total_tests'] == 0:
            logger.warning("No tests completed")
            return
        
        # Overall accuracy
        accuracy = (self.results['correct_predictions'] / self.results['total_tests']) * 100
        logger.info(f"📊 OVERALL ACCURACY: {accuracy:.2f}%")
        logger.info(f"   Total Tests: {self.results['total_tests']}")
        logger.info(f"   Correct: {self.results['correct_predictions']}")
        logger.info(f"   Incorrect: {self.results['total_tests'] - self.results['correct_predictions']}\n")
        
        # Accuracy by model
        logger.info(f"🤖 ACCURACY BY MODEL:")
        for model, stats in self.results['by_model'].items():
            if stats['total'] > 0:
                model_acc = (stats['correct'] / stats['total']) * 100
                logger.info(f"   {model}: {model_acc:.2f}% ({stats['correct']}/{stats['total']})")
        logger.info("")
        
        # Accuracy by category
        logger.info(f"🏆 ACCURACY BY CATEGORY:")
        for category, stats in self.results['by_category'].items():
            if stats['total'] > 0:
                cat_acc = (stats['correct'] / stats['total']) * 100
                logger.info(f"   {category}: {cat_acc:.2f}% ({stats['correct']}/{stats['total']})")
        logger.info("")
        
        # Analyze prediction distribution
        self.analyze_prediction_distribution()
        
        # Identify improvement areas
        self.identify_improvements()
    
    def analyze_prediction_distribution(self):
        """Analyze distribution of predictions"""
        logger.info(f"📈 PREDICTION DISTRIBUTION:")
        
        outcomes = {}
        for pred in self.results['predictions']:
            outcome = pred['predicted']
            if outcome not in outcomes:
                outcomes[outcome] = {'count': 0, 'correct': 0}
            outcomes[outcome]['count'] += 1
            if pred['correct']:
                outcomes[outcome]['correct'] += 1
        
        for outcome, stats in sorted(outcomes.items(), key=lambda x: x[1]['count'], reverse=True):
            accuracy = (stats['correct'] / stats['count']) * 100 if stats['count'] > 0 else 0
            logger.info(f"   {outcome}: {stats['count']} predictions ({accuracy:.1f}% accurate)")
        logger.info("")
    
    def identify_improvements(self):
        """Identify areas for improvement"""
        logger.info(f"💡 IMPROVEMENT RECOMMENDATIONS:\n")
        
        # Check for bias
        outcomes = [p['predicted'] for p in self.results['predictions']]
        if outcomes:
            draw_pct = (outcomes.count('Draw') / len(outcomes)) * 100
            home_pct = (outcomes.count('Home') / len(outcomes)) * 100
            away_pct = (outcomes.count('Away') / len(outcomes)) * 100
            
            if draw_pct > 40:
                logger.info(f"   ⚠️  HIGH DRAW BIAS: {draw_pct:.1f}% of predictions are draws")
                logger.info(f"       → Consider retraining model with more discriminative features")
            
            if home_pct > 50:
                logger.info(f"   ⚠️  HOME BIAS: {home_pct:.1f}% of predictions favor home team")
                logger.info(f"       → Review home advantage weighting in model")
            
            if away_pct < 20:
                logger.info(f"   ⚠️  LOW AWAY PREDICTIONS: Only {away_pct:.1f}% predict away wins")
                logger.info(f"       → Model may undervalue away team strength")
        
        # Check confidence calibration
        high_conf_correct = sum(1 for p in self.results['predictions'] 
                               if p['confidence'] > 0.5 and p['correct'])
        high_conf_total = sum(1 for p in self.results['predictions'] 
                             if p['confidence'] > 0.5)
        
        if high_conf_total > 0:
            high_conf_acc = (high_conf_correct / high_conf_total) * 100
            logger.info(f"\n   📊 HIGH CONFIDENCE PREDICTIONS (>50%):")
            logger.info(f"       Accuracy: {high_conf_acc:.1f}% ({high_conf_correct}/{high_conf_total})")
            
            if high_conf_acc < 60:
                logger.info(f"       ⚠️  Model is overconfident - predictions don't match confidence")
                logger.info(f"       → Consider probability calibration")
        
        # Model comparison
        if self.results['by_model']['Model1']['total'] > 0 and self.results['by_model']['Model2']['total'] > 0:
            m1_acc = (self.results['by_model']['Model1']['correct'] / 
                     self.results['by_model']['Model1']['total']) * 100
            m2_acc = (self.results['by_model']['Model2']['correct'] / 
                     self.results['by_model']['Model2']['total']) * 100
            
            logger.info(f"\n   🔄 MODEL COMPARISON:")
            if m1_acc > m2_acc + 10:
                logger.info(f"       ✅ Model1 significantly outperforms Model2")
                logger.info(f"       → Consider using Model1 for more leagues")
            elif m2_acc > m1_acc + 10:
                logger.info(f"       ⚠️  Model2 outperforms Model1")
                logger.info(f"       → Model1 may need retraining with better features")
            else:
                logger.info(f"       ℹ️  Models perform similarly")
        
        logger.info(f"\n{'='*60}\n")


def main():
    """Main test execution"""
    tester = ModelAccuracyTester()
    
    # Test European leagues (Model1)
    logger.info("Testing European Leagues (Model1)...")
    european_data = r"C:\Users\user\Desktop\Ftball_main\FOOTBALL\data\football_data1.csv"
    if os.path.exists(european_data):
        tester.run_tests(european_data, sample_size=100, category='European Leagues')
    else:
        logger.error(f"European data not found: {european_data}")
    
    # Test other leagues (Model2)
    logger.info("\nTesting Other Leagues (Model2)...")
    other_data = r"C:\Users\user\Desktop\Ftball_main\FOOTBALL\data\football_data2.csv"
    if os.path.exists(other_data):
        # Reset for new category
        tester.results = {
            'total_tests': 0,
            'correct_predictions': 0,
            'predictions': [],
            'by_category': {},
            'by_model': {'Model1': {'total': 0, 'correct': 0}, 'Model2': {'total': 0, 'correct': 0}}
        }
        tester.run_tests(other_data, sample_size=50, category='Others')
    else:
        logger.warning(f"Other leagues data not found: {other_data}")


if __name__ == "__main__":
    main()
