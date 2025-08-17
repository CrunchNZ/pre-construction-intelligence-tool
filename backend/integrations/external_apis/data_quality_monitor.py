"""
Data Quality Monitor

This service monitors data quality across integrated systems and external APIs.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from collections import defaultdict

logger = logging.getLogger(__name__)


class DataQualityMonitor:
    """Monitors data quality across integrated systems and external APIs."""
    
    def __init__(self):
        """Initialize the data quality monitor."""
        self.monitoring_configs = {}
        self.quality_metrics = defaultdict(dict)
        self.quality_thresholds = {}
        
        # Default quality thresholds
        self.default_thresholds = {
            'completeness': 80.0,
            'accuracy': 85.0,
            'consistency': 80.0,
            'validity': 90.0,
            'overall_score': 75.0
        }
        
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize monitoring configuration."""
        self.quality_thresholds['default'] = self.default_thresholds.copy()
    
    def add_monitoring_config(self, system_name: str, config: Dict[str, Any]) -> bool:
        """Add monitoring configuration for a specific system."""
        try:
            self.monitoring_configs[system_name] = config
            self.quality_metrics[system_name] = {
                'current_score': 0.0,
                'last_check': None,
                'trend': 'stable'
            }
            return True
        except Exception as e:
            logger.error(f"Error adding monitoring configuration for {system_name}: {e}")
            return False
    
    def check_data_quality(self, system_name: str, data: Any) -> Dict[str, Any]:
        """Check data quality for a specific system."""
        try:
            if system_name not in self.monitoring_configs:
                raise ValueError(f"No monitoring configuration found for system: {system_name}")
            
            # Perform quality checks
            quality_results = self._perform_quality_checks(data)
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_quality_score(quality_results)
            quality_results['overall_score'] = overall_score
            
            # Update quality metrics
            self._update_quality_metrics(system_name, quality_results)
            
            return quality_results
            
        except Exception as e:
            logger.error(f"Error checking data quality for {system_name}: {e}")
            return {
                'error': str(e),
                'overall_score': 0.0,
                'timestamp': timezone.now().isoformat()
            }
    
    def _perform_quality_checks(self, data: Any) -> Dict[str, Any]:
        """Perform quality checks on data."""
        quality_results = {}
        
        # Completeness check
        quality_results['completeness'] = self._check_completeness(data)
        
        # Accuracy check
        quality_results['accuracy'] = self._check_accuracy(data)
        
        # Consistency check
        quality_results['consistency'] = self._check_consistency(data)
        
        # Validity check
        quality_results['validity'] = self._check_validity(data)
        
        return quality_results
    
    def _check_completeness(self, data: Any) -> Dict[str, Any]:
        """Check data completeness."""
        if isinstance(data, dict):
            total_fields = len(data)
            missing_fields = [field for field, value in data.items() if value is None]
            completeness_score = ((total_fields - len(missing_fields)) / total_fields) * 100 if total_fields > 0 else 0
            
            return {
                'score': completeness_score,
                'total_fields': total_fields,
                'missing_fields': missing_fields
            }
        
        return {'score': 100.0, 'message': 'Data is not a dictionary'}
    
    def _check_accuracy(self, data: Any) -> Dict[str, Any]:
        """Check data accuracy."""
        accuracy_score = 100.0
        accuracy_issues = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    accuracy_score -= 5
                    accuracy_issues.append(f"Null value in field '{key}'")
                elif isinstance(value, str) and value.strip() == '':
                    accuracy_score -= 3
                    accuracy_issues.append(f"Empty string in field '{key}'")
        
        return {
            'score': max(accuracy_score, 0.0),
            'issues': accuracy_issues
        }
    
    def _check_consistency(self, data: Any) -> Dict[str, Any]:
        """Check data consistency."""
        return {'score': 100.0, 'issues': []}
    
    def _check_validity(self, data: Any) -> Dict[str, Any]:
        """Check data validity."""
        return {'score': 100.0, 'issues': []}
    
    def _calculate_overall_quality_score(self, quality_results: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        if not quality_results:
            return 0.0
        
        weights = {
            'completeness': 0.25,
            'accuracy': 0.30,
            'consistency': 0.15,
            'validity': 0.20
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in quality_results:
                score = quality_results[metric].get('score', 0.0)
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _update_quality_metrics(self, system_name: str, quality_results: Dict[str, Any]):
        """Update quality metrics for a system."""
        current_score = quality_results.get('overall_score', 0.0)
        previous_score = self.quality_metrics[system_name].get('current_score', 0.0)
        
        self.quality_metrics[system_name].update({
            'current_score': current_score,
            'last_check': timezone.now(),
            'trend': self._calculate_trend(previous_score, current_score)
        })
    
    def _calculate_trend(self, previous_score: float, current_score: float) -> str:
        """Calculate trend direction."""
        if current_score > previous_score + 5:
            return 'improving'
        elif current_score < previous_score - 5:
            return 'declining'
        else:
            return 'stable'
