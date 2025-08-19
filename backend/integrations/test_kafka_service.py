"""
Test suite for Kafka Service

This module provides comprehensive testing for the Kafka integration service,
ensuring all functionality works correctly in both development and testing environments.

Author: Pre-Construction Intelligence Team
Date: December 2024
"""

import json
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from django.test import TestCase
from django.conf import settings

from .kafka_service import (
    KafkaConfig,
    TopicConfig,
    KafkaMessage,
    KafkaProducerService,
    KafkaConsumerService,
    KafkaTopicManager,
    ConstructionDataStreamService,
    get_construction_stream_service,
    close_construction_stream_service
)


class KafkaConfigTestCase(TestCase):
    """Test cases for KafkaConfig dataclass."""
    
    def test_kafka_config_defaults(self):
        """Test KafkaConfig with default values."""
        config = KafkaConfig(bootstrap_servers=['localhost:9092'])
        
        self.assertEqual(config.bootstrap_servers, ['localhost:9092'])
        self.assertEqual(config.security_protocol, 'PLAINTEXT')
        self.assertIsNone(config.sasl_mechanism)
        self.assertIsNone(config.sasl_plain_username)
        self.assertIsNone(config.sasl_plain_password)
        self.assertFalse(config.ssl_check_hostname)
        self.assertIsNone(config.ssl_cafile)
        self.assertIsNone(config.ssl_certfile)
        self.assertIsNone(config.ssl_keyfile)
    
    def test_kafka_config_custom_values(self):
        """Test KafkaConfig with custom values."""
        config = KafkaConfig(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            security_protocol='SASL_SSL',
            sasl_mechanism='PLAIN',
            sasl_plain_username='user',
            sasl_plain_password='pass',
            ssl_check_hostname=True,
            ssl_cafile='/path/to/ca.pem',
            ssl_certfile='/path/to/cert.pem',
            ssl_keyfile='/path/to/key.pem'
        )
        
        self.assertEqual(config.bootstrap_servers, ['kafka1:9092', 'kafka2:9092'])
        self.assertEqual(config.security_protocol, 'SASL_SSL')
        self.assertEqual(config.sasl_mechanism, 'PLAIN')
        self.assertEqual(config.sasl_plain_username, 'user')
        self.assertEqual(config.sasl_plain_password, 'pass')
        self.assertTrue(config.ssl_check_hostname)
        self.assertEqual(config.ssl_cafile, '/path/to/ca.pem')
        self.assertEqual(config.ssl_certfile, '/path/to/cert.pem')
        self.assertEqual(config.ssl_keyfile, '/path/to/key.pem')


class TopicConfigTestCase(TestCase):
    """Test cases for TopicConfig dataclass."""
    
    def test_topic_config_defaults(self):
        """Test TopicConfig with default values."""
        config = TopicConfig(name='test.topic')
        
        self.assertEqual(config.name, 'test.topic')
        self.assertEqual(config.num_partitions, 1)
        self.assertEqual(config.replication_factor, 1)
        self.assertEqual(config.retention_ms, 604800000)  # 7 days
        self.assertEqual(config.cleanup_policy, 'delete')
        self.assertEqual(config.compression_type, 'gzip')
    
    def test_topic_config_custom_values(self):
        """Test TopicConfig with custom values."""
        config = TopicConfig(
            name='custom.topic',
            num_partitions=5,
            replication_factor=3,
            retention_ms=86400000,  # 1 day
            cleanup_policy='compact',
            compression_type='gzip'
        )
        
        self.assertEqual(config.name, 'custom.topic')
        self.assertEqual(config.num_partitions, 5)
        self.assertEqual(config.replication_factor, 3)
        self.assertEqual(config.retention_ms, 86400000)
        self.assertEqual(config.cleanup_policy, 'compact')
        self.assertEqual(config.compression_type, 'gzip')


class KafkaMessageTestCase(TestCase):
    """Test cases for KafkaMessage class."""
    
    def test_kafka_message_creation(self):
        """Test KafkaMessage creation with basic data."""
        message = KafkaMessage(
            topic='test.topic',
            key='test_key',
            value={'data': 'test_value'},
            headers={'header1': 'value1'}
        )
        
        self.assertEqual(message.topic, 'test.topic')
        self.assertEqual(message.key, 'test_key')
        self.assertEqual(message.value, {'data': 'test_value'})
        self.assertEqual(message.headers, {'header1': 'value1'})
        self.assertIsNotNone(message.timestamp)
        self.assertIsNotNone(message.message_id)
    
    def test_kafka_message_to_dict(self):
        """Test KafkaMessage to_dict method."""
        message = KafkaMessage(
            topic='test.topic',
            key='test_key',
            value={'data': 'test_value'}
        )
        
        message_dict = message.to_dict()
        
        self.assertEqual(message_dict['topic'], 'test.topic')
        self.assertEqual(message_dict['key'], 'test_key')
        self.assertEqual(message_dict['value'], {'data': 'test_value'})
        self.assertIn('timestamp', message_dict)
        self.assertIn('message_id', message_dict)
    
    def test_kafka_message_str_representation(self):
        """Test KafkaMessage string representation."""
        message = KafkaMessage(
            topic='test.topic',
            key='test_key',
            value='test_value'
        )
        
        str_repr = str(message)
        self.assertIn('KafkaMessage', str_repr)
        self.assertIn('test.topic', str_repr)
        self.assertIn('test_key', str_repr)
        self.assertIn('id', str_repr)


class KafkaProducerServiceTestCase(TestCase):
    """Test cases for KafkaProducerService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KafkaConfig(bootstrap_servers=['localhost:9092'])
    
    @patch('integrations.kafka_service.KafkaProducer')
    def test_producer_initialization(self, mock_kafka_producer):
        """Test Kafka producer initialization."""
        mock_producer_instance = Mock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        service = KafkaProducerService(self.config)
        
        self.assertIsNotNone(service.producer)
        mock_kafka_producer.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaProducer')
    def test_send_message(self, mock_kafka_producer):
        """Test sending a message."""
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        service = KafkaProducerService(self.config)
        
        future = service.send_message('test.topic', 'test_key', 'test_value')
        
        self.assertEqual(future, mock_future)
        mock_producer_instance.send.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaProducer')
    def test_send_message_sync_success(self, mock_kafka_producer):
        """Test synchronous message sending with success."""
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_metadata = Mock()
        mock_metadata.topic = 'test.topic'
        mock_metadata.partition = 0
        mock_metadata.offset = 123
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        service = KafkaProducerService(self.config)
        
        success = service.send_message_sync('test.topic', 'test_key', 'test_value')
        
        self.assertTrue(success)
        mock_future.get.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaProducer')
    def test_send_message_sync_timeout(self, mock_kafka_producer):
        """Test synchronous message sending with timeout."""
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_future.get.side_effect = Exception("Timeout")
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        service = KafkaProducerService(self.config)
        
        success = service.send_message_sync('test.topic', 'test_key', 'test_value')
        
        self.assertFalse(success)
    
    @patch('integrations.kafka_service.KafkaProducer')
    def test_send_batch(self, mock_kafka_producer):
        """Test sending multiple messages in batch."""
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        service = KafkaProducerService(self.config)
        
        messages = [
            KafkaMessage('topic1', 'key1', 'value1'),
            KafkaMessage('topic2', 'key2', 'value2')
        ]
        
        futures = service.send_batch(messages)
        
        self.assertEqual(len(futures), 2)
        self.assertEqual(mock_producer_instance.send.call_count, 2)
    
    @patch('integrations.kafka_service.KafkaProducer')
    def test_close_producer(self, mock_kafka_producer):
        """Test closing the producer."""
        mock_producer_instance = Mock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        service = KafkaProducerService(self.config)
        service.close()
        
        mock_producer_instance.flush.assert_called_once()
        mock_producer_instance.close.assert_called_once()


class KafkaConsumerServiceTestCase(TestCase):
    """Test cases for KafkaConsumerService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KafkaConfig(bootstrap_servers=['localhost:9092'])
        self.group_id = 'test_group'
        self.topics = ['test.topic1', 'test.topic2']
    
    @patch('integrations.kafka_service.KafkaConsumer')
    def test_consumer_initialization(self, mock_kafka_consumer):
        """Test Kafka consumer initialization."""
        mock_consumer_instance = Mock()
        mock_kafka_consumer.return_value = mock_consumer_instance
        
        service = KafkaConsumerService(self.config, self.group_id, self.topics)
        
        self.assertIsNotNone(service.consumer)
        mock_kafka_consumer.assert_called_once()
        mock_consumer_instance.subscribe.assert_called_once_with(self.topics)
    
    @patch('integrations.kafka_service.KafkaConsumer')
    def test_register_callback(self, mock_kafka_consumer):
        """Test registering a callback function."""
        mock_consumer_instance = Mock()
        mock_kafka_consumer.return_value = mock_consumer_instance
        
        service = KafkaConsumerService(self.config, self.group_id, self.topics)
        
        def test_callback(message):
            pass
        
        service.register_callback('test.topic1', test_callback)
        
        self.assertIn('test.topic1', service._callbacks)
        self.assertEqual(service._callbacks['test.topic1'], test_callback)
    
    @patch('integrations.kafka_service.KafkaConsumer')
    def test_consumer_close(self, mock_kafka_consumer):
        """Test closing the consumer."""
        mock_consumer_instance = Mock()
        mock_kafka_consumer.return_value = mock_consumer_instance
        
        service = KafkaConsumerService(self.config, self.group_id, self.topics)
        service.close()
        
        mock_consumer_instance.close.assert_called_once()


class KafkaTopicManagerTestCase(TestCase):
    """Test cases for KafkaTopicManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KafkaConfig(bootstrap_servers=['localhost:9092'])
    
    @patch('integrations.kafka_service.KafkaAdminClient')
    def test_admin_client_initialization(self, mock_admin_client):
        """Test Kafka admin client initialization."""
        mock_admin_instance = Mock()
        mock_admin_client.return_value = mock_admin_instance
        
        manager = KafkaTopicManager(self.config)
        
        self.assertIsNotNone(manager.admin_client)
        mock_admin_client.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaAdminClient')
    def test_create_topic_success(self, mock_admin_client):
        """Test successful topic creation."""
        mock_admin_instance = Mock()
        mock_admin_client.return_value = mock_admin_instance
        
        manager = KafkaTopicManager(self.config)
        topic_config = TopicConfig('test.topic')
        
        success = manager.create_topic(topic_config)
        
        self.assertTrue(success)
        mock_admin_instance.create_topics.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaAdminClient')
    def test_list_topics(self, mock_admin_client):
        """Test listing topics."""
        mock_admin_instance = Mock()
        mock_admin_instance.list_topics.return_value = ['topic1', 'topic2']
        mock_admin_client.return_value = mock_admin_instance
        
        manager = KafkaTopicManager(self.config)
        topics = manager.list_topics()
        
        self.assertEqual(topics, ['topic1', 'topic2'])
        mock_admin_instance.list_topics.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaAdminClient')
    def test_delete_topic_success(self, mock_admin_client):
        """Test successful topic deletion."""
        mock_admin_instance = Mock()
        mock_admin_client.return_value = mock_admin_instance
        
        manager = KafkaTopicManager(self.config)
        
        success = manager.delete_topic('test.topic')
        
        self.assertTrue(success)
        mock_admin_instance.delete_topics.assert_called_once_with(['test.topic'])
    
    @patch('integrations.kafka_service.KafkaAdminClient')
    def test_admin_client_close(self, mock_admin_client):
        """Test closing the admin client."""
        mock_admin_instance = Mock()
        mock_admin_client.return_value = mock_admin_instance
        
        manager = KafkaTopicManager(self.config)
        manager.close()
        
        mock_admin_instance.close.assert_called_once()


class ConstructionDataStreamServiceTestCase(TestCase):
    """Test cases for ConstructionDataStreamService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.patcher = patch('integrations.kafka_service.settings')
        self.mock_settings = self.patcher.start()
        self.mock_settings.KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
        self.mock_settings.KAFKA_SECURITY_PROTOCOL = 'PLAINTEXT'
    
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
    
    @patch('integrations.kafka_service.KafkaProducerService')
    @patch('integrations.kafka_service.KafkaTopicManager')
    def test_service_initialization(self, mock_topic_manager_class, mock_producer_class):
        """Test service initialization."""
        mock_producer = Mock()
        mock_topic_manager = Mock()
        mock_producer_class.return_value = mock_producer
        mock_topic_manager_class.return_value = mock_topic_manager
        mock_topic_manager.list_topics.return_value = []
        
        service = ConstructionDataStreamService()
        
        self.assertIsNotNone(service.producer)
        self.assertIsNotNone(service.topic_manager)
        mock_topic_manager.list_topics.assert_called_once()
    
    @patch('integrations.kafka_service.KafkaProducerService')
    @patch('integrations.kafka_service.KafkaTopicManager')
    def test_stream_project_data(self, mock_topic_manager_class, mock_producer_class):
        """Test streaming project data."""
        mock_producer = Mock()
        mock_topic_manager = Mock()
        mock_producer_class.return_value = mock_producer
        mock_topic_manager_class.return_value = mock_topic_manager
        mock_producer.send_message_sync.return_value = True
        mock_topic_manager.list_topics.return_value = []
        
        service = ConstructionDataStreamService()
        project_data = {'id': '123', 'name': 'Test Project'}
        
        service.stream_project_data(project_data)
        
        mock_producer.send_message_sync.assert_called_once()
        call_args = mock_producer.send_message_sync.call_args
        self.assertEqual(call_args[1]['topic'], 'construction.projects')
        self.assertEqual(call_args[1]['key'], 'project_123')
        self.assertEqual(call_args[1]['value'], project_data)
    
    @patch('integrations.kafka_service.KafkaProducerService')
    @patch('integrations.kafka_service.KafkaTopicManager')
    def test_stream_supplier_data(self, mock_topic_manager_class, mock_producer_class):
        """Test streaming supplier data."""
        mock_producer = Mock()
        mock_topic_manager = Mock()
        mock_producer_class.return_value = mock_producer
        mock_topic_manager_class.return_value = mock_topic_manager
        mock_producer.send_message_sync.return_value = True
        mock_topic_manager.list_topics.return_value = []
        
        service = ConstructionDataStreamService()
        supplier_data = {'id': '456', 'name': 'Test Supplier'}
        
        service.stream_supplier_data(supplier_data)
        
        mock_producer.send_message_sync.assert_called_once()
        call_args = mock_producer.send_message_sync.call_args
        self.assertEqual(call_args[1]['topic'], 'construction.suppliers')
        self.assertEqual(call_args[1]['key'], 'supplier_456')
        self.assertEqual(call_args[1]['value'], supplier_data)
    
    @patch('integrations.kafka_service.KafkaProducerService')
    @patch('integrations.kafka_service.KafkaTopicManager')
    def test_service_close(self, mock_topic_manager_class, mock_producer_class):
        """Test closing the service."""
        mock_producer = Mock()
        mock_topic_manager = Mock()
        mock_producer_class.return_value = mock_producer
        mock_topic_manager_class.return_value = mock_topic_manager
        mock_topic_manager.list_topics.return_value = []
        
        service = ConstructionDataStreamService()
        service.close()
        
        mock_producer.close.assert_called_once()
        mock_topic_manager.close.assert_called_once()


class GlobalServiceTestCase(TestCase):
    """Test cases for global service functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset global service
        close_construction_stream_service()
    
    def tearDown(self):
        """Clean up after tests."""
        close_construction_stream_service()
    
    @patch('integrations.kafka_service.ConstructionDataStreamService')
    def test_get_construction_stream_service(self, mock_service_class):
        """Test getting the global construction stream service."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        service = get_construction_stream_service()
        
        self.assertEqual(service, mock_service)
        mock_service_class.assert_called_once()
    
    @patch('integrations.kafka_service.ConstructionDataStreamService')
    def test_get_construction_stream_service_singleton(self, mock_service_class):
        """Test that get_construction_stream_service returns the same instance."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        service1 = get_construction_stream_service()
        service2 = get_construction_stream_service()
        
        self.assertEqual(service1, service2)
        mock_service_class.assert_called_once()  # Only called once
    
    def test_close_construction_stream_service(self):
        """Test closing the global construction stream service."""
        # First get the service
        with patch('integrations.kafka_service.ConstructionDataStreamService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            service = get_construction_stream_service()
        
        # Then close it
        close_construction_stream_service()
        
        # Verify the service was closed
        mock_service.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
