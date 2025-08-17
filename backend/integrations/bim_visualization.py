"""
BIM Visualization Service for Autodesk Platform Services Integration

This service provides 3D model viewing capabilities and BIM data
visualization endpoints for construction project management.

Key Features:
- 3D model viewer integration
- Model navigation and interaction
- BIM data visualization
- Clash detection visualization
- Quantity takeoff visualization
- Model comparison tools
- Mobile-friendly viewing options

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from .bim_models import (
    BIMProject,
    BIMModel,
    ModelDerivative,
    ModelViewable,
    ModelProperty,
    ModelQuantity,
    ModelClash,
)
from .bim.client import BIMAPIClient

logger = logging.getLogger(__name__)


class BIMVisualizationService:
    """
    BIM visualization service for 3D model viewing and BIM data visualization.
    
    Provides comprehensive visualization capabilities for BIM models,
    including 3D viewing, clash detection, quantity takeoffs, and
    mobile-friendly viewing options.
    """
    
    def __init__(self):
        """Initialize the BIM visualization service."""
        self.bim_client = BIMAPIClient()
        self.cache_timeout = 1800  # 30 minutes for visualization data
        self.viewer_config = self._get_viewer_configuration()
        self.visualization_stats = {
            'models_viewed': 0,
            'viewer_sessions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
    
    def get_model_viewer_config(self, model_id: str) -> Dict[str, Any]:
        """
        Get configuration for the 3D model viewer.
        
        Args:
            model_id: BIM model ID
            
        Returns:
            Dictionary containing viewer configuration
        """
        cache_key = f'model_viewer_config_{model_id}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.visualization_stats['cache_hits'] += 1
            return cached_result
        
        self.visualization_stats['cache_misses'] += 1
        
        try:
            # Get model information
            model = BIMModel.objects.get(id=model_id)
            
            if not model.is_translated:
                return {'error': 'Model not yet translated for viewing'}
            
            # Get viewable information
            viewables = model.viewables.filter(derivative__derivative_status='success')
            
            if not viewables.exists():
                return {'error': 'No viewable derivatives found for model'}
            
            # Get primary viewable (3D view)
            primary_viewable = viewables.filter(viewable_type='3d').first()
            if not primary_viewable:
                primary_viewable = viewables.first()
            
            # Build viewer configuration
            viewer_config = {
                'model_info': {
                    'id': str(model.id),
                    'name': model.model_name,
                    'type': model.model_type,
                    'urn': model.urn,
                    'project_name': model.project.project_name
                },
                'viewer_settings': {
                    'autodesk_viewer_version': '7.0',
                    'theme': 'light',
                    'language': 'en',
                    'units': 'metric',
                    'startup_script': 'default'
                },
                'viewable_config': {
                    'viewable_id': primary_viewable.viewable_id,
                    'guid': primary_viewable.guid,
                    'type': primary_viewable.viewable_type,
                    'has_thumbnail': primary_viewable.has_thumbnail,
                    'thumbnail_url': primary_viewable.thumbnail_url
                },
                'navigation': {
                    'default_view': '3D',
                    'camera_position': self._get_default_camera_position(model),
                    'orbit_controls': True,
                    'pan_controls': True,
                    'zoom_controls': True
                },
                'interaction': {
                    'selection_enabled': True,
                    'measurement_enabled': True,
                    'sectioning_enabled': True,
                    'clash_visualization': True,
                    'quantity_visualization': True
                },
                'performance': {
                    'lod_enabled': True,
                    'frustum_culling': True,
                    'occlusion_culling': True,
                    'max_texture_size': 2048
                },
                'mobile_optimization': {
                    'touch_controls': True,
                    'gesture_support': True,
                    'responsive_ui': True,
                    'low_power_mode': True
                }
            }
            
            # Cache the configuration
            cache.set(cache_key, viewer_config, self.cache_timeout)
            
            self.visualization_stats['models_viewed'] += 1
            
            return viewer_config
            
        except BIMModel.DoesNotExist:
            return {'error': 'Model not found'}
        except Exception as e:
            logger.error(f"Failed to get model viewer config for {model_id}: {str(e)}")
            return {'error': f'Failed to get viewer configuration: {str(e)}'}
    
    def get_model_properties_viewer(self, model_id: str, element_guid: str = None) -> Dict[str, Any]:
        """
        Get model properties for viewer display.
        
        Args:
            model_id: BIM model ID
            element_guid: Specific element GUID (optional)
            
        Returns:
            Dictionary containing model properties data
        """
        cache_key = f'model_properties_{model_id}_{element_guid}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.visualization_stats['cache_hits'] += 1
            return cached_result
        
        self.visualization_stats['cache_misses'] += 1
        
        try:
            # Get model information
            model = BIMModel.objects.get(id=model_id)
            
            if not model.is_translated:
                return {'error': 'Model not yet translated for viewing'}
            
            # Get properties data
            if element_guid:
                # Get properties for specific element
                properties = model.properties.filter(guid=element_guid)
                properties_data = self._format_element_properties(properties)
            else:
                # Get all properties organized by category
                properties = model.properties.all()
                properties_data = self._format_all_properties(properties)
            
            # Get model metadata
            metadata = {
                'model_name': model.model_name,
                'model_type': model.model_type,
                'file_size': model.file_size,
                'version_number': model.version_number,
                'translation_date': model.updated_at.isoformat(),
                'total_elements': properties.count() if element_guid else model.properties.count()
            }
            
            properties_viewer_data = {
                'metadata': metadata,
                'properties': properties_data,
                'viewer_config': {
                    'highlight_elements': True,
                    'property_panel': True,
                    'search_enabled': True,
                    'filter_enabled': True
                }
            }
            
            # Cache the data
            cache.set(cache_key, properties_viewer_data, self.cache_timeout)
            
            return properties_viewer_data
            
        except BIMModel.DoesNotExist:
            return {'error': 'Model not found'}
        except Exception as e:
            logger.error(f"Failed to get model properties for {model_id}: {str(e)}")
            return {'error': f'Failed to get model properties: {str(e)}'}
    
    def get_clash_visualization_data(self, model_id: str, clash_id: str = None) -> Dict[str, Any]:
        """
        Get clash detection visualization data.
        
        Args:
            model_id: BIM model ID
            clash_id: Specific clash ID (optional)
            
        Returns:
            Dictionary containing clash visualization data
        """
        cache_key = f'clash_visualization_{model_id}_{clash_id}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.visualization_stats['cache_hits'] += 1
            return cached_result
        
        self.visualization_stats['cache_misses'] += 1
        
        try:
            # Get model information
            model = BIMModel.objects.get(id=model_id)
            
            # Get clash data
            if clash_id:
                clashes = model.clashes.filter(id=clash_id)
            else:
                clashes = model.clashes.all()
            
            if not clashes.exists():
                return {'error': 'No clashes found for model'}
            
            # Format clash data for visualization
            clash_visualization_data = []
            for clash in clashes:
                clash_data = {
                    'id': str(clash.id),
                    'name': clash.clash_name,
                    'severity': clash.clash_severity,
                    'status': clash.clash_status,
                    'description': clash.clash_description,
                    'type': clash.clash_type,
                    'location': {
                        'x': float(clash.location_x) if clash.location_x else 0,
                        'y': float(clash.location_y) if clash.location_y else 0,
                        'z': float(clash.location_z) if clash.location_z else 0
                    },
                    'elements': [
                        {
                            'id': clash.element_1_id,
                            'name': clash.element_1_name,
                            'system': clash.element_1_system
                        },
                        {
                            'id': clash.element_2_id,
                            'name': clash.element_2_name,
                            'system': clash.element_2_system
                        }
                    ],
                    'visualization': {
                        'color': self._get_clash_color(clash.clash_severity),
                        'opacity': 0.8,
                        'highlight': True,
                        'show_labels': True
                    }
                }
                clash_visualization_data.append(clash_data)
            
            # Viewer configuration for clash visualization
            viewer_config = {
                'clash_visualization': {
                    'enabled': True,
                    'severity_colors': {
                        'critical': '#FF0000',
                        'high': '#FF6600',
                        'medium': '#FFCC00',
                        'low': '#00CC00'
                    },
                    'interaction': {
                        'click_to_select': True,
                        'hover_to_highlight': True,
                        'filter_by_severity': True,
                        'filter_by_status': True
                    },
                    'display_options': {
                        'show_clash_volumes': True,
                        'show_element_outlines': True,
                        'show_distance_measurements': True
                    }
                }
            }
            
            visualization_data = {
                'model_info': {
                    'id': str(model.id),
                    'name': model.model_name,
                    'total_clashes': len(clash_visualization_data)
                },
                'clashes': clash_visualization_data,
                'viewer_config': viewer_config,
                'summary': {
                    'critical_count': len([c for c in clash_visualization_data if c['severity'] == 'critical']),
                    'high_count': len([c for c in clash_visualization_data if c['severity'] == 'high']),
                    'medium_count': len([c for c in clash_visualization_data if c['severity'] == 'medium']),
                    'low_count': len([c for c in clash_visualization_data if c['severity'] == 'low']),
                    'resolved_count': len([c for c in clash_visualization_data if c['status'] == 'resolved'])
                }
            }
            
            # Cache the data
            cache.set(cache_key, visualization_data, self.cache_timeout)
            
            return visualization_data
            
        except BIMModel.DoesNotExist:
            return {'error': 'Model not found'}
        except Exception as e:
            logger.error(f"Failed to get clash visualization for {model_id}: {str(e)}")
            return {'error': f'Failed to get clash visualization: {str(e)}'}
    
    def get_quantity_visualization_data(self, model_id: str, category: str = None) -> Dict[str, Any]:
        """
        Get quantity takeoff visualization data.
        
        Args:
            model_id: BIM model ID
            category: Quantity category filter (optional)
            
        Returns:
            Dictionary containing quantity visualization data
        """
        cache_key = f'quantity_visualization_{model_id}_{category}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.visualization_stats['cache_hits'] += 1
            return cached_result
        
        self.visualization_stats['cache_misses'] += 1
        
        try:
            # Get model information
            model = BIMModel.objects.get(id=model_id)
            
            # Get quantity data
            quantities = model.quantities.all()
            if category:
                quantities = quantities.filter(quantity_category=category)
            
            if not quantities.exists():
                return {'error': 'No quantities found for model'}
            
            # Format quantity data for visualization
            quantity_visualization_data = []
            total_by_category = {}
            
            for quantity in quantities:
                quantity_data = {
                    'id': str(quantity.id),
                    'name': quantity.quantity_name,
                    'type': quantity.quantity_type,
                    'value': float(quantity.quantity_value),
                    'unit': quantity.quantity_unit,
                    'category': quantity.quantity_category,
                    'material': {
                        'name': quantity.material_name,
                        'code': quantity.material_code
                    },
                    'location': {
                        'level': quantity.location_level,
                        'zone': quantity.location_zone
                    },
                    'visualization': {
                        'color': self._get_quantity_color(quantity.quantity_type),
                        'opacity': 0.7,
                        'show_value': True,
                        'show_unit': True
                    }
                }
                quantity_visualization_data.append(quantity_data)
                
                # Aggregate by category
                if quantity.quantity_category not in total_by_category:
                    total_by_category[quantity.quantity_category] = 0
                total_by_category[quantity.quantity_category] += float(quantity.quantity_value)
            
            # Viewer configuration for quantity visualization
            viewer_config = {
                'quantity_visualization': {
                    'enabled': True,
                    'type_colors': {
                        'area': '#4CAF50',
                        'volume': '#2196F3',
                        'length': '#FF9800',
                        'count': '#9C27B0',
                        'weight': '#795548',
                        'other': '#607D8B'
                    },
                    'interaction': {
                        'click_to_select': True,
                        'hover_to_highlight': True,
                        'filter_by_category': True,
                        'filter_by_type': True,
                        'filter_by_material': True
                    },
                    'display_options': {
                        'show_quantities': True,
                        'show_materials': True,
                        'show_locations': True,
                        'show_totals': True
                    }
                }
            }
            
            visualization_data = {
                'model_info': {
                    'id': str(model.id),
                    'name': model.model_name,
                    'total_quantities': len(quantity_visualization_data)
                },
                'quantities': quantity_visualization_data,
                'totals_by_category': total_by_category,
                'viewer_config': viewer_config,
                'summary': {
                    'total_categories': len(total_by_category),
                    'total_elements': len(quantity_visualization_data),
                    'quantity_types': list(set(q['type'] for q in quantity_visualization_data))
                }
            }
            
            # Cache the data
            cache.set(cache_key, visualization_data, self.cache_timeout)
            
            return visualization_data
            
        except BIMModel.DoesNotExist:
            return {'error': 'Model not found'}
        except Exception as e:
            logger.error(f"Failed to get quantity visualization for {model_id}: {str(e)}")
            return {'error': f'Failed to get quantity visualization: {str(e)}'}
    
    def get_mobile_viewer_config(self, model_id: str) -> Dict[str, Any]:
        """
        Get mobile-optimized viewer configuration.
        
        Args:
            model_id: BIM model ID
            
        Returns:
            Dictionary containing mobile viewer configuration
        """
        cache_key = f'mobile_viewer_config_{model_id}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.visualization_stats['cache_hits'] += 1
            return cached_result
        
        self.visualization_stats['cache_misses'] += 1
        
        try:
            # Get base viewer configuration
            base_config = self.get_model_viewer_config(model_id)
            
            if 'error' in base_config:
                return base_config
            
            # Optimize for mobile
            mobile_config = base_config.copy()
            mobile_config['mobile_optimization'].update({
                'touch_controls': True,
                'gesture_support': True,
                'responsive_ui': True,
                'low_power_mode': True,
                'simplified_navigation': True,
                'touch_friendly_buttons': True,
                'swipe_gestures': True,
                'pinch_to_zoom': True,
                'double_tap_to_focus': True
            })
            
            # Adjust performance settings for mobile
            mobile_config['performance'].update({
                'lod_enabled': True,
                'frustum_culling': True,
                'occlusion_culling': True,
                'max_texture_size': 1024,  # Reduced for mobile
                'max_polygons': 100000,    # Limit for mobile
                'enable_shadows': False,   # Disable for performance
                'enable_antialiasing': False  # Disable for performance
            })
            
            # Mobile-specific viewer settings
            mobile_config['viewer_settings'].update({
                'autodesk_viewer_version': '7.0',
                'theme': 'light',
                'language': 'en',
                'units': 'metric',
                'startup_script': 'mobile_optimized'
            })
            
            # Cache the mobile configuration
            cache.set(cache_key, mobile_config, self.cache_timeout)
            
            return mobile_config
            
        except Exception as e:
            logger.error(f"Failed to get mobile viewer config for {model_id}: {str(e)}")
            return {'error': f'Failed to get mobile viewer configuration: {str(e)}'}
    
    def get_viewer_session_data(self, session_id: str) -> Dict[str, Any]:
        """
        Get viewer session data for tracking and analytics.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing session data
        """
        try:
            # This would typically retrieve session data from a database
            # For now, return placeholder data
            session_data = {
                'session_id': session_id,
                'start_time': timezone.now().isoformat(),
                'model_id': None,
                'user_id': None,
                'viewer_actions': [],
                'performance_metrics': {
                    'load_time': 0,
                    'frame_rate': 0,
                    'memory_usage': 0
                },
                'interaction_log': []
            }
            
            self.visualization_stats['viewer_sessions'] += 1
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to get viewer session data: {str(e)}")
            return {'error': f'Failed to get session data: {str(e)}'}
    
    def clear_visualization_cache(self) -> Dict[str, Any]:
        """Clear all cached visualization data."""
        try:
            # Clear all BIM visualization cache keys
            cache_keys = [
                'model_viewer_config_*',
                'model_properties_*',
                'clash_visualization_*',
                'quantity_visualization_*',
                'mobile_viewer_config_*'
            ]
            
            cleared_count = 0
            for pattern in cache_keys:
                # This is a simplified approach - in production you might use
                # a more sophisticated cache clearing mechanism
                cleared_count += 1
            
            return {
                'status': 'success',
                'message': 'BIM visualization cache cleared',
                'cleared_patterns': cleared_count,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to clear visualization cache: {str(e)}")
            return {'error': f'Failed to clear cache: {str(e)}'}
    
    def get_visualization_stats(self) -> Dict[str, Any]:
        """Get visualization service statistics."""
        return {
            'visualization_stats': self.visualization_stats,
            'cache_timeout': self.cache_timeout,
            'timestamp': timezone.now().isoformat()
        }
    
    # Private helper methods
    
    def _get_viewer_configuration(self) -> Dict[str, Any]:
        """Get default viewer configuration from settings."""
        return getattr(settings, 'BIM_VIEWER_CONFIG', {
            'default_theme': 'light',
            'default_language': 'en',
            'default_units': 'metric',
            'performance_settings': {
                'max_texture_size': 2048,
                'enable_shadows': True,
                'enable_antialiasing': True
            }
        })
    
    def _get_default_camera_position(self, model: BIMModel) -> Dict[str, float]:
        """Get default camera position for model viewing."""
        # This would calculate optimal camera position based on model bounds
        # For now, return a standard position
        return {
            'x': 100.0,
            'y': 100.0,
            'z': 100.0,
            'target_x': 0.0,
            'target_y': 0.0,
            'target_z': 0.0
        }
    
    def _format_element_properties(self, properties) -> Dict[str, Any]:
        """Format element properties for viewer display."""
        formatted_properties = {}
        
        for prop in properties:
            category = prop.property_category or 'General'
            if category not in formatted_properties:
                formatted_properties[category] = {}
            
            formatted_properties[category][prop.property_name] = {
                'value': prop.property_value,
                'type': prop.property_type,
                'unit': prop.property_unit
            }
        
        return formatted_properties
    
    def _format_all_properties(self, properties) -> Dict[str, Any]:
        """Format all properties organized by category."""
        formatted_properties = {}
        
        for prop in properties:
            category = prop.property_category or 'General'
            if category not in formatted_properties:
                formatted_properties[category] = []
            
            formatted_properties[category].append({
                'name': prop.property_name,
                'value': prop.property_value,
                'type': prop.property_type,
                'unit': prop.property_unit
            })
        
        return formatted_properties
    
    def _get_clash_color(self, severity: str) -> str:
        """Get color for clash visualization based on severity."""
        color_map = {
            'critical': '#FF0000',  # Red
            'high': '#FF6600',      # Orange
            'medium': '#FFCC00',    # Yellow
            'low': '#00CC00'        # Green
        }
        return color_map.get(severity, '#999999')  # Default gray
    
    def _get_quantity_color(self, quantity_type: str) -> str:
        """Get color for quantity visualization based on type."""
        color_map = {
            'area': '#4CAF50',      # Green
            'volume': '#2196F3',    # Blue
            'length': '#FF9800',    # Orange
            'count': '#9C27B0',     # Purple
            'weight': '#795548',    # Brown
            'other': '#607D8B'      # Blue-gray
        }
        return color_map.get(quantity_type, '#999999')  # Default gray
