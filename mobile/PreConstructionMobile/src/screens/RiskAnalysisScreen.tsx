import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Card, Chip } from 'react-native-paper';

const RiskAnalysisScreen = () => {
  const risks = [
    {
      id: 1,
      title: 'Weather Delay Risk',
      severity: 'High',
      probability: 'Medium',
      impact: 'Schedule delay of 2-3 weeks',
      mitigation: 'Pre-ordered materials, backup suppliers',
    },
    {
      id: 2,
      title: 'Supplier Performance Risk',
      severity: 'Medium',
      probability: 'Low',
      impact: 'Cost overrun of 5-10%',
      mitigation: 'Performance monitoring, penalties',
    },
    {
      id: 3,
      title: 'Regulatory Compliance Risk',
      severity: 'High',
      probability: 'Low',
      impact: 'Project halt, fines',
      mitigation: 'Regular compliance checks',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'High':
        return '#f44336';
      case 'Medium':
        return '#ff9800';
      case 'Low':
        return '#4caf50';
      default:
        return '#666';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Risk Analysis</Text>
          <Text style={styles.subtitle}>Monitor and manage project risks</Text>
        </View>

        {risks.map((risk) => (
          <Card key={risk.id} style={styles.riskCard}>
            <Card.Content>
              <View style={styles.riskHeader}>
                <Text style={styles.riskTitle}>{risk.title}</Text>
                <Chip
                  mode="outlined"
                  textStyle={{ color: getSeverityColor(risk.severity) }}
                  style={[
                    styles.severityChip,
                    { borderColor: getSeverityColor(risk.severity) },
                  ]}
                >
                  {risk.severity}
                </Chip>
              </View>

              <View style={styles.riskDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Probability:</Text>
                  <Text style={styles.detailValue}>{risk.probability}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Impact:</Text>
                  <Text style={styles.detailValue}>{risk.impact}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Mitigation:</Text>
                  <Text style={styles.detailValue}>{risk.mitigation}</Text>
                </View>
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
  riskCard: {
    margin: 10,
    elevation: 4,
  },
  riskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  riskTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  severityChip: {
    marginLeft: 10,
  },
  riskDetails: {
    marginTop: 10,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    textAlign: 'right',
  },
});

export default RiskAnalysisScreen;
