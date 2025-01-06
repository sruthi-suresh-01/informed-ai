import * as userActions from './userActions';
import * as chatActions from './chatActions';
import * as adminActions from './adminActions';

export const actions = {
  user: userActions,
  chat: chatActions,
  admin: adminActions
} as const;
