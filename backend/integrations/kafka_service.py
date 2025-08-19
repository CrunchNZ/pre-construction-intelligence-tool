"""
Kafka Service for Real-time Data Streaming

This module provides a comprehensive Kafka integration service for the Pre-Construction
Intelligence Tool, enabling real-time data streaming from various construction management
systems and external integrations.

Features:
- Producer/Consumer management for different data types
- Topic management and configuration
- Data serialization/deserialization
- Error handling and retry mechanisms
- Performance monitoring and metrics
- Integration with Django models and Celery tasks

Author: Pre-Construction Intelligence Team
Date: December 2024
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.producer.future import Future
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class KafkaConfig:
    """Configuration for Kafka connection and topics."""
    bootstrap_servers: List[str]
    security_protocol: str = 'PLAINTEXT'
    sasl_mechanism: Optional[str] = None
    sasl_plain_username: Optional[str] = None
    sasl_plain_password: Optional[str] = None
    ssl_check_hostname: bool = False
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None


@dataclass
class TopicConfig:
    """Configuration for Kafka topics."""
    name: str
    num_partitions: int = 1
    replication_factor: int = 1
    retention_ms: int = 604800000  # 7 days
    cleanup_policy: str = 'delete'
    compression_type: str = 'gzip'


class KafkaMessage:
    """Represents a Kafka message with metadata."""
    
    def __init__(self, topic: str, key: str, value: Any, headers: Optional[Dict] = None):
        self.topic = topic
        self.key = key
        self.value = value
        self.headers = headers or {}
        self.timestamp = datetime.utcnow()
        self.message_id = f"{topic}_{key}_{int(time.time() * 1000)}"
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary format."""
        return {
            'topic': self.topic,
            'key': self.key,
            'value': self.value,
            'headers': self.headers,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id
        }
    
    def __str__(self) -> str:
        return f"KafkaMessage(topic={self.topic}, key={self.key}, id={self.message_id})"


class KafkaProducerService:
    """Service for producing messages to Kafka topics."""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer = None
        self._lock = threading.Lock()
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize the Kafka producer with configuration."""
        try:
            producer_config = {
                'bootstrap_servers': self.config.bootstrap_servers,
                'security_protocol': self.config.security_protocol,
                'value_serializer': lambda v: json.dumps(v, default=str).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None,
                'acks': 'all',
                'retries': 3,
                'batch_size': 16384,
                'linger_ms': 5,

                'max_in_flight_requests_per_connection': 5,
                'request_timeout_ms': 30000,
                'delivery_timeout_ms': 120000,
            }
            
            if self.config.sasl_mechanism:
                producer_config.update({
                    'sasl_mechanism': self.config.sasl_mechanism,
                    'sasl_plain_username': self.config.sasl_plain_username,
                    'sasl_plain_password': self.config.sasl_plain_password,
                })
            
            if self.config.ssl_cafile:
                producer_config.update({
                    'ssl_check_hostname': self.config.ssl_check_hostname,
                    'ssl_cafile': self.config.ssl_cafile,
                    'ssl_certfile': self.config.ssl_certfile,
                    'ssl_keyfile': self.config.ssl_keyfile,
                })
            
            self.producer = KafkaProducer(**producer_config)
            logger.info(f"Kafka producer initialized successfully for {self.config.bootstrap_servers}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def send_message(self, topic: str, key: str, value: Any, 
                    headers: Optional[Dict] = None) -> Future:
        """
        Send a message to a Kafka topic.
        
        Args:
            topic: Target topic name
            key: Message key
            value: Message value
            headers: Optional message headers
            
        Returns:
            Future object for tracking message delivery
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not initialized")
        
        try:
            message_headers = []
            if headers:
                for k, v in headers.items():
                    message_headers.append((k, str(v).encode('utf-8')))
            
            future = self.producer.send(
                topic=topic,
                key=key,
                value=value,
                headers=message_headers
            )
            
            logger.debug(f"Message sent to topic {topic} with key {key}")
            return future
            
        except Exception as e:
            logger.error(f"Failed to send message to topic {topic}: {e}")
            raise
    
    def send_message_sync(self, topic: str, key: str, value: Any, 
                         headers: Optional[Dict] = None, timeout: int = 30) -> bool:
        """
        Send a message synchronously with delivery confirmation.
        
        Args:
            topic: Target topic name
            key: Message key
            value: Message value
            headers: Optional message headers
            timeout: Timeout in seconds for delivery confirmation
            
        Returns:
            True if message was delivered successfully, False otherwise
        """
        try:
            future = self.send_message(topic, key, value, headers)
            record_metadata = future.get(timeout=timeout)
            
            logger.info(f"Message delivered to {record_metadata.topic} "
                       f"partition {record_metadata.partition} "
                       f"offset {record_metadata.offset}")
            return True
            
        except KafkaTimeoutError:
            logger.error(f"Message delivery timeout for topic {topic}")
            return False
        except Exception as e:
            logger.error(f"Failed to deliver message to topic {topic}: {e}")
            return False
    
    def send_batch(self, messages: List[KafkaMessage]) -> List[Future]:
        """
        Send multiple messages in batch.
        
        Args:
            messages: List of KafkaMessage objects
            
        Returns:
            List of Future objects for tracking delivery
        """
        futures = []
        for message in messages:
            future = self.send_message(
                topic=message.topic,
                key=message.key,
                value=message.value,
                headers=message.headers
            )
            futures.append(future)
        
        return futures
    
    def flush(self, timeout: int = 30):
        """Flush all pending messages."""
        if self.producer:
            self.producer.flush(timeout=timeout)
    
    def close(self):
        """Close the producer and flush remaining messages."""
        if self.producer:
            self.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


class KafkaConsumerService:
    """Service for consuming messages from Kafka topics."""
    
    def __init__(self, config: KafkaConfig, group_id: str, topics: List[str]):
        self.config = config
        self.group_id = group_id
        self.topics = topics
        self.consumer = None
        self._running = False
        self._callbacks = {}
        self._initialize_consumer()
    
    def _initialize_consumer(self):
        """Initialize the Kafka consumer with configuration."""
        try:
            consumer_config = {
                'bootstrap_servers': self.config.bootstrap_servers,
                'group_id': self.group_id,
                'auto_offset_reset': 'earliest',
                'enable_auto_commit': True,
                'auto_commit_interval_ms': 1000,
                'session_timeout_ms': 30000,
                'heartbeat_interval_ms': 3000,
                'max_poll_records': 500,
                'max_poll_interval_ms': 300000,
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'key_deserializer': lambda m: m.decode('utf-8') if m else None,
            }
            
            if self.config.sasl_mechanism:
                consumer_config.update({
                    'security_protocol': self.config.security_protocol,
                    'sasl_mechanism': self.config.sasl_mechanism,
                    'sasl_plain_username': self.config.sasl_plain_username,
                    'sasl_plain_password': self.config.sasl_plain_password,
                })
            
            if self.config.ssl_cafile:
                consumer_config.update({
                    'ssl_check_hostname': self.config.ssl_check_hostname,
                    'ssl_cafile': self.config.ssl_cafile,
                    'ssl_certfile': self.config.ssl_certfile,
                    'ssl_keyfile': self.config.ssl_keyfile,
                })
            
            self.consumer = KafkaConsumer(**consumer_config)
            self.consumer.subscribe(self.topics)
            logger.info(f"Kafka consumer initialized for topics: {self.topics}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise
    
    def register_callback(self, topic: str, callback: Callable[[KafkaMessage], None]):
        """
        Register a callback function for a specific topic.
        
        Args:
            topic: Topic name to register callback for
            callback: Function to call when message is received
        """
        self._callbacks[topic] = callback
        logger.info(f"Callback registered for topic: {topic}")
    
    def start_consuming(self):
        """Start consuming messages from subscribed topics."""
        if not self.consumer:
            raise RuntimeError("Kafka consumer not initialized")
        
        self._running = True
        logger.info(f"Starting consumer for group: {self.group_id}")
        
        try:
            while self._running:
                message_batch = self.consumer.poll(timeout_ms=1000, max_records=100)
                
                for topic_partition, messages in message_batch.items():
                    topic = topic_partition.topic
                    
                    for message in messages:
                        try:
                            kafka_message = KafkaMessage(
                                topic=topic,
                                key=message.key,
                                value=message.value,
                                headers=dict(message.headers) if message.headers else {}
                            )
                            
                            # Call registered callback if exists
                            if topic in self._callbacks:
                                self._callbacks[topic](kafka_message)
                            else:
                                logger.debug(f"No callback registered for topic: {topic}")
                            
                        except Exception as e:
                            logger.error(f"Error processing message from topic {topic}: {e}")
                            continue
                
                # Commit offsets
                self.consumer.commit()
                
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
        finally:
            self.stop_consuming()
    
    def stop_consuming(self):
        """Stop consuming messages."""
        self._running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")
    
    def close(self):
        """Close the consumer."""
        self.stop_consuming()


class KafkaTopicManager:
    """Manager for creating and configuring Kafka topics."""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.admin_client = None
        self._initialize_admin_client()
    
    def _initialize_admin_client(self):
        """Initialize the Kafka admin client."""
        try:
            admin_config = {
                'bootstrap_servers': self.config.bootstrap_servers,
                'security_protocol': self.config.security_protocol,
            }
            
            if self.config.sasl_mechanism:
                admin_config.update({
                    'sasl_mechanism': self.config.sasl_mechanism,
                    'sasl_plain_username': self.config.sasl_plain_username,
                    'sasl_plain_password': self.config.sasl_plain_password,
                })
            
            if self.config.ssl_cafile:
                admin_config.update({
                    'ssl_check_hostname': self.config.ssl_check_hostname,
                    'ssl_cafile': self.config.ssl_cafile,
                    'ssl_certfile': self.config.ssl_certfile,
                    'ssl_keyfile': self.config.ssl_keyfile,
                })
            
            self.admin_client = KafkaAdminClient(**admin_config)
            logger.info("Kafka admin client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka admin client: {e}")
            raise
    
    def create_topic(self, topic_config: TopicConfig) -> bool:
        """
        Create a new Kafka topic.
        
        Args:
            topic_config: Topic configuration
            
        Returns:
            True if topic created successfully, False otherwise
        """
        if not self.admin_client:
            raise RuntimeError("Kafka admin client not initialized")
        
        try:
            topic = NewTopic(
                name=topic_config.name,
                num_partitions=topic_config.num_partitions,
                replication_factor=topic_config.replication_factor,
                topic_configs={
                    'retention.ms': str(topic_config.retention_ms),
                    'cleanup.policy': topic_config.cleanup_policy,
                    'compression.type': topic_config.compression_type,
                }
            )
            
            self.admin_client.create_topics([topic])
            logger.info(f"Topic created successfully: {topic_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create topic {topic_config.name}: {e}")
            return False
    
    def list_topics(self) -> List[str]:
        """List all available topics."""
        if not self.admin_client:
            raise RuntimeError("Kafka admin client not initialized")
        
        try:
            metadata = self.admin_client.list_topics()
            return list(metadata)
        except Exception as e:
            logger.error(f"Failed to list topics: {e}")
            return []
    
    def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a Kafka topic.
        
        Args:
            topic_name: Name of topic to delete
            
        Returns:
            True if topic deleted successfully, False otherwise
        """
        if not self.admin_client:
            raise RuntimeError("Kafka admin client not initialized")
        
        try:
            self.admin_client.delete_topics([topic_name])
            logger.info(f"Topic deleted successfully: {topic_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete topic {topic_name}: {e}")
            return False
    
    def close(self):
        """Close the admin client."""
        if self.admin_client:
            self.admin_client.close()
            logger.info("Kafka admin client closed")


class ConstructionDataStreamService:
    """Service for streaming construction data through Kafka."""
    
    def __init__(self):
        self.config = self._get_kafka_config()
        self.producer = KafkaProducerService(self.config)
        self.topic_manager = KafkaTopicManager(self.config)
        self._setup_topics()
    
    def _get_kafka_config(self) -> KafkaConfig:
        """Get Kafka configuration from Django settings."""
        return KafkaConfig(
            bootstrap_servers=getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092']),
            security_protocol=getattr(settings, 'KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT'),
            sasl_mechanism=getattr(settings, 'KAFKA_SASL_MECHANISM', None),
            sasl_plain_username=getattr(settings, 'KAFKA_SASL_PLAIN_USERNAME', None),
            sasl_plain_password=getattr(settings, 'KAFKA_SASL_PLAIN_PASSWORD', None),
        )
    
    def _setup_topics(self):
        """Set up default topics for construction data."""
        default_topics = [
            TopicConfig('construction.projects', num_partitions=3),
            TopicConfig('construction.suppliers', num_partitions=2),
            TopicConfig('construction.risks', num_partitions=2),
            TopicConfig('construction.analytics', num_partitions=3),
            TopicConfig('construction.integrations', num_partitions=2),
            TopicConfig('construction.ml_predictions', num_partitions=2),
        ]
        
        existing_topics = self.topic_manager.list_topics()
        
        for topic_config in default_topics:
            if topic_config.name not in existing_topics:
                self.topic_manager.create_topic(topic_config)
    
    def stream_project_data(self, project_data: Dict[str, Any]):
        """Stream project data to Kafka."""
        try:
            success = self.producer.send_message_sync(
                topic='construction.projects',
                key=f"project_{project_data.get('id', 'unknown')}",
                value=project_data,
                headers={'data_type': 'project', 'timestamp': str(datetime.utcnow())}
            )
            
            if success:
                logger.info(f"Project data streamed successfully: {project_data.get('id')}")
            else:
                logger.error(f"Failed to stream project data: {project_data.get('id')}")
                
        except Exception as e:
            logger.error(f"Error streaming project data: {e}")
    
    def stream_supplier_data(self, supplier_data: Dict[str, Any]):
        """Stream supplier data to Kafka."""
        try:
            success = self.producer.send_message_sync(
                topic='construction.suppliers',
                key=f"supplier_{supplier_data.get('id', 'unknown')}",
                value=supplier_data,
                headers={'data_type': 'supplier', 'timestamp': str(datetime.utcnow())}
            )
            
            if success:
                logger.info(f"Supplier data streamed successfully: {supplier_data.get('id')}")
            else:
                logger.error(f"Failed to stream supplier data: {supplier_data.get('id')}")
                
        except Exception as e:
            logger.error(f"Error streaming supplier data: {e}")
    
    def stream_risk_data(self, risk_data: Dict[str, Any]):
        """Stream risk assessment data to Kafka."""
        try:
            success = self.producer.send_message_sync(
                topic='construction.risks',
                key=f"risk_{risk_data.get('id', 'unknown')}",
                value=risk_data,
                headers={'data_type': 'risk', 'timestamp': str(datetime.utcnow())}
            )
            
            if success:
                logger.info(f"Risk data streamed successfully: {risk_data.get('id')}")
            else:
                logger.error(f"Failed to stream risk data: {risk_data.get('id')}")
                
        except Exception as e:
            logger.error(f"Error streaming risk data: {e}")
    
    def stream_ml_prediction(self, prediction_data: Dict[str, Any]):
        """Stream ML prediction data to Kafka."""
        try:
            success = self.producer.send_message_sync(
                topic='construction.ml_predictions',
                key=f"prediction_{prediction_data.get('model_id', 'unknown')}",
                value=prediction_data,
                headers={'data_type': 'ml_prediction', 'timestamp': str(datetime.utcnow())}
            )
            
            if success:
                logger.info(f"ML prediction streamed successfully: {prediction_data.get('model_id')}")
            else:
                logger.error(f"Failed to stream ML prediction: {prediction_data.get('model_id')}")
                
        except Exception as e:
            logger.error(f"Error streaming ML prediction: {e}")
    
    def close(self):
        """Close all Kafka connections."""
        self.producer.close()
        self.topic_manager.close()
        logger.info("Construction data stream service closed")


# Global instance for easy access
construction_stream_service = None


def get_construction_stream_service() -> ConstructionDataStreamService:
    """Get or create the global construction stream service instance."""
    global construction_stream_service
    if construction_stream_service is None:
        construction_stream_service = ConstructionDataStreamService()
    return construction_stream_service


def close_construction_stream_service():
    """Close the global construction stream service instance."""
    global construction_stream_service
    if construction_stream_service:
        construction_stream_service.close()
        construction_stream_service = None
