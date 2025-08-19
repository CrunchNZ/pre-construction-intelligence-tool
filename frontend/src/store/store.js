import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from 'redux';

// Import reducers
import authReducer from './slices/authSlice';
import projectsReducer from './slices/projectsSlice';
import suppliersReducer from './slices/suppliersSlice';
import riskReducer from './slices/riskSlice';
import analyticsReducer from './slices/analyticsSlice';
import uiReducer from './slices/uiSlice';
import mlInsightsReducer from './slices/mlInsightsSlice';

// Combine reducers
const rootReducer = combineReducers({
  auth: authReducer,
  projects: projectsReducer,
  suppliers: suppliersReducer,
  risk: riskReducer,
  analytics: analyticsReducer,
  ui: uiReducer,
  mlInsights: mlInsightsReducer,
});

// Create store
export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['items.dates'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Export types for TypeScript-like development
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
