"""
Custom Analytics Dashboards

This module provides comprehensive analytics dashboard creation and management
capabilities for historical data analysis, including pre-built dashboards and
custom dashboard builder functionality.

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
import json
from collections import defaultdict

from .data_aggregation import DataAggregator
from .statistical_analysis import DescriptiveStatistics, InferentialStatistics, AdvancedStatisticalModeling
from .trend_detection import TrendDetector
from .data_visualization import DataVisualizer

logger = logging.getLogger(__name__)


class AnalyticsDashboardBuilder:
    """Builder class for creating custom analytics dashboards."""
    
    def __init__(self):
        """Initialize the dashboard builder."""
        self.data_aggregator = DataAggregator()
        self.descriptive_stats = DescriptiveStatistics()
        self.inferential_stats = InferentialStatistics()
        self.advanced_stats = AdvancedStatisticalModeling()
        self.trend_detector = TrendDetector()
        self.visualizer = DataVisualizer()
        
        # Pre-defined dashboard templates
        self.dashboard_templates = {
            'executive_summary': self._get_executive_summary_template(),
            'procurement_analysis': self._get_procurement_analysis_template(),
            'project_performance': self._get_project_performance_template(),
            'financial_analysis': self._get_financial_analysis_template(),
            'bim_analytics': self._get_bim_analytics_template(),
            'supplier_performance': self._get_supplier_performance_template(),
            'risk_analysis': self._get_risk_analysis_template(),
            'trend_analysis': self._get_trend_analysis_template()
        }
    
    def create_dashboard(self, dashboard_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a dashboard based on type and parameters."""
        try:
            if dashboard_type not in self.dashboard_templates:
                return {'error': f'Unknown dashboard type: {dashboard_type}'}
            
            template = self.dashboard_templates[dashboard_type]
            
            # Set default parameters
            if parameters is None:
                parameters = {}
            
            default_params = {
                'start_date': timezone.now() - timedelta(days=365),
                'end_date': timezone.now(),
                'include_charts': True,
                'include_metrics': True,
                'include_recommendations': True
            }
            
            # Update with provided parameters
            default_params.update(parameters)
            
            # Build dashboard
            dashboard = self._build_dashboard(template, default_params)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return {'error': str(e)}
    
    def create_custom_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom dashboard based on configuration."""
        try:
            if not dashboard_config or 'sections' not in dashboard_config:
                return {'error': 'Invalid dashboard configuration'}
            
            dashboard = {
                'dashboard_id': dashboard_config.get('dashboard_id', f'custom_{int(timezone.now().timestamp())}'),
                'title': dashboard_config.get('title', 'Custom Dashboard'),
                'description': dashboard_config.get('description', ''),
                'created_at': timezone.now().isoformat(),
                'sections': [],
                'overall_metrics': {},
                'recommendations': []
            }
            
            # Build each section
            for section_config in dashboard_config['sections']:
                section = self._build_custom_section(section_config)
                if section:
                    dashboard['sections'].append(section)
            
            # Calculate overall metrics
            dashboard['overall_metrics'] = self._calculate_overall_dashboard_metrics(dashboard['sections'])
            
            # Generate recommendations
            dashboard['recommendations'] = self._generate_dashboard_recommendations(dashboard)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating custom dashboard: {e}")
            return {'error': str(e)}
    
    def _build_dashboard(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build dashboard based on template and parameters."""
        try:
            dashboard = {
                'dashboard_id': template['id'],
                'title': template['title'],
                'description': template['description'],
                'created_at': timezone.now().isoformat(),
                'parameters': parameters,
                'sections': [],
                'overall_metrics': {},
                'recommendations': []
            }
            
            # Build each section
            for section_template in template['sections']:
                section = self._build_section(section_template, parameters)
                if section:
                    dashboard['sections'].append(section)
            
            # Calculate overall metrics
            dashboard['overall_metrics'] = self._calculate_overall_dashboard_metrics(dashboard['sections'])
            
            # Generate recommendations
            dashboard['recommendations'] = self._generate_dashboard_recommendations(dashboard)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error building dashboard: {e}")
            return {'error': str(e)}
    
    def _build_section(self, section_template: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build a dashboard section based on template."""
        try:
            section = {
                'section_id': section_template['id'],
                'title': section_template['title'],
                'type': section_template['type'],
                'content': {}
            }
            
            # Build content based on section type
            if section_template['type'] == 'metrics':
                section['content'] = self._build_metrics_section(section_template, parameters)
            elif section_template['type'] == 'chart':
                section['content'] = self._build_chart_section(section_template, parameters)
            elif section_template['type'] == 'table':
                section['content'] = self._build_table_section(section_template, parameters)
            elif section_template['type'] == 'summary':
                section['content'] = self._build_summary_section(section_template, parameters)
            
            return section
            
        except Exception as e:
            logger.error(f"Error building section: {e}")
            return None
    
    def _build_custom_section(self, section_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build a custom dashboard section."""
        try:
            section = {
                'section_id': section_config.get('id', f'section_{int(timezone.now().timestamp())}'),
                'title': section_config.get('title', 'Custom Section'),
                'type': section_config.get('type', 'summary'),
                'content': {}
            }
            
            # Build content based on section type
            if section_config['type'] == 'metrics':
                section['content'] = self._build_custom_metrics_section(section_config)
            elif section_config['type'] == 'chart':
                section['content'] = self._build_custom_chart_section(section_config)
            elif section_config['type'] == 'table':
                section['content'] = self._build_custom_table_section(section_config)
            elif section_config['type'] == 'summary':
                section['content'] = self._build_custom_summary_section(section_config)
            
            return section
            
        except Exception as e:
            logger.error(f"Error building custom section: {e}")
            return None
    
    def _build_metrics_section(self, section_template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a metrics section."""
        try:
            metrics = {}
            
            # Get data based on data_source
            data_source = section_template.get('data_source', '')
            if data_source == 'procurement':
                data = self.data_aggregator.aggregate_procurement_data(
                    parameters['start_date'], parameters['end_date']
                )
                metrics = self._extract_procurement_metrics(data)
            elif data_source == 'projects':
                data = self.data_aggregator.aggregate_project_data(
                    parameters['start_date'], parameters['end_date']
                )
                metrics = self._extract_project_metrics(data)
            elif data_source == 'financial':
                data = self.data_aggregator.aggregate_financial_data(
                    parameters['start_date'], parameters['end_date']
                )
                metrics = self._extract_financial_metrics(data)
            elif data_source == 'bim':
                data = self.data_aggregator.aggregate_bim_data(
                    parameters['start_date'], parameters['end_date']
                )
                metrics = self._extract_bim_metrics(data)
            
            return {
                'metrics': metrics,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building metrics section: {e}")
            return {'error': str(e)}
    
    def _build_chart_section(self, section_template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a chart section."""
        try:
            chart_data = {}
            
            # Get data and create chart
            data_source = section_template.get('data_source', '')
            chart_type = section_template.get('chart_type', 'line')
            
            if data_source == 'procurement':
                data = self.data_aggregator.aggregate_procurement_data(
                    parameters['start_date'], parameters['end_date']
                )
                chart_data = self._create_procurement_chart(data, chart_type)
            elif data_source == 'projects':
                data = self.data_aggregator.aggregate_project_data(
                    parameters['start_date'], parameters['end_date']
                )
                chart_data = self._create_project_chart(data, chart_type)
            elif data_source == 'financial':
                data = self.data_aggregator.aggregate_financial_data(
                    parameters['start_date'], parameters['end_date']
                )
                chart_data = self._create_financial_chart(data, chart_type)
            elif data_source == 'bim':
                data = self.data_aggregator.aggregate_bim_data(
                    parameters['start_date'], parameters['end_date']
                )
                chart_data = self._create_bim_chart(data, chart_type)
            
            return {
                'chart': chart_data,
                'chart_type': chart_type,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building chart section: {e}")
            return {'error': str(e)}
    
    def _build_table_section(self, section_template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a table section."""
        try:
            table_data = {}
            
            # Get data based on data_source
            data_source = section_template.get('data_source', '')
            if data_source == 'procurement':
                data = self.data_aggregator.aggregate_procurement_data(
                    parameters['start_date'], parameters['end_date']
                )
                table_data = self._extract_procurement_table_data(data)
            elif data_source == 'projects':
                data = self.data_aggregator.aggregate_project_data(
                    parameters['start_date'], parameters['end_date']
                )
                table_data = self._extract_project_table_data(data)
            elif data_source == 'financial':
                data = self.data_aggregator.aggregate_financial_data(
                    parameters['start_date'], parameters['end_date']
                )
                table_data = self._extract_financial_table_data(data)
            elif data_source == 'bim':
                data = self.data_aggregator.aggregate_bim_data(
                    parameters['start_date'], parameters['end_date']
                )
                table_data = self._extract_bim_table_data(data)
            
            return {
                'table': table_data,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building table section: {e}")
            return {'error': str(e)}
    
    def _build_summary_section(self, section_template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a summary section."""
        try:
            summary = {}
            
            # Get data based on data_source
            data_source = section_template.get('data_source', '')
            if data_source == 'procurement':
                data = self.data_aggregator.aggregate_procurement_data(
                    parameters['start_date'], parameters['end_date']
                )
                summary = self._create_procurement_summary(data)
            elif data_source == 'projects':
                data = self.data_aggregator.aggregate_project_data(
                    parameters['start_date'], parameters['end_date']
                )
                summary = self._create_project_summary(data)
            elif data_source == 'financial':
                data = self.data_aggregator.aggregate_financial_data(
                    parameters['start_date'], parameters['end_date']
                )
                summary = self._create_financial_summary(data)
            elif data_source == 'bim':
                data = self.data_aggregator.aggregate_bim_data(
                    parameters['start_date'], parameters['end_date']
                )
                summary = self._create_bim_summary(data)
            
            return {
                'summary': summary,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building summary section: {e}")
            return {'error': str(e)}
    
    def _build_custom_metrics_section(self, section_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build a custom metrics section."""
        try:
            # This would implement custom metrics based on user configuration
            # For now, return a placeholder
            return {
                'metrics': {
                    'custom_metric_1': 0,
                    'custom_metric_2': 0
                },
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building custom metrics section: {e}")
            return {'error': str(e)}
    
    def _build_custom_chart_section(self, section_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build a custom chart section."""
        try:
            # This would implement custom charts based on user configuration
            # For now, return a placeholder
            return {
                'chart': {'error': 'Custom chart not implemented'},
                'chart_type': 'custom',
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building custom chart section: {e}")
            return {'error': str(e)}
    
    def _build_custom_table_section(self, section_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build a custom table section."""
        try:
            # This would implement custom tables based on user configuration
            # For now, return a placeholder
            return {
                'table': {'error': 'Custom table not implemented'},
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building custom table section: {e}")
            return {'error': str(e)}
    
    def _build_custom_summary_section(self, section_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build a custom summary section."""
        try:
            # This would implement custom summaries based on user configuration
            # For now, return a placeholder
            return {
                'summary': {'error': 'Custom summary not implemented'},
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building custom summary section: {e}")
            return {'error': str(e)}
    
    def _extract_procurement_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key procurement metrics."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            
            return {
                'total_purchase_orders': summary.get('total_purchase_orders', 0),
                'total_po_value': summary.get('total_po_value', 0),
                'average_po_value': summary.get('average_po_value', 0),
                'total_invoices': summary.get('total_invoices', 0),
                'outstanding_amount': summary.get('outstanding_amount', 0),
                'payment_rate': data.get('payment_performance', {}).get('payment_rate_percentage', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting procurement metrics: {e}")
            return {}
    
    def _extract_project_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key project metrics."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            performance = data.get('project_performance', {})
            
            return {
                'total_projects': summary.get('total_projects', 0),
                'total_budget': summary.get('total_budget', 0),
                'completed_projects': summary.get('completed_projects', 0),
                'completion_rate': performance.get('completion_rate_percentage', 0),
                'change_order_impact': performance.get('change_order_impact_percentage', 0),
                'total_rfis': summary.get('total_rfis', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting project metrics: {e}")
            return {}
    
    def _extract_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key financial metrics."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            
            return {
                'total_transactions': summary.get('total_transactions', 0),
                'total_debits': summary.get('total_debits', 0),
                'total_credits': summary.get('total_credits', 0),
                'net_amount': summary.get('net_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting financial metrics: {e}")
            return {}
    
    def _extract_bim_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key BIM metrics."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            performance = data.get('bim_performance', {})
            
            return {
                'total_models': summary.get('total_models', 0),
                'total_components': summary.get('total_components', 0),
                'total_clashes': summary.get('total_clashes', 0),
                'resolved_clashes': summary.get('resolved_clashes', 0),
                'resolution_efficiency': performance.get('clash_resolution_efficiency_percentage', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting BIM metrics: {e}")
            return {}
    
    def _create_procurement_chart(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """Create procurement chart."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            # Create time series data for chart
            trends = data.get('trends', {})
            if 'monthly_trends' in trends:
                chart_data = self.visualizer.create_time_series_chart(
                    trends['monthly_trends'],
                    value_field='total_value',
                    date_field='month',
                    title='Procurement Trends',
                    chart_type=chart_type
                )
                return chart_data
            
            return {'error': 'No trend data available'}
            
        except Exception as e:
            logger.error(f"Error creating procurement chart: {e}")
            return {'error': str(e)}
    
    def _create_project_chart(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """Create project chart."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            # Create comparison chart for project status
            project_status = [
                {'label': 'Completed', 'value': data.get('summary', {}).get('completed_projects', 0)},
                {'label': 'In Progress', 'value': data.get('summary', {}).get('in_progress_projects', 0)},
                {'label': 'Delayed', 'value': data.get('summary', {}).get('delayed_projects', 0)}
            ]
            
            chart_data = self.visualizer.create_comparison_chart(
                project_status,
                value_field='value',
                label_field='label',
                chart_type=chart_type,
                title='Project Status Distribution'
            )
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating project chart: {e}")
            return {'error': str(e)}
    
    def _create_financial_chart(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """Create financial chart."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            # Create time series data for chart
            trends = data.get('trends', {})
            if 'monthly_trends' in trends:
                chart_data = self.visualizer.create_time_series_chart(
                    trends['monthly_trends'],
                    value_field='net_amount',
                    date_field='month',
                    title='Financial Trends',
                    chart_type=chart_type
                )
                return chart_data
            
            return {'error': 'No trend data available'}
            
        except Exception as e:
            logger.error(f"Error creating financial chart: {e}")
            return {'error': str(e)}
    
    def _create_bim_chart(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """Create BIM chart."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            # Create comparison chart for clash analysis
            clash_data = data.get('clash_analysis', {})
            clash_status = [
                {'label': 'Resolved', 'value': clash_data.get('resolved_clashes', 0)},
                {'label': 'Pending', 'value': clash_data.get('pending_clashes', 0)},
                {'label': 'Critical', 'value': clash_data.get('critical_clashes', 0)}
            ]
            
            chart_data = self.visualizer.create_comparison_chart(
                clash_status,
                value_field='value',
                label_field='label',
                chart_type=chart_type,
                title='Clash Resolution Status'
            )
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating BIM chart: {e}")
            return {'error': str(e)}
    
    def _extract_procurement_table_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract procurement table data."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            return {
                'headers': ['Supplier', 'PO Count', 'Total Value', 'Average Value'],
                'rows': data.get('supplier_breakdown', [])
            }
            
        except Exception as e:
            logger.error(f"Error extracting procurement table data: {e}")
            return {}
    
    def _extract_project_table_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project table data."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            return {
                'headers': ['Project Type', 'Count', 'Total Budget', 'Status'],
                'rows': []  # This would be populated with actual project data
            }
            
        except Exception as e:
            logger.error(f"Error extracting project table data: {e}")
            return {}
    
    def _extract_financial_table_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial table data."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            return {
                'headers': ['Cost Center', 'Transaction Count', 'Total Debits', 'Total Credits', 'Net Amount'],
                'rows': data.get('cost_center_breakdown', [])
            }
            
        except Exception as e:
            logger.error(f"Error extracting financial table data: {e}")
            return {}
    
    def _extract_bim_table_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract BIM table data."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            return {
                'headers': ['Model', 'Components', 'File Size', 'Last Updated'],
                'rows': []  # This would be populated with actual BIM data
            }
            
        except Exception as e:
            logger.error(f"Error extracting BIM table data: {e}")
            return {}
    
    def _create_procurement_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create procurement summary."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            payment_perf = data.get('payment_performance', {})
            
            return {
                'overview': f"Total procurement value: ${summary.get('total_po_value', 0):,.2f}",
                'key_insights': [
                    f"Average PO value: ${summary.get('average_po_value', 0):,.2f}",
                    f"Payment rate: {payment_perf.get('payment_rate_percentage', 0):.1f}%",
                    f"Outstanding amount: ${summary.get('outstanding_amount', 0):,.2f}"
                ],
                'recommendations': [
                    "Monitor payment performance",
                    "Review outstanding invoices",
                    "Analyze supplier performance trends"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating procurement summary: {e}")
            return {}
    
    def _create_project_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project summary."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            performance = data.get('project_performance', {})
            
            return {
                'overview': f"Total projects: {summary.get('total_projects', 0)}",
                'key_insights': [
                    f"Completion rate: {performance.get('completion_rate_percentage', 0):.1f}%",
                    f"Change order impact: {performance.get('change_order_impact_percentage', 0):.1f}%",
                    f"Total RFIs: {summary.get('total_rfis', 0)}"
                ],
                'recommendations': [
                    "Focus on improving completion rates",
                    "Monitor change order impacts",
                    "Reduce RFI frequency through better planning"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating project summary: {e}")
            return {}
    
    def _create_financial_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create financial summary."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            
            return {
                'overview': f"Net financial position: ${summary.get('net_amount', 0):,.2f}",
                'key_insights': [
                    f"Total transactions: {summary.get('total_transactions', 0)}",
                    f"Total debits: ${summary.get('total_debits', 0):,.2f}",
                    f"Total credits: ${summary.get('total_credits', 0):,.2f}"
                ],
                'recommendations': [
                    "Monitor cash flow trends",
                    "Review cost center performance",
                    "Analyze transaction patterns"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating financial summary: {e}")
            return {}
    
    def _create_bim_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIM summary."""
        try:
            if 'error' in data:
                return {'error': data['error']}
            
            summary = data.get('summary', {})
            performance = data.get('bim_performance', {})
            
            return {
                'overview': f"Total BIM models: {summary.get('total_models', 0)}",
                'key_insights': [
                    f"Total components: {summary.get('total_components', 0)}",
                    f"Clash resolution rate: {summary.get('resolved_clashes', 0)}/{summary.get('total_clashes', 0)}",
                    f"Resolution efficiency: {performance.get('clash_resolution_efficiency_percentage', 0):.1f}%"
                ],
                'recommendations': [
                    "Improve clash detection early in design",
                    "Streamline coordination processes",
                    "Monitor model complexity"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating BIM summary: {e}")
            return {}
    
    def _calculate_overall_dashboard_metrics(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall dashboard metrics."""
        try:
            overall_metrics = {
                'total_sections': len(sections),
                'sections_with_errors': 0,
                'last_updated': timezone.now().isoformat()
            }
            
            # Count sections with errors
            for section in sections:
                if 'content' in section and 'error' in section['content']:
                    overall_metrics['sections_with_errors'] += 1
            
            return overall_metrics
            
        except Exception as e:
            logger.error(f"Error calculating overall dashboard metrics: {e}")
            return {}
    
    def _generate_dashboard_recommendations(self, dashboard: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on dashboard data."""
        try:
            recommendations = []
            
            # Check for data quality issues
            if dashboard.get('overall_metrics', {}).get('sections_with_errors', 0) > 0:
                recommendations.append("Review and fix data quality issues in dashboard sections")
            
            # Add general recommendations
            recommendations.extend([
                "Regularly update dashboard data for accurate insights",
                "Monitor key performance indicators for trends",
                "Use insights to drive data-driven decision making"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating dashboard recommendations: {e}")
            return []
    
    def _get_executive_summary_template(self) -> Dict[str, Any]:
        """Get executive summary dashboard template."""
        return {
            'id': 'executive_summary',
            'title': 'Executive Summary Dashboard',
            'description': 'High-level overview of key performance indicators across all systems',
            'sections': [
                {
                    'id': 'overall_metrics',
                    'title': 'Overall Performance Metrics',
                    'type': 'metrics',
                    'data_source': 'cross_system'
                },
                {
                    'id': 'procurement_overview',
                    'title': 'Procurement Overview',
                    'type': 'summary',
                    'data_source': 'procurement'
                },
                {
                    'id': 'project_status',
                    'title': 'Project Status',
                    'type': 'chart',
                    'data_source': 'projects',
                    'chart_type': 'pie'
                },
                {
                    'id': 'financial_summary',
                    'title': 'Financial Summary',
                    'type': 'summary',
                    'data_source': 'financial'
                }
            ]
        }
    
    def _get_procurement_analysis_template(self) -> Dict[str, Any]:
        """Get procurement analysis dashboard template."""
        return {
            'id': 'procurement_analysis',
            'title': 'Procurement Analysis Dashboard',
            'description': 'Comprehensive analysis of procurement activities and performance',
            'sections': [
                {
                    'id': 'procurement_metrics',
                    'title': 'Key Procurement Metrics',
                    'type': 'metrics',
                    'data_source': 'procurement'
                },
                {
                    'id': 'procurement_trends',
                    'title': 'Procurement Trends',
                    'type': 'chart',
                    'data_source': 'procurement',
                    'chart_type': 'line'
                },
                {
                    'id': 'supplier_performance',
                    'title': 'Supplier Performance',
                    'type': 'table',
                    'data_source': 'procurement'
                },
                {
                    'id': 'procurement_summary',
                    'title': 'Procurement Summary',
                    'type': 'summary',
                    'data_source': 'procurement'
                }
            ]
        }
    
    def _get_project_performance_template(self) -> Dict[str, Any]:
        """Get project performance dashboard template."""
        return {
            'id': 'project_performance',
            'title': 'Project Performance Dashboard',
            'description': 'Analysis of project performance, status, and key metrics',
            'sections': [
                {
                    'id': 'project_metrics',
                    'title': 'Project Performance Metrics',
                    'type': 'metrics',
                    'data_source': 'projects'
                },
                {
                    'id': 'project_status_chart',
                    'title': 'Project Status Distribution',
                    'type': 'chart',
                    'data_source': 'projects',
                    'chart_type': 'doughnut'
                },
                {
                    'id': 'change_order_analysis',
                    'title': 'Change Order Analysis',
                    'type': 'table',
                    'data_source': 'projects'
                },
                {
                    'id': 'project_summary',
                    'title': 'Project Summary',
                    'type': 'summary',
                    'data_source': 'projects'
                }
            ]
        }
    
    def _get_financial_analysis_template(self) -> Dict[str, Any]:
        """Get financial analysis dashboard template."""
        return {
            'id': 'financial_analysis',
            'title': 'Financial Analysis Dashboard',
            'description': 'Comprehensive financial analysis and reporting',
            'sections': [
                {
                    'id': 'financial_metrics',
                    'title': 'Financial Performance Metrics',
                    'type': 'metrics',
                    'data_source': 'financial'
                },
                {
                    'id': 'financial_trends',
                    'title': 'Financial Trends',
                    'type': 'chart',
                    'data_source': 'financial',
                    'chart_type': 'line'
                },
                {
                    'id': 'cost_center_analysis',
                    'title': 'Cost Center Analysis',
                    'type': 'table',
                    'data_source': 'financial'
                },
                {
                    'id': 'financial_summary',
                    'title': 'Financial Summary',
                    'type': 'summary',
                    'data_source': 'financial'
                }
            ]
        }
    
    def _get_bim_analytics_template(self) -> Dict[str, Any]:
        """Get BIM analytics dashboard template."""
        return {
            'id': 'bim_analytics',
            'title': 'BIM Analytics Dashboard',
            'description': 'Building Information Modeling analytics and performance metrics',
            'sections': [
                {
                    'id': 'bim_metrics',
                    'title': 'BIM Performance Metrics',
                    'type': 'metrics',
                    'data_source': 'bim'
                },
                {
                    'id': 'clash_analysis',
                    'title': 'Clash Analysis',
                    'type': 'chart',
                    'data_source': 'bim',
                    'chart_type': 'bar'
                },
                {
                    'id': 'model_performance',
                    'title': 'Model Performance',
                    'type': 'table',
                    'data_source': 'bim'
                },
                {
                    'id': 'bim_summary',
                    'title': 'BIM Summary',
                    'type': 'summary',
                    'data_source': 'bim'
                }
            ]
        }
    
    def _get_supplier_performance_template(self) -> Dict[str, Any]:
        """Get supplier performance dashboard template."""
        return {
            'id': 'supplier_performance',
            'title': 'Supplier Performance Dashboard',
            'description': 'Analysis of supplier performance and relationships',
            'sections': [
                {
                    'id': 'supplier_metrics',
                    'title': 'Supplier Performance Metrics',
                    'type': 'metrics',
                    'data_source': 'procurement'
                },
                {
                    'id': 'supplier_ranking',
                    'title': 'Supplier Performance Ranking',
                    'type': 'chart',
                    'data_source': 'procurement',
                    'chart_type': 'horizontal_bar'
                },
                {
                    'id': 'supplier_details',
                    'title': 'Supplier Details',
                    'type': 'table',
                    'data_source': 'procurement'
                }
            ]
        }
    
    def _get_risk_analysis_template(self) -> Dict[str, Any]:
        """Get risk analysis dashboard template."""
        return {
            'id': 'risk_analysis',
            'title': 'Risk Analysis Dashboard',
            'description': 'Comprehensive risk assessment and monitoring',
            'sections': [
                {
                    'id': 'risk_metrics',
                    'title': 'Risk Metrics',
                    'type': 'metrics',
                    'data_source': 'cross_system'
                },
                {
                    'id': 'risk_trends',
                    'title': 'Risk Trends',
                    'type': 'chart',
                    'data_source': 'cross_system',
                    'chart_type': 'line'
                },
                {
                    'id': 'risk_summary',
                    'title': 'Risk Summary',
                    'type': 'summary',
                    'data_source': 'cross_system'
                }
            ]
        }
    
    def _get_trend_analysis_template(self) -> Dict[str, Any]:
        """Get trend analysis dashboard template."""
        return {
            'id': 'trend_analysis',
            'title': 'Trend Analysis Dashboard',
            'description': 'Comprehensive trend analysis across all systems',
            'sections': [
                {
                    'id': 'trend_overview',
                    'title': 'Trend Overview',
                    'type': 'summary',
                    'data_source': 'cross_system'
                },
                {
                    'id': 'trend_charts',
                    'title': 'Trend Analysis Charts',
                    'type': 'chart',
                    'data_source': 'cross_system',
                    'chart_type': 'line'
                }
            ]
        }
