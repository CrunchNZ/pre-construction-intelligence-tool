import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Card, Button } from 'react-native-paper';

const ReportsScreen = () => {
  const reports = [
    {
      id: 1,
      name: 'Monthly Project Summary',
      type: 'PDF',
      size: '2.4 MB',
      lastGenerated: '2024-08-15',
    },
    {
      id: 2,
      name: 'Supplier Performance Report',
      type: 'Excel',
      size: '1.8 MB',
      lastGenerated: '2024-08-14',
    },
    {
      id: 3,
      name: 'Risk Assessment Summary',
      type: 'PDF',
      size: '3.1 MB',
      lastGenerated: '2024-08-13',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Reports</Text>
          <Text style={styles.subtitle}>Generate and manage reports</Text>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Quick Reports</Text>
            <Button
              mode="contained"
              style={styles.button}
              onPress={() => {}}
            >
              Generate Project Summary
            </Button>
            <Button
              mode="outlined"
              style={styles.button}
              onPress={() => {}}
            >
              Export Supplier Data
            </Button>
          </Card.Content>
        </Card>

        <Text style={styles.sectionTitle}>Recent Reports</Text>
        {reports.map((report) => (
          <Card key={report.id} style={styles.reportCard}>
            <Card.Content>
              <View style={styles.reportHeader}>
                <Text style={styles.reportName}>{report.name}</Text>
                <Text style={styles.reportType}>{report.type}</Text>
              </View>
              <View style={styles.reportDetails}>
                <Text style={styles.reportSize}>Size: {report.size}</Text>
                <Text style={styles.reportDate}>
                  Generated: {report.lastGenerated}
                </Text>
              </View>
              <View style={styles.reportActions}>
                <Button mode="outlined" compact onPress={() => {}}>
                  Download
                </Button>
                <Button mode="outlined" compact onPress={() => {}}>
                  Share
                </Button>
              </View>
            </Card.Content>
          </Card>
        ))}
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
  card: {
    margin: 10,
    elevation: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  button: {
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    margin: 20,
    marginBottom: 10,
  },
  reportCard: {
    margin: 10,
    elevation: 4,
  },
  reportHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  reportName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  reportType: {
    fontSize: 12,
    color: '#666',
    backgroundColor: '#e0e0e0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  reportDetails: {
    marginBottom: 15,
  },
  reportSize: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  reportDate: {
    fontSize: 14,
    color: '#666',
  },
  reportActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
});

export default ReportsScreen;
