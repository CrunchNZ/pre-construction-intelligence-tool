"""
Procore Integration Package

This package provides integration with Procore construction management system,
including project data synchronization, analytics, and real-time updates.

Key Components:
- API Client: Handles authentication and API communication
- Data Models: Represents Procore entities in our system
- Sync Service: Manages data synchronization and updates
- API Endpoints: RESTful endpoints for Procore data access
- Monitoring: Health checks and performance monitoring
- Tasks: Automated synchronization and maintenance tasks

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

default_app_config = 'integrations.procore.apps.ProcoreConfig'
