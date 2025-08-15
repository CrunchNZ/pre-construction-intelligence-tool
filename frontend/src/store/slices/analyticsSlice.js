import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  analytics: {},
  loading: false,
  error: null,
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    fetchAnalyticsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchAnalyticsSuccess: (state, action) => {
      state.loading = false;
      state.analytics = action.payload;
      state.error = null;
    },
    fetchAnalyticsFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { fetchAnalyticsStart, fetchAnalyticsSuccess, fetchAnalyticsFailure } = analyticsSlice.actions;

export default analyticsSlice.reducer;
