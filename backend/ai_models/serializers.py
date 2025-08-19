from rest_framework import serializers
from .models import MLModel, ModelTrainingHistory, FeatureEngineering, ModelPrediction


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for ML Model"""
    
    created_by = serializers.ReadOnlyField(source='created_by.username')
    model_type_display = serializers.CharField(source='get_model_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.ReadOnlyField()
    performance_summary = serializers.ReadOnlyField()
    
    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'model_type', 'model_type_display', 'version', 'description',
            'status', 'status_display', 'algorithm', 'hyperparameters', 'feature_columns',
            'target_column', 'model_file_path', 'scaler_file_path', 'encoder_file_path',
            'accuracy', 'precision', 'recall', 'f1_score', 'mae', 'rmse',
            'created_by', 'created_at', 'updated_at', 'last_trained',
            'training_data_size', 'validation_data_size', 'training_duration',
            'is_active', 'performance_summary'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_active', 'performance_summary'
        ]


class MLModelCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ML Model"""
    
    class Meta:
        model = MLModel
        fields = [
            'name', 'model_type', 'version', 'description', 'algorithm',
            'hyperparameters', 'feature_columns', 'target_column'
        ]


class MLModelUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ML Model"""
    
    class Meta:
        model = MLModel
        fields = [
            'description', 'status', 'hyperparameters', 'feature_columns',
            'target_column', 'model_file_path', 'scaler_file_path', 'encoder_file_path'
        ]


class ModelTrainingHistorySerializer(serializers.ModelSerializer):
    """Serializer for Model Training History"""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    training_time_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = ModelTrainingHistory
        fields = [
            'id', 'model', 'model_name', 'training_run_id', 'training_accuracy',
            'validation_accuracy', 'training_loss', 'validation_loss', 'precision',
            'recall', 'f1_score', 'epochs', 'batch_size', 'learning_rate',
            'hyperparameters', 'started_at', 'completed_at', 'duration',
            'data_size', 'status', 'status_display', 'error_message',
            'training_time_minutes'
        ]
        read_only_fields = ['id', 'model_name', 'training_time_minutes']


class ModelTrainingHistoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Model Training History"""
    
    class Meta:
        model = ModelTrainingHistory
        fields = [
            'model', 'training_run_id', 'training_accuracy', 'validation_accuracy',
            'training_loss', 'validation_loss', 'precision', 'recall', 'f1_score',
            'epochs', 'batch_size', 'learning_rate', 'hyperparameters',
            'started_at', 'completed_at', 'duration', 'data_size', 'status'
        ]


class FeatureEngineeringSerializer(serializers.ModelSerializer):
    """Serializer for Feature Engineering"""
    
    created_by = serializers.ReadOnlyField(source='created_by.username')
    scaling_method_display = serializers.CharField(source='get_scaling_method_display', read_only=True)
    encoding_method_display = serializers.CharField(source='get_encoding_method_display', read_only=True)
    
    class Meta:
        model = FeatureEngineering
        fields = [
            'id', 'name', 'description', 'input_features', 'output_features',
            'transformations', 'scaling_method', 'scaling_method_display',
            'encoding_method', 'encoding_method_display', 'validation_rules',
            'data_quality_checks', 'created_by', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeatureEngineeringCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Feature Engineering"""
    
    class Meta:
        model = FeatureEngineering
        fields = [
            'name', 'description', 'input_features', 'output_features',
            'transformations', 'scaling_method', 'encoding_method',
            'validation_rules', 'data_quality_checks'
        ]


class ModelPredictionSerializer(serializers.ModelSerializer):
    """Serializer for Model Prediction"""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    is_accurate = serializers.ReadOnlyField()
    
    class Meta:
        model = ModelPrediction
        fields = [
            'id', 'model', 'model_name', 'input_features', 'input_data_hash',
            'prediction_value', 'prediction_confidence', 'prediction_interval_lower',
            'prediction_interval_upper', 'actual_value', 'prediction_error',
            'created_at', 'project_id', 'user_id', 'is_accurate'
        ]
        read_only_fields = ['id', 'input_data_hash', 'created_at', 'is_accurate']


class ModelPredictionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Model Prediction"""
    
    class Meta:
        model = ModelPrediction
        fields = [
            'model', 'input_features', 'prediction_value', 'prediction_confidence',
            'prediction_interval_lower', 'prediction_interval_upper', 'actual_value',
            'project_id', 'user_id'
        ]


class ModelPerformanceSerializer(serializers.Serializer):
    """Serializer for model performance metrics"""
    
    model_id = serializers.IntegerField()
    model_name = serializers.CharField()
    model_type = serializers.CharField()
    accuracy = serializers.FloatField(allow_null=True)
    precision = serializers.FloatField(allow_null=True)
    recall = serializers.FloatField(allow_null=True)
    f1_score = serializers.FloatField(allow_null=True)
    mae = serializers.FloatField(allow_null=True)
    rmse = serializers.FloatField(allow_null=True)
    last_trained = serializers.DateTimeField(allow_null=True)
    total_predictions = serializers.IntegerField()
    recent_accuracy = serializers.FloatField(allow_null=True)


class TrainingMetricsSerializer(serializers.Serializer):
    """Serializer for training metrics over time"""
    
    training_run_id = serializers.CharField()
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField()
    training_accuracy = serializers.FloatField()
    validation_accuracy = serializers.FloatField()
    training_loss = serializers.FloatField()
    validation_loss = serializers.FloatField()
    duration_minutes = serializers.FloatField()
    status = serializers.CharField()


class PredictionRequestSerializer(serializers.Serializer):
    """Serializer for prediction requests"""
    
    model_id = serializers.IntegerField()
    input_features = serializers.JSONField()
    project_id = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.CharField(required=False, allow_blank=True)
    include_confidence = serializers.BooleanField(default=False)
    include_intervals = serializers.BooleanField(default=False)


class PredictionResponseSerializer(serializers.Serializer):
    """Serializer for prediction responses"""
    
    prediction_id = serializers.IntegerField()
    prediction_value = serializers.FloatField()
    prediction_confidence = serializers.FloatField(allow_null=True)
    prediction_interval_lower = serializers.FloatField(allow_null=True)
    prediction_interval_upper = serializers.FloatField(allow_null=True)
    model_name = serializers.CharField()
    model_version = serializers.CharField()
    created_at = serializers.DateTimeField()
    processing_time_ms = serializers.FloatField()
