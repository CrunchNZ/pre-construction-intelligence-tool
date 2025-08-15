import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  risks: [],
  loading: false,
  error: null,
};

const riskSlice = createSlice({
  name: 'risk',
  initialState,
  reducers: {
    fetchRisksStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchRisksSuccess: (state, action) => {
      state.loading = false;
      state.risks = action.payload;
      state.error = null;
    },
    fetchRisksFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { fetchRisksStart, fetchRisksSuccess, fetchRisksFailure } = riskSlice.actions;

export default riskSlice.reducer;
