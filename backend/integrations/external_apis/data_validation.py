"""
Data Validation and Cleaning Service

This service provides comprehensive data validation, cleaning, and quality assurance
for external API data and integrated system data.

Features:
- Data type validation and conversion
- Data quality scoring and assessment
- Automated data cleaning and normalization
- Outlier detection and handling
- Data consistency validation
- Schema validation and enforcement

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

logger = logging.getLogger(__name__)


class DataValidator:
    """Data validation and cleaning service."""
    
    def __init__(self):
        """Initialize the data validator."""
        # Common validation patterns
        self.patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?1?\d{9,15}$',
            'postal_code': r'^\d{5}(-\d{4})?$',
            'currency': r'^\$?\d+(?:,\d{3})*(?:\.\d{2})?$',
            'percentage': r'^\d+(?:\.\d+)?%?$',
            'date_iso': r'^\d{4}-\d{2}-\d{2}$',
            'datetime_iso': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
        }
        
        # Data type mappings
        self.type_mappings = {
            'string': str,
            'integer': int,
            'float': float,
            'decimal': Decimal,
            'boolean': bool,
            'date': date,
            'datetime': datetime,
            'json': dict
        }
    
    def validate_data(self, data: Any, schema: Dict[str, Any]) -> Tuple[bool, List[str], Any]:
        """
        Validate data against a schema and return validation results.
        
        Args:
            data: Data to validate
            schema: Validation schema definition
            
        Returns:
            Tuple of (is_valid, errors, cleaned_data)
        """
        errors = []
        cleaned_data = {}
        
        try:
            if not isinstance(schema, dict):
                raise ValueError("Schema must be a dictionary")
            
            # Validate required fields
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    errors.append(f"Required field '{field}' is missing")
            
            # Validate each field
            for field_name, field_schema in schema.get('properties', {}).items():
                if field_name in data:
                    field_value = data[field_name]
                    field_errors, cleaned_value = self._validate_field(
                        field_name, field_value, field_schema
                    )
                    errors.extend(field_errors)
                    cleaned_data[field_name] = cleaned_value
                elif field_name in required_fields:
                    cleaned_data[field_name] = None
            
            # Apply schema-level validations
            schema_errors = self._validate_schema_level(data, schema)
            errors.extend(schema_errors)
            
            is_valid = len(errors) == 0
            
            return is_valid, errors, cleaned_data
            
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            errors.append(f"Validation system error: {str(e)}")
            return False, errors, {}
    
    def _validate_field(self, field_name: str, value: Any, 
                       field_schema: Dict[str, Any]) -> Tuple[List[str], Any]:
        """Validate a single field according to its schema."""
        errors = []
        cleaned_value = value
        
        try:
            # Type validation
            if 'type' in field_schema:
                type_errors, cleaned_value = self._validate_type(
                    field_name, value, field_schema['type']
                )
                errors.extend(type_errors)
            
            # Pattern validation
            if 'pattern' in field_schema and cleaned_value:
                if not re.match(field_schema['pattern'], str(cleaned_value)):
                    errors.append(f"Field '{field_name}' does not match required pattern")
            
            # Enum validation
            if 'enum' in field_schema and cleaned_value is not None:
                if cleaned_value not in field_schema['enum']:
                    errors.append(f"Field '{field_name}' value '{cleaned_value}' is not in allowed values: {field_schema['enum']}")
            
            # Range validation
            if 'minimum' in field_schema and cleaned_value is not None:
                if cleaned_value < field_schema['minimum']:
                    errors.append(f"Field '{field_name}' value {cleaned_value} is below minimum {field_schema['minimum']}")
            
            if 'maximum' in field_schema and cleaned_value is not None:
                if cleaned_value > field_schema['maximum']:
                    errors.append(f"Field '{field_name}' value {cleaned_value} is above maximum {field_schema['maximum']}")
            
            # Length validation
            if 'minLength' in field_schema and cleaned_value:
                if len(str(cleaned_value)) < field_schema['minLength']:
                    errors.append(f"Field '{field_name}' length {len(str(cleaned_value))} is below minimum {field_schema['minLength']}")
            
            if 'maxLength' in field_schema and cleaned_value:
                if len(str(cleaned_value)) > field_schema['maxLength']:
                    errors.append(f"Field '{field_name}' length {len(str(cleaned_value))} is above maximum {field_schema['maxLength']}")
            
            # Custom validation
            if 'custom_validation' in field_schema:
                custom_errors = field_schema['custom_validation'](field_name, cleaned_value)
                if custom_errors:
                    errors.extend(custom_errors)
            
            return errors, cleaned_value
            
        except Exception as e:
            logger.error(f"Field validation error for {field_name}: {e}")
            errors.append(f"Field '{field_name}' validation error: {str(e)}")
            return errors, value
    
    def _validate_type(self, field_name: str, value: Any, 
                      expected_type: str) -> Tuple[List[str], Any]:
        """Validate and convert data type."""
        errors = []
        cleaned_value = value
        
        try:
            if expected_type not in self.type_mappings:
                errors.append(f"Unknown type '{expected_type}' for field '{field_name}'")
                return errors, value
            
            target_type = self.type_mappings[expected_type]
            
            # Handle None values
            if value is None:
                return errors, None
            
            # Type conversion
            if expected_type == 'string':
                cleaned_value = str(value)
            elif expected_type == 'integer':
                cleaned_value = int(float(value))  # Handle decimal strings
            elif expected_type == 'float':
                cleaned_value = float(value)
            elif expected_type == 'decimal':
                cleaned_value = Decimal(str(value))
            elif expected_type == 'boolean':
                if isinstance(value, str):
                    cleaned_value = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    cleaned_value = bool(value)
            elif expected_type == 'date':
                if isinstance(value, str):
                    cleaned_value = datetime.strptime(value, '%Y-%m-%d').date()
                elif isinstance(value, datetime):
                    cleaned_value = value.date()
                else:
                    cleaned_value = value
            elif expected_type == 'datetime':
                if isinstance(value, str):
                    cleaned_value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    cleaned_value = value
            elif expected_type == 'json':
                if isinstance(value, str):
                    cleaned_value = json.loads(value)
                else:
                    cleaned_value = value
            
            # Verify conversion was successful
            if not isinstance(cleaned_value, target_type):
                errors.append(f"Field '{field_name}' could not be converted to {expected_type}")
                return errors, value
            
            return errors, cleaned_value
            
        except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError) as e:
            errors.append(f"Field '{field_name}' type conversion error: {str(e)}")
            return errors, value
    
    def _validate_schema_level(self, data: Any, schema: Dict[str, Any]) -> List[str]:
        """Apply schema-level validations."""
        errors = []
        
        try:
            # Additional properties validation
            if schema.get('additionalProperties') is False:
                allowed_properties = set(schema.get('properties', {}).keys())
                data_properties = set(data.keys()) if isinstance(data, dict) else set()
                extra_properties = data_properties - allowed_properties
                if extra_properties:
                    errors.append(f"Additional properties not allowed: {extra_properties}")
            
            # Dependencies validation
            if 'dependencies' in schema:
                for field, dependency in schema['dependencies'].items():
                    if field in data:
                        if isinstance(dependency, list):
                            # Required dependencies
                            for dep_field in dependency:
                                if dep_field not in data:
                                    errors.append(f"Field '{field}' requires field '{dep_field}'")
                        elif isinstance(dependency, dict):
                            # Conditional dependencies
                            if 'required' in dependency:
                                for dep_field in dependency['required']:
                                    if dep_field not in data:
                                        errors.append(f"Field '{field}' requires field '{dep_field}'")
            
            return errors
            
        except Exception as e:
            logger.error(f"Schema-level validation error: {e}")
            errors.append(f"Schema-level validation error: {str(e)}")
            return errors
    
    def clean_data(self, data: Any, cleaning_rules: Dict[str, Any]) -> Any:
        """
        Clean data according to specified cleaning rules.
        
        Args:
            data: Data to clean
            cleaning_rules: Rules for data cleaning
            
        Returns:
            Cleaned data
        """
        try:
            if isinstance(data, dict):
                cleaned_data = {}
                for key, value in data.items():
                    if key in cleaning_rules:
                        cleaned_data[key] = self._apply_cleaning_rules(value, cleaning_rules[key])
                    else:
                        cleaned_data[key] = self._apply_default_cleaning(value)
                return cleaned_data
            elif isinstance(data, list):
                return [self.clean_data(item, cleaning_rules) for item in data]
            else:
                return self._apply_default_cleaning(data)
                
        except Exception as e:
            logger.error(f"Data cleaning error: {e}")
            return data
    
    def _apply_cleaning_rules(self, value: Any, rules: Dict[str, Any]) -> Any:
        """Apply specific cleaning rules to a value."""
        cleaned_value = value
        
        try:
            # Remove whitespace
            if rules.get('trim_whitespace', False) and isinstance(cleaned_value, str):
                cleaned_value = cleaned_value.strip()
            
            # Convert case
            if 'case' in rules and isinstance(cleaned_value, str):
                if rules['case'] == 'lower':
                    cleaned_value = cleaned_value.lower()
                elif rules['case'] == 'upper':
                    cleaned_value = cleaned_value.upper()
                elif rules['case'] == 'title':
                    cleaned_value = cleaned_value.title()
            
            # Remove special characters
            if rules.get('remove_special_chars', False) and isinstance(cleaned_value, str):
                cleaned_value = re.sub(r'[^\w\s-]', '', cleaned_value)
            
            # Replace values
            if 'replace' in rules:
                for old_val, new_val in rules['replace'].items():
                    if cleaned_value == old_val:
                        cleaned_value = new_val
            
            # Default values
            if cleaned_value is None and 'default' in rules:
                cleaned_value = rules['default']
            
            return cleaned_value
            
        except Exception as e:
            logger.error(f"Error applying cleaning rules: {e}")
            return value
    
    def _apply_default_cleaning(self, value: Any) -> Any:
        """Apply default cleaning to a value."""
        if isinstance(value, str):
            # Remove leading/trailing whitespace
            value = value.strip()
            
            # Handle empty strings
            if value == '':
                return None
        
        elif isinstance(value, (int, float)):
            # Handle NaN and infinity
            if value != value or value == float('inf') or value == float('-inf'):
                return None
        
        return value
    
    def assess_data_quality(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the quality of data against a schema.
        
        Args:
            data: Data to assess
            schema: Schema for quality assessment
            
        Returns:
            Data quality assessment results
        """
        try:
            quality_metrics = {
                'completeness': 0.0,
                'accuracy': 0.0,
                'consistency': 0.0,
                'validity': 0.0,
                'overall_score': 0.0,
                'issues': [],
                'recommendations': []
            }
            
            if not isinstance(data, dict):
                quality_metrics['issues'].append("Data is not a dictionary")
                return quality_metrics
            
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])
            
            total_fields = len(properties)
            valid_fields = 0
            complete_fields = 0
            consistent_fields = 0
            
            # Assess each field
            for field_name, field_schema in properties.items():
                field_value = data.get(field_name)
                
                # Completeness
                if field_name in required_fields:
                    if field_value is not None:
                        complete_fields += 1
                    else:
                        quality_metrics['issues'].append(f"Required field '{field_name}' is missing")
                else:
                    complete_fields += 1  # Optional fields are considered complete
                
                # Validity
                if field_value is not None:
                    field_errors, _ = self._validate_field(field_name, field_value, field_schema)
                    if not field_errors:
                        valid_fields += 1
                    else:
                        quality_metrics['issues'].extend(field_errors)
                
                # Consistency (basic check for now)
                consistent_fields += 1
            
            # Calculate metrics
            if total_fields > 0:
                quality_metrics['completeness'] = (complete_fields / total_fields) * 100
                quality_metrics['validity'] = (valid_fields / total_fields) * 100
                quality_metrics['consistency'] = (consistent_fields / total_fields) * 100
                
                # Overall score (weighted average)
                quality_metrics['overall_score'] = (
                    quality_metrics['completeness'] * 0.3 +
                    quality_metrics['validity'] * 0.4 +
                    quality_metrics['consistency'] * 0.3
                )
            
            # Generate recommendations
            quality_metrics['recommendations'] = self._generate_quality_recommendations(quality_metrics)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Data quality assessment error: {e}")
            return {
                'error': str(e),
                'overall_score': 0.0
            }
    
    def _generate_quality_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        
        if metrics['completeness'] < 80:
            recommendations.append("Improve data completeness by ensuring required fields are populated")
        
        if metrics['validity'] < 80:
            recommendations.append("Improve data validity by enforcing data type and format constraints")
        
        if metrics['consistency'] < 80:
            recommendations.append("Improve data consistency by standardizing data formats and values")
        
        if metrics['overall_score'] < 70:
            recommendations.append("Implement comprehensive data quality monitoring and validation")
        
        if not recommendations:
            recommendations.append("Data quality is within acceptable limits")
        
        return recommendations
    
    def detect_outliers(self, data: List[Any], method: str = 'iqr', 
                       threshold: float = 1.5) -> List[Tuple[int, Any, str]]:
        """
        Detect outliers in numerical data.
        
        Args:
            data: List of numerical values
            method: Outlier detection method ('iqr', 'zscore', 'modified_zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            List of (index, value, reason) tuples for outliers
        """
        outliers = []
        
        try:
            if not data or len(data) < 3:
                return outliers
            
            # Filter out non-numeric values
            numeric_data = []
            for i, value in enumerate(data):
                try:
                    numeric_value = float(value)
                    numeric_data.append((i, numeric_value))
                except (ValueError, TypeError):
                    continue
            
            if len(numeric_data) < 3:
                return outliers
            
            if method == 'iqr':
                outliers = self._detect_outliers_iqr(numeric_data, threshold)
            elif method == 'zscore':
                outliers = self._detect_outliers_zscore(numeric_data, threshold)
            elif method == 'modified_zscore':
                outliers = self._detect_outliers_modified_zscore(numeric_data, threshold)
            else:
                logger.warning(f"Unknown outlier detection method: {method}")
                return outliers
            
            return outliers
            
        except Exception as e:
            logger.error(f"Outlier detection error: {e}")
            return outliers
    
    def _detect_outliers_iqr(self, numeric_data: List[Tuple[int, float]], 
                             threshold: float) -> List[Tuple[int, Any, str]]:
        """Detect outliers using Interquartile Range method."""
        outliers = []
        
        try:
            values = [item[1] for item in numeric_data]
            values.sort()
            
            n = len(values)
            q1_index = int(0.25 * n)
            q3_index = int(0.75 * n)
            
            q1 = values[q1_index]
            q3 = values[q3_index]
            iqr = q3 - q1
            
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            for index, value in numeric_data:
                if value < lower_bound:
                    outliers.append((index, value, f"Below lower bound ({lower_bound:.2f})"))
                elif value > upper_bound:
                    outliers.append((index, value, f"Above upper bound ({upper_bound:.2f})"))
            
            return outliers
            
        except Exception as e:
            logger.error(f"IQR outlier detection error: {e}")
            return outliers
    
    def _detect_outliers_zscore(self, numeric_data: List[Tuple[int, float]], 
                                threshold: float) -> List[Tuple[int, Any, str]]:
        """Detect outliers using Z-score method."""
        outliers = []
        
        try:
            values = [item[1] for item in numeric_data]
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            if std_dev == 0:
                return outliers
            
            for index, value in numeric_data:
                z_score = abs((value - mean) / std_dev)
                if z_score > threshold:
                    outliers.append((index, value, f"Z-score: {z_score:.2f}"))
            
            return outliers
            
        except Exception as e:
            logger.error(f"Z-score outlier detection error: {e}")
            return outliers
    
    def _detect_outliers_modified_zscore(self, numeric_data: List[Tuple[int, float]], 
                                         threshold: float) -> List[Tuple[int, Any, str]]:
        """Detect outliers using Modified Z-score method."""
        outliers = []
        
        try:
            values = [item[1] for item in numeric_data]
            median = sorted(values)[len(values) // 2]
            
            # Calculate Median Absolute Deviation (MAD)
            mad_values = [abs(x - median) for x in values]
            mad = sorted(mad_values)[len(mad_values) // 2]
            
            if mad == 0:
                return outliers
            
            for index, value in numeric_data:
                modified_z_score = abs(0.6745 * (value - median) / mad)
                if modified_z_score > threshold:
                    outliers.append((index, value, f"Modified Z-score: {modified_z_score:.2f}"))
            
            return outliers
            
        except Exception as e:
            logger.error(f"Modified Z-score outlier detection error: {e}")
            return outliers
