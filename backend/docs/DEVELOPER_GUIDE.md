# Pre-Construction Intelligence Platform - Developer Guide

## 🚀 Welcome to the Pre-Construction Intelligence Platform

This comprehensive guide will help you integrate with our construction intelligence platform, providing access to AI-powered analytics, real-time data streaming, and comprehensive project management capabilities.

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Overview](#api-overview)
4. [SDKs](#sdks)
5. [Core Endpoints](#core-endpoints)
6. [AI/ML Integration](#aiml-integration)
7. [Real-time Data Streaming](#real-time-data-streaming)
8. [Webhooks](#webhooks)
9. [Rate Limiting](#rate-limiting)
10. [Error Handling](#error-handling)
11. [Best Practices](#best-practices)
12. [Examples](#examples)
13. [Troubleshooting](#troubleshooting)
14. [Support](#support)

## 🚀 Quick Start

### 1. Get Your API Credentials

First, you'll need to obtain your API credentials:

- **API Key**: For programmatic access
- **Session Token**: For web-based applications
- **Base URL**: Your API endpoint

Contact our team at `api-support@preconstruction-intelligence.com` to get started.

### 2. Choose Your SDK

We provide SDKs in multiple languages:

- **Python**: `pip install preconstruction-intelligence-python`
- **JavaScript**: `npm install @preconstruction-intelligence/js-sdk`
- **REST API**: Direct HTTP calls

### 3. Make Your First API Call

#### Python Example
```python
from preconstruction_intelligence import createSDK, Project
from datetime import date

# Initialize SDK
sdk = createSDK(
    base_url='https://api.preconstruction-intelligence.com',
    api_key='your_api_key_here'
)

# Create a project
project = Project(
    name='Downtown Office Complex',
    description='Modern office building in downtown area',
    status='planning',
    start_date=date(2024, 6, 1),
    estimated_completion=date(2025, 12, 31),
    budget=25000000,
    location='Downtown Business District',
    project_manager='John Smith'
)

# Create the project via API
result = sdk.create_project(project)
print(f"Project created with ID: {result['id']}")
```

#### JavaScript Example
```javascript
import { createSDK, Project } from '@preconstruction-intelligence/js-sdk';

// Initialize SDK
const sdk = createSDK(
    'https://api.preconstruction-intelligence.com',
    'your_api_key_here'
);

// Create a project
const project = new Project({
    name: 'Downtown Office Complex',
    description: 'Modern office building in downtown area',
    status: 'planning',
    start_date: '2024-06-01',
    estimated_completion: '2025-12-31',
    budget: 25000000,
    location: 'Downtown Business District',
    project_manager: 'John Smith'
});

// Create the project via API
const result = await sdk.createProject(project);
console.log(`Project created with ID: ${result.id}`);
```

#### REST API Example
```bash
curl -X POST "https://api.preconstruction-intelligence.com/api/projects/" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Office Complex",
    "description": "Modern office building in downtown area",
    "status": "planning",
    "start_date": "2024-06-01",
    "estimated_completion": "2025-12-31",
    "budget": 25000000,
    "location": "Downtown Business District",
    "project_manager": "John Smith"
  }'
```

## 🔐 Authentication

### API Key Authentication

For programmatic access, use API key authentication:

```python
# Python
sdk = createSDK(
    base_url='https://api.preconstruction-intelligence.com',
    api_key='your_api_key_here'
)
```

```javascript
// JavaScript
const sdk = createSDK(
    'https://api.preconstruction-intelligence.com',
    'your_api_key_here'
);
```

```bash
# REST API
curl -H "Authorization: Bearer your_api_key_here" \
     "https://api.preconstruction-intelligence.com/api/projects/"
```

### Session Authentication

For web applications, use session authentication:

```python
# Python
sdk = createSDK(
    base_url='https://api.preconstruction-intelligence.com',
    session_token='your_session_token_here'
)
```

```javascript
// JavaScript
const sdk = createSDK(
    'https://api.preconstruction-intelligence.com',
    null,
    'your_session_token_here'
);
```

### Security Best Practices

- **Never expose API keys** in client-side code
- **Use HTTPS** for all API calls
- **Rotate API keys** regularly
- **Store credentials securely** using environment variables or secure storage
- **Use the principle of least privilege** when assigning API permissions

## 🌐 API Overview

### Base URL
```
https://api.preconstruction-intelligence.com
```

### API Versioning
- **Current Version**: v1.0.0
- **Version Header**: `Accept: application/vnd.preconstruction-intelligence.v1+json`
- **Default**: Latest stable version

### Response Format
All API responses follow a consistent JSON format:

```json
{
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  },
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "pages": 8
  }
}
```

### Error Responses
```json
{
  "error": "Error message description",
  "code": "error_code",
  "details": {
    "field": ["Specific error details"]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

## 🛠️ SDKs

### Python SDK

#### Installation
```bash
pip install preconstruction-intelligence-python
```

#### Features
- **Full API Coverage**: All endpoints supported
- **Data Models**: Type-safe data classes
- **Error Handling**: Comprehensive exception handling
- **Retry Logic**: Automatic retry with exponential backoff
- **Rate Limiting**: Built-in rate limit handling
- **Async Support**: Available for high-performance applications

#### Advanced Usage
```python
from preconstruction_intelligence import createSDK, Project, Supplier
from datetime import date, timedelta

sdk = createSDK('https://api.preconstruction-intelligence.com', 'your_api_key')

# Batch operations
projects = []
for i in range(5):
    project = Project(
        name=f'Project {i+1}',
        status='planning',
        start_date=date.today() + timedelta(days=i*30),
        budget=1000000 * (i+1)
    )
    projects.append(project)

# Create multiple projects
results = []
for project in projects:
    try:
        result = sdk.create_project(project)
        results.append(result)
    except Exception as e:
        print(f"Failed to create project {project.name}: {e}")

# Get projects with advanced filtering
projects = sdk.get_projects(
    page=1,
    page_size=50,
    search='office',
    status='active',
    start_date='2024-01-01',
    end_date='2024-12-31',
    ordering='-created_at'
)
```

### JavaScript SDK

#### Installation
```bash
npm install @preconstruction-intelligence/js-sdk
```

#### Features
- **Modern JavaScript**: ES6+ features and async/await
- **Browser & Node.js**: Universal compatibility
- **TypeScript Support**: Full type definitions included
- **Error Handling**: Comprehensive error classes
- **Retry Logic**: Automatic retry with exponential backoff
- **Rate Limiting**: Built-in rate limit handling

#### Advanced Usage
```javascript
import { createSDK, Project, Supplier } from '@preconstruction-intelligence/js-sdk';

const sdk = createSDK('https://api.preconstruction-intelligence.com', 'your_api_key');

// Batch operations with Promise.all
const createProjects = async () => {
    const projects = Array.from({ length: 5 }, (_, i) => new Project({
        name: `Project ${i + 1}`,
        status: 'planning',
        start_date: new Date(Date.now() + i * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        budget: 1000000 * (i + 1)
    }));

    try {
        const results = await Promise.all(
            projects.map(project => sdk.createProject(project))
        );
        console.log(`Created ${results.length} projects`);
        return results;
    } catch (error) {
        console.error('Failed to create projects:', error);
        throw error;
    }
};

// Get projects with advanced filtering
const getFilteredProjects = async () => {
    const projects = await sdk.getProjects({
        page: 1,
        pageSize: 50,
        search: 'office',
        status: 'active',
        startDate: '2024-01-01',
        endDate: '2024-12-31',
        ordering: '-created_at'
    });
    
    return projects;
};
```

## 🔌 Core Endpoints

### Projects

#### Get Projects
```http
GET /api/projects/
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `search` (string): Search term
- `status` (string): Filter by status
- `start_date` (date): Filter by start date (YYYY-MM-DD)
- `end_date` (date): Filter by end date (YYYY-MM-DD)
- `ordering` (string): Order by field (- for descending)

**Example:**
```python
projects = sdk.get_projects(
    page=1,
    page_size=20,
    search='office',
    status='active',
    ordering='-created_at'
)
```

#### Create Project
```http
POST /api/projects/
```

**Request Body:**
```json
{
  "name": "Project Name",
  "description": "Project description",
  "status": "planning",
  "start_date": "2024-06-01",
  "estimated_completion": "2025-12-31",
  "budget": 25000000,
  "location": "Project location",
  "project_manager": "Manager name"
}
```

**Example:**
```python
project = Project(
    name='Downtown Office Complex',
    description='Modern office building',
    status='planning',
    start_date=date(2024, 6, 1),
    budget=25000000
)

result = sdk.create_project(project)
```

### Suppliers

#### Get Suppliers
```http
GET /api/suppliers/
```

**Query Parameters:**
- `page` (int): Page number
- `page_size` (int): Items per page
- `search` (string): Search term
- `specialties` (array): Filter by specialties
- `min_rating` (float): Minimum rating filter
- `ordering` (string): Order by field

**Example:**
```python
suppliers = sdk.get_suppliers(
    search='electrical',
    specialties=['electrical', 'plumbing'],
    min_rating=4.0,
    ordering='-rating'
)
```

### Risk Analysis

#### Get Risks
```http
GET /api/risks/
```

**Query Parameters:**
- `project_id` (int): Filter by project
- `risk_type` (string): Filter by risk type
- `status` (string): Filter by status
- `probability` (string): Filter by probability
- `impact` (string): Filter by impact

**Example:**
```python
risks = sdk.get_risks(
    project_id=123,
    risk_type='financial',
    status='open',
    probability='high'
)
```

## 🤖 AI/ML Integration

### ML Predictions

#### Get Predictions
```http
GET /api/ai/predictions/
```

**Query Parameters:**
- `model_name` (string): Filter by model name
- `prediction_type` (string): Filter by prediction type
- `page` (int): Page number
- `page_size` (int): Items per page

**Example:**
```python
predictions = sdk.get_ml_predictions(
    model_name='cost_prediction_v2',
    prediction_type='cost_prediction'
)
```

#### Create Prediction
```http
POST /api/ai/predictions/
```

**Request Body:**
```json
{
  "model_name": "cost_prediction_v2",
  "prediction_type": "cost_prediction",
  "input_data": {
    "project_size": 50000,
    "location": "urban",
    "complexity": "high",
    "materials": ["steel", "concrete", "glass"]
  }
}
```

**Example:**
```python
prediction = MLPrediction(
    model_name='cost_prediction_v2',
    prediction_type='cost_prediction',
    input_data={
        'project_size': 50000,
        'location': 'urban',
        'complexity': 'high'
    }
)

result = sdk.create_ml_prediction(prediction)
```

### Model Training

#### Train Model
```http
POST /api/ai/models/train/
```

**Request Body:**
```json
{
  "model_name": "cost_prediction_v3",
  "model_type": "cost_prediction",
  "training_data": {
    "data_source": "historical_projects",
    "features": ["size", "location", "complexity", "materials"],
    "target": "final_cost"
  },
  "parameters": {
    "algorithm": "xgboost",
    "max_depth": 6,
    "learning_rate": 0.1
  }
}
```

**Example:**
```python
training_job = sdk.train_ml_model(
    model_name='cost_prediction_v3',
    model_type='cost_prediction',
    training_data={
        'data_source': 'historical_projects',
        'features': ['size', 'location', 'complexity'],
        'target': 'final_cost'
    },
    parameters={
        'algorithm': 'xgboost',
        'max_depth': 6
    }
)
```

## 📡 Real-time Data Streaming

### Kafka Topics

#### Get Topics
```http
GET /api/kafka/topics/
```

**Example:**
```python
topics = sdk.get_kafka_topics()
print(f"Available topics: {topics['topics']}")
```

#### Publish Message
```http
POST /api/kafka/publish/
```

**Request Body:**
```json
{
  "topic": "construction.projects",
  "message": {
    "event_type": "project.created",
    "project_id": 123,
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
      "name": "New Project",
      "status": "active"
    }
  }
}
```

**Example:**
```python
message = {
    'event_type': 'project.created',
    'project_id': 123,
    'timestamp': datetime.now().isoformat(),
    'data': {
        'name': 'New Project',
        'status': 'active'
    }
}

result = sdk.publish_message('construction.projects', message)
```

### Available Topics

- `construction.projects` - Project lifecycle events
- `construction.suppliers` - Supplier updates
- `construction.risks` - Risk assessment events
- `construction.analytics` - Analytics and metrics
- `construction.integrations` - External system sync events
- `construction.ml_predictions` - ML model outputs

## 🔗 Webhooks

### Supported Events

- `project.created` - New project created
- `project.updated` - Project updated
- `project.deleted` - Project deleted
- `supplier.added` - New supplier added
- `risk.identified` - New risk identified
- `ml.prediction.completed` - ML prediction completed
- `integration.sync.completed` - Integration sync completed

### Webhook Configuration

```json
{
  "url": "https://your-app.com/webhooks",
  "events": ["project.created", "project.updated"],
  "secret": "your_webhook_secret",
  "active": true
}
```

### Webhook Payload

```json
{
  "event": "project.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "project_id": 123,
    "name": "Project Name",
    "status": "active"
  },
  "signature": "sha256=..."
}
```

## ⚡ Rate Limiting

### Rate Limits

- **Default**: 1,000 requests per hour
- **Authenticated**: 5,000 requests per hour
- **Admin**: 10,000 requests per hour
- **ML Endpoints**: 100 requests per hour
- **Kafka Endpoints**: 1,000 requests per hour

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 850
X-RateLimit-Reset: 1642233600
```

### Handling Rate Limits

Our SDKs automatically handle rate limiting with exponential backoff:

```python
# Python SDK automatically retries with backoff
try:
    result = sdk.get_projects()
except RateLimitError:
    # SDK will automatically retry with exponential backoff
    pass
```

```javascript
// JavaScript SDK automatically retries with backoff
try {
    const result = await sdk.getProjects();
} catch (error) {
    if (error instanceof RateLimitError) {
        // SDK will automatically retry with exponential backoff
    }
}
```

## ❌ Error Handling

### Error Types

- **AuthenticationError**: Invalid or missing credentials
- **ValidationError**: Invalid request data
- **RateLimitError**: Rate limit exceeded
- **APIError**: General API errors

### Error Handling Examples

#### Python
```python
try:
    project = sdk.get_project(999999)
except AuthenticationError:
    print("Please check your API credentials")
except ValidationError as e:
    print(f"Validation failed: {e}")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### JavaScript
```javascript
try {
    const project = await sdk.getProject(999999);
} catch (error) {
    if (error instanceof AuthenticationError) {
        console.error('Please check your API credentials');
    } else if (error instanceof ValidationError) {
        console.error(`Validation failed: ${error.message}`);
    } else if (error instanceof RateLimitError) {
        console.error('Rate limit exceeded, please wait');
    } else if (error instanceof APIError) {
        console.error(`API error ${error.statusCode}: ${error.message}`);
    } else {
        console.error(`Unexpected error: ${error.message}`);
    }
}
```

## 🎯 Best Practices

### 1. Authentication
- Store API keys securely
- Use environment variables
- Rotate keys regularly
- Use the principle of least privilege

### 2. Error Handling
- Always handle errors gracefully
- Implement retry logic for transient failures
- Log errors for debugging
- Provide user-friendly error messages

### 3. Rate Limiting
- Implement exponential backoff
- Cache responses when possible
- Batch requests when feasible
- Monitor rate limit usage

### 4. Data Validation
- Validate data before sending
- Use SDK data models
- Handle required vs optional fields
- Implement proper error handling

### 5. Performance
- Use pagination for large datasets
- Implement caching strategies
- Use async operations when possible
- Monitor API response times

### 6. Security
- Use HTTPS for all requests
- Never expose API keys in client code
- Validate all input data
- Implement proper access controls

## 📖 Examples

### Complete Project Management Workflow

```python
from preconstruction_intelligence import createSDK, Project, Supplier, RiskAssessment
from datetime import date

# Initialize SDK
sdk = createSDK('https://api.preconstruction-intelligence.com', 'your_api_key')

# 1. Create a project
project = Project(
    name='Downtown Office Complex',
    description='Modern office building with sustainable features',
    status='planning',
    start_date=date(2024, 6, 1),
    estimated_completion=date(2025, 12, 31),
    budget=25000000,
    location='Downtown Business District',
    project_manager='John Smith'
)

project_result = sdk.create_project(project)
project_id = project_result['id']
print(f"Project created with ID: {project_id}")

# 2. Add suppliers
suppliers = [
    Supplier(
        name='ABC Construction',
        contact_person='Mike Johnson',
        email='mike@abc-construction.com',
        phone='555-0123',
        specialties=['general_contractor', 'foundation'],
        rating=4.8
    ),
    Supplier(
        name='XYZ Electrical',
        contact_person='Sarah Wilson',
        email='sarah@xyz-electrical.com',
        phone='555-0456',
        specialties=['electrical', 'lighting'],
        rating=4.9
    )
]

for supplier in suppliers:
    supplier_result = sdk.create_supplier(supplier)
    print(f"Supplier {supplier.name} added with ID: {supplier_result['id']}")

# 3. Assess risks
risks = [
    RiskAssessment(
        project_id=project_id,
        risk_type='financial',
        description='Budget overrun due to material cost increases',
        probability='medium',
        impact='high',
        mitigation_strategy='Establish price escalation clauses with suppliers'
    ),
    RiskAssessment(
        project_id=project_id,
        risk_type='schedule',
        description='Permit delays from city planning department',
        probability='high',
        impact='medium',
        mitigation_strategy='Submit permits early and maintain regular communication'
    )
]

for risk in risks:
    risk_result = sdk.create_risk_assessment(risk)
    print(f"Risk assessment created with ID: {risk_result['id']}")

# 4. Get ML predictions
predictions = sdk.get_ml_predictions(
    model_name='cost_prediction_v2',
    prediction_type='cost_prediction'
)

print(f"Found {len(predictions['results'])} cost predictions")

# 5. Get analytics
analytics = sdk.get_project_analytics(
    project_id=project_id,
    start_date='2024-01-01',
    end_date='2024-12-31'
)

print(f"Project analytics: {analytics}")
```

### Real-time Data Processing

```python
import asyncio
from preconstruction_intelligence import createSDK

async def process_real_time_data():
    sdk = createSDK('https://api.preconstruction-intelligence.com', 'your_api_key')
    
    # Get available topics
    topics = sdk.get_kafka_topics()
    print(f"Available topics: {topics['topics']}")
    
    # Publish project update
    message = {
        'event_type': 'project.updated',
        'project_id': 123,
        'timestamp': datetime.now().isoformat(),
        'data': {
            'status': 'active',
            'progress': 25
        }
    }
    
    result = sdk.publish_message('construction.projects', message)
    print(f"Message published: {result}")
    
    # Get real-time analytics
    dashboard = sdk.get_analytics_dashboard(project_id=123)
    print(f"Real-time dashboard: {dashboard}")

# Run the async function
asyncio.run(process_real_time_data())
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors
**Problem**: `401 Unauthorized` responses
**Solutions**:
- Verify API key is correct
- Check API key permissions
- Ensure API key is not expired
- Verify base URL is correct

#### 2. Rate Limiting
**Problem**: `429 Too Many Requests` responses
**Solutions**:
- Implement exponential backoff
- Reduce request frequency
- Use batch operations
- Implement caching

#### 3. Validation Errors
**Problem**: `400 Bad Request` responses
**Solutions**:
- Check required fields
- Validate data types
- Use SDK data models
- Review API documentation

#### 4. Network Issues
**Problem**: Connection timeouts or failures
**Solutions**:
- Check network connectivity
- Verify firewall settings
- Use retry logic
- Contact support if persistent

### Debug Mode

Enable debug logging in Python SDK:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

sdk = createSDK('https://api.preconstruction-intelligence.com', 'your_api_key')
```

Enable debug logging in JavaScript SDK:

```javascript
// Set console level to debug
console.debug = console.log;

const sdk = createSDK('https://api.preconstruction-intelligence.com', 'your_api_key');
```

### Health Check

Check API status:

```python
# Python
status = sdk.get_api_status()
print(f"API Status: {status}")
```

```javascript
// JavaScript
const status = await sdk.getAPIStatus();
console.log('API Status:', status);
```

## 🆘 Support

### Getting Help

- **Documentation**: [https://docs.preconstruction-intelligence.com](https://docs.preconstruction-intelligence.com)
- **API Reference**: [https://api.preconstruction-intelligence.com/docs](https://api.preconstruction-intelligence.com/docs)
- **SDK Documentation**: [https://docs.preconstruction-intelligence.com/sdks](https://docs.preconstruction-intelligence.com/sdks)
- **Support Email**: `api-support@preconstruction-intelligence.com`
- **Status Page**: [https://status.preconstruction-intelligence.com](https://status.preconstruction-intelligence.com)

### Community

- **GitHub**: [https://github.com/preconstruction-intelligence](https://github.com/preconstruction-intelligence)
- **Discord**: [https://discord.gg/preconstruction-intelligence](https://discord.gg/preconstruction-intelligence)
- **Stack Overflow**: Tag questions with `preconstruction-intelligence`

### Feedback

We welcome your feedback and suggestions:

- **Feature Requests**: Submit via GitHub issues
- **Bug Reports**: Include detailed error messages and steps to reproduce
- **Documentation**: Help improve our docs with pull requests
- **General Feedback**: Email us at `feedback@preconstruction-intelligence.com`

---

**Happy Building! 🏗️**

For the latest updates and announcements, follow us on [Twitter](https://twitter.com/preconstruction_intel) and [LinkedIn](https://linkedin.com/company/preconstruction-intelligence).
