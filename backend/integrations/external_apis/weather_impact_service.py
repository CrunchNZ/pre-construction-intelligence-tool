"""
Weather Impact Analysis Service

This service analyzes weather data and provides insights on how weather conditions
affect construction project planning, scheduling, and risk assessment.

Features:
- Weather impact scoring for different project types
- Historical weather pattern analysis
- Project scheduling recommendations
- Risk assessment based on weather conditions
- Automated weather monitoring and alerts

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from .weather_client import OpenWeatherMapClient

logger = logging.getLogger(__name__)


class WeatherImpactService:
    """Service for analyzing weather impact on construction projects."""
    
    def __init__(self):
        """Initialize the weather impact service."""
        self.weather_client = OpenWeatherMapClient()
        
        # Project type weather sensitivity mapping
        self.project_sensitivity = {
            'excavation': {
                'rain': 'high',
                'wind': 'medium',
                'temperature': 'medium',
                'humidity': 'low'
            },
            'concrete': {
                'rain': 'high',
                'wind': 'medium',
                'temperature': 'high',
                'humidity': 'medium'
            },
            'roofing': {
                'rain': 'high',
                'wind': 'high',
                'temperature': 'medium',
                'humidity': 'low'
            },
            'electrical': {
                'rain': 'high',
                'wind': 'low',
                'temperature': 'low',
                'humidity': 'medium'
            },
            'plumbing': {
                'rain': 'medium',
                'wind': 'low',
                'temperature': 'medium',
                'humidity': 'low'
            },
            'steel_erection': {
                'rain': 'medium',
                'wind': 'high',
                'temperature': 'low',
                'humidity': 'low'
            },
            'interior_finishing': {
                'rain': 'low',
                'wind': 'low',
                'temperature': 'medium',
                'humidity': 'medium'
            }
        }
    
    def analyze_project_weather_risk(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze weather risk for a specific construction project.
        
        Args:
            project_data: Project information including location, type, and schedule
            
        Returns:
            Comprehensive weather risk analysis
        """
        try:
            location = project_data.get('location')
            project_type = project_data.get('project_type', 'construction')
            start_date = project_data.get('start_date')
            duration_days = project_data.get('duration_days', 30)
            
            if not location:
                raise ValueError("Project location is required")
            
            # Get weather data and impact analysis
            weather_impact = self.weather_client.get_weather_impact_score(
                location, project_type
            )
            
            # Calculate project-specific risk factors
            risk_factors = self._calculate_project_risk_factors(
                project_data, weather_impact
            )
            
            # Generate scheduling recommendations
            scheduling_recommendations = self._generate_scheduling_recommendations(
                project_data, weather_impact
            )
            
            # Calculate cost impact
            cost_impact = self._calculate_cost_impact(
                project_data, weather_impact, risk_factors
            )
            
            return {
                'project_id': project_data.get('project_id'),
                'location': location,
                'project_type': project_type,
                'analysis_date': timezone.now().isoformat(),
                'weather_impact': weather_impact,
                'risk_factors': risk_factors,
                'scheduling_recommendations': scheduling_recommendations,
                'cost_impact': cost_impact,
                'overall_risk_score': self._calculate_overall_risk_score(
                    weather_impact, risk_factors, cost_impact
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing project weather risk: {e}")
            return {
                'error': str(e),
                'analysis_date': timezone.now().isoformat()
            }
    
    def analyze_portfolio_weather_risk(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze weather risk across multiple projects in a portfolio.
        
        Args:
            projects: List of project data dictionaries
            
        Returns:
            Portfolio-level weather risk analysis
        """
        try:
            portfolio_analysis = {
                'total_projects': len(projects),
                'analysis_date': timezone.now().isoformat(),
                'projects': [],
                'portfolio_risk_summary': {},
                'high_risk_projects': [],
                'weather_trends': {},
                'recommendations': []
            }
            
            total_risk_score = 0
            high_risk_count = 0
            
            for project in projects:
                project_analysis = self.analyze_project_weather_risk(project)
                portfolio_analysis['projects'].append(project_analysis)
                
                if 'overall_risk_score' in project_analysis:
                    risk_score = project_analysis['overall_risk_score']
                    total_risk_score += risk_score
                    
                    if risk_score > 70:
                        high_risk_count += 1
                        portfolio_analysis['high_risk_projects'].append({
                            'project_id': project.get('project_id'),
                            'location': project.get('location'),
                            'risk_score': risk_score,
                            'primary_concerns': self._identify_primary_concerns(project_analysis)
                        })
            
            # Calculate portfolio averages
            if portfolio_analysis['projects']:
                avg_risk_score = total_risk_score / len(portfolio_analysis['projects'])
                portfolio_analysis['portfolio_risk_summary'] = {
                    'average_risk_score': round(avg_risk_score, 2),
                    'high_risk_percentage': round((high_risk_count / len(projects)) * 100, 2),
                    'total_risk_score': total_risk_score
                }
            
            # Analyze weather trends across locations
            portfolio_analysis['weather_trends'] = self._analyze_portfolio_weather_trends(
                portfolio_analysis['projects']
            )
            
            # Generate portfolio-level recommendations
            portfolio_analysis['recommendations'] = self._generate_portfolio_recommendations(
                portfolio_analysis
            )
            
            return portfolio_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio weather risk: {e}")
            return {
                'error': str(e),
                'analysis_date': timezone.now().isoformat()
            }
    
    def get_weather_forecast_for_scheduling(self, location: str, 
                                          start_date: datetime, 
                                          duration_days: int) -> Dict[str, Any]:
        """
        Get weather forecast optimized for project scheduling.
        
        Args:
            location: Project location
            start_date: Project start date
            duration_days: Project duration in days
            
        Returns:
            Scheduling-optimized weather forecast
        """
        try:
            # Get extended forecast
            forecast = self.weather_client.get_weather_forecast(location, days=min(duration_days + 7, 5))
            
            # Analyze forecast for scheduling optimization
            scheduling_analysis = self._analyze_forecast_for_scheduling(
                forecast, start_date, duration_days
            )
            
            return {
                'location': location,
                'start_date': start_date.isoformat(),
                'duration_days': duration_days,
                'forecast': forecast,
                'scheduling_analysis': scheduling_analysis,
                'optimal_start_date': scheduling_analysis.get('optimal_start_date'),
                'weather_constraints': scheduling_analysis.get('weather_constraints'),
                'recommendations': scheduling_analysis.get('recommendations')
            }
            
        except Exception as e:
            logger.error(f"Error getting weather forecast for scheduling: {e}")
            return {
                'error': str(e),
                'location': location
            }
    
    def create_weather_monitoring_alert(self, project_data: Dict[str, Any], 
                                       alert_thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a weather monitoring alert for a project.
        
        Args:
            project_data: Project information
            alert_thresholds: Weather conditions that trigger alerts
            
        Returns:
            Alert configuration and monitoring setup
        """
        try:
            location = project_data.get('location')
            project_id = project_data.get('project_id')
            
            alert_config = {
                'project_id': project_id,
                'location': location,
                'alert_thresholds': alert_thresholds,
                'created_date': timezone.now().isoformat(),
                'status': 'active',
                'monitoring_schedule': 'hourly',
                'notification_channels': ['email', 'sms', 'dashboard'],
                'escalation_rules': self._generate_escalation_rules(alert_thresholds)
            }
            
            # Store alert configuration (in production, this would go to database)
            cache_key = f"weather_alert_{project_id}"
            cache.set(cache_key, alert_config, 86400)  # 24 hours
            
            return {
                'alert_id': f"weather_alert_{project_id}_{int(timezone.now().timestamp())}",
                'config': alert_config,
                'status': 'created'
            }
            
        except Exception as e:
            logger.error(f"Error creating weather monitoring alert: {e}")
            return {
                'error': str(e)
            }
    
    def _calculate_project_risk_factors(self, project_data: Dict[str, Any], 
                                       weather_impact: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate project-specific weather risk factors."""
        risk_factors = {
            'schedule_impact': 0,
            'cost_impact': 0,
            'safety_risk': 0,
            'quality_risk': 0,
            'resource_availability': 0
        }
        
        project_type = project_data.get('project_type', 'construction')
        sensitivity = self.project_sensitivity.get(project_type, {})
        
        # Calculate schedule impact
        weather_score = weather_impact.get('impact_score', 0)
        if weather_score > 70:
            risk_factors['schedule_impact'] = 3  # High
        elif weather_score > 40:
            risk_factors['schedule_impact'] = 2  # Medium
        else:
            risk_factors['schedule_impact'] = 1  # Low
        
        # Calculate safety risk based on weather conditions
        current_weather = weather_impact.get('current_conditions', {})
        if 'weather' in current_weather and current_weather['weather']:
            weather_main = current_weather['weather'][0]['main'].lower()
            if weather_main in ['storm', 'snow', 'rain']:
                risk_factors['safety_risk'] = 3
            elif weather_main in ['fog', 'wind']:
                risk_factors['safety_risk'] = 2
            else:
                risk_factors['safety_risk'] = 1
        
        # Calculate quality risk
        if 'main' in current_weather:
            temp = current_weather['main'].get('temp', 20)
            humidity = current_weather['main'].get('humidity', 50)
            
            if temp < 0 or temp > 35:
                risk_factors['quality_risk'] = 3
            elif temp < 5 or temp > 30:
                risk_factors['quality_risk'] = 2
            else:
                risk_factors['quality_risk'] = 1
            
            if humidity > 80:
                risk_factors['quality_risk'] = max(risk_factors['quality_risk'], 2)
        
        # Calculate resource availability
        alerts = weather_impact.get('alerts', [])
        risk_factors['resource_availability'] = min(len(alerts) + 1, 3)
        
        return risk_factors
    
    def _generate_scheduling_recommendations(self, project_data: Dict[str, Any], 
                                           weather_impact: Dict[str, Any]) -> List[str]:
        """Generate weather-based scheduling recommendations."""
        recommendations = []
        
        project_type = project_data.get('project_type', 'construction')
        weather_score = weather_impact.get('impact_score', 0)
        
        # High-level scheduling recommendations
        if weather_score > 70:
            recommendations.append("Consider postponing project start date due to adverse weather conditions")
            recommendations.append("Implement contingency plans for weather-related delays")
        elif weather_score > 40:
            recommendations.append("Monitor weather forecasts closely and prepare for potential delays")
            recommendations.append("Schedule weather-sensitive activities during favorable conditions")
        
        # Project type specific recommendations
        if project_type == 'concrete':
            if weather_score > 50:
                recommendations.append("Schedule concrete work during moderate temperature periods")
                recommendations.append("Ensure proper curing conditions are maintained")
        
        elif project_type == 'roofing':
            if weather_score > 40:
                recommendations.append("Avoid roofing work during high wind or precipitation")
                recommendations.append("Implement wind protection measures")
        
        elif project_type == 'excavation':
            if weather_score > 60:
                recommendations.append("Monitor soil conditions and drainage during wet weather")
                recommendations.append("Implement erosion control measures")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Weather conditions are favorable for project execution")
        
        return recommendations
    
    def _calculate_cost_impact(self, project_data: Dict[str, Any], 
                              weather_impact: Dict[str, Any], 
                              risk_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential cost impact of weather conditions."""
        base_cost = project_data.get('estimated_cost', 100000)
        weather_score = weather_impact.get('impact_score', 0)
        
        # Calculate cost multipliers based on risk factors
        schedule_multiplier = 1.0 + (risk_factors.get('schedule_impact', 1) * 0.1)
        safety_multiplier = 1.0 + (risk_factors.get('safety_risk', 1) * 0.05)
        quality_multiplier = 1.0 + (risk_factors.get('quality_risk', 1) * 0.08)
        
        # Calculate additional costs
        additional_costs = {
            'weather_protection': weather_score * 100,  # $100 per impact point
            'safety_equipment': risk_factors.get('safety_risk', 1) * 5000,
            'quality_control': risk_factors.get('quality_risk', 1) * 3000,
            'contingency': base_cost * 0.05 * (weather_score / 100)
        }
        
        total_additional_cost = sum(additional_costs.values())
        adjusted_total_cost = base_cost * schedule_multiplier * safety_multiplier * quality_multiplier
        
        return {
            'base_cost': base_cost,
            'additional_costs': additional_costs,
            'total_additional_cost': total_additional_cost,
            'adjusted_total_cost': adjusted_total_cost,
            'cost_increase_percentage': round(((adjusted_total_cost - base_cost) / base_cost) * 100, 2)
        }
    
    def _calculate_overall_risk_score(self, weather_impact: Dict[str, Any], 
                                     risk_factors: Dict[str, Any], 
                                     cost_impact: Dict[str, Any]) -> float:
        """Calculate overall project risk score (0-100)."""
        weather_score = weather_impact.get('impact_score', 0)
        
        # Weighted risk calculation
        risk_score = (
            weather_score * 0.4 +  # Weather impact: 40%
            sum(risk_factors.values()) * 5 +  # Risk factors: 30%
            (cost_impact.get('cost_increase_percentage', 0) * 0.3)  # Cost impact: 30%
        )
        
        return min(risk_score, 100.0)
    
    def _identify_primary_concerns(self, project_analysis: Dict[str, Any]) -> List[str]:
        """Identify primary weather concerns for a project."""
        concerns = []
        weather_impact = project_analysis.get('weather_impact', {})
        
        if 'current_conditions' in weather_impact:
            current = weather_impact['current_conditions']
            if 'weather' in current and current['weather']:
                weather_main = current['weather'][0]['main'].lower()
                if weather_main in ['rain', 'snow', 'storm']:
                    concerns.append(f"Active {weather_main} conditions")
            
            if 'main' in current:
                temp = current['main'].get('temp', 20)
                if temp < 0:
                    concerns.append("Freezing temperatures")
                elif temp > 35:
                    concerns.append("Extreme heat")
        
        alerts = weather_impact.get('alerts', [])
        if alerts:
            concerns.append(f"{len(alerts)} active weather alerts")
        
        return concerns
    
    def _analyze_portfolio_weather_trends(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weather trends across project portfolio."""
        trends = {
            'high_risk_locations': [],
            'weather_patterns': {},
            'seasonal_impacts': {}
        }
        
        # Analyze locations with high risk
        location_risk = {}
        for project in projects:
            location = project.get('location')
            risk_score = project.get('overall_risk_score', 0)
            
            if location not in location_risk:
                location_risk[location] = []
            location_risk[location].append(risk_score)
        
        # Calculate average risk by location
        for location, scores in location_risk.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > 60:
                trends['high_risk_locations'].append({
                    'location': location,
                    'average_risk': round(avg_score, 2),
                    'project_count': len(scores)
                })
        
        return trends
    
    def _generate_portfolio_recommendations(self, portfolio_analysis: Dict[str, Any]) -> List[str]:
        """Generate portfolio-level weather risk recommendations."""
        recommendations = []
        
        high_risk_percentage = portfolio_analysis.get('portfolio_risk_summary', {}).get('high_risk_percentage', 0)
        
        if high_risk_percentage > 30:
            recommendations.append("Implement portfolio-wide weather risk management strategy")
            recommendations.append("Consider diversifying project locations to reduce weather concentration risk")
        
        if portfolio_analysis.get('high_risk_projects'):
            recommendations.append("Prioritize high-risk projects for weather monitoring and contingency planning")
            recommendations.append("Review and update weather risk mitigation strategies for high-risk locations")
        
        # Location-specific recommendations
        high_risk_locations = portfolio_analysis.get('weather_trends', {}).get('high_risk_locations', [])
        if high_risk_locations:
            recommendations.append("Develop location-specific weather response plans for high-risk areas")
        
        if not recommendations:
            recommendations.append("Portfolio weather risk is within acceptable limits")
        
        return recommendations
    
    def _analyze_forecast_for_scheduling(self, forecast: Dict[str, Any], 
                                        start_date: datetime, 
                                        duration_days: int) -> Dict[str, Any]:
        """Analyze weather forecast for optimal project scheduling."""
        analysis = {
            'optimal_start_date': start_date,
            'weather_constraints': [],
            'recommendations': []
        }
        
        if 'list' not in forecast:
            return analysis
        
        # Find optimal start date within next 7 days
        best_start_date = start_date
        best_weather_score = 100
        
        for days_offset in range(7):
            candidate_date = start_date + timedelta(days=days_offset)
            weather_score = self._calculate_date_weather_score(forecast, candidate_date, duration_days)
            
            if weather_score < best_weather_score:
                best_weather_score = weather_score
                best_start_date = candidate_date
        
        analysis['optimal_start_date'] = best_start_date
        analysis['weather_constraints'] = self._identify_scheduling_constraints(forecast, start_date, duration_days)
        analysis['recommendations'] = self._generate_scheduling_recommendations_from_forecast(forecast, start_date, duration_days)
        
        return analysis
    
    def _calculate_date_weather_score(self, forecast: Dict[str, Any], 
                                     start_date: datetime, 
                                     duration_days: int) -> float:
        """Calculate weather score for a specific start date."""
        if 'list' not in forecast:
            return 100
        
        score = 0
        start_timestamp = start_date.timestamp()
        
        for item in forecast['list']:
            item_timestamp = item.get('dt', 0)
            if start_timestamp <= item_timestamp <= start_timestamp + (duration_days * 86400):
                # Add weather impact for this period
                if 'weather' in item and item['weather']:
                    weather_main = item['weather'][0]['main'].lower()
                    if weather_main in ['rain', 'snow', 'storm']:
                        score += 10
                    elif weather_main in ['fog', 'mist']:
                        score += 5
                
                if 'main' in item:
                    temp = item['main'].get('temp', 20)
                    if temp < 0 or temp > 35:
                        score += 15
                    elif temp < 5 or temp > 30:
                        score += 8
        
        return score
    
    def _identify_scheduling_constraints(self, forecast: Dict[str, Any], 
                                        start_date: datetime, 
                                        duration_days: int) -> List[str]:
        """Identify weather constraints for project scheduling."""
        constraints = []
        
        if 'list' not in forecast:
            return constraints
        
        start_timestamp = start_date.timestamp()
        
        for item in forecast['list']:
            item_timestamp = item.get('dt', 0)
            if start_timestamp <= item_timestamp <= start_timestamp + (duration_days * 86400):
                if 'weather' in item and item['weather']:
                    weather_main = item['weather'][0]['main'].lower()
                    if weather_main in ['storm']:
                        constraints.append("Severe weather conditions")
                    elif weather_main in ['rain', 'snow']:
                        constraints.append("Precipitation expected")
        
        return list(set(constraints))  # Remove duplicates
    
    def _generate_scheduling_recommendations_from_forecast(self, forecast: Dict[str, Any], 
                                                         start_date: datetime, 
                                                         duration_days: int) -> List[str]:
        """Generate scheduling recommendations based on forecast analysis."""
        recommendations = []
        
        if 'list' not in forecast:
            return ["Insufficient forecast data for scheduling recommendations"]
        
        # Analyze forecast patterns
        precipitation_days = 0
        high_wind_days = 0
        
        start_timestamp = start_date.timestamp()
        
        for item in forecast['list']:
            item_timestamp = item.get('dt', 0)
            if start_timestamp <= item_timestamp <= start_timestamp + (duration_days * 86400):
                if 'weather' in item and item['weather']:
                    weather_main = item['weather'][0]['main'].lower()
                    if weather_main in ['rain', 'snow']:
                        precipitation_days += 1
                
                if 'wind' in item:
                    wind_speed = item['wind'].get('speed', 0)
                    if wind_speed > 15:
                        high_wind_days += 1
        
        if precipitation_days > duration_days * 0.3:
            recommendations.append("High precipitation expected - consider weather protection measures")
        
        if high_wind_days > duration_days * 0.2:
            recommendations.append("Multiple high-wind days expected - secure materials and equipment")
        
        if not recommendations:
            recommendations.append("Weather conditions appear favorable for project execution")
        
        return recommendations
    
    def _generate_escalation_rules(self, alert_thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate escalation rules for weather alerts."""
        escalation_rules = [
            {
                'level': 1,
                'condition': 'weather_score > 50',
                'action': 'Send email notification to project manager',
                'timeout': '1 hour'
            },
            {
                'level': 2,
                'condition': 'weather_score > 70',
                'action': 'Send SMS to project manager and site supervisor',
                'timeout': '30 minutes'
            },
            {
                'level': 3,
                'condition': 'weather_score > 85',
                'action': 'Send emergency notification to all project stakeholders',
                'timeout': '15 minutes'
            }
        ]
        
        return escalation_rules
