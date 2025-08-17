"""
Statistical Analysis Modules

This module provides comprehensive statistical analysis capabilities for historical data,
including descriptive statistics, inferential statistics, correlation analysis, and
statistical modeling for construction project data.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Sum, Count, Min, Max, StdDev, Variance
from django.core.cache import cache
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

logger = logging.getLogger(__name__)


class DescriptiveStatistics:
    """Module for calculating descriptive statistics on historical data."""
    
    def __init__(self):
        """Initialize the descriptive statistics module."""
        self.cache_timeout = 1800  # 30 minutes cache
    
    def calculate_numeric_statistics(self, data: List[float]) -> Dict[str, float]:
        """Calculate comprehensive numeric statistics for a dataset."""
        try:
            if not data or len(data) == 0:
                return {}
            
            data_array = np.array(data)
            
            # Basic statistics
            basic_stats = {
                'count': len(data),
                'mean': float(np.mean(data_array)),
                'median': float(np.median(data_array)),
                'mode': float(stats.mode(data_array, keepdims=False)[0]) if len(data_array) > 0 else 0,
                'std_deviation': float(np.std(data_array)),
                'variance': float(np.var(data_array)),
                'min': float(np.min(data_array)),
                'max': float(np.max(data_array)),
                'range': float(np.max(data_array) - np.min(data_array))
            }
            
            # Percentiles
            percentiles = [25, 50, 75, 90, 95, 99]
            for p in percentiles:
                basic_stats[f'percentile_{p}'] = float(np.percentile(data_array, p))
            
            # Skewness and kurtosis
            basic_stats['skewness'] = float(stats.skew(data_array))
            basic_stats['kurtosis'] = float(stats.kurtosis(data_array))
            
            # Quartiles and IQR
            q1, q3 = np.percentile(data_array, [25, 75])
            basic_stats['q1'] = float(q1)
            basic_stats['q3'] = float(q3)
            basic_stats['iqr'] = float(q3 - q1)
            
            return basic_stats
            
        except Exception as e:
            logger.error(f"Error calculating numeric statistics: {e}")
            return {}
    
    def analyze_project_budgets(self, project_data: List[Dict]) -> Dict[str, Any]:
        """Analyze project budget statistics."""
        try:
            budgets = [project.get('budget', 0) for project in project_data if project.get('budget')]
            
            if not budgets:
                return {'error': 'No budget data available'}
            
            budget_stats = self.calculate_numeric_statistics(budgets)
            
            # Budget categories
            budget_categories = {
                'small': len([b for b in budgets if b < 1000000]),  # < $1M
                'medium': len([b for b in budgets if 1000000 <= b < 10000000]),  # $1M - $10M
                'large': len([b for b in budgets if b >= 10000000])  # >= $10M
            }
            
            # Budget efficiency analysis
            completed_projects = [p for p in project_data if p.get('status') == 'completed']
            if completed_projects:
                actual_vs_budget = []
                for project in completed_projects:
                    if project.get('budget') and project.get('actual_cost'):
                        variance = (project['actual_cost'] - project['budget']) / project['budget'] * 100
                        actual_vs_budget.append(variance)
                
                if actual_vs_budget:
                    budget_stats['budget_variance_stats'] = self.calculate_numeric_statistics(actual_vs_budget)
            
            result = {
                'budget_statistics': budget_stats,
                'budget_categories': budget_categories,
                'total_projects': len(project_data),
                'projects_with_budgets': len(budgets)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing project budgets: {e}")
            return {'error': str(e)}
    
    def analyze_supplier_performance(self, supplier_data: List[Dict]) -> Dict[str, Any]:
        """Analyze supplier performance statistics."""
        try:
            # Extract performance metrics
            delivery_times = []
            quality_scores = []
            cost_variance = []
            
            for supplier in supplier_data:
                if supplier.get('avg_delivery_time'):
                    delivery_times.append(supplier['avg_delivery_time'])
                if supplier.get('quality_score'):
                    quality_scores.append(supplier['quality_score'])
                if supplier.get('cost_variance'):
                    cost_variance.append(supplier['cost_variance'])
            
            result = {
                'delivery_time_stats': self.calculate_numeric_statistics(delivery_times) if delivery_times else {},
                'quality_score_stats': self.calculate_numeric_statistics(quality_scores) if quality_scores else {},
                'cost_variance_stats': self.calculate_numeric_statistics(cost_variance) if cost_variance else {},
                'total_suppliers': len(supplier_data),
                'suppliers_with_delivery_data': len(delivery_times),
                'suppliers_with_quality_data': len(quality_scores),
                'suppliers_with_cost_data': len(cost_variance)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing supplier performance: {e}")
            return {'error': str(e)}
    
    def analyze_time_series_data(self, time_series_data: List[Dict], 
                               date_field: str = 'date',
                               value_field: str = 'value') -> Dict[str, Any]:
        """Analyze time series data for trends and patterns."""
        try:
            if not time_series_data:
                return {'error': 'No time series data available'}
            
            # Sort by date
            sorted_data = sorted(time_series_data, key=lambda x: x.get(date_field))
            
            # Extract values and dates
            values = [item.get(value_field, 0) for item in sorted_data]
            dates = [item.get(date_field) for item in sorted_data]
            
            if not values or not dates:
                return {'error': 'Invalid time series data'}
            
            # Basic statistics
            value_stats = self.calculate_numeric_statistics(values)
            
            # Trend analysis
            trend_analysis = self._analyze_trend(values, dates)
            
            # Seasonality analysis
            seasonality_analysis = self._analyze_seasonality(values, dates)
            
            # Volatility analysis
            volatility_analysis = self._analyze_volatility(values)
            
            result = {
                'value_statistics': value_stats,
                'trend_analysis': trend_analysis,
                'seasonality_analysis': seasonality_analysis,
                'volatility_analysis': volatility_analysis,
                'data_points': len(values),
                'date_range': {
                    'start': dates[0].isoformat() if hasattr(dates[0], 'isoformat') else str(dates[0]),
                    'end': dates[-1].isoformat() if hasattr(dates[-1], 'isoformat') else str(dates[-1])
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing time series data: {e}")
            return {'error': str(e)}
    
    def _analyze_trend(self, values: List[float], dates: List) -> Dict[str, Any]:
        """Analyze trend in time series data."""
        try:
            if len(values) < 2:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Linear trend
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Trend strength
            trend_strength = 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.3 else 'weak'
            trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            
            # Moving averages
            moving_avg_3 = np.convolve(values, np.ones(3)/3, mode='valid')
            moving_avg_7 = np.convolve(values, np.ones(7)/7, mode='valid')
            
            return {
                'slope': float(slope),
                'intercept': float(intercept),
                'correlation_coefficient': float(r_value),
                'p_value': float(p_value),
                'trend_strength': trend_strength,
                'trend_direction': trend_direction,
                'moving_average_3': [float(x) for x in moving_avg_3],
                'moving_average_7': [float(x) for x in moving_avg_7]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'error': str(e)}
    
    def _analyze_seasonality(self, values: List[float], dates: List) -> Dict[str, Any]:
        """Analyze seasonality in time series data."""
        try:
            if len(values) < 12:  # Need at least 12 data points for seasonality
                return {'error': 'Insufficient data for seasonality analysis'}
            
            # Monthly seasonality (assuming monthly data)
            monthly_values = defaultdict(list)
            for i, date in enumerate(dates):
                if hasattr(date, 'month'):
                    month = date.month
                elif hasattr(date, 'strftime'):
                    month = date.month
                else:
                    month = i % 12 + 1  # Fallback
                
                monthly_values[month].append(values[i])
            
            # Calculate monthly averages
            monthly_averages = {}
            for month in range(1, 13):
                if month in monthly_values:
                    monthly_averages[month] = float(np.mean(monthly_values[month]))
                else:
                    monthly_averages[month] = 0.0
            
            # Seasonality strength
            overall_mean = np.mean(values)
            seasonal_variance = np.var([avg - overall_mean for avg in monthly_averages.values()])
            total_variance = np.var(values)
            seasonality_strength = seasonal_variance / total_variance if total_variance > 0 else 0
            
            return {
                'monthly_averages': monthly_averages,
                'seasonality_strength': float(seasonality_strength),
                'overall_mean': float(overall_mean)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing seasonality: {e}")
            return {'error': str(e)}
    
    def _analyze_volatility(self, values: List[float]) -> Dict[str, Any]:
        """Analyze volatility in time series data."""
        try:
            if len(values) < 2:
                return {'error': 'Insufficient data for volatility analysis'}
            
            # Calculate returns (percentage changes)
            returns = []
            for i in range(1, len(values)):
                if values[i-1] != 0:
                    return_pct = (values[i] - values[i-1]) / values[i-1] * 100
                    returns.append(return_pct)
            
            if not returns:
                return {'error': 'Cannot calculate returns'}
            
            # Volatility metrics
            volatility_stats = {
                'return_volatility': float(np.std(returns)),
                'return_mean': float(np.mean(returns)),
                'max_return': float(np.max(returns)),
                'min_return': float(np.min(returns)),
                'return_range': float(np.max(returns) - np.min(returns))
            }
            
            # Value at Risk (VaR) at 95% confidence
            var_95 = np.percentile(returns, 5)
            volatility_stats['var_95'] = float(var_95)
            
            return volatility_stats
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return {'error': str(e)}


class InferentialStatistics:
    """Module for performing inferential statistical analysis."""
    
    def __init__(self):
        """Initialize the inferential statistics module."""
        self.cache_timeout = 1800  # 30 minutes cache
    
    def perform_hypothesis_test(self, sample1: List[float], sample2: List[float] = None,
                              test_type: str = 't_test', alpha: float = 0.05) -> Dict[str, Any]:
        """Perform hypothesis testing on sample data."""
        try:
            if not sample1 or len(sample1) == 0:
                return {'error': 'Sample 1 is empty'}
            
            if test_type == 't_test_one_sample':
                # One-sample t-test
                t_stat, p_value = stats.ttest_1samp(sample1, 0)
                test_result = 'reject' if p_value < alpha else 'fail_to_reject'
                
                result = {
                    'test_type': 'one_sample_t_test',
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'alpha': alpha,
                    'test_result': test_result,
                    'sample_size': len(sample1),
                    'sample_mean': float(np.mean(sample1)),
                    'sample_std': float(np.std(sample1))
                }
                
            elif test_type == 't_test' and sample2:
                # Two-sample t-test
                if not sample2 or len(sample2) == 0:
                    return {'error': 'Sample 2 is empty for two-sample test'}
                
                t_stat, p_value = stats.ttest_ind(sample1, sample2)
                test_result = 'reject' if p_value < alpha else 'fail_to_reject'
                
                result = {
                    'test_type': 'two_sample_t_test',
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'alpha': alpha,
                    'test_result': test_result,
                    'sample1_size': len(sample1),
                    'sample2_size': len(sample2),
                    'sample1_mean': float(np.mean(sample1)),
                    'sample2_mean': float(np.mean(sample2)),
                    'sample1_std': float(np.std(sample1)),
                    'sample2_std': float(np.std(sample2))
                }
                
            elif test_type == 'anova' and sample2:
                # One-way ANOVA
                if not sample2 or len(sample2) == 0:
                    return {'error': 'Sample 2 is empty for ANOVA test'}
                
                f_stat, p_value = stats.f_oneway(sample1, sample2)
                test_result = 'reject' if p_value < alpha else 'fail_to_reject'
                
                result = {
                    'test_type': 'one_way_anova',
                    'f_statistic': float(f_stat),
                    'p_value': float(p_value),
                    'alpha': alpha,
                    'test_result': test_result,
                    'sample1_size': len(sample1),
                    'sample2_size': len(sample2),
                    'sample1_mean': float(np.mean(sample1)),
                    'sample2_mean': float(np.mean(sample2))
                }
                
            else:
                return {'error': f'Invalid test type: {test_type}'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing hypothesis test: {e}")
            return {'error': str(e)}
    
    def calculate_confidence_intervals(self, data: List[float], confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculate confidence intervals for sample data."""
        try:
            if not data or len(data) == 0:
                return {'error': 'No data provided'}
            
            if confidence_level <= 0 or confidence_level >= 1:
                return {'error': 'Confidence level must be between 0 and 1'}
            
            data_array = np.array(data)
            n = len(data_array)
            mean = np.mean(data_array)
            std = np.std(data_array, ddof=1)  # Sample standard deviation
            
            # Calculate standard error
            se = std / np.sqrt(n)
            
            # Calculate critical value (t-distribution for small samples, normal for large)
            if n < 30:
                # Use t-distribution
                critical_value = stats.t.ppf((1 + confidence_level) / 2, n - 1)
            else:
                # Use normal distribution
                critical_value = stats.norm.ppf((1 + confidence_level) / 2)
            
            # Calculate margin of error
            margin_of_error = critical_value * se
            
            # Calculate confidence interval
            lower_bound = mean - margin_of_error
            upper_bound = mean + margin_of_error
            
            result = {
                'confidence_level': confidence_level,
                'sample_size': n,
                'sample_mean': float(mean),
                'sample_std': float(std),
                'standard_error': float(se),
                'critical_value': float(critical_value),
                'margin_of_error': float(margin_of_error),
                'confidence_interval': {
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating confidence intervals: {e}")
            return {'error': str(e)}
    
    def perform_correlation_analysis(self, data1: List[float], data2: List[float]) -> Dict[str, Any]:
        """Perform correlation analysis between two datasets."""
        try:
            if not data1 or not data2 or len(data1) != len(data2):
                return {'error': 'Datasets must have the same length and be non-empty'}
            
            # Calculate correlation coefficients
            pearson_corr, pearson_p = stats.pearsonr(data1, data2)
            spearman_corr, spearman_p = stats.spearmanr(data1, data2)
            
            # Determine correlation strength
            def get_correlation_strength(corr):
                abs_corr = abs(corr)
                if abs_corr >= 0.8:
                    return 'very_strong'
                elif abs_corr >= 0.6:
                    return 'strong'
                elif abs_corr >= 0.4:
                    return 'moderate'
                elif abs_corr >= 0.2:
                    return 'weak'
                else:
                    return 'very_weak'
            
            result = {
                'pearson_correlation': {
                    'coefficient': float(pearson_corr),
                    'p_value': float(pearson_p),
                    'strength': get_correlation_strength(pearson_corr)
                },
                'spearman_correlation': {
                    'coefficient': float(spearman_corr),
                    'p_value': float(spearman_p),
                    'strength': get_correlation_strength(spearman_corr)
                },
                'sample_size': len(data1),
                'data1_mean': float(np.mean(data1)),
                'data2_mean': float(np.mean(data2)),
                'data1_std': float(np.std(data1)),
                'data2_std': float(np.std(data2))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing correlation analysis: {e}")
            return {'error': str(e)}


class AdvancedStatisticalModeling:
    """Module for advanced statistical modeling and analysis."""
    
    def __init__(self):
        """Initialize the advanced statistical modeling module."""
        self.cache_timeout = 1800  # 30 minutes cache
    
    def perform_regression_analysis(self, x_data: List[float], y_data: List[float],
                                  regression_type: str = 'linear') -> Dict[str, Any]:
        """Perform regression analysis on data."""
        try:
            if not x_data or not y_data or len(x_data) != len(y_data):
                return {'error': 'X and Y data must have the same length and be non-empty'}
            
            if regression_type == 'linear':
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
                
                # Calculate predictions
                x_array = np.array(x_data)
                y_pred = slope * x_array + intercept
                
                # Calculate R-squared
                r_squared = r_value ** 2
                
                # Calculate residuals
                residuals = np.array(y_data) - y_pred
                residual_stats = {
                    'mean': float(np.mean(residuals)),
                    'std': float(np.std(residuals)),
                    'min': float(np.min(residuals)),
                    'max': float(np.max(residuals))
                }
                
                result = {
                    'regression_type': 'linear',
                    'coefficients': {
                        'slope': float(slope),
                        'intercept': float(intercept)
                    },
                    'statistics': {
                        'correlation_coefficient': float(r_value),
                        'r_squared': float(r_squared),
                        'p_value': float(p_value),
                        'standard_error': float(std_err)
                    },
                    'residuals': residual_stats,
                    'sample_size': len(x_data),
                    'predictions': [float(y) for y in y_pred]
                }
                
            else:
                return {'error': f'Unsupported regression type: {regression_type}'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing regression analysis: {e}")
            return {'error': str(e)}
    
    def perform_cluster_analysis(self, data: List[List[float]], n_clusters: int = 3) -> Dict[str, Any]:
        """Perform cluster analysis on multidimensional data."""
        try:
            if not data or len(data) == 0:
                return {'error': 'No data provided for clustering'}
            
            # Convert to numpy array
            data_array = np.array(data)
            
            # Standardize the data
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data_array)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(data_scaled)
            
            # Calculate cluster statistics
            cluster_stats = {}
            for i in range(n_clusters):
                cluster_mask = cluster_labels == i
                cluster_data = data_array[cluster_mask]
                
                if len(cluster_data) > 0:
                    cluster_stats[f'cluster_{i}'] = {
                        'size': int(len(cluster_data)),
                        'mean': [float(x) for x in np.mean(cluster_data, axis=0)],
                        'std': [float(x) for x in np.std(cluster_data, axis=0)]
                    }
            
            # Calculate silhouette score
            from sklearn.metrics import silhouette_score
            silhouette_avg = silhouette_score(data_scaled, cluster_labels)
            
            result = {
                'n_clusters': n_clusters,
                'cluster_labels': [int(label) for label in cluster_labels],
                'cluster_centers': [center.tolist() for center in kmeans.cluster_centers_],
                'cluster_statistics': cluster_stats,
                'silhouette_score': float(silhouette_avg),
                'inertia': float(kmeans.inertia_),
                'sample_size': len(data),
                'n_features': data_array.shape[1] if len(data_array.shape) > 1 else 1
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing cluster analysis: {e}")
            return {'error': str(e)}
    
    def perform_principal_component_analysis(self, data: List[List[float]], 
                                          n_components: int = None) -> Dict[str, Any]:
        """Perform Principal Component Analysis on data."""
        try:
            if not data or len(data) == 0:
                return {'error': 'No data provided for PCA'}
            
            # Convert to numpy array
            data_array = np.array(data)
            
            # Standardize the data
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data_array)
            
            # Perform PCA
            if n_components is None:
                n_components = min(data_array.shape)
            
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(data_scaled)
            
            # Calculate explained variance
            explained_variance_ratio = pca.explained_variance_ratio_
            cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
            
            result = {
                'n_components': n_components,
                'n_features': data_array.shape[1] if len(data_array.shape) > 1 else 1,
                'explained_variance_ratio': [float(x) for x in explained_variance_ratio],
                'cumulative_variance_ratio': [float(x) for x in cumulative_variance_ratio],
                'total_explained_variance': float(sum(explained_variance_ratio)),
                'pca_components': pca_result.tolist(),
                'feature_importance': [float(x) for x in pca.components_[0]] if len(pca.components_) > 0 else []
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing PCA: {e}")
            return {'error': str(e)}
    
    def calculate_statistical_power(self, effect_size: float, alpha: float = 0.05,
                                  sample_size: int = None, power: float = None) -> Dict[str, Any]:
        """Calculate statistical power for hypothesis testing."""
        try:
            from statsmodels.stats.power import TTestPower
            
            # Initialize power analysis
            power_analysis = TTestPower()
            
            if power is None and sample_size is not None:
                # Calculate power given sample size
                calculated_power = power_analysis.power(
                    effect_size, sample_size, alpha, alternative='two-sided'
                )
                
                result = {
                    'effect_size': effect_size,
                    'alpha': alpha,
                    'sample_size': sample_size,
                    'calculated_power': float(calculated_power),
                    'power_adequate': calculated_power >= 0.8
                }
                
            elif sample_size is None and power is not None:
                # Calculate required sample size given power
                required_sample_size = power_analysis.solve_power(
                    effect_size, power=power, alpha=alpha, alternative='two-sided'
                )
                
                result = {
                    'effect_size': effect_size,
                    'alpha': alpha,
                    'required_power': power,
                    'required_sample_size': int(required_sample_size),
                    'power_adequate': power >= 0.8
                }
                
            else:
                return {'error': 'Must specify either sample_size or power, but not both'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating statistical power: {e}")
            return {'error': str(e)}
