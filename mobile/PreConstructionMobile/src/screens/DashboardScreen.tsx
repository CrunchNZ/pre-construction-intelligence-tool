import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import { Card } from 'react-native-paper';

const { width } = Dimensions.get('window');

const DashboardScreen = () => {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Pre-Construction Intelligence</Text>
          <Text style={styles.subtitle}>Mobile Dashboard</Text>
        </View>

        <View style={styles.statsContainer}>
          <Card style={styles.card}>
            <Card.Content>
              <Text style={styles.cardTitle}>Active Projects</Text>
              <Text style={styles.cardValue}>12</Text>
              <Text style={styles.cardSubtitle}>+2 this week</Text>
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Content>
              <Text style={styles.cardTitle}>Total Suppliers</Text>
              <Text style={styles.cardValue}>48</Text>
              <Text style={styles.cardSubtitle}>+5 this month</Text>
            </Card.Content>
          </Card>
        </View>

        <View style={styles.statsContainer}>
          <Card style={styles.card}>
            <Card.Content>
              <Text style={styles.cardTitle}>Risk Score</Text>
              <Text style={styles.cardValue}>Medium</Text>
              <Text style={styles.cardSubtitle}>3 active risks</Text>
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Content>
              <Text style={styles.cardTitle}>Cost Variance</Text>
              <Text style={styles.cardValue}>-2.3%</Text>
              <Text style={styles.cardSubtitle}>Under budget</Text>
            </Card.Content>
          </Card>
        </View>

        <Card style={styles.fullWidthCard}>
          <Card.Content>
            <Text style={styles.cardTitle}>Recent Activity</Text>
            <Text style={styles.activityItem}>• New project "Office Complex A" added</Text>
            <Text style={styles.activityItem}>• Supplier "ABC Construction" updated</Text>
            <Text style={styles.activityItem}>• Risk assessment completed for Project X</Text>
            <Text style={styles.activityItem}>• Monthly report generated</Text>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    backgroundColor: '#1976d2',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    marginTop: 5,
    opacity: 0.9,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 10,
  },
  card: {
    width: (width - 40) / 2 - 10,
    marginBottom: 10,
    elevation: 4,
  },
  fullWidthCard: {
    margin: 10,
    elevation: 4,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  cardValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#666',
  },
  activityItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
    paddingLeft: 10,
  },
});

export default DashboardScreen;
