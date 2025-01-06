import { Action } from 'redux';
import { Message, WeatherAlert, User, UserDetails, UserMedicalDetails, UserSettings, NotificationItem } from '../types';

export interface AdminAction extends Action {
  payload?: WeatherAlert | WeatherAlert[] | string | Error;
}

export interface ChatAction extends Action {
  payload?: any;
  chatThreadId?: string;
  resetMessages?: boolean;
  messages?: Message[];
  chat_thread_id?: string;
  query?: string;
  query_id?: string;
}

export interface UserAction extends Action {
  payload?: User | string | Error | any;
}

export interface UserState {
  user: User | null;
  loggedIn: boolean;
  isLoading: boolean;
  user_details: UserDetails;
  user_medical_details: UserMedicalDetails;
  user_settings: UserSettings;
  notifications: NotificationItem[];
  error: string | null;
  isNotificationsLoading: boolean;
}

export interface ChatState {
  messages: Message[];
  waitingForResponse: boolean;
  currentChatThreadId: string | null;
  error: string | null;
  isLoading: boolean;
}

export interface AdminState {
  weatherAlerts: WeatherAlert[];
  error: string | null;
  isLoading: boolean;
}

export interface RootState {
  user: UserState;
  chat: ChatState;
  admin: AdminState;
}
