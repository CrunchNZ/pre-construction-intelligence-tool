/**
 * Pre-Construction Intelligence JavaScript SDK
 * 
 * A comprehensive JavaScript SDK for interacting with the Pre-Construction Intelligence API.
 * Provides easy access to all endpoints with proper error handling, authentication, and data validation.
 */

/**
 * Project data model
 */
class Project {
    constructor(data = {}) {
        this.id = data.id || null;
        this.name = data.name || '';
        this.description = data.description || '';
        this.status = data.status || 'planning';
        this.start_date = data.start_date || null;
        this.estimated_completion = data.estimated_completion || null;
        this.budget = data.budget || null;
        this.location = data.location || '';
        this.project_manager = data.project_manager || '';
        this.created_at = data.created_at || null;
        this.updated_at = data.updated_at || null;
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            status: this.status,
            start_date: this.start_date,
            estimated_completion: this.estimated_completion,
            budget: this.budget,
            location: this.location,
            project_manager: this.project_manager,
            created_at: this.created_at,
            updated_at: this.updated_at
        };
    }
}

/**
 * Supplier data model
 */
class Supplier {
    constructor(data = {}) {
        this.id = data.id || null;
        this.name = data.name || '';
        this.contact_person = data.contact_person || '';
        this.email = data.email || '';
        this.phone = data.phone || '';
        this.address = data.address || '';
        this.specialties = data.specialties || [];
        this.rating = data.rating || null;
        this.created_at = data.created_at || null;
        this.updated_at = data.updated_at || null;
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            contact_person: this.contact_person,
            email: this.email,
            phone: this.phone,
            address: this.address,
            specialties: this.specialties,
            rating: this.rating,
            created_at: this.created_at,
            updated_at: this.updated_at
        };
    }
}

/**
 * Risk assessment data model
 */
class RiskAssessment {
    constructor(data = {}) {
        this.id = data.id || null;
        this.project_id = data.project_id || 0;
        this.risk_type = data.risk_type || '';
        this.description = data.description || '';
        this.probability = data.probability || 'low';
        this.impact = data.impact || 'low';
        this.mitigation_strategy = data.mitigation_strategy || '';
        this.status = data.status || 'open';
        this.created_at = data.created_at || null;
        this.updated_at = data.updated_at || null;
    }

    toJSON() {
        return {
            id: this.id,
            project_id: this.project_id,
            risk_type: this.risk_type,
            description: this.description,
            probability: this.probability,
            impact: this.impact,
            mitigation_strategy: this.mitigation_strategy,
            status: this.status,
            created_at: this.created_at,
            updated_at: this.updated_at
        };
    }
}

/**
 * ML prediction data model
 */
class MLPrediction {
    constructor(data = {}) {
        this.id = data.id || null;
        this.model_name = data.model_name || '';
        this.prediction_type = data.prediction_type || '';
        this.input_data = data.input_data || {};
        this.prediction_result = data.prediction_result || {};
        this.confidence_score = data.confidence_score || null;
        this.created_at = data.created_at || null;
    }

    toJSON() {
        return {
            id: this.id,
            model_name: this.model_name,
            prediction_type: this.prediction_type,
            input_data: this.input_data,
            prediction_result: this.prediction_result,
            confidence_score: this.confidence_score,
            created_at: this.created_at
        };
    }
}

/**
 * Custom error classes
 */
class PreConstructionIntelligenceError extends Error {
    constructor(message) {
        super(message);
        this.name = 'PreConstructionIntelligenceError';
    }
}

class AuthenticationError extends PreConstructionIntelligenceError {
    constructor(message) {
        super(message);
        this.name = 'AuthenticationError';
    }
}

class ValidationError extends PreConstructionIntelligenceError {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class RateLimitError extends PreConstructionIntelligenceError {
    constructor(message) {
        super(message);
        this.name = 'RateLimitError';
    }
}

class APIError extends PreConstructionIntelligenceError {
    constructor(message, statusCode, responseData = null) {
        super(message);
        this.name = 'APIError';
        this.statusCode = statusCode;
        this.responseData = responseData;
    }
}

/**
 * Main SDK class
 */
class PreConstructionIntelligenceSDK {
    /**
     * Initialize the SDK
     * 
     * @param {string} baseUrl - Base URL for the API
     * @param {string} apiKey - API key for authentication
     * @param {string} sessionToken - Session token for authentication
     */
    constructor(baseUrl, apiKey = null, sessionToken = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.sessionToken = sessionToken;
        this.maxRetries = 3;
        this.retryDelay = 1000;
        
        // Configure default headers
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'User-Agent': 'PreConstructionIntelligence-JavaScript-SDK/1.0.0'
        };

        if (apiKey) {
            this.defaultHeaders['Authorization'] = `Bearer ${apiKey}`;
        }

        console.log(`SDK initialized for ${this.baseUrl}`);
    }

    /**
     * Make HTTP request with retry logic and error handling
     * 
     * @param {string} method - HTTP method
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} params - Query parameters
     * @param {number} retryCount - Current retry attempt
     * @returns {Promise<Object>} Response data
     */
    async _makeRequest(method, endpoint, data = null, params = null, retryCount = 0) {
        const url = new URL(endpoint, this.baseUrl);
        
        // Add query parameters
        if (params) {
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined) {
                    if (Array.isArray(params[key])) {
                        params[key].forEach(value => url.searchParams.append(key, value));
                    } else {
                        url.searchParams.append(key, params[key]);
                    }
                }
            });
        }

        // Prepare request options
        const options = {
            method: method.toUpperCase(),
            headers: { ...this.defaultHeaders },
            credentials: 'include' // Include cookies for session authentication
        };

        // Add request body for POST/PUT requests
        if (data && (method.toUpperCase() === 'POST' || method.toUpperCase() === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url.toString(), options);
            
            // Handle different response status codes
            if (response.ok) {
                if (response.status === 204) {
                    return {};
                }
                return await response.json();
            } else if (response.status === 400) {
                const errorData = await response.json().catch(() => ({}));
                throw new ValidationError(`Validation failed: ${errorData.error || 'Unknown error'}`);
            } else if (response.status === 401) {
                throw new AuthenticationError('Authentication failed. Please check your credentials.');
            } else if (response.status === 403) {
                throw new APIError('Access denied. Insufficient permissions.', 403);
            } else if (response.status === 404) {
                throw new APIError('Resource not found.', 404);
            } else if (response.status === 429) {
                if (retryCount < this.maxRetries) {
                    const waitTime = this.retryDelay * Math.pow(2, retryCount);
                    console.warn(`Rate limited. Retrying in ${waitTime}ms...`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    return this._makeRequest(method, endpoint, data, params, retryCount + 1);
                } else {
                    throw new RateLimitError('Rate limit exceeded. Please try again later.');
                }
            } else if (response.status >= 500) {
                if (retryCount < this.maxRetries) {
                    const waitTime = this.retryDelay * Math.pow(2, retryCount);
                    console.warn(`Server error. Retrying in ${waitTime}ms...`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    return this._makeRequest(method, endpoint, data, params, retryCount + 1);
                } else {
                    throw new APIError(`Server error: ${response.status}`, response.status);
                }
            } else {
                throw new APIError(`Unexpected response: ${response.status}`, response.status);
            }
        } catch (error) {
            if (error instanceof PreConstructionIntelligenceError) {
                throw error;
            }
            
            if (retryCount < this.maxRetries) {
                const waitTime = this.retryDelay * Math.pow(2, retryCount);
                console.warn(`Request failed. Retrying in ${waitTime}ms...`);
                await new Promise(resolve => setTimeout(resolve, waitTime));
                return this._makeRequest(method, endpoint, data, params, retryCount + 1);
            } else {
                throw new APIError(`Request failed: ${error.message}`, 0);
            }
        }
    }

    // Core API Methods

    /**
     * Get list of projects with filtering and pagination
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Projects and pagination info
     */
    async getProjects(options = {}) {
        const {
            page = 1,
            pageSize = 20,
            search = null,
            status = null,
            startDate = null,
            endDate = null,
            ordering = null
        } = options;

        const params = { page, page_size: pageSize };
        
        if (search) params.search = search;
        if (status) params.status = status;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (ordering) params.ordering = ordering;

        return this._makeRequest('GET', '/api/projects/', null, params);
    }

    /**
     * Get a specific project by ID
     * 
     * @param {number} projectId - Project ID
     * @returns {Promise<Object>} Project data
     */
    async getProject(projectId) {
        return this._makeRequest('GET', `/api/projects/${projectId}/`);
    }

    /**
     * Create a new project
     * 
     * @param {Project} project - Project object
     * @returns {Promise<Object>} Created project data
     */
    async createProject(project) {
        const data = project.toJSON();
        // Remove null values and convert dates to strings
        Object.keys(data).forEach(key => {
            if (data[key] === null) delete data[key];
            if (data[key] instanceof Date) data[key] = data[key].toISOString().split('T')[0];
        });

        return this._makeRequest('POST', '/api/projects/', data);
    }

    /**
     * Update an existing project
     * 
     * @param {number} projectId - Project ID
     * @param {Project} project - Updated project data
     * @returns {Promise<Object>} Updated project data
     */
    async updateProject(projectId, project) {
        const data = project.toJSON();
        // Remove null values and convert dates to strings
        Object.keys(data).forEach(key => {
            if (data[key] === null) delete data[key];
            if (data[key] instanceof Date) data[key] = data[key].toISOString().split('T')[0];
        });

        return this._makeRequest('PUT', `/api/projects/${projectId}/`, data);
    }

    /**
     * Delete a project
     * 
     * @param {number} projectId - Project ID
     * @returns {Promise<boolean>} True if successful
     */
    async deleteProject(projectId) {
        await this._makeRequest('DELETE', `/api/projects/${projectId}/`);
        return true;
    }

    // Suppliers API Methods

    /**
     * Get list of suppliers with filtering and pagination
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Suppliers and pagination info
     */
    async getSuppliers(options = {}) {
        const {
            page = 1,
            pageSize = 20,
            search = null,
            specialties = null,
            minRating = null,
            ordering = null
        } = options;

        const params = { page, page_size: pageSize };
        
        if (search) params.search = search;
        if (specialties) params.specialties = specialties;
        if (minRating) params.min_rating = minRating;
        if (ordering) params.ordering = ordering;

        return this._makeRequest('GET', '/api/suppliers/', null, params);
    }

    /**
     * Get a specific supplier by ID
     * 
     * @param {number} supplierId - Supplier ID
     * @returns {Promise<Object>} Supplier data
     */
    async getSupplier(supplierId) {
        return this._makeRequest('GET', `/api/suppliers/${supplierId}/`);
    }

    /**
     * Create a new supplier
     * 
     * @param {Supplier} supplier - Supplier object
     * @returns {Promise<Object>} Created supplier data
     */
    async createSupplier(supplier) {
        const data = supplier.toJSON();
        Object.keys(data).forEach(key => {
            if (data[key] === null) delete data[key];
        });

        return this._makeRequest('POST', '/api/suppliers/', data);
    }

    // Risk Analysis API Methods

    /**
     * Get list of risk assessments with filtering and pagination
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Risks and pagination info
     */
    async getRisks(options = {}) {
        const {
            projectId = null,
            page = 1,
            pageSize = 20,
            riskType = null,
            status = null,
            probability = null,
            impact = null
        } = options;

        const params = { page, page_size: pageSize };
        
        if (projectId) params.project_id = projectId;
        if (riskType) params.risk_type = riskType;
        if (status) params.status = status;
        if (probability) params.probability = probability;
        if (impact) params.impact = impact;

        return this._makeRequest('GET', '/api/risks/', null, params);
    }

    /**
     * Create a new risk assessment
     * 
     * @param {RiskAssessment} risk - Risk assessment object
     * @returns {Promise<Object>} Created risk assessment data
     */
    async createRiskAssessment(risk) {
        const data = risk.toJSON();
        Object.keys(data).forEach(key => {
            if (data[key] === null) delete data[key];
        });

        return this._makeRequest('POST', '/api/risks/', data);
    }

    // AI/ML API Methods

    /**
     * Get list of ML predictions
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Predictions and pagination info
     */
    async getMLPredictions(options = {}) {
        const {
            modelName = null,
            predictionType = null,
            page = 1,
            pageSize = 20
        } = options;

        const params = { page, page_size: pageSize };
        
        if (modelName) params.model_name = modelName;
        if (predictionType) params.prediction_type = predictionType;

        return this._makeRequest('GET', '/api/ai/predictions/', null, params);
    }

    /**
     * Create a new ML prediction request
     * 
     * @param {MLPrediction} prediction - ML prediction object
     * @returns {Promise<Object>} Created prediction data
     */
    async createMLPrediction(prediction) {
        const data = prediction.toJSON();
        Object.keys(data).forEach(key => {
            if (data[key] === null) delete data[key];
        });

        return this._makeRequest('POST', '/api/ai/predictions/', data);
    }

    /**
     * Train a new ML model
     * 
     * @param {string} modelName - Name of the model
     * @param {string} modelType - Type of model
     * @param {Object} trainingData - Training data configuration
     * @param {Object} parameters - Model training parameters
     * @returns {Promise<Object>} Training job information
     */
    async trainMLModel(modelName, modelType, trainingData, parameters = null) {
        const data = {
            model_name: modelName,
            model_type: modelType,
            training_data: trainingData
        };

        if (parameters) data.parameters = parameters;

        return this._makeRequest('POST', '/api/ai/models/train/', data);
    }

    // Analytics API Methods

    /**
     * Get analytics dashboard data
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Analytics dashboard data
     */
    async getAnalyticsDashboard(options = {}) {
        const {
            projectId = null,
            startDate = null,
            endDate = null
        } = options;

        const params = {};
        
        if (projectId) params.project_id = projectId;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        return this._makeRequest('GET', '/api/analytics/dashboard/', null, params);
    }

    /**
     * Get analytics for a specific project
     * 
     * @param {number} projectId - Project ID
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Project analytics data
     */
    async getProjectAnalytics(projectId, options = {}) {
        const {
            startDate = null,
            endDate = null
        } = options;

        const params = {};
        
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        return this._makeRequest('GET', `/api/analytics/projects/${projectId}/`, null, params);
    }

    // Integration API Methods

    /**
     * Get list of available integrations
     * 
     * @returns {Promise<Object>} List of integrations
     */
    async getIntegrations() {
        return this._makeRequest('GET', '/api/integrations/');
    }

    /**
     * Trigger synchronization for a specific integration
     * 
     * @param {string} integrationName - Name of the integration
     * @param {number} projectId - Optional project ID to sync
     * @returns {Promise<Object>} Sync job information
     */
    async syncIntegration(integrationName, projectId = null) {
        const data = { integration_name: integrationName };
        if (projectId) data.project_id = projectId;

        return this._makeRequest('POST', '/api/integrations/sync/', data);
    }

    // Kafka/Real-time API Methods

    /**
     * Get list of available Kafka topics
     * 
     * @returns {Promise<Object>} List of Kafka topics
     */
    async getKafkaTopics() {
        return this._makeRequest('GET', '/api/kafka/topics/');
    }

    /**
     * Publish a message to a Kafka topic
     * 
     * @param {string} topic - Kafka topic name
     * @param {Object} message - Message data
     * @returns {Promise<Object>} Publication confirmation
     */
    async publishMessage(topic, message) {
        const data = { topic, message };
        return this._makeRequest('POST', '/api/kafka/publish/', data);
    }

    // Utility Methods

    /**
     * Get API status and health information
     * 
     * @returns {Promise<Object>} API status information
     */
    async getAPIStatus() {
        return this._makeRequest('GET', '/api/status/');
    }

    /**
     * Get API documentation schema
     * 
     * @returns {Promise<Object>} OpenAPI schema
     */
    async getAPIDocumentation() {
        return this._makeRequest('GET', '/api/schema/');
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    // CommonJS
    module.exports = {
        PreConstructionIntelligenceSDK,
        Project,
        Supplier,
        RiskAssessment,
        MLPrediction,
        PreConstructionIntelligenceError,
        AuthenticationError,
        ValidationError,
        RateLimitError,
        APIError
    };
} else if (typeof define === 'function' && define.amd) {
    // AMD
    define([], function() {
        return {
            PreConstructionIntelligenceSDK,
            Project,
            Supplier,
            RiskAssessment,
            MLPrediction,
            PreConstructionIntelligenceError,
            AuthenticationError,
            ValidationError,
            RateLimitError,
            APIError
        };
    });
} else if (typeof window !== 'undefined') {
    // Browser global
    window.PreConstructionIntelligenceSDK = PreConstructionIntelligenceSDK;
    window.Project = Project;
    window.Supplier = Supplier;
    window.RiskAssessment = RiskAssessment;
    window.MLPrediction = MLPrediction;
    window.PreConstructionIntelligenceError = PreConstructionIntelligenceError;
    window.AuthenticationError = AuthenticationError;
    window.ValidationError = ValidationError;
    window.RateLimitError = RateLimitError;
    window.APIError = APIError;
}

// Convenience function for quick SDK initialization
function createSDK(baseUrl, apiKey = null, sessionToken = null) {
    return new PreConstructionIntelligenceSDK(baseUrl, apiKey, sessionToken);
}

// Export convenience function
if (typeof module !== 'undefined' && module.exports) {
    module.exports.createSDK = createSDK;
} else if (typeof define === 'function' && define.amd) {
    // AMD - already included in main export
} else if (typeof window !== 'undefined') {
    window.createSDK = createSDK;
}
