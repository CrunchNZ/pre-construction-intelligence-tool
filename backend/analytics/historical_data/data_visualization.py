"""
Data Visualization Services

This module provides comprehensive data visualization services for historical data analysis,
including chart generation, dashboard creation, and interactive visualization components
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
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

logger = logging.getLogger(__name__)


class DataVisualizer:
    """Comprehensive data visualization service for historical analysis."""
    
    def __init__(self):
        """Initialize the data visualizer."""
        self.cache_timeout = 1800  # 30 minutes cache
        self.default_figsize = (12, 8)
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Configure matplotlib for non-interactive backend
        plt.switch_backend('Agg')
    
    def create_time_series_chart(self, data: List[Dict], value_field: str = 'value',
                                date_field: str = 'date', title: str = 'Time Series Chart',
                                chart_type: str = 'line', include_trend: bool = True,
                                include_forecast: bool = False) -> Dict[str, Any]:
        """Create time series chart with various visualization options."""
        try:
            if not data or len(data) < 2:
                return {'error': 'Insufficient data for time series chart'}
            
            # Sort data by date
            sorted_data = sorted(data, key=lambda x: x.get(date_field))
            
            # Extract values and dates
            values = [item.get(value_field, 0) for item in sorted_data]
            dates = [item.get(date_field) for item in sorted_data]
            
            # Convert dates to datetime if needed
            processed_dates = []
            for date in dates:
                if isinstance(date, str):
                    try:
                        processed_dates.append(datetime.fromisoformat(date))
                    except:
                        processed_dates.append(date)
                else:
                    processed_dates.append(date)
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=self.default_figsize)
            
            # Plot main data
            if chart_type == 'line':
                ax.plot(processed_dates, values, marker='o', linewidth=2, markersize=4, 
                       color=self.color_palette[0], label='Actual Values')
            elif chart_type == 'area':
                ax.fill_between(processed_dates, values, alpha=0.6, color=self.color_palette[0])
                ax.plot(processed_dates, values, color=self.color_palette[0], linewidth=2)
            elif chart_type == 'bar':
                ax.bar(processed_dates, values, alpha=0.7, color=self.color_palette[0])
            else:
                ax.plot(processed_dates, values, marker='o', linewidth=2, markersize=4, 
                       color=self.color_palette[0], label='Actual Values')
            
            # Add trend line if requested
            if include_trend and len(values) > 2:
                trend_line = self._calculate_trend_line(processed_dates, values)
                if trend_line:
                    ax.plot(processed_dates, trend_line, '--', color=self.color_palette[1], 
                           linewidth=2, label='Trend Line')
            
            # Add moving averages
            if len(values) > 5:
                ma_3 = self._calculate_moving_average(values, 3)
                ma_5 = self._calculate_moving_average(values, 5)
                
                if ma_3:
                    ma_3_dates = processed_dates[2:]  # Adjust for window size
                    ax.plot(ma_3_dates, ma_3, color=self.color_palette[2], linewidth=1.5, 
                           label='3-Period MA', alpha=0.8)
                
                if ma_5:
                    ma_5_dates = processed_dates[4:]  # Adjust for window size
                    ax.plot(ma_5_dates, ma_5, color=self.color_palette[3], linewidth=1.5, 
                           label='5-Period MA', alpha=0.8)
            
            # Customize chart
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64 string
            chart_data = self._figure_to_base64(fig)
            
            # Clean up
            plt.close(fig)
            
            return {
                'chart_type': 'time_series',
                'chart_data': chart_data,
                'data_summary': {
                    'total_points': len(values),
                    'date_range': {
                        'start': str(processed_dates[0]),
                        'end': str(processed_dates[-1])
                    },
                    'value_range': {
                        'min': float(min(values)),
                        'max': float(max(values)),
                        'mean': float(np.mean(values))
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating time series chart: {e}")
            return {'error': str(e)}
    
    def create_comparison_chart(self, datasets: List[Dict], value_field: str = 'value',
                               label_field: str = 'label', chart_type: str = 'bar',
                               title: str = 'Comparison Chart') -> Dict[str, Any]:
        """Create comparison chart for multiple datasets."""
        try:
            if not datasets or len(datasets) < 2:
                return {'error': 'Need at least 2 datasets for comparison'}
            
            # Extract data
            labels = [dataset.get(label_field, f'Dataset {i+1}') for i, dataset in enumerate(datasets)]
            values = [dataset.get(value_field, 0) for dataset in datasets]
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=self.default_figsize)
            
            # Create chart based on type
            if chart_type == 'bar':
                bars = ax.bar(labels, values, color=self.color_palette[:len(values)], alpha=0.8)
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
                
            elif chart_type == 'horizontal_bar':
                bars = ax.barh(labels, values, color=self.color_palette[:len(values)], alpha=0.8)
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    width = bar.get_width()
                    ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2.,
                           f'{value:.2f}', ha='left', va='center', fontweight='bold')
                
            elif chart_type == 'pie':
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                      colors=self.color_palette[:len(values)])
                ax.axis('equal')
                
            elif chart_type == 'doughnut':
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                      colors=self.color_palette[:len(values)])
                ax.add_patch(plt.Circle((0, 0), 0.7, fc='white'))
                ax.axis('equal')
                
            else:
                # Default to bar chart
                bars = ax.bar(labels, values, color=self.color_palette[:len(values)], alpha=0.8)
            
            # Customize chart
            ax.set_title(title, fontsize=16, fontweight='bold')
            
            if chart_type not in ['pie', 'doughnut']:
                ax.set_xlabel('Categories', fontsize=12)
                ax.set_ylabel('Values', fontsize=12)
                ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels if needed
            if chart_type in ['bar'] and len(labels) > 5:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64 string
            chart_data = self._figure_to_base64(fig)
            
            # Clean up
            plt.close(fig)
            
            return {
                'chart_type': 'comparison',
                'chart_data': chart_data,
                'data_summary': {
                    'total_datasets': len(datasets),
                    'value_range': {
                        'min': float(min(values)),
                        'max': float(max(values)),
                        'mean': float(np.mean(values))
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating comparison chart: {e}")
            return {'error': str(e)}
    
    def create_distribution_chart(self, data: List[float], chart_type: str = 'histogram',
                                 title: str = 'Distribution Chart', bins: int = 20) -> Dict[str, Any]:
        """Create distribution chart for data analysis."""
        try:
            if not data or len(data) < 5:
                return {'error': 'Insufficient data for distribution chart'}
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=self.default_figsize)
            
            # Create chart based on type
            if chart_type == 'histogram':
                ax.hist(data, bins=bins, alpha=0.7, color=self.color_palette[0], edgecolor='black')
                
                # Add mean and median lines
                mean_val = np.mean(data)
                median_val = np.median(data)
                ax.axvline(mean_val, color=self.color_palette[1], linestyle='--', linewidth=2, 
                          label=f'Mean: {mean_val:.2f}')
                ax.axvline(median_val, color=self.color_palette[2], linestyle='--', linewidth=2, 
                          label=f'Median: {median_val:.2f}')
                
            elif chart_type == 'box':
                ax.boxplot(data, patch_artist=True, boxprops=dict(facecolor=self.color_palette[0], alpha=0.7))
                
            elif chart_type == 'violin':
                ax.violinplot(data, points=100, showmeans=True, showextrema=True)
                
            elif chart_type == 'density':
                # Kernel density estimation
                from scipy.stats import gaussian_kde
                kde = gaussian_kde(data)
                x_range = np.linspace(min(data), max(data), 200)
                ax.plot(x_range, kde(x_range), color=self.color_palette[0], linewidth=2)
                ax.fill_between(x_range, kde(x_range), alpha=0.3, color=self.color_palette[0])
                
            else:
                # Default to histogram
                ax.hist(data, bins=bins, alpha=0.7, color=self.color_palette[0], edgecolor='black')
            
            # Customize chart
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('Values', fontsize=12)
            ax.set_ylabel('Frequency' if chart_type == 'histogram' else 'Density', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            if chart_type == 'histogram':
                ax.legend()
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64 string
            chart_data = self._figure_to_base64(fig)
            
            # Clean up
            plt.close(fig)
            
            return {
                'chart_type': 'distribution',
                'chart_data': chart_data,
                'data_summary': {
                    'total_points': len(data),
                    'statistics': {
                        'mean': float(np.mean(data)),
                        'median': float(np.median(data)),
                        'std': float(np.std(data)),
                        'min': float(min(data)),
                        'max': float(max(data))
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating distribution chart: {e}")
            return {'error': str(e)}
    
    def create_correlation_matrix(self, data: Dict[str, List[float]], 
                                title: str = 'Correlation Matrix') -> Dict[str, Any]:
        """Create correlation matrix heatmap."""
        try:
            if not data or len(data) < 2:
                return {'error': 'Need at least 2 variables for correlation matrix'}
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Calculate correlation matrix
            corr_matrix = df.corr()
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=self.default_figsize)
            
            # Create heatmap
            im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
            
            # Add correlation values as text
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                                 ha="center", va="center", color="black", fontweight='bold')
            
            # Customize chart
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xticks(range(len(corr_matrix.columns)))
            ax.set_yticks(range(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
            ax.set_yticklabels(corr_matrix.columns)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Correlation Coefficient', rotation=270, labelpad=15)
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64 string
            chart_data = self._figure_to_base64(fig)
            
            # Clean up
            plt.close(fig)
            
            return {
                'chart_type': 'correlation_matrix',
                'chart_data': chart_data,
                'data_summary': {
                    'variables': list(corr_matrix.columns),
                    'correlation_matrix': corr_matrix.to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating correlation matrix: {e}")
            return {'error': str(e)}
    
    def create_trend_analysis_chart(self, trend_data: Dict, title: str = 'Trend Analysis') -> Dict[str, Any]:
        """Create comprehensive trend analysis chart."""
        try:
            if not trend_data or 'trends' not in trend_data:
                return {'error': 'Invalid trend data format'}
            
            # Create subplots for different trend components
            trends = trend_data['trends']
            n_trends = len(trends)
            
            if n_trends == 0:
                return {'error': 'No trend data available'}
            
            # Determine subplot layout
            if n_trends <= 2:
                fig, axes = plt.subplots(1, n_trends, figsize=(15, 6))
                if n_trends == 1:
                    axes = [axes]
            else:
                fig, axes = plt.subplots(2, 2, figsize=(15, 12))
                axes = axes.flatten()
            
            # Plot each trend type
            trend_types = list(trends.keys())
            for i, trend_type in enumerate(trend_types):
                if i >= len(axes):
                    break
                
                ax = axes[i]
                trend_info = trends[trend_type]
                
                if trend_type == 'linear' and 'coefficients' in trend_info:
                    # Plot linear trend
                    self._plot_linear_trend(ax, trend_info, trend_data.get('data_summary', {}))
                    
                elif trend_type == 'seasonal' and 'seasonal_components' in trend_info:
                    # Plot seasonal components
                    self._plot_seasonal_trend(ax, trend_info)
                    
                elif trend_type == 'cyclical' and 'autocorrelation' in trend_info:
                    # Plot autocorrelation
                    self._plot_cyclical_trend(ax, trend_info)
                    
                elif trend_type == 'structural_breaks' and 'segments' in trend_info:
                    # Plot structural breaks
                    self._plot_structural_breaks(ax, trend_info, trend_data.get('data_summary', {}))
                
                ax.set_title(f'{trend_type.title()} Trend', fontweight='bold')
                ax.grid(True, alpha=0.3)
            
            # Hide unused subplots
            for i in range(n_trends, len(axes)):
                axes[i].set_visible(False)
            
            # Add overall title
            fig.suptitle(title, fontsize=18, fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64 string
            chart_data = self._figure_to_base64(fig)
            
            # Clean up
            plt.close(fig)
            
            return {
                'chart_type': 'trend_analysis',
                'chart_data': chart_data,
                'trends_analyzed': trend_types
            }
            
        except Exception as e:
            logger.error(f"Error creating trend analysis chart: {e}")
            return {'error': str(e)}
    
    def create_dashboard(self, charts: List[Dict], layout: str = 'grid',
                        title: str = 'Data Analysis Dashboard') -> Dict[str, Any]:
        """Create a comprehensive dashboard with multiple charts."""
        try:
            if not charts or len(charts) == 0:
                return {'error': 'No charts provided for dashboard'}
            
            # Determine layout
            n_charts = len(charts)
            if layout == 'grid':
                if n_charts <= 2:
                    rows, cols = 1, n_charts
                elif n_charts <= 4:
                    rows, cols = 2, 2
                else:
                    rows, cols = 3, 3
            elif layout == 'vertical':
                rows, cols = n_charts, 1
            elif layout == 'horizontal':
                rows, cols = 1, n_charts
            else:
                rows, cols = 2, 2
            
            # Create figure
            fig = plt.figure(figsize=(cols * 6, rows * 5))
            
            # Add charts to dashboard
            for i, chart in enumerate(charts):
                if i >= rows * cols:
                    break
                
                ax = fig.add_subplot(rows, cols, i + 1)
                
                # Add chart title
                chart_title = chart.get('title', f'Chart {i+1}')
                ax.set_title(chart_title, fontsize=12, fontweight='bold')
                
                # Add placeholder text (in real implementation, you'd render the actual chart)
                ax.text(0.5, 0.5, f'Chart {i+1}\n{chart_title}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=10)
                ax.set_xticks([])
                ax.set_yticks([])
            
            # Add overall title
            fig.suptitle(title, fontsize=16, fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64 string
            chart_data = self._figure_to_base64(fig)
            
            # Clean up
            plt.close(fig)
            
            return {
                'chart_type': 'dashboard',
                'chart_data': chart_data,
                'dashboard_info': {
                    'total_charts': n_charts,
                    'layout': layout,
                    'chart_titles': [chart.get('title', f'Chart {i+1}') for i, chart in enumerate(charts)]
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return {'error': str(e)}
    
    def _calculate_trend_line(self, dates: List, values: List[float]) -> Optional[List[float]]:
        """Calculate trend line for time series data."""
        try:
            if len(values) < 2:
                return None
            
            # Convert dates to numeric values for regression
            date_nums = [(date - dates[0]).days if hasattr(date, '__sub__') else i 
                        for i, date in enumerate(dates)]
            
            # Linear regression
            z = np.polyfit(date_nums, values, 1)
            p = np.poly1d(z)
            
            # Generate trend line values
            trend_line = [float(p(x)) for x in date_nums]
            return trend_line
            
        except Exception as e:
            logger.error(f"Error calculating trend line: {e}")
            return None
    
    def _calculate_moving_average(self, values: List[float], window: int) -> Optional[List[float]]:
        """Calculate moving average with specified window size."""
        try:
            if len(values) < window:
                return None
            
            moving_avg = []
            for i in range(window - 1, len(values)):
                window_values = values[i - window + 1:i + 1]
                moving_avg.append(float(np.mean(window_values)))
            
            return moving_avg
            
        except Exception as e:
            logger.error(f"Error calculating moving average: {e}")
            return None
    
    def _plot_linear_trend(self, ax, trend_info: Dict, data_summary: Dict):
        """Plot linear trend information."""
        try:
            # This would plot the actual trend data
            # For now, add placeholder
            ax.text(0.5, 0.5, 'Linear Trend\nSlope: {:.2f}\nR²: {:.2f}'.format(
                trend_info.get('coefficients', {}).get('slope', 0),
                trend_info.get('coefficients', {}).get('correlation', 0) ** 2
            ), ha='center', va='center', transform=ax.transAxes)
            
        except Exception as e:
            logger.error(f"Error plotting linear trend: {e}")
    
    def _plot_seasonal_trend(self, ax, trend_info: Dict):
        """Plot seasonal trend information."""
        try:
            # This would plot the seasonal components
            # For now, add placeholder
            ax.text(0.5, 0.5, 'Seasonal Trend\nStrength: {}'.format(
                trend_info.get('seasonality_strength', 'unknown')
            ), ha='center', va='center', transform=ax.transAxes)
            
        except Exception as e:
            logger.error(f"Error plotting seasonal trend: {e}")
    
    def _plot_cyclical_trend(self, ax, trend_info: Dict):
        """Plot cyclical trend information."""
        try:
            # This would plot the autocorrelation
            # For now, add placeholder
            ax.text(0.5, 0.5, 'Cyclical Trend\nStrength: {}'.format(
                trend_info.get('cyclical_strength', 'unknown')
            ), ha='center', va='center', transform=ax.transAxes)
            
        except Exception as e:
            logger.error(f"Error plotting cyclical trend: {e}")
    
    def _plot_structural_breaks(self, ax, trend_info: Dict, data_summary: Dict):
        """Plot structural breaks information."""
        try:
            # This would plot the segmented time series
            # For now, add placeholder
            breaks_detected = trend_info.get('break_analysis', {}).get('breaks_detected', False)
            ax.text(0.5, 0.5, 'Structural Breaks\nDetected: {}'.format(
                'Yes' if breaks_detected else 'No'
            ), ha='center', va='center', transform=ax.transAxes)
            
        except Exception as e:
            logger.error(f"Error plotting structural breaks: {e}")
    
    def _figure_to_base64(self, fig: Figure) -> str:
        """Convert matplotlib figure to base64 string."""
        try:
            # Create canvas
            canvas = FigureCanvasAgg(fig)
            
            # Save to bytes buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            # Convert to base64
            img_str = base64.b64encode(buf.read()).decode()
            
            # Close buffer
            buf.close()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error converting figure to base64: {e}")
            return ""
    
    def export_chart_data(self, chart_data: Dict, format: str = 'json') -> Dict[str, Any]:
        """Export chart data in various formats."""
        try:
            if format == 'json':
                return {
                    'format': 'json',
                    'data': chart_data,
                    'export_timestamp': timezone.now().isoformat()
                }
            elif format == 'csv':
                # Convert to CSV format if applicable
                return {
                    'format': 'csv',
                    'data': self._convert_to_csv(chart_data),
                    'export_timestamp': timezone.now().isoformat()
                }
            else:
                return {'error': f'Unsupported export format: {format}'}
                
        except Exception as e:
            logger.error(f"Error exporting chart data: {e}")
            return {'error': str(e)}
    
    def _convert_to_csv(self, chart_data: Dict) -> str:
        """Convert chart data to CSV format."""
        try:
            # This is a simplified CSV conversion
            # In a real implementation, you'd handle different chart types appropriately
            csv_lines = []
            
            if 'data_summary' in chart_data:
                summary = chart_data['data_summary']
                csv_lines.append('Metric,Value')
                for key, value in summary.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            csv_lines.append(f'{key}_{sub_key},{sub_value}')
                    else:
                        csv_lines.append(f'{key},{value}')
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            logger.error(f"Error converting to CSV: {e}")
            return ""
