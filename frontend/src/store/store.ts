import { configureStore } from '@reduxjs/toolkit';
import rootReducer from './reducers';
export const store = configureStore({
  reducer: rootReducer,
});


// Infer the `AppDispatch` type from the store itself
// TODO: This needs to be fixed
export type AppDispatch = typeof store.dispatch;

export default store;
