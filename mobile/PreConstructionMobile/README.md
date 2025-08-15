# Pre-Construction Intelligence Mobile App

A React Native mobile application for the Pre-Construction Intelligence Tool, providing on-the-go access to project management, supplier analytics, and risk assessment.

## Features

- **Dashboard**: Overview of key metrics and recent activity
- **Projects**: Manage and monitor construction projects
- **Suppliers**: Track supplier performance and ratings
- **Risk Analysis**: Monitor project risks and mitigation strategies
- **Analytics**: View performance metrics and trends
- **Reports**: Generate and access project reports
- **Settings**: Configure app preferences and account settings

## Tech Stack

- **React Native**: 0.76.0
- **Navigation**: React Navigation v6
- **UI Components**: React Native Paper
- **Icons**: React Native Vector Icons
- **TypeScript**: Full TypeScript support

## Prerequisites

- Node.js >= 18
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **iOS (macOS only):**
   ```bash
   cd ios && pod install && cd ..
   ```

3. **Start Metro bundler:**
   ```bash
   npm start
   ```

## Running the App

### Android
```bash
npm run android
```

### iOS
```bash
npm run ios
```

## Project Structure

```
src/
├── screens/           # Screen components
│   ├── DashboardScreen.tsx
│   ├── ProjectsScreen.tsx
│   ├── SuppliersScreen.tsx
│   ├── RiskAnalysisScreen.tsx
│   ├── AnalyticsScreen.tsx
│   ├── ReportsScreen.tsx
│   └── SettingsScreen.tsx
├── components/        # Reusable components
├── services/         # API and business logic
└── utils/            # Utility functions
```

## Development

The app follows React Native best practices with:
- TypeScript for type safety
- Component-based architecture
- Consistent styling with StyleSheet
- Proper navigation structure
- Material Design principles

## Building for Production

### Android
```bash
cd android
./gradlew assembleRelease
```

### iOS
```bash
cd ios
xcodebuild -workspace PreConstructionMobile.xcworkspace -scheme PreConstructionMobile -configuration Release
```

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new components
3. Test on both Android and iOS platforms
4. Update documentation as needed

## License

Proprietary - Internal use only
