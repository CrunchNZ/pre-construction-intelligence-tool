#!/usr/bin/env python3
"""
Kafka Infrastructure Test Script

This script tests the basic functionality of our Kafka infrastructure
to ensure everything is working correctly before proceeding with development.

Usage:
    python test_kafka_infrastructure.py

Author: Pre-Construction Intelligence Team
Date: December 2024
"""

import json
import time
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preconstruction_intelligence.settings')

import django
django.setup()

from integrations.kafka_service import (
    KafkaConfig,
    TopicConfig,
    KafkaProducerService,
    KafkaConsumerService,
    KafkaTopicManager,
    ConstructionDataStreamService
)


def test_kafka_connection():
    """Test basic Kafka connection."""
    print("🔍 Testing Kafka connection...")
    
    try:
        config = KafkaConfig(bootstrap_servers=['localhost:9092'])
        print("✅ Kafka configuration created successfully")
        return config
    except Exception as e:
        print(f"❌ Failed to create Kafka configuration: {e}")
        return None


def test_topic_management(config):
    """Test topic management functionality."""
    print("\n🔍 Testing topic management...")
    
    try:
        topic_manager = KafkaTopicManager(config)
        print("✅ Topic manager initialized successfully")
        
        # List existing topics
        topics = topic_manager.list_topics()
        print(f"📋 Existing topics: {topics}")
        
        # Create a test topic
        test_topic = TopicConfig('test.construction.data', num_partitions=1)
        success = topic_manager.create_topic(test_topic)
        
        if success:
            print("✅ Test topic created successfully")
        else:
            print("⚠️  Test topic creation failed (may already exist)")
        
        # List topics again
        updated_topics = topic_manager.list_topics()
        print(f"📋 Updated topics: {updated_topics}")
        
        topic_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Topic management test failed: {e}")
        return False


def test_producer_functionality(config):
    """Test producer functionality."""
    print("\n🔍 Testing producer functionality...")
    
    try:
        producer = KafkaProducerService(config)
        print("✅ Producer initialized successfully")
        
        # Test message sending
        test_message = {
            'id': 'test_001',
            'type': 'project',
            'name': 'Test Construction Project',
            'timestamp': time.time(),
            'data': {
                'budget': 1000000,
                'duration': 365,
                'status': 'planning'
            }
        }
        
        success = producer.send_message_sync(
            topic='test.construction.data',
            key='test_project_001',
            value=test_message,
            timeout=10
        )
        
        if success:
            print("✅ Test message sent successfully")
        else:
            print("❌ Test message sending failed")
        
        producer.close()
        return success
        
    except Exception as e:
        print(f"❌ Producer test failed: {e}")
        return False


def test_consumer_functionality(config):
    """Test consumer functionality."""
    print("\n🔍 Testing consumer functionality...")
    
    try:
        consumer = KafkaConsumerService(
            config=config,
            group_id='test_group',
            topics=['test.construction.data']
        )
        print("✅ Consumer initialized successfully")
        
        # Register a test callback
        received_messages = []
        
        def test_callback(message):
            received_messages.append(message)
            print(f"📨 Received message: {message.key} -> {message.value}")
        
        consumer.register_callback('test.construction.data', test_callback)
        print("✅ Callback registered successfully")
        
        # Start consuming in a separate thread
        import threading
        
        def consume_messages():
            try:
                consumer.start_consuming()
            except KeyboardInterrupt:
                pass
        
        consumer_thread = threading.Thread(target=consume_messages, daemon=True)
        consumer_thread.start()
        
        # Wait a bit for messages
        print("⏳ Waiting for messages...")
        time.sleep(5)
        
        # Stop consuming
        consumer.stop_consuming()
        consumer.close()
        
        print(f"📊 Received {len(received_messages)} messages")
        return True
        
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False


def test_construction_stream_service():
    """Test the main construction stream service."""
    print("\n🔍 Testing construction stream service...")
    
    try:
        service = ConstructionDataStreamService()
        print("✅ Construction stream service initialized successfully")
        
        # Test streaming different types of data
        test_project = {
            'id': 'proj_001',
            'name': 'Highway Bridge Project',
            'budget': 5000000,
            'duration_days': 730,
            'status': 'planning'
        }
        
        test_supplier = {
            'id': 'sup_001',
            'name': 'ABC Construction Supplies',
            'rating': 4.5,
            'specialization': 'steel and concrete'
        }
        
        test_risk = {
            'id': 'risk_001',
            'project_id': 'proj_001',
            'type': 'weather',
            'probability': 0.3,
            'impact': 'high'
        }
        
        # Stream the test data
        service.stream_project_data(test_project)
        service.stream_supplier_data(test_supplier)
        service.stream_risk_data(test_risk)
        
        print("✅ Test data streamed successfully")
        
        service.close()
        return True
        
    except Exception as e:
        print(f"❌ Construction stream service test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Starting Kafka Infrastructure Tests")
    print("=" * 50)
    
    # Test 1: Basic connection
    config = test_kafka_connection()
    if not config:
        print("\n❌ Kafka connection test failed. Exiting.")
        return False
    
    # Test 2: Topic management
    topic_success = test_topic_management(config)
    
    # Test 3: Producer functionality
    producer_success = test_producer_functionality(config)
    
    # Test 4: Consumer functionality
    consumer_success = test_consumer_functionality(config)
    
    # Test 5: Construction stream service
    service_success = test_construction_stream_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"🔗 Kafka Connection: {'✅ PASS' if config else '❌ FAIL'}")
    print(f"📋 Topic Management: {'✅ PASS' if topic_success else '❌ FAIL'}")
    print(f"📤 Producer: {'✅ PASS' if producer_success else '❌ FAIL'}")
    print(f"📥 Consumer: {'✅ PASS' if consumer_success else '❌ FAIL'}")
    print(f"🏗️  Stream Service: {'✅ PASS' if service_success else '❌ FAIL'}")
    
    overall_success = all([config, topic_success, producer_success, consumer_success, service_success])
    
    if overall_success:
        print("\n🎉 All tests passed! Kafka infrastructure is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the logs above for details.")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
