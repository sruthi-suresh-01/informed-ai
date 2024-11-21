import { combineReducers } from 'redux';
import userReducer from './userReducer';
import chatReducer from './chatReducer';
import adminReducer from './adminReducer';

const rootReducer = combineReducers({
  user: userReducer,
  chat: chatReducer,
  admin: adminReducer,
});

export default rootReducer;
