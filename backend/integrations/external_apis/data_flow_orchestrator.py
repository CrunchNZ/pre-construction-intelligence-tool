"""
Data Flow Orchestrator

This service orchestrates data flow between different integrated systems and external APIs,
ensuring data consistency, proper sequencing, and error handling across the entire data pipeline.

Features:
- Data flow orchestration and sequencing
- Dependency management between data sources
- Data transformation and enrichment
- Error handling and recovery
- Performance monitoring and optimization
- Data flow visualization and monitoring

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time

logger = logging.getLogger(__name__)


class DataFlowOrchestrator:
    """Orchestrates data flow between integrated systems and external APIs."""
    
    def __init__(self):
        """Initialize the data flow orchestrator."""
        self.flow_registry = {}
        self.dependency_graph = {}
        self.execution_history = []
        self.performance_metrics = {}
        self.error_handlers = {}
        self.transformation_pipelines = {}
        
        # Execution configuration
        self.max_concurrent_flows = 5
        self.flow_timeout = 300  # 5 minutes
        self.retry_attempts = 3
        self.retry_delay = 60  # 1 minute
        
        # Initialize default error handlers
        self._initialize_default_error_handlers()
    
    def register_data_flow(self, flow_name: str, flow_config: Dict[str, Any]) -> bool:
        """
        Register a new data flow configuration.
        
        Args:
            flow_name: Unique name for the data flow
            flow_config: Configuration dictionary for the flow
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate flow configuration
            if not self._validate_flow_config(flow_config):
                logger.error(f"Invalid flow configuration for {flow_name}")
                return False
            
            # Register the flow
            self.flow_registry[flow_name] = flow_config
            
            # Build dependency graph
            self._build_dependency_graph(flow_name, flow_config)
            
            logger.info(f"Data flow '{flow_name}' registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering data flow '{flow_name}': {e}")
            return False
    
    def execute_data_flow(self, flow_name: str, 
                          input_data: Optional[Dict[str, Any]] = None,
                          async_execution: bool = False) -> Dict[str, Any]:
        """
        Execute a registered data flow.
        
        Args:
            flow_name: Name of the flow to execute
            input_data: Input data for the flow
            async_execution: Whether to execute asynchronously
            
        Returns:
            Execution results
        """
        try:
            if flow_name not in self.flow_registry:
                raise ValueError(f"Data flow '{flow_name}' not found")
            
            flow_config = self.flow_registry[flow_name]
            execution_id = f"{flow_name}_{int(timezone.now().timestamp())}"
            
            # Record execution start
            execution_record = {
                'execution_id': execution_id,
                'flow_name': flow_name,
                'start_time': timezone.now(),
                'status': 'running',
                'input_data': input_data,
                'steps': [],
                'errors': [],
                'performance_metrics': {}
            }
            
            self.execution_history.append(execution_record)
            
            if async_execution:
                # Execute asynchronously
                asyncio.create_task(self._execute_flow_async(execution_record))
                return {
                    'execution_id': execution_id,
                    'status': 'started_async',
                    'message': f"Flow '{flow_name}' started asynchronously"
                }
            else:
                # Execute synchronously
                return self._execute_flow_sync(execution_record)
                
        except Exception as e:
            logger.error(f"Error executing data flow '{flow_name}': {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def execute_multiple_flows(self, flow_names: List[str], 
                              input_data: Optional[Dict[str, str, Any]] = None,
                              parallel: bool = True) -> Dict[str, Any]:
        """
        Execute multiple data flows.
        
        Args:
            flow_names: List of flow names to execute
            input_data: Input data for each flow (keyed by flow name)
            parallel: Whether to execute flows in parallel
            
        Returns:
            Execution results for all flows
        """
        try:
            results = {}
            
            if parallel:
                # Execute flows in parallel using ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=self.max_concurrent_flows) as executor:
                    future_to_flow = {}
                    
                    for flow_name in flow_names:
                        flow_input = input_data.get(flow_name, {}) if input_data else {}
                        future = executor.submit(self.execute_data_flow, flow_name, flow_input)
                        future_to_flow[future] = flow_name
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_flow):
                        flow_name = future_to_flow[future]
                        try:
                            result = future.result(timeout=self.flow_timeout)
                            results[flow_name] = result
                        except Exception as e:
                            results[flow_name] = {
                                'error': str(e),
                                'status': 'failed'
                            }
            else:
                # Execute flows sequentially
                for flow_name in flow_names:
                    flow_input = input_data.get(flow_name, {}) if input_data else {}
                    result = self.execute_data_flow(flow_name, flow_input)
                    results[flow_name] = result
                    
                    # Check if we should continue on failure
                    if result.get('status') == 'failed' and not flow_config.get('continue_on_failure', False):
                        break
            
            return {
                'total_flows': len(flow_names),
                'successful_flows': len([r for r in results.values() if r.get('status') == 'completed']),
                'failed_flows': len([r for r in results.values() if r.get('status') == 'failed']),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error executing multiple flows: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def get_flow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific flow execution.
        
        Args:
            execution_id: Execution ID to check
            
        Returns:
            Flow execution status and details
        """
        for execution in self.execution_history:
            if execution['execution_id'] == execution_id:
                return execution
        return None
    
    def get_flow_performance_metrics(self, flow_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific flow.
        
        Args:
            flow_name: Name of the flow
            
        Returns:
            Performance metrics
        """
        return self.performance_metrics.get(flow_name, {})
    
    def add_transformation_pipeline(self, pipeline_name: str, 
                                   transformations: List[Callable]) -> bool:
        """
        Add a data transformation pipeline.
        
        Args:
            pipeline_name: Name of the transformation pipeline
            transformations: List of transformation functions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.transformation_pipelines[pipeline_name] = transformations
            logger.info(f"Transformation pipeline '{pipeline_name}' added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding transformation pipeline '{pipeline_name}': {e}")
            return False
    
    def add_error_handler(self, error_type: str, handler: Callable) -> bool:
        """
        Add a custom error handler for specific error types.
        
        Args:
            error_type: Type of error to handle
            handler: Error handling function
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.error_handlers[error_type] = handler
            logger.info(f"Error handler for '{error_type}' added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding error handler for '{error_type}': {e}")
            return False
    
    def _validate_flow_config(self, flow_config: Dict[str, Any]) -> bool:
        """Validate flow configuration."""
        required_fields = ['steps', 'dependencies']
        
        for field in required_fields:
            if field not in flow_config:
                logger.error(f"Missing required field '{field}' in flow configuration")
                return False
        
        # Validate steps
        steps = flow_config['steps']
        if not isinstance(steps, list) or len(steps) == 0:
            logger.error("Flow must have at least one step")
            return False
        
        for step in steps:
            if not isinstance(step, dict) or 'name' not in step:
                logger.error("Each step must have a name")
                return False
        
        return True
    
    def _build_dependency_graph(self, flow_name: str, flow_config: Dict[str, Any]):
        """Build dependency graph for a flow."""
        dependencies = flow_config.get('dependencies', {})
        self.dependency_graph[flow_name] = dependencies
    
    def _execute_flow_sync(self, execution_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data flow synchronously."""
        try:
            flow_name = execution_record['flow_name']
            flow_config = self.flow_registry[flow_name]
            steps = flow_config['steps']
            
            # Check dependencies
            dependency_errors = self._check_dependencies(flow_name)
            if dependency_errors:
                execution_record['errors'].extend(dependency_errors)
                execution_record['status'] = 'failed'
                return {
                    'execution_id': execution_record['execution_id'],
                    'status': 'failed',
                    'errors': dependency_errors
                }
            
            # Execute steps
            current_data = execution_record.get('input_data', {})
            
            for step in steps:
                step_result = self._execute_step(step, current_data, execution_record)
                
                if step_result['status'] == 'failed':
                    execution_record['status'] = 'failed'
                    execution_record['errors'].append(step_result['error'])
                    break
                
                # Update data for next step
                if 'output' in step_result:
                    current_data.update(step_result['output'])
                
                # Record step execution
                execution_record['steps'].append(step_result)
            
            # Update execution record
            execution_record['end_time'] = timezone.now()
            execution_record['status'] = 'completed' if execution_record['status'] != 'failed' else 'failed'
            execution_record['output_data'] = current_data
            
            # Calculate performance metrics
            self._calculate_performance_metrics(execution_record)
            
            return {
                'execution_id': execution_record['execution_id'],
                'status': execution_record['status'],
                'output_data': current_data,
                'errors': execution_record['errors'],
                'performance_metrics': execution_record['performance_metrics']
            }
            
        except Exception as e:
            logger.error(f"Error in synchronous flow execution: {e}")
            execution_record['status'] = 'failed'
            execution_record['errors'].append(str(e))
            execution_record['end_time'] = timezone.now()
            
            return {
                'execution_id': execution_record['execution_id'],
                'status': 'failed',
                'error': str(e)
            }
    
    async def _execute_flow_async(self, execution_record: Dict[str, Any]):
        """Execute a data flow asynchronously."""
        try:
            # Execute the flow synchronously in the async context
            result = self._execute_flow_sync(execution_record)
            
            # Update the execution record
            for execution in self.execution_history:
                if execution['execution_id'] == execution_record['execution_id']:
                    execution.update(execution_record)
                    break
            
            logger.info(f"Async flow execution completed: {result['status']}")
            
        except Exception as e:
            logger.error(f"Error in asynchronous flow execution: {e}")
            execution_record['status'] = 'failed'
            execution_record['errors'].append(str(e))
            execution_record['end_time'] = timezone.now()
    
    def _execute_step(self, step: Dict[str, Any], 
                     current_data: Dict[str, Any], 
                     execution_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in the data flow."""
        step_name = step['name']
        step_type = step.get('type', 'function')
        
        step_result = {
            'name': step_name,
            'type': step_type,
            'start_time': timezone.now(),
            'status': 'running',
            'input': current_data.copy()
        }
        
        try:
            if step_type == 'function':
                result = self._execute_function_step(step, current_data)
            elif step_type == 'api_call':
                result = self._execute_api_step(step, current_data)
            elif step_type == 'transformation':
                result = self._execute_transformation_step(step, current_data)
            elif step_type == 'validation':
                result = self._execute_validation_step(step, current_data)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
            
            step_result.update(result)
            step_result['status'] = 'completed'
            
        except Exception as e:
            error_msg = f"Step '{step_name}' failed: {str(e)}"
            logger.error(error_msg)
            
            # Try to handle the error
            handled = self._handle_step_error(step, e, current_data)
            
            step_result['status'] = 'failed' if not handled else 'completed_with_errors'
            step_result['error'] = error_msg
            step_result['error_handled'] = handled
        
        finally:
            step_result['end_time'] = timezone.now()
            if 'start_time' in step_result:
                duration = (step_result['end_time'] - step_result['start_time']).total_seconds()
                step_result['duration'] = duration
        
        return step_result
    
    def _execute_function_step(self, step: Dict[str, Any], 
                              current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function-based step."""
        function_name = step.get('function')
        if not function_name:
            raise ValueError("Function name not specified for function step")
        
        # Get function from registry or import
        function = self._get_function(function_name)
        if not function:
            raise ValueError(f"Function '{function_name}' not found")
        
        # Execute function
        function_input = self._prepare_function_input(step, current_data)
        output = function(**function_input)
        
        return {
            'output': output if isinstance(output, dict) else {'result': output},
            'function_name': function_name
        }
    
    def _execute_api_step(self, step: Dict[str, Any], 
                          current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API call step."""
        api_config = step.get('api_config', {})
        endpoint = api_config.get('endpoint')
        method = api_config.get('method', 'GET')
        
        if not endpoint:
            raise ValueError("API endpoint not specified")
        
        # Prepare API request
        url = self._interpolate_variables(endpoint, current_data)
        headers = self._interpolate_variables(api_config.get('headers', {}), current_data)
        params = self._interpolate_variables(api_config.get('params', {}), current_data)
        data = self._interpolate_variables(api_config.get('data', {}), current_data)
        
        # Make API call (simplified - in production, use proper HTTP client)
        try:
            # This is a placeholder - in production, implement actual HTTP calls
            api_response = self._make_api_call(method, url, headers, params, data)
            
            return {
                'output': {'api_response': api_response},
                'api_endpoint': endpoint,
                'method': method
            }
            
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def _execute_transformation_step(self, step: Dict[str, Any], 
                                    current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data transformation step."""
        pipeline_name = step.get('pipeline')
        if not pipeline_name:
            raise ValueError("Transformation pipeline not specified")
        
        if pipeline_name not in self.transformation_pipelines:
            raise ValueError(f"Transformation pipeline '{pipeline_name}' not found")
        
        transformations = self.transformation_pipelines[pipeline_name]
        transformed_data = current_data.copy()
        
        for transformation in transformations:
            try:
                transformed_data = transformation(transformed_data)
            except Exception as e:
                raise Exception(f"Transformation failed: {str(e)}")
        
        return {
            'output': transformed_data,
            'pipeline_name': pipeline_name,
            'transformations_applied': len(transformations)
        }
    
    def _execute_validation_step(self, step: Dict[str, Any], 
                                current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data validation step."""
        schema = step.get('schema')
        if not schema:
            raise ValueError("Validation schema not specified")
        
        # Import and use DataValidator
        from .data_validation import DataValidator
        validator = DataValidator()
        
        # Validate data
        is_valid, errors, cleaned_data = validator.validate_data(current_data, schema)
        
        if not is_valid:
            raise Exception(f"Data validation failed: {errors}")
        
        return {
            'output': cleaned_data,
            'validation_passed': True,
            'errors_fixed': len(errors) if errors else 0
        }
    
    def _check_dependencies(self, flow_name: str) -> List[str]:
        """Check if flow dependencies are satisfied."""
        errors = []
        dependencies = self.dependency_graph.get(flow_name, {})
        
        for dep_name, dep_config in dependencies.items():
            if not self._is_dependency_satisfied(dep_name, dep_config):
                errors.append(f"Dependency '{dep_name}' not satisfied")
        
        return errors
    
    def _is_dependency_satisfied(self, dep_name: str, dep_config: Dict[str, Any]) -> bool:
        """Check if a specific dependency is satisfied."""
        dep_type = dep_config.get('type', 'flow')
        
        if dep_type == 'flow':
            # Check if dependent flow has completed successfully
            return self._check_flow_dependency(dep_name, dep_config)
        elif dep_type == 'data':
            # Check if required data is available
            return self._check_data_dependency(dep_name, dep_config)
        elif dep_type == 'external':
            # Check if external service is available
            return self._check_external_dependency(dep_name, dep_config)
        else:
            logger.warning(f"Unknown dependency type: {dep_type}")
            return False
    
    def _check_flow_dependency(self, dep_name: str, dep_config: Dict[str, Any]) -> bool:
        """Check if a flow dependency is satisfied."""
        # Look for successful execution of dependent flow
        for execution in self.execution_history:
            if (execution['flow_name'] == dep_name and 
                execution['status'] == 'completed'):
                
                # Check if execution is within required timeframe
                if 'timeout' in dep_config:
                    timeout_hours = dep_config['timeout']
                    if execution['end_time'] < timezone.now() - timedelta(hours=timeout_hours):
                        return False
                
                return True
        
        return False
    
    def _check_data_dependency(self, dep_name: str, dep_config: Dict[str, Any]) -> bool:
        """Check if a data dependency is satisfied."""
        # Check if required data exists in cache or database
        cache_key = dep_config.get('cache_key')
        if cache_key:
            return cache.get(cache_key) is not None
        
        return True  # Default to satisfied if no specific check defined
    
    def _check_external_dependency(self, dep_name: str, dep_config: Dict[str, Any]) -> bool:
        """Check if an external dependency is satisfied."""
        # Check if external service is available
        health_check_url = dep_config.get('health_check')
        if health_check_url:
            try:
                # This is a placeholder - implement actual health check
                return self._check_service_health(health_check_url)
            except Exception:
                return False
        
        return True  # Default to satisfied if no health check defined
    
    def _handle_step_error(self, step: Dict[str, Any], 
                           error: Exception, 
                           current_data: Dict[str, Any]) -> bool:
        """Handle step execution errors."""
        error_type = type(error).__name__
        
        # Check for custom error handler
        if error_type in self.error_handlers:
            try:
                handler = self.error_handlers[error_type]
                return handler(step, error, current_data)
            except Exception as e:
                logger.error(f"Error in custom error handler: {e}")
                return False
        
        # Check for step-specific error handling
        error_handling = step.get('error_handling', {})
        if error_handling.get('retry', False):
            return self._retry_step(step, current_data)
        
        if error_handling.get('fallback', False):
            return self._execute_fallback(step, current_data)
        
        return False
    
    def _retry_step(self, step: Dict[str, Any], current_data: Dict[str, Any]) -> bool:
        """Retry a failed step."""
        max_retries = step.get('max_retries', self.retry_attempts)
        retry_count = step.get('retry_count', 0)
        
        if retry_count < max_retries:
            step['retry_count'] = retry_count + 1
            logger.info(f"Retrying step '{step['name']}' (attempt {retry_count + 1})")
            
            # Wait before retry
            time.sleep(self.retry_delay)
            
            # Re-execute step
            try:
                result = self._execute_step(step, current_data, {})
                return result['status'] == 'completed'
            except Exception:
                return False
        
        return False
    
    def _execute_fallback(self, step: Dict[str, Any], current_data: Dict[str, Any]) -> bool:
        """Execute fallback logic for a failed step."""
        fallback_config = step.get('fallback', {})
        fallback_function = fallback_config.get('function')
        
        if fallback_function:
            try:
                function = self._get_function(fallback_function)
                if function:
                    function(current_data)
                    return True
            except Exception as e:
                logger.error(f"Fallback execution failed: {e}")
        
        return False
    
    def _calculate_performance_metrics(self, execution_record: Dict[str, Any]):
        """Calculate performance metrics for flow execution."""
        flow_name = execution_record['flow_name']
        
        if flow_name not in self.performance_metrics:
            self.performance_metrics[flow_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'average_duration': 0,
                'total_duration': 0
            }
        
        metrics = self.performance_metrics[flow_name]
        metrics['total_executions'] += 1
        
        if execution_record['status'] == 'completed':
            metrics['successful_executions'] += 1
        else:
            metrics['failed_executions'] += 1
        
        # Calculate duration
        if 'start_time' in execution_record and 'end_time' in execution_record:
            duration = (execution_record['end_time'] - execution_record['start_time']).total_seconds()
            metrics['total_duration'] += duration
            metrics['average_duration'] = metrics['total_duration'] / metrics['total_executions']
    
    def _get_function(self, function_name: str):
        """Get a function by name (placeholder implementation)."""
        # In production, implement function registry or dynamic import
        return None
    
    def _prepare_function_input(self, step: Dict[str, Any], 
                               current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for function execution."""
        input_mapping = step.get('input_mapping', {})
        function_input = {}
        
        for param_name, data_path in input_mapping.items():
            if data_path in current_data:
                function_input[param_name] = current_data[data_path]
        
        return function_input
    
    def _interpolate_variables(self, template: Any, data: Dict[str, Any]) -> Any:
        """Interpolate variables in templates using data values."""
        if isinstance(template, str):
            for key, value in data.items():
                template = template.replace(f"${{{key}}}", str(value))
            return template
        elif isinstance(template, dict):
            return {k: self._interpolate_variables(v, data) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._interpolate_variables(item, data) for item in template]
        else:
            return template
    
    def _make_api_call(self, method: str, url: str, headers: Dict, 
                       params: Dict, data: Dict) -> Dict[str, Any]:
        """Make an API call (placeholder implementation)."""
        # In production, implement actual HTTP client
        return {
            'status': 'success',
            'method': method,
            'url': url,
            'response': 'API call placeholder'
        }
    
    def _check_service_health(self, health_check_url: str) -> bool:
        """Check if a service is healthy (placeholder implementation)."""
        # In production, implement actual health check
        return True
    
    def _initialize_default_error_handlers(self):
        """Initialize default error handlers."""
        # Add default error handlers here
        pass
