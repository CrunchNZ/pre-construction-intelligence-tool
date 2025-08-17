"""
Trend Detection Algorithms

This module provides comprehensive trend detection algorithms for historical data,
including pattern recognition, anomaly detection, and predictive trend analysis
for construction project data.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import find_peaks, savgol_filter
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class TrendDetector:
    """Comprehensive trend detection for construction project data."""
    
    def __init__(self):
        """Initialize the trend detector."""
        self.cache_timeout = 1800  # 30 minutes cache
        self.min_data_points = 10  # Minimum data points for trend analysis
    
    def detect_trends(self, data: List[Dict], value_field: str = 'value',
                     date_field: str = 'date', trend_types: List[str] = None) -> Dict[str, Any]:
        """Detect multiple types of trends in time series data."""
        try:
            if not data or len(data) < self.min_data_points:
                return {'error': f'Insufficient data. Need at least {self.min_data_points} data points.'}
            
            if trend_types is None:
                trend_types = ['linear', 'seasonal', 'cyclical', 'structural_breaks']
            
            # Sort data by date
            sorted_data = sorted(data, key=lambda x: x.get(date_field))
            
            # Extract values and dates
            values = [item.get(value_field, 0) for item in sorted_data]
            dates = [item.get(date_field) for item in sorted_data]
            
            if not values or not dates:
                return {'error': 'Invalid data format'}
            
            # Convert to numpy arrays
            values_array = np.array(values)
            dates_array = np.array(dates)
            
            # Initialize results
            trend_results = {
                'data_summary': {
                    'total_points': len(values),
                    'date_range': {
                        'start': dates[0].isoformat() if hasattr(dates[0], 'isoformat') else str(dates[0]),
                        'end': dates[-1].isoformat() if hasattr(dates[-1], 'isoformat') else str(dates[-1])
                    }
                },
                'trends': {}
            }
            
            # Detect different types of trends
            if 'linear' in trend_types:
                trend_results['trends']['linear'] = self._detect_linear_trend(values_array, dates_array)
            
            if 'seasonal' in trend_types:
                trend_results['trends']['seasonal'] = self._detect_seasonal_trends(values_array, dates_array)
            
            if 'cyclical' in trend_types:
                trend_results['trends']['cyclical'] = self._detect_cyclical_trends(values_array, dates_array)
            
            if 'structural_breaks' in trend_types:
                trend_results['trends']['structural_breaks'] = self._detect_structural_breaks(values_array, dates_array)
            
            # Overall trend assessment
            trend_results['overall_assessment'] = self._assess_overall_trends(trend_results['trends'])
            
            return trend_results
            
        except Exception as e:
            logger.error(f"Error detecting trends: {e}")
            return {'error': str(e)}
    
    def _detect_linear_trend(self, values: np.ndarray, dates: np.ndarray) -> Dict[str, Any]:
        """Detect linear trends in time series data."""
        try:
            # Create time index
            time_index = np.arange(len(values))
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_index, values)
            
            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(r_value)
            
            # Calculate moving averages
            window_sizes = [3, 5, 7]
            moving_averages = {}
            for window in window_sizes:
                if len(values) >= window:
                    moving_averages[f'ma_{window}'] = self._calculate_moving_average(values, window)
            
            # Detect trend changes
            trend_changes = self._detect_trend_changes(values, time_index)
            
            result = {
                'trend_type': 'linear',
                'coefficients': {
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'correlation': float(r_value),
                    'p_value': float(p_value),
                    'standard_error': float(std_err)
                },
                'trend_assessment': {
                    'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'strength': trend_strength,
                    'significance': 'significant' if p_value < 0.05 else 'not_significant'
                },
                'moving_averages': moving_averages,
                'trend_changes': trend_changes,
                'forecast': self._generate_linear_forecast(slope, intercept, len(values), 12)  # 12 periods ahead
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting linear trend: {e}")
            return {'error': str(e)}
    
    def _detect_seasonal_trends(self, values: np.ndarray, dates: np.ndarray) -> Dict[str, Any]:
        """Detect seasonal patterns in time series data."""
        try:
            if len(values) < 12:  # Need at least 12 data points for seasonal analysis
                return {'error': 'Insufficient data for seasonal analysis'}
            
            # Extract seasonal components
            seasonal_components = self._extract_seasonal_components(values, dates)
            
            # Detect seasonality strength
            seasonality_strength = self._calculate_seasonality_strength(values, seasonal_components)
            
            # Identify peak and trough seasons
            peak_seasons = self._identify_peak_seasons(seasonal_components)
            
            # Seasonal decomposition
            seasonal_decomposition = self._perform_seasonal_decomposition(values)
            
            result = {
                'trend_type': 'seasonal',
                'seasonality_strength': seasonality_strength,
                'seasonal_components': seasonal_components,
                'peak_seasons': peak_seasons,
                'seasonal_decomposition': seasonal_decomposition,
                'forecast': self._generate_seasonal_forecast(values, seasonal_components, 12)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting seasonal trends: {e}")
            return {'error': str(e)}
    
    def _detect_cyclical_trends(self, values: np.ndarray, dates: np.ndarray) -> Dict[str, Any]:
        """Detect cyclical patterns in time series data."""
        try:
            if len(values) < 20:  # Need sufficient data for cyclical analysis
                return {'error': 'Insufficient data for cyclical analysis'}
            
            # Remove trend and seasonality
            detrended_values = self._remove_trend_and_seasonality(values)
            
            # Detect cycles using autocorrelation
            autocorr = self._calculate_autocorrelation(detrended_values)
            
            # Find cycle lengths
            cycle_lengths = self._find_cycle_lengths(autocorr)
            
            # Detect business cycles
            business_cycles = self._detect_business_cycles(values, dates)
            
            result = {
                'trend_type': 'cyclical',
                'cycle_lengths': cycle_lengths,
                'autocorrelation': autocorr[:20].tolist(),  # First 20 lags
                'business_cycles': business_cycles,
                'cyclical_strength': self._calculate_cyclical_strength(autocorr)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting cyclical trends: {e}")
            return {'error': str(e)}
    
    def _detect_structural_breaks(self, values: np.ndarray, dates: np.ndarray) -> Dict[str, Any]:
        """Detect structural breaks in time series data."""
        try:
            if len(values) < 15:  # Need sufficient data for break detection
                return {'error': 'Insufficient data for structural break detection'}
            
            # CUSUM test for structural breaks
            cusum_results = self._cusum_test(values)
            
            # Chow test for structural breaks
            chow_results = self._chow_test(values)
            
            # Detect change points
            change_points = self._detect_change_points(values)
            
            # Segment the series
            segments = self._segment_time_series(values, change_points)
            
            result = {
                'trend_type': 'structural_breaks',
                'cusum_test': cusum_results,
                'chow_test': chow_results,
                'change_points': change_points,
                'segments': segments,
                'break_analysis': self._analyze_structural_breaks(values, change_points)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting structural breaks: {e}")
            return {'error': str(e)}
    
    def _calculate_trend_strength(self, correlation: float) -> str:
        """Calculate the strength of a trend based on correlation coefficient."""
        abs_corr = abs(correlation)
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
    
    def _calculate_moving_average(self, values: np.ndarray, window: int) -> List[float]:
        """Calculate moving average with specified window size."""
        try:
            if len(values) < window:
                return []
            
            moving_avg = []
            for i in range(window - 1, len(values)):
                window_values = values[i - window + 1:i + 1]
                moving_avg.append(float(np.mean(window_values)))
            
            return moving_avg
            
        except Exception as e:
            logger.error(f"Error calculating moving average: {e}")
            return []
    
    def _detect_trend_changes(self, values: np.ndarray, time_index: np.ndarray) -> List[Dict]:
        """Detect points where trend changes direction."""
        try:
            if len(values) < 5:
                return []
            
            # Calculate first differences
            first_diff = np.diff(values)
            
            # Find points where sign changes (trend reversal)
            trend_changes = []
            for i in range(1, len(first_diff)):
                if (first_diff[i-1] > 0 and first_diff[i] < 0) or (first_diff[i-1] < 0 and first_diff[i] > 0):
                    trend_changes.append({
                        'index': int(i),
                        'time_period': int(time_index[i]),
                        'value': float(values[i]),
                        'change_type': 'peak' if first_diff[i-1] > 0 else 'trough'
                    })
            
            return trend_changes
            
        except Exception as e:
            logger.error(f"Error detecting trend changes: {e}")
            return []
    
    def _extract_seasonal_components(self, values: np.ndarray, dates: np.ndarray) -> Dict[str, Any]:
        """Extract seasonal components from time series data."""
        try:
            # Group by month (assuming monthly data)
            monthly_groups = defaultdict(list)
            for i, date in enumerate(dates):
                if hasattr(date, 'month'):
                    month = date.month
                elif hasattr(date, 'strftime'):
                    month = date.month
                else:
                    month = i % 12 + 1  # Fallback
                
                monthly_groups[month].append(values[i])
            
            # Calculate monthly averages
            monthly_averages = {}
            monthly_std = {}
            for month in range(1, 13):
                if month in monthly_groups:
                    monthly_averages[month] = float(np.mean(monthly_groups[month]))
                    monthly_std[month] = float(np.std(monthly_groups[month]))
                else:
                    monthly_averages[month] = 0.0
                    monthly_std[month] = 0.0
            
            return {
                'monthly_averages': monthly_averages,
                'monthly_std': monthly_std,
                'seasonal_pattern': self._classify_seasonal_pattern(monthly_averages)
            }
            
        except Exception as e:
            logger.error(f"Error extracting seasonal components: {e}")
            return {}
    
    def _calculate_seasonality_strength(self, values: np.ndarray, seasonal_components: Dict) -> str:
        """Calculate the strength of seasonality."""
        try:
            if 'monthly_averages' not in seasonal_components:
                return 'unknown'
            
            monthly_avgs = seasonal_components['monthly_averages']
            overall_mean = np.mean(values)
            
            # Calculate seasonal variance
            seasonal_variance = np.var([avg - overall_mean for avg in monthly_avgs.values()])
            total_variance = np.var(values)
            
            if total_variance == 0:
                return 'none'
            
            seasonality_ratio = seasonal_variance / total_variance
            
            if seasonality_ratio > 0.6:
                return 'very_strong'
            elif seasonality_ratio > 0.4:
                return 'strong'
            elif seasonality_ratio > 0.2:
                return 'moderate'
            elif seasonality_ratio > 0.1:
                return 'weak'
            else:
                return 'none'
                
        except Exception as e:
            logger.error(f"Error calculating seasonality strength: {e}")
            return 'unknown'
    
    def _identify_peak_seasons(self, seasonal_components: Dict) -> Dict[str, Any]:
        """Identify peak and trough seasons."""
        try:
            if 'monthly_averages' not in seasonal_components:
                return {}
            
            monthly_avgs = seasonal_components['monthly_averages']
            
            # Find peak and trough months
            peak_month = max(monthly_avgs, key=monthly_avgs.get)
            trough_month = min(monthly_avgs, key=monthly_avgs.get)
            
            # Convert month numbers to names
            month_names = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            
            return {
                'peak_season': {
                    'month': peak_month,
                    'month_name': month_names.get(peak_month, f'Month {peak_month}'),
                    'value': monthly_avgs[peak_month]
                },
                'trough_season': {
                    'month': trough_month,
                    'month_name': month_names.get(trough_month, f'Month {trough_month}'),
                    'value': monthly_avgs[trough_month]
                }
            }
            
        except Exception as e:
            logger.error(f"Error identifying peak seasons: {e}")
            return {}
    
    def _perform_seasonal_decomposition(self, values: np.ndarray) -> Dict[str, Any]:
        """Perform seasonal decomposition of time series."""
        try:
            if len(values) < 12:
                return {'error': 'Insufficient data for seasonal decomposition'}
            
            # Simple seasonal decomposition
            # Trend component using moving average
            trend = self._calculate_moving_average(values, 12)
            
            # Seasonal component
            seasonal = []
            for i in range(len(values)):
                if i < len(trend):
                    seasonal.append(values[i] - trend[i])
                else:
                    seasonal.append(0)
            
            # Residual component
            residual = []
            for i in range(len(values)):
                if i < len(trend):
                    residual.append(values[i] - trend[i] - seasonal[i])
                else:
                    residual.append(values[i])
            
            return {
                'trend': [float(x) for x in trend],
                'seasonal': [float(x) for x in seasonal],
                'residual': [float(x) for x in residual]
            }
            
        except Exception as e:
            logger.error(f"Error performing seasonal decomposition: {e}")
            return {}
    
    def _remove_trend_and_seasonality(self, values: np.ndarray) -> np.ndarray:
        """Remove trend and seasonality to isolate cyclical components."""
        try:
            # Remove trend using first differencing
            detrended = np.diff(values)
            
            # Remove seasonality using seasonal differencing
            if len(detrended) >= 12:
                deseasonalized = np.diff(detrended, n=12)
            else:
                deseasonalized = detrended
            
            return deseasonalized
            
        except Exception as e:
            logger.error(f"Error removing trend and seasonality: {e}")
            return values
    
    def _calculate_autocorrelation(self, values: np.ndarray) -> np.ndarray:
        """Calculate autocorrelation function."""
        try:
            if len(values) < 2:
                return np.array([])
            
            # Calculate autocorrelation for different lags
            max_lag = min(20, len(values) // 2)
            autocorr = []
            
            for lag in range(max_lag + 1):
                if lag == 0:
                    autocorr.append(1.0)
                else:
                    # Calculate correlation between values and lagged values
                    corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
                    autocorr.append(corr if not np.isnan(corr) else 0.0)
            
            return np.array(autocorr)
            
        except Exception as e:
            logger.error(f"Error calculating autocorrelation: {e}")
            return np.array([])
    
    def _find_cycle_lengths(self, autocorr: np.ndarray) -> List[int]:
        """Find cycle lengths from autocorrelation function."""
        try:
            if len(autocorr) < 3:
                return []
            
            # Find peaks in autocorrelation (excluding lag 0)
            peaks, _ = find_peaks(autocorr[1:], height=0.3)
            peaks = peaks + 1  # Adjust for offset
            
            # Filter significant peaks
            significant_peaks = [peak for peak in peaks if autocorr[peak] > 0.5]
            
            return significant_peaks.tolist()
            
        except Exception as e:
            logger.error(f"Error finding cycle lengths: {e}")
            return []
    
    def _detect_business_cycles(self, values: np.ndarray, dates: np.ndarray) -> List[Dict]:
        """Detect business cycles in the data."""
        try:
            if len(values) < 20:
                return []
            
            # Simple business cycle detection using peaks and troughs
            peaks, _ = find_peaks(values, height=np.mean(values))
            troughs, _ = find_peaks(-values, height=-np.mean(values))
            
            cycles = []
            for i in range(min(len(peaks), len(troughs))):
                if peaks[i] > troughs[i]:  # Peak after trough
                    cycle_length = peaks[i] - troughs[i]
                    cycle = {
                        'expansion_start': int(troughs[i]),
                        'expansion_end': int(peaks[i]),
                        'expansion_length': int(cycle_length),
                        'expansion_magnitude': float(values[peaks[i]] - values[troughs[i]])
                    }
                    cycles.append(cycle)
            
            return cycles
            
        except Exception as e:
            logger.error(f"Error detecting business cycles: {e}")
            return []
    
    def _calculate_cyclical_strength(self, autocorr: np.ndarray) -> str:
        """Calculate the strength of cyclical patterns."""
        try:
            if len(autocorr) < 3:
                return 'none'
            
            # Calculate average autocorrelation for lags > 0
            avg_autocorr = np.mean(np.abs(autocorr[1:]))
            
            if avg_autocorr > 0.6:
                return 'very_strong'
            elif avg_autocorr > 0.4:
                return 'strong'
            elif avg_autocorr > 0.2:
                return 'moderate'
            elif avg_autocorr > 0.1:
                return 'weak'
            else:
                return 'none'
                
        except Exception as e:
            logger.error(f"Error calculating cyclical strength: {e}")
            return 'unknown'
    
    def _cusum_test(self, values: np.ndarray) -> Dict[str, Any]:
        """Perform CUSUM test for structural breaks."""
        try:
            if len(values) < 10:
                return {'error': 'Insufficient data for CUSUM test'}
            
            # Calculate CUSUM statistics
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if std_val == 0:
                return {'error': 'Zero standard deviation'}
            
            # Calculate CUSUM
            cusum = np.cumsum((values - mean_val) / std_val)
            
            # Find break points
            threshold = 1.358 * np.sqrt(len(values))  # 95% confidence level
            breaks = np.where(np.abs(cusum) > threshold)[0]
            
            return {
                'cusum_statistics': cusum.tolist(),
                'threshold': float(threshold),
                'break_points': breaks.tolist(),
                'significant_breaks': len(breaks)
            }
            
        except Exception as e:
            logger.error(f"Error performing CUSUM test: {e}")
            return {'error': str(e)}
    
    def _chow_test(self, values: np.ndarray) -> Dict[str, Any]:
        """Perform Chow test for structural breaks."""
        try:
            if len(values) < 15:
                return {'error': 'Insufficient data for Chow test'}
            
            # Simple Chow test implementation
            n = len(values)
            mid_point = n // 2
            
            # Split data into two segments
            segment1 = values[:mid_point]
            segment2 = values[mid_point:]
            
            # Calculate RSS for each segment and combined
            rss1 = np.sum((segment1 - np.mean(segment1)) ** 2)
            rss2 = np.sum((segment2 - np.mean(segment2)) ** 2)
            rss_combined = np.sum((values - np.mean(values)) ** 2)
            
            # Calculate Chow test statistic
            if rss1 + rss2 > 0:
                chow_stat = ((rss_combined - (rss1 + rss2)) / 2) / ((rss1 + rss2) / (n - 4))
                p_value = 1 - stats.f.cdf(chow_stat, 2, n - 4)
            else:
                chow_stat = 0
                p_value = 1
            
            return {
                'chow_statistic': float(chow_stat),
                'p_value': float(p_value),
                'break_point': int(mid_point),
                'significant_break': p_value < 0.05
            }
            
        except Exception as e:
            logger.error(f"Error performing Chow test: {e}")
            return {'error': str(e)}
    
    def _detect_change_points(self, values: np.ndarray) -> List[int]:
        """Detect change points in time series."""
        try:
            if len(values) < 10:
                return []
            
            # Simple change point detection using rolling statistics
            window_size = min(5, len(values) // 3)
            change_points = []
            
            for i in range(window_size, len(values) - window_size):
                before_mean = np.mean(values[i-window_size:i])
                after_mean = np.mean(values[i:i+window_size])
                
                # Calculate change magnitude
                change_magnitude = abs(after_mean - before_mean)
                threshold = np.std(values) * 0.5  # 0.5 standard deviations
                
                if change_magnitude > threshold:
                    change_points.append(i)
            
            return change_points
            
        except Exception as e:
            logger.error(f"Error detecting change points: {e}")
            return []
    
    def _segment_time_series(self, values: np.ndarray, change_points: List[int]) -> List[Dict]:
        """Segment time series based on change points."""
        try:
            if not change_points:
                return [{'segment': 0, 'start': 0, 'end': len(values) - 1, 'values': values.tolist()}]
            
            segments = []
            start_idx = 0
            
            for i, change_point in enumerate(change_points):
                segment = {
                    'segment': i,
                    'start': start_idx,
                    'end': change_point - 1,
                    'values': values[start_idx:change_point].tolist(),
                    'mean': float(np.mean(values[start_idx:change_point])),
                    'std': float(np.std(values[start_idx:change_point]))
                }
                segments.append(segment)
                start_idx = change_point
            
            # Add final segment
            final_segment = {
                'segment': len(change_points),
                'start': start_idx,
                'end': len(values) - 1,
                'values': values[start_idx:].tolist(),
                'mean': float(np.mean(values[start_idx:])),
                'std': float(np.std(values[start_idx:]))
            }
            segments.append(final_segment)
            
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting time series: {e}")
            return []
    
    def _analyze_structural_breaks(self, values: np.ndarray, change_points: List[int]) -> Dict[str, Any]:
        """Analyze structural breaks in time series."""
        try:
            if not change_points:
                return {'breaks_detected': False}
            
            # Calculate break statistics
            break_magnitudes = []
            for cp in change_points:
                if cp > 0 and cp < len(values):
                    before_mean = np.mean(values[:cp])
                    after_mean = np.mean(values[cp:])
                    magnitude = abs(after_mean - before_mean)
                    break_magnitudes.append(magnitude)
            
            return {
                'breaks_detected': True,
                'number_of_breaks': len(change_points),
                'break_points': change_points,
                'average_break_magnitude': float(np.mean(break_magnitudes)) if break_magnitudes else 0,
                'largest_break': float(np.max(break_magnitudes)) if break_magnitudes else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing structural breaks: {e}")
            return {'error': str(e)}
    
    def _assess_overall_trends(self, trend_results: Dict) -> Dict[str, Any]:
        """Assess overall trend patterns across all detected trends."""
        try:
            overall_assessment = {
                'primary_trend': 'unknown',
                'trend_confidence': 0.0,
                'pattern_complexity': 'simple',
                'forecast_reliability': 'low'
            }
            
            # Determine primary trend
            if 'linear' in trend_results:
                linear_trend = trend_results['linear']
                if 'trend_assessment' in linear_trend:
                    overall_assessment['primary_trend'] = linear_trend['trend_assessment']['direction']
                    if linear_trend['trend_assessment']['strength'] in ['strong', 'very_strong']:
                        overall_assessment['trend_confidence'] = 0.8
                    elif linear_trend['trend_assessment']['strength'] == 'moderate':
                        overall_assessment['trend_confidence'] = 0.6
                    else:
                        overall_assessment['trend_confidence'] = 0.4
            
            # Assess pattern complexity
            complexity_score = 0
            if 'seasonal' in trend_results:
                complexity_score += 1
            if 'cyclical' in trend_results:
                complexity_score += 1
            if 'structural_breaks' in trend_results:
                complexity_score += 1
            
            if complexity_score == 0:
                overall_assessment['pattern_complexity'] = 'simple'
            elif complexity_score == 1:
                overall_assessment['pattern_complexity'] = 'moderate'
            else:
                overall_assessment['pattern_complexity'] = 'complex'
            
            # Assess forecast reliability
            if overall_assessment['trend_confidence'] > 0.7 and overall_assessment['pattern_complexity'] == 'simple':
                overall_assessment['forecast_reliability'] = 'high'
            elif overall_assessment['trend_confidence'] > 0.5:
                overall_assessment['forecast_reliability'] = 'medium'
            else:
                overall_assessment['forecast_reliability'] = 'low'
            
            return overall_assessment
            
        except Exception as e:
            logger.error(f"Error assessing overall trends: {e}")
            return {'error': str(e)}
    
    def _generate_linear_forecast(self, slope: float, intercept: float, 
                                current_period: int, periods_ahead: int) -> List[float]:
        """Generate linear forecast based on trend parameters."""
        try:
            forecast = []
            for i in range(1, periods_ahead + 1):
                future_period = current_period + i
                forecast_value = slope * future_period + intercept
                forecast.append(float(forecast_value))
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating linear forecast: {e}")
            return []
    
    def _generate_seasonal_forecast(self, values: np.ndarray, seasonal_components: Dict, 
                                  periods_ahead: int) -> List[float]:
        """Generate seasonal forecast based on seasonal components."""
        try:
            if 'monthly_averages' not in seasonal_components:
                return []
            
            monthly_avgs = seasonal_components['monthly_averages']
            forecast = []
            
            for i in range(periods_ahead):
                month = (len(values) + i) % 12 + 1
                forecast_value = monthly_avgs.get(month, np.mean(values))
                forecast.append(float(forecast_value))
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating seasonal forecast: {e}")
            return []
    
    def _classify_seasonal_pattern(self, monthly_averages: Dict[int, float]) -> str:
        """Classify the type of seasonal pattern."""
        try:
            if not monthly_averages:
                return 'unknown'
            
            # Calculate seasonal range
            seasonal_range = max(monthly_averages.values()) - min(monthly_averages.values())
            overall_mean = np.mean(list(monthly_averages.values()))
            
            if overall_mean == 0:
                return 'unknown'
            
            # Calculate coefficient of variation
            cv = seasonal_range / overall_mean
            
            if cv > 0.5:
                return 'strong_seasonal'
            elif cv > 0.2:
                return 'moderate_seasonal'
            elif cv > 0.1:
                return 'weak_seasonal'
            else:
                return 'no_seasonal'
                
        except Exception as e:
            logger.error(f"Error classifying seasonal pattern: {e}")
            return 'unknown'
