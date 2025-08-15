# Pre-Construction Intelligence Tool

## Project Overview
An AI-powered platform that analyzes historical project data to inform tenders, estimates, and procurement decisions. Built for construction procurement and estimating teams to minimize overruns and improve bid success rates.

## Key Features
- **Historical Data Analysis**: Aggregate and analyze completed project data from Procore, Jobpac, Greentree, and ProcurePro
- **AI Risk Modeling**: Machine learning algorithms for flagging high-risk items with weather and supply chain integration
- **Supplier Scorecards**: Automated scoring based on historical performance metrics
- **Predictive Insights**: Forecasts for bid success, potential overruns, and optimal suppliers
- **Custom Dashboards**: Interactive analytics with exportable reports (PDF/Excel)
- **Multi-platform**: Web and mobile applications with voice search capabilities

## Tech Stack
- **Backend**: Python/Django with Celery for task queuing
- **Frontend**: React (web) + React Native (mobile)
- **Database**: PostgreSQL + BigQuery for analytics
- **AI/ML**: scikit-learn/TensorFlow for predictions
- **Cloud**: Azure with Kubernetes (AKS)
- **Authentication**: Azure AD with OAuth 2.0
- **Monitoring**: Azure Application Insights

## Project Structure
```
pre-con/
├── backend/                 # Django backend API
├── frontend/                # React web application
├── mobile/                  # React Native mobile app
├── ai_models/              # ML models and training scripts
├── integrations/            # External API connectors
├── docs/                   # Documentation
├── tests/                  # Test suites
├── docker/                 # Docker configurations
├── azure/                  # Azure deployment configs
└── scripts/                # Utility scripts
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker
- Azure CLI
- PostgreSQL

### Local Development Setup
1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd pre-con
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Mobile setup**:
   ```bash
   cd mobile
   npm install
   npx react-native run-ios  # or run-android
   ```

### Environment Configuration
Create `.env` files in each component directory with:
- API keys for external services
- Database credentials
- Azure configuration
- OAuth settings

## Development Workflow
1. **Phase 1**: Core integrations and basic analytics
2. **Phase 2**: AI modeling and predictive features
3. **Phase 3**: Security, optimization, and testing
4. **Phase 4**: Deployment and validation

## Testing
- Unit tests: 90% coverage target
- Integration tests with mock APIs
- Load testing for <2s response times
- Security scanning and compliance checks

## Deployment
- **Dev**: Local development environment
- **Test**: Azure staging environment
- **Prod**: Azure production with AKS

## Contributing
Follow the established coding standards and ensure all tests pass before submitting changes.

## License
Proprietary - Internal use only
