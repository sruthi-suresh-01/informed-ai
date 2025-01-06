import { combineReducers, Reducer } from 'redux';
import userReducer from './userReducer';
import chatReducer from './chatReducer';
import adminReducer from './adminReducer';
import { UserAction, ChatAction, AdminAction } from '../types';
import { UserState, ChatState, AdminState } from '../types';

const rootReducer = combineReducers({
  user: userReducer as Reducer<UserState, UserAction>,
  chat: chatReducer as Reducer<ChatState, ChatAction>,
  admin: adminReducer as Reducer<AdminState, AdminAction>,
});

export default rootReducer;
