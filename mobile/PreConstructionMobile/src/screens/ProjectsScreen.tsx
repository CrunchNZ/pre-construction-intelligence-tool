import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Card, Chip } from 'react-native-paper';

const ProjectsScreen = () => {
  const projects = [
    {
      id: 1,
      name: 'Office Complex A',
      status: 'In Progress',
      progress: 65,
      budget: '$2.5M',
      variance: '-2.3%',
    },
    {
      id: 2,
      name: 'Residential Tower B',
      status: 'Planning',
      progress: 15,
      budget: '$1.8M',
      variance: '0%',
    },
    {
      id: 3,
      name: 'Shopping Center C',
      status: 'Completed',
      progress: 100,
      budget: '$3.2M',
      variance: '+1.2%',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Progress':
        return '#1976d2';
      case 'Planning':
        return '#ff9800';
      case 'Completed':
        return '#4caf50';
      default:
        return '#666';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Projects</Text>
          <Text style={styles.subtitle}>Manage your construction projects</Text>
        </View>

        {projects.map((project) => (
          <Card key={project.id} style={styles.projectCard}>
            <Card.Content>
              <View style={styles.projectHeader}>
                <Text style={styles.projectName}>{project.name}</Text>
                <Chip
                  mode="outlined"
                  textStyle={{ color: getStatusColor(project.status) }}
                  style={[
                    styles.statusChip,
                    { borderColor: getStatusColor(project.status) },
                  ]}
                >
                  {project.status}
                </Chip>
              </View>

              <View style={styles.projectDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Progress:</Text>
                  <Text style={styles.detailValue}>{project.progress}%</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Budget:</Text>
                  <Text style={styles.detailValue}>{project.budget}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Variance:</Text>
                  <Text
                    style={[
                      styles.detailValue,
                      {
                        color:
                          project.variance.startsWith('+') ||
                          project.variance === '0%'
                            ? '#4caf50'
                            : '#f44336',
                      },
                    ]}
                  >
                    {project.variance}
                  </Text>
                </View>
              </View>

              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${project.progress}%` },
                  ]}
                />
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
  projectCard: {
    margin: 10,
    elevation: 4,
  },
  projectHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  projectName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  statusChip: {
    marginLeft: 10,
  },
  projectDetails: {
    marginBottom: 15,
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
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#1976d2',
    borderRadius: 4,
  },
});

export default ProjectsScreen;
