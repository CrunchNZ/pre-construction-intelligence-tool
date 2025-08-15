import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Card, List, Switch } from 'react-native-paper';

const SettingsScreen = () => {
  const [notifications, setNotifications] = React.useState(true);
  const [darkMode, setDarkMode] = React.useState(false);
  const [autoSync, setAutoSync] = React.useState(true);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Settings</Text>
          <Text style={styles.subtitle}>Configure your preferences</Text>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>App Preferences</Text>
            <List.Item
              title="Push Notifications"
              description="Receive alerts for important updates"
              right={() => (
                <Switch
                  value={notifications}
                  onValueChange={setNotifications}
                />
              )}
            />
            <List.Item
              title="Dark Mode"
              description="Use dark theme for the app"
              right={() => (
                <Switch value={darkMode} onValueChange={setDarkMode} />
              )}
            />
            <List.Item
              title="Auto Sync"
              description="Automatically sync data in background"
              right={() => (
                <Switch value={autoSync} onValueChange={setAutoSync} />
              )}
            />
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Account</Text>
            <List.Item
              title="Profile"
              description="View and edit your profile"
              right={() => <List.Icon icon="account" />}
            />
            <List.Item
              title="Security"
              description="Change password and security settings"
              right={() => <List.Icon icon="shield" />}
            />
            <List.Item
              title="Privacy"
              description="Manage privacy and data settings"
              right={() => <List.Icon icon="eye" />}
            />
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardTitle}>Support</Text>
            <List.Item
              title="Help Center"
              description="Get help and documentation"
              right={() => <List.Icon icon="help-circle" />}
            />
            <List.Item
              title="Contact Support"
              description="Get in touch with our team"
              right={() => <List.Icon icon="message" />}
            />
            <List.Item
              title="About"
              description="App version and information"
              right={() => <List.Icon icon="information" />}
            />
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
});

export default SettingsScreen;
