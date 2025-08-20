# Pre-Construction Intelligence SDKs

This directory contains comprehensive SDKs for the Pre-Construction Intelligence platform, providing easy access to all API endpoints with proper error handling, authentication, and data validation.

## 📚 Available SDKs

- **Python SDK** (`python_sdk.py`) - Full-featured Python SDK with type hints and data classes
- **JavaScript SDK** (`javascript_sdk.js`) - Universal JavaScript/TypeScript SDK for browser and Node.js

## 🚀 Quick Start

### Python SDK

#### Installation

```bash
# Copy the SDK file to your project
cp python_sdk.py your_project/

# Install required dependencies
pip install requests
```

#### Basic Usage

```python
from python_sdk import createSDK, Project
from datetime import date

# Initialize the SDK
sdk = createSDK(
    base_url='https://api.preconstruction-intelligence.com',
    api_key='your_api_key_here'
)

# Create a project
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

# Create the project via API
result = sdk.create_project(project)
print(f"Project created with ID: {result['id']}")

# Get projects with filtering
projects = sdk.get_projects(
    page=1,
    page_size=20,
    search='office',
    status='active',
    ordering='-created_at'
)

print(f"Found {len(projects['results'])} projects")
```

### JavaScript SDK

#### Installation

```bash
# Copy the SDK file to your project
cp javascript_sdk.js your_project/

# For Node.js projects, you can also use npm
npm install @preconstruction-intelligence/js-sdk
```

#### Basic Usage

```javascript
import { createSDK, Project } from './javascript_sdk.js';

// Initialize the SDK
const sdk = createSDK(
    'https://api.preconstruction-intelligence.com',
    'your_api_key_here'
);

// Create a project
const project = new Project({
    name: 'Downtown Office Complex',
    description: 'Modern office building with sustainable features',
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

// Get projects with filtering
const projects = await sdk.getProjects({
    page: 1,
    pageSize: 20,
    search: 'office',
    status: 'active',
    ordering: '-created_at'
});

console.log(`Found ${projects.results.length} projects`);
```

## 🔐 Authentication

### API Key Authentication

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

### Session Authentication

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

## 📊 Data Models

### Project

```python
# Python
from python_sdk import Project

project = Project(
    id=1,
    name='Project Name',
    description='Project description',
    status='planning',  # planning, active, completed, on_hold
    start_date=date(2024, 6, 1),
    estimated_completion=date(2025, 12, 31),
    budget=25000000,
    location='Project location',
    project_manager='Manager name'
)
```

```javascript
// JavaScript
import { Project } from './javascript_sdk.js';

const project = new Project({
    id: 1,
    name: 'Project Name',
    description: 'Project description',
    status: 'planning', // planning, active, completed, on_hold
    start_date: '2024-06-01',
    estimated_completion: '2025-12-31',
    budget: 25000000,
    location: 'Project location',
    project_manager: 'Manager name'
});
```

### Supplier

```python
# Python
from python_sdk import Supplier

supplier = Supplier(
    id=1,
    name='Supplier Name',
    contact_person='Contact Person',
    email='contact@supplier.com',
    phone='555-0123',
    address='Supplier Address',
    specialties=['electrical', 'plumbing'],
    rating=4.8
)
```

```javascript
// JavaScript
import { Supplier } from './javascript_sdk.js';

const supplier = new Supplier({
    id: 1,
    name: 'Supplier Name',
    contact_person: 'Contact Person',
    email: 'contact@supplier.com',
    phone: '555-0123',
    address: 'Supplier Address',
    specialties: ['electrical', 'plumbing'],
    rating: 4.8
});
```

### Risk Assessment

```python
# Python
from python_sdk import RiskAssessment

risk = RiskAssessment(
    id=1,
    project_id=1,
    risk_type='financial',
    description='Risk description',
    probability='medium',  # low, medium, high
    impact='high',         # low, medium, high
    mitigation_strategy='Mitigation strategy',
    status='open'          # open, mitigated, closed
)
```

```javascript
// JavaScript
import { RiskAssessment } from './javascript_sdk.js';

const risk = new RiskAssessment({
    id: 1,
    project_id: 1,
    risk_type: 'financial',
    description: 'Risk description',
    probability: 'medium', // low, medium, high
    impact: 'high',        // low, medium, high
    mitigation_strategy: 'Mitigation strategy',
    status: 'open'         // open, mitigated, closed
});
```

### ML Prediction

```python
# Python
from python_sdk import MLPrediction

prediction = MLPrediction(
    id=1,
    model_name='cost_prediction_v2',
    prediction_type='cost_prediction',
    input_data={
        'project_size': 50000,
        'location': 'urban',
        'complexity': 'high'
    },
    prediction_result={
        'estimated_cost': 27500000,
        'confidence': 0.85
    },
    confidence_score=0.85
)
```

```javascript
// JavaScript
import { MLPrediction } from './javascript_sdk.js';

const prediction = new MLPrediction({
    id: 1,
    model_name: 'cost_prediction_v2',
    prediction_type: 'cost_prediction',
    input_data: {
        project_size: 50000,
        location: 'urban',
        complexity: 'high'
    },
    prediction_result: {
        estimated_cost: 27500000,
        confidence: 0.85
    },
    confidence_score: 0.85
});
```

## 🔌 Core API Methods

### Projects

```python
# Python SDK
# Get projects with filtering
projects = sdk.get_projects(
    page=1,
    page_size=20,
    search='office',
    status='active',
    start_date='2024-01-01',
    end_date='2024-12-31',
    ordering='-created_at'
)

# Get specific project
project = sdk.get_project(project_id=123)

# Create project
result = sdk.create_project(project)

# Update project
result = sdk.update_project(project_id=123, project=updated_project)

# Delete project
sdk.delete_project(project_id=123)
```

```javascript
// JavaScript SDK
// Get projects with filtering
const projects = await sdk.getProjects({
    page: 1,
    pageSize: 20,
    search: 'office',
    status: 'active',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    ordering: '-created_at'
});

// Get specific project
const project = await sdk.getProject(123);

// Create project
const result = await sdk.createProject(project);

// Update project
const result = await sdk.updateProject(123, updatedProject);

// Delete project
await sdk.deleteProject(123);
```

### Suppliers

```python
# Python SDK
# Get suppliers with filtering
suppliers = sdk.get_suppliers(
    page=1,
    page_size=20,
    search='electrical',
    specialties=['electrical', 'plumbing'],
    min_rating=4.0,
    ordering='-rating'
)

# Get specific supplier
supplier = sdk.get_supplier(supplier_id=456)

# Create supplier
result = sdk.create_supplier(supplier)
```

```javascript
// JavaScript SDK
// Get suppliers with filtering
const suppliers = await sdk.getSuppliers({
    page: 1,
    pageSize: 20,
    search: 'electrical',
    specialties: ['electrical', 'plumbing'],
    minRating: 4.0,
    ordering: '-rating'
});

// Get specific supplier
const supplier = await sdk.getSupplier(456);

// Create supplier
const result = await sdk.createSupplier(supplier);
```

### Risk Analysis

```python
# Python SDK
# Get risks with filtering
risks = sdk.get_risks(
    project_id=123,
    page=1,
    page_size=20,
    risk_type='financial',
    status='open',
    probability='high',
    impact='high'
)

# Create risk assessment
result = sdk.create_risk_assessment(risk)
```

```javascript
// JavaScript SDK
// Get risks with filtering
const risks = await sdk.getRisks({
    projectId: 123,
    page: 1,
    pageSize: 20,
    riskType: 'financial',
    status: 'open',
    probability: 'high',
    impact: 'high'
});

// Create risk assessment
const result = await sdk.createRiskAssessment(risk);
```

## 🤖 AI/ML Integration

### ML Predictions

```python
# Python SDK
# Get ML predictions
predictions = sdk.get_ml_predictions(
    model_name='cost_prediction_v2',
    prediction_type='cost_prediction',
    page=1,
    page_size=20
)

# Create ML prediction
result = sdk.create_ml_prediction(prediction)

# Train ML model
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

```javascript
// JavaScript SDK
// Get ML predictions
const predictions = await sdk.getMLPredictions({
    modelName: 'cost_prediction_v2',
    predictionType: 'cost_prediction',
    page: 1,
    pageSize: 20
});

// Create ML prediction
const result = await sdk.createMLPrediction(prediction);

// Train ML model
const trainingJob = await sdk.trainMLModel(
    'cost_prediction_v3',
    'cost_prediction',
    {
        data_source: 'historical_projects',
        features: ['size', 'location', 'complexity'],
        target: 'final_cost'
    },
    {
        algorithm: 'xgboost',
        max_depth: 6
    }
);
```

## 📡 Real-time Data Streaming

### Kafka Topics

```python
# Python SDK
# Get available topics
topics = sdk.get_kafka_topics()

# Publish message
message = {
    'event_type': 'project.updated',
    'project_id': 123,
    'timestamp': datetime.now().isoformat(),
    'data': {
        'name': 'Updated Project',
        'status': 'active',
        'progress': 50
    }
}

result = sdk.publish_message('construction.projects', message)
```

```javascript
// JavaScript SDK
// Get available topics
const topics = await sdk.getKafkaTopics();

// Publish message
const message = {
    event_type: 'project.updated',
    project_id: 123,
    timestamp: new Date().toISOString(),
    data: {
        name: 'Updated Project',
        status: 'active',
        progress: 50
    }
};

const result = await sdk.publishMessage('construction.projects', message);
```

## 📊 Analytics

### Dashboard Analytics

```python
# Python SDK
# Get analytics dashboard
dashboard = sdk.get_analytics_dashboard(
    project_id=123,
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Get project analytics
project_analytics = sdk.get_project_analytics(
    project_id=123,
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

```javascript
// JavaScript SDK
// Get analytics dashboard
const dashboard = await sdk.getAnalyticsDashboard({
    projectId: 123,
    startDate: '2024-01-01',
    endDate: '2024-12-31'
});

// Get project analytics
const projectAnalytics = await sdk.getProjectAnalytics(123, {
    startDate: '2024-01-01',
    endDate: '2024-12-31'
});
```

## 🔗 Integrations

### External System Integration

```python
# Python SDK
# Get available integrations
integrations = sdk.get_integrations()

# Sync integration
sync_job = sdk.sync_integration(
    integration_name='procore',
    project_id=123
)
```

```javascript
// JavaScript SDK
// Get available integrations
const integrations = await sdk.getIntegrations();

// Sync integration
const syncJob = await sdk.syncIntegration('procore', 123);
```

## ❌ Error Handling

### Python SDK

```python
from python_sdk import (
    PreConstructionIntelligenceError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    APIError
)

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

### JavaScript SDK

```javascript
import {
    PreConstructionIntelligenceError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    APIError
} from './javascript_sdk.js';

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
- Store API keys securely using environment variables
- Never expose API keys in client-side code
- Rotate API keys regularly
- Use the principle of least privilege

### 2. Error Handling
- Always handle errors gracefully
- Implement retry logic for transient failures
- Log errors for debugging
- Provide user-friendly error messages

### 3. Rate Limiting
- The SDKs automatically handle rate limiting with exponential backoff
- Monitor rate limit usage
- Implement caching strategies when possible

### 4. Data Validation
- Use SDK data models for type safety
- Validate data before sending
- Handle required vs optional fields properly

### 5. Performance
- Use pagination for large datasets
- Implement caching strategies
- Use async operations when possible
- Monitor API response times

## 🔧 Configuration

### Environment Variables

```bash
# Python
export PRECONSTRUCTION_API_KEY="your_api_key_here"
export PRECONSTRUCTION_BASE_URL="https://api.preconstruction-intelligence.com"

# JavaScript
export PRECONSTRUCTION_API_KEY="your_api_key_here"
export PRECONSTRUCTION_BASE_URL="https://api.preconstruction-intelligence.com"
```

### SDK Configuration

```python
# Python SDK
sdk = createSDK(
    base_url=os.getenv('PRECONSTRUCTION_BASE_URL'),
    api_key=os.getenv('PRECONSTRUCTION_API_KEY')
)
```

```javascript
// JavaScript SDK
const sdk = createSDK(
    process.env.PRECONSTRUCTION_BASE_URL,
    process.env.PRECONSTRUCTION_API_KEY
);
```

## 📖 Examples

### Complete Project Management Workflow

```python
from python_sdk import createSDK, Project, Supplier, RiskAssessment
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
from python_sdk import createSDK

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

## 🆘 Support

### Getting Help

- **Documentation**: [https://docs.preconstruction-intelligence.com](https://docs.preconstruction-intelligence.com)
- **API Reference**: [https://api.preconstruction-intelligence.com/docs](https://api.preconstruction-intelligence.com/docs)
- **Support Email**: `api-support@preconstruction-intelligence.com`
- **Status Page**: [https://status.preconstruction-intelligence.com](https://status.preconstruction-intelligence.com)

### Community

- **GitHub**: [https://github.com/preconstruction-intelligence](https://github.com/preconstruction-intelligence)
- **Discord**: [https://discord.gg/preconstruction-intelligence](https://discord.gg/preconstruction-intelligence)
- **Stack Overflow**: Tag questions with `preconstruction-intelligence`

---

**Happy Building! 🏗️**

For the latest updates and announcements, follow us on [Twitter](https://twitter.com/preconstruction_intel) and [LinkedIn](https://linkedin.com/company/preconstruction-intelligence).
