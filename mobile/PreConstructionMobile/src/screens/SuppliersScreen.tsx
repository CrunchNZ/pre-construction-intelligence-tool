import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Card, Chip, Avatar } from 'react-native-paper';

const SuppliersScreen = () => {
  const suppliers = [
    {
      id: 1,
      name: 'ABC Construction',
      category: 'General Contractor',
      rating: 4.8,
      projects: 15,
      status: 'Active',
    },
    {
      id: 2,
      name: 'XYZ Electrical',
      category: 'Electrical',
      rating: 4.6,
      projects: 8,
      status: 'Active',
    },
    {
      id: 3,
      name: 'LMN Plumbing',
      category: 'Plumbing',
      rating: 4.9,
      projects: 12,
      status: 'Active',
    },
  ];

  const getRatingColor = (rating: number) => {
    if (rating >= 4.5) return '#4caf50';
    if (rating >= 4.0) return '#ff9800';
    return '#f44336';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Suppliers</Text>
          <Text style={styles.subtitle}>Manage your supplier network</Text>
        </View>

        {suppliers.map((supplier) => (
          <Card key={supplier.id} style={styles.supplierCard}>
            <Card.Content>
              <View style={styles.supplierHeader}>
                <Avatar.Text
                  size={50}
                  label={supplier.name.substring(0, 2).toUpperCase()}
                  style={styles.avatar}
                />
                <View style={styles.supplierInfo}>
                  <Text style={styles.supplierName}>{supplier.name}</Text>
                  <Text style={styles.supplierCategory}>{supplier.category}</Text>
                </View>
                <Chip
                  mode="outlined"
                  textStyle={{ color: '#4caf50' }}
                  style={[styles.statusChip, { borderColor: '#4caf50' }]}
                >
                  {supplier.status}
                </Chip>
              </View>

              <View style={styles.supplierDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Rating:</Text>
                  <Text
                    style={[
                      styles.detailValue,
                      { color: getRatingColor(supplier.rating) },
                    ]}
                  >
                    {supplier.rating}/5.0
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Projects:</Text>
                  <Text style={styles.detailValue}>{supplier.projects}</Text>
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
  supplierCard: {
    margin: 10,
    elevation: 4,
  },
  supplierHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  avatar: {
    backgroundColor: '#1976d2',
    marginRight: 15,
  },
  supplierInfo: {
    flex: 1,
  },
  supplierName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  supplierCategory: {
    fontSize: 14,
    color: '#666',
  },
  statusChip: {
    marginLeft: 10,
  },
  supplierDetails: {
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
  },
});

export default SuppliersScreen;
