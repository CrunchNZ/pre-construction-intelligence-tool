import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  suppliers: [],
  loading: false,
  error: null,
};

const suppliersSlice = createSlice({
  name: 'suppliers',
  initialState,
  reducers: {
    fetchSuppliersStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchSuppliersSuccess: (state, action) => {
      state.loading = false;
      state.suppliers = action.payload;
      state.error = null;
    },
    fetchSuppliersFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { fetchSuppliersStart, fetchSuppliersSuccess, fetchSuppliersFailure } = suppliersSlice.actions;

export default suppliersSlice.reducer;
