import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  projects: [],
  loading: false,
  error: null,
};

const projectsSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    fetchProjectsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchProjectsSuccess: (state, action) => {
      state.loading = false;
      state.projects = action.payload;
      state.error = null;
    },
    fetchProjectsFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { fetchProjectsStart, fetchProjectsSuccess, fetchProjectsFailure } = projectsSlice.actions;

export default projectsSlice.reducer;
