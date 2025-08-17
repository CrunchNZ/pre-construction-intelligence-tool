"""
OpenWeatherMap API Client

This module provides a comprehensive client for integrating with the OpenWeatherMap API
to retrieve weather data for construction project locations and perform weather impact analysis.

Features:
- Current weather conditions
- 5-day weather forecasts
- Historical weather data
- Weather alerts and warnings
- Location-based weather queries
- Rate limiting and error handling

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import json

logger = logging.getLogger(__name__)


class OpenWeatherMapClient:
    """Client for OpenWeatherMap API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenWeatherMap client.
        
        Args:
            api_key: OpenWeatherMap API key. If not provided, uses settings.
        """
        self.api_key = api_key or getattr(settings, 'OPENWEATHERMAP_API_KEY', None)
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is required")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PreConstructionIntelligence/1.0'
        })
        
        # Rate limiting configuration
        self.rate_limit = {
            'calls_per_minute': 60,
            'calls_per_day': 1000,
            'last_call': None,
            'call_count': 0
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the OpenWeatherMap API with rate limiting.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            API response data
            
        Raises:
            requests.RequestException: If the request fails
        """
        # Check rate limiting
        self._check_rate_limit()
        
        # Add API key to params
        params['appid'] = self.api_key
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            # Update rate limiting
            self._update_rate_limit()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"OpenWeatherMap API request failed: {e}")
            raise
    
    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        now = timezone.now()
        
        # Reset daily count if it's a new day
        if (self.rate_limit['last_call'] and 
            now.date() > self.rate_limit['last_call'].date()):
            self.rate_limit['call_count'] = 0
        
        # Check daily limit
        if self.rate_limit['call_count'] >= self.rate_limit['calls_per_day']:
            raise Exception("Daily API call limit exceeded")
        
        # Check minute limit
        if (self.rate_limit['last_call'] and 
            (now - self.rate_limit['last_call']).seconds < 60):
            if self.rate_limit['call_count'] % 60 >= self.rate_limit['calls_per_minute']:
                raise Exception("Minute API call limit exceeded")
    
    def _update_rate_limit(self) -> None:
        """Update rate limiting counters."""
        self.rate_limit['last_call'] = timezone.now()
        self.rate_limit['call_count'] += 1
    
    def get_current_weather(self, location: str, units: str = 'metric') -> Dict[str, Any]:
        """
        Get current weather for a location.
        
        Args:
            location: City name, coordinates, or location identifier
            units: Units for temperature and measurements (metric, imperial, kelvin)
            
        Returns:
            Current weather data
        """
        cache_key = f"weather_current_{location}_{units}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"{self.base_url}/weather"
        params = {
            'q': location,
            'units': units,
            'lang': 'en'
        }
        
        data = self._make_request(endpoint, params)
        
        # Cache for 10 minutes
        cache.set(cache_key, data, 600)
        
        return data
    
    def get_weather_forecast(self, location: str, days: int = 5, units: str = 'metric') -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: City name, coordinates, or location identifier
            days: Number of days for forecast (1-5)
            units: Units for temperature and measurements
            
        Returns:
            Weather forecast data
        """
        cache_key = f"weather_forecast_{location}_{days}_{units}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"{self.base_url}/forecast"
        params = {
            'q': location,
            'units': units,
            'lang': 'en',
            'cnt': min(days * 8, 40)  # 8 forecasts per day, max 40
        }
        
        data = self._make_request(endpoint, params)
        
        # Cache for 1 hour
        cache.set(cache_key, data, 3600)
        
        return data
    
    def get_weather_alerts(self, location: str) -> List[Dict[str, Any]]:
        """
        Get weather alerts for a location.
        
        Args:
            location: City name, coordinates, or location identifier
            
        Returns:
            List of weather alerts
        """
        endpoint = f"{self.base_url}/onecall"
        params = {
            'q': location,
            'exclude': 'current,minutely,hourly,daily',
            'alerts': 1
        }
        
        try:
            data = self._make_request(endpoint, params)
            return data.get('alerts', [])
        except Exception as e:
            logger.warning(f"Could not retrieve weather alerts for {location}: {e}")
            return []
    
    def get_location_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a location name.
        
        Args:
            location: City name or location identifier
            
        Returns:
            Dictionary with lat and lon coordinates
        """
        cache_key = f"coordinates_{location}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"{self.geocoding_url}/direct"
        params = {
            'q': location,
            'limit': 1
        }
        
        try:
            data = self._make_request(endpoint, params)
            if data:
                coordinates = {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon']
                }
                # Cache coordinates for 24 hours
                cache.set(cache_key, coordinates, 86400)
                return coordinates
        except Exception as e:
            logger.warning(f"Could not get coordinates for {location}: {e}")
        
        return None
    
    def get_weather_impact_score(self, location: str, project_type: str = 'construction') -> Dict[str, Any]:
        """
        Calculate weather impact score for construction projects.
        
        Args:
            location: Project location
            project_type: Type of construction project
            
        Returns:
            Weather impact analysis with score and recommendations
        """
        try:
            current_weather = self.get_current_weather(location)
            forecast = self.get_weather_forecast(location, days=3)
            alerts = self.get_weather_alerts(location)
            
            # Calculate impact score based on weather conditions
            impact_score = self._calculate_impact_score(
                current_weather, forecast, alerts, project_type
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                current_weather, forecast, alerts, project_type
            )
            
            return {
                'location': location,
                'project_type': project_type,
                'impact_score': impact_score,
                'current_conditions': current_weather,
                'forecast_summary': self._summarize_forecast(forecast),
                'alerts': alerts,
                'recommendations': recommendations,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating weather impact for {location}: {e}")
            return {
                'location': location,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def _calculate_impact_score(self, current: Dict, forecast: Dict, 
                               alerts: List, project_type: str) -> float:
        """Calculate weather impact score (0-100, higher = more impact)."""
        score = 0.0
        
        # Current conditions impact
        if 'main' in current:
            temp = current['main'].get('temp', 20)
            humidity = current['main'].get('humidity', 50)
            pressure = current['main'].get('pressure', 1013)
            
            # Temperature impact
            if temp < 0 or temp > 35:
                score += 20
            elif temp < 5 or temp > 30:
                score += 10
            
            # Humidity impact
            if humidity > 80:
                score += 15
            elif humidity < 20:
                score += 5
            
            # Pressure impact (storm systems)
            if pressure < 1000:
                score += 25
        
        # Weather condition impact
        if 'weather' in current and current['weather']:
            weather_main = current['weather'][0]['main'].lower()
            if weather_main in ['rain', 'snow', 'storm']:
                score += 30
            elif weather_main in ['fog', 'mist']:
                score += 15
        
        # Wind impact
        if 'wind' in current:
            wind_speed = current['wind'].get('speed', 0)
            if wind_speed > 20:
                score += 25
            elif wind_speed > 10:
                score += 10
        
        # Forecast impact
        if 'list' in forecast:
            for item in forecast['list'][:8]:  # Next 24 hours
                if 'weather' in item and item['weather']:
                    weather_main = item['weather'][0]['main'].lower()
                    if weather_main in ['rain', 'snow', 'storm']:
                        score += 5
        
        # Alerts impact
        score += len(alerts) * 10
        
        # Project type adjustments
        if project_type == 'outdoor':
            score *= 1.2
        elif project_type == 'roofing':
            score *= 1.3
        elif project_type == 'underground':
            score *= 0.7
        
        return min(score, 100.0)
    
    def _generate_recommendations(self, current: Dict, forecast: Dict, 
                                 alerts: List, project_type: str) -> List[str]:
        """Generate weather-based recommendations for construction projects."""
        recommendations = []
        
        # Temperature recommendations
        if 'main' in current:
            temp = current['main'].get('temp', 20)
            if temp < 0:
                recommendations.append("Consider postponing outdoor concrete work due to freezing temperatures")
            elif temp > 35:
                recommendations.append("Implement heat stress prevention measures for workers")
        
        # Precipitation recommendations
        if 'weather' in current and current['weather']:
            weather_main = current['weather'][0]['main'].lower()
            if weather_main in ['rain', 'snow']:
                recommendations.append("Cover exposed materials and equipment")
                recommendations.append("Implement proper drainage measures")
        
        # Wind recommendations
        if 'wind' in current:
            wind_speed = current['wind'].get('speed', 0)
            if wind_speed > 20:
                recommendations.append("Secure loose materials and equipment")
                recommendations.append("Consider postponing crane operations")
        
        # Alert-based recommendations
        for alert in alerts:
            if 'event' in alert:
                event = alert['event'].lower()
                if 'storm' in event:
                    recommendations.append("Prepare for severe weather conditions")
                elif 'flood' in event:
                    recommendations.append("Implement flood protection measures")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Weather conditions are favorable for construction activities")
        
        return recommendations
    
    def _summarize_forecast(self, forecast: Dict) -> Dict[str, Any]:
        """Create a summary of the weather forecast."""
        if 'list' not in forecast:
            return {}
        
        summary = {
            'high_temp': float('-inf'),
            'low_temp': float('inf'),
            'precipitation_chance': 0,
            'windy_days': 0,
            'clear_days': 0
        }
        
        for item in forecast['list']:
            if 'main' in item:
                temp = item['main'].get('temp', 20)
                summary['high_temp'] = max(summary['high_temp'], temp)
                summary['low_temp'] = min(summary['low_temp'], temp)
            
            if 'weather' in item and item['weather']:
                weather_main = item['weather'][0]['main'].lower()
                if weather_main in ['rain', 'snow']:
                    summary['precipitation_chance'] += 1
                elif weather_main == 'clear':
                    summary['clear_days'] += 1
            
            if 'wind' in item:
                wind_speed = item['wind'].get('speed', 0)
                if wind_speed > 15:
                    summary['windy_days'] += 1
        
        # Convert to more reasonable values
        if summary['high_temp'] == float('-inf'):
            summary['high_temp'] = None
        if summary['low_temp'] == float('inf'):
            summary['low_temp'] = None
        
        summary['total_periods'] = len(forecast['list'])
        
        return summary
