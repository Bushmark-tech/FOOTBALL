"""
Model 1 Production Readiness Test
Tests Model1 accuracy on European leagues and identifies production issues
"""

import os
import sys
import django
import logging
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

import pandas as pd
import numpy as np
from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class Model1ProductionTester:
    """Test Model1 for production readiness"""
    
    def __init__(self):
        self.model1, self.model2 = load_prediction_models()
        self.results = {
            'total': 0,
            'correct': 0,
            'predictions': [],
            'by_outcome': {},
            'confidence_buckets': {
                'high': {'total': 0, 'correct': 0},  # >60%
                'medium': {'total': 0, 'correct': 0},  # 40-60%
                'low': {'total': 0, 'correct': 0}  # <40%
            }
        }
        
    def load_european_data(self, sample_size=100):
        """Load European league data for testing"""
        try:
            df = pd.read_csv(r"C:\Users\user\Desktop\Ftball_main\FOOTBALL\data\football_data1.csv")
            
            # Filter for complete data
            df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTR'])
            
            # Sort by date and take recent matches
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date'])
                df = df.sort_values('Date', ascending=False)
            
            # Sample
            df = df.head(sample_size)
            
            print(f"✅ Loaded {len(df)} European league matches for testing\n")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def get_actual_outcome(self, row):
        """Get actual match outcome"""
        result = str(row['FTR']).upper()
        if result == 'H':
            return 'Home'
        elif result == 'A':
            return 'Away'
        elif result == 'D':
            return 'Draw'
        return None
    
    def test_match(self, home_team, away_team, actual_outcome):
        """Test a single match prediction"""
        try:
            # Make prediction using Model1
            result = advanced_predict_match(
                home_team, 
                away_team, 
                self.model1, 
                self.model2,
                category='European Leagues'
            )
            
            if not result:
                return None
            
            predicted = result.get('outcome')
            confidence = result.get('confidence', 0)
            probs = result.get('probabilities', {})
            model_used = result.get('model_type')
            
            # Check correctness
            is_correct = predicted == actual_outcome
            
            # Handle double chance
            if predicted in ['1X', 'X2', '12']:
                if predicted == '1X' and actual_outcome in ['Home', 'Draw']:
                    is_correct = True
                elif predicted == 'X2' and actual_outcome in ['Draw', 'Away']:
                    is_correct = True
                elif predicted == '12' and actual_outcome in ['Home', 'Away']:
                    is_correct = True
            
            # Record result
            self.results['total'] += 1
            if is_correct:
                self.results['correct'] += 1
            
            # Track by outcome
            if predicted not in self.results['by_outcome']:
                self.results['by_outcome'][predicted] = {'total': 0, 'correct': 0}
            self.results['by_outcome'][predicted]['total'] += 1
            if is_correct:
                self.results['by_outcome'][predicted]['correct'] += 1
            
            # Track by confidence
            if confidence > 0.6:
                bucket = 'high'
            elif confidence > 0.4:
                bucket = 'medium'
            else:
                bucket = 'low'
            
            self.results['confidence_buckets'][bucket]['total'] += 1
            if is_correct:
                self.results['confidence_buckets'][bucket]['correct'] += 1
            
            # Store prediction
            self.results['predictions'].append({
                'match': f"{home_team} vs {away_team}",
                'predicted': predicted,
                'actual': actual_outcome,
                'correct': is_correct,
                'confidence': confidence,
                'probabilities': probs,
                'model': model_used
            })
            
            return is_correct
            
        except Exception as e:
            print(f"❌ Error testing {home_team} vs {away_team}: {e}")
            return None
    
    def run_tests(self, sample_size=100):
        """Run all tests"""
        print("="*70)
        print("🏆 MODEL 1 PRODUCTION READINESS TEST - EUROPEAN LEAGUES")
        print("="*70)
        print()
        
        # Load data
        df = self.load_european_data(sample_size)
        if df is None or df.empty:
            print("❌ No test data available")
            return
        
        # Run tests
        print("🔄 Running predictions...\n")
        for idx, row in df.iterrows():
            home_team = str(row['HomeTeam'])
            away_team = str(row['AwayTeam'])
            actual = self.get_actual_outcome(row)
            
            if actual:
                self.test_match(home_team, away_team, actual)
        
        # Generate report
        self.generate_production_report()
    
    def generate_production_report(self):
        """Generate production readiness report"""
        print("="*70)
        print("📊 PRODUCTION READINESS REPORT")
        print("="*70)
        print()
        
        if self.results['total'] == 0:
            print("❌ No tests completed")
            return
        
        # Overall accuracy
        accuracy = (self.results['correct'] / self.results['total']) * 100
        
        print(f"📈 OVERALL ACCURACY: {accuracy:.1f}%")
        print(f"   ✅ Correct: {self.results['correct']}/{self.results['total']}")
        print(f"   ❌ Incorrect: {self.results['total'] - self.results['correct']}/{self.results['total']}")
        print()
        
        # Production readiness assessment
        print("🎯 PRODUCTION READINESS:")
        if accuracy >= 55:
            print(f"   ✅ EXCELLENT - Model is production-ready (>{accuracy:.1f}%)")
            production_ready = "YES"
        elif accuracy >= 45:
            print(f"   ⚠️  GOOD - Acceptable for production ({accuracy:.1f}%)")
            print(f"       → Monitor performance and consider improvements")
            production_ready = "YES (with monitoring)"
        elif accuracy >= 35:
            print(f"   ⚠️  FAIR - Marginal for production ({accuracy:.1f}%)")
            print(f"       → Needs improvement before full deployment")
            production_ready = "CONDITIONAL"
        else:
            print(f"   ❌ POOR - NOT production-ready ({accuracy:.1f}%)")
            print(f"       → Requires retraining with better features")
            production_ready = "NO"
        print()
        
        # Accuracy by prediction type
        print("📊 ACCURACY BY PREDICTION TYPE:")
        for outcome in sorted(self.results['by_outcome'].keys()):
            stats = self.results['by_outcome'][outcome]
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total']) * 100
                pct = (stats['total'] / self.results['total']) * 100
                print(f"   {outcome:12} {acc:5.1f}% accurate ({stats['correct']:2}/{stats['total']:2}) - {pct:4.1f}% of predictions")
        print()
        
        # Confidence calibration
        print("🎯 CONFIDENCE CALIBRATION:")
        for bucket, stats in self.results['confidence_buckets'].items():
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total']) * 100
                print(f"   {bucket.capitalize():8} confidence: {acc:5.1f}% accurate ({stats['correct']}/{stats['total']})")
        print()
        
        # Identify issues
        self.identify_production_issues(accuracy, production_ready)
    
    def identify_production_issues(self, accuracy, production_ready):
        """Identify specific production issues"""
        print("⚠️  POTENTIAL PRODUCTION ISSUES:")
        print()
        
        issues_found = False
        
        # Check for prediction bias
        outcomes = [p['predicted'] for p in self.results['predictions']]
        if outcomes:
            draw_pct = (outcomes.count('Draw') / len(outcomes)) * 100
            home_pct = (outcomes.count('Home') / len(outcomes)) * 100
            away_pct = (outcomes.count('Away') / len(outcomes)) * 100
            
            if draw_pct > 45:
                print(f"   1. ❌ DRAW BIAS: {draw_pct:.1f}% predictions are draws")
                print(f"      → Model struggles to pick clear winners")
                print(f"      → Impact: Users may lose trust in predictions")
                issues_found = True
            
            if home_pct > 55:
                print(f"   2. ⚠️  HOME BIAS: {home_pct:.1f}% favor home team")
                print(f"      → Overvaluing home advantage")
                print(f"      → Impact: Poor accuracy for away wins")
                issues_found = True
            
            if away_pct < 15:
                print(f"   3. ⚠️  AWAY UNDERVALUATION: Only {away_pct:.1f}% predict away wins")
                print(f"      → Missing profitable away win opportunities")
                issues_found = True
        
        # Check confidence calibration
        high_conf = self.results['confidence_buckets']['high']
        if high_conf['total'] > 0:
            high_acc = (high_conf['correct'] / high_conf['total']) * 100
            if high_acc < 65:
                print(f"   4. ❌ OVERCONFIDENCE: High confidence predictions only {high_acc:.1f}% accurate")
                print(f"      → Model confidence doesn't match actual accuracy")
                print(f"      → Impact: Users may bet on false confidence")
                issues_found = True
        
        # Check for model selection issues
        model1_count = sum(1 for p in self.results['predictions'] if p.get('model') == 'Model1')
        model2_count = sum(1 for p in self.results['predictions'] if p.get('model') == 'Model2')
        
        if model2_count > model1_count:
            print(f"   5. ⚠️  MODEL SELECTION: Using Model2 ({model2_count}) more than Model1 ({model1_count})")
            print(f"      → European leagues should primarily use Model1")
            print(f"      → Impact: Lower accuracy due to wrong model")
            issues_found = True
        
        # Check variance in probabilities
        avg_max_prob = np.mean([max(p['probabilities'].values()) for p in self.results['predictions'] 
                                if p['probabilities']])
        if avg_max_prob < 0.45:
            print(f"   6. ⚠️  LOW CONFIDENCE: Average max probability {avg_max_prob:.1%}")
            print(f"      → Model is too uncertain")
            print(f"      → Impact: No clear betting recommendations")
            issues_found = True
        
        if not issues_found:
            print("   ✅ No major production issues detected!")
        
        print()
        print("="*70)
        print()
        
        # Final recommendation
        print("💡 FINAL RECOMMENDATION:")
        print()
        if production_ready == "YES":
            print("   ✅ Model1 is READY for production deployment")
            print("   → Deploy with confidence")
            print("   → Monitor accuracy weekly")
            print("   → Retrain quarterly with new data")
        elif production_ready == "YES (with monitoring)":
            print("   ⚠️  Model1 can be deployed with CLOSE MONITORING")
            print("   → Set up accuracy tracking dashboard")
            print("   → Review predictions daily for first 2 weeks")
            print("   → Plan model improvements in parallel")
        elif production_ready == "CONDITIONAL":
            print("   ⚠️  Deploy to LIMITED users first (beta testing)")
            print("   → Start with 10-20% of traffic")
            print("   → Collect user feedback")
            print("   → Improve model based on real-world performance")
        else:
            print("   ❌ DO NOT deploy to production yet")
            print("   → Retrain model with better features")
            print("   → Add more discriminative variables")
            print("   → Test again before deployment")
        
        print()
        print("="*70)


def main():
    """Run Model1 production test"""
    tester = Model1ProductionTester()
    tester.run_tests(sample_size=100)


if __name__ == "__main__":
    main()
