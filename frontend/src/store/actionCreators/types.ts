import { ResponseType } from '../../types';

export interface UserRegistrationInput {
  email: string;
  firstName: string;
  lastName: string;
}

export interface UserLoginInput {
  email: string;
  password: string;
}

export interface NotificationUpdateInput {
  notification_ids: string[];
  status: string;
}

export interface ApiUserDetails {
  first_name: string;
  last_name: string;
  age: number;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  phone_number: string;
  ethnicity: string;
  language: string;
}

export interface ApiUserSettings {
  daily_updates: boolean;
  daily_update_prompt: string;
}

export interface ApiNotificationItem {
  notification_id: string;
  title: string;
  content: string;
  status: 'READY' | 'DELIVERED' | 'VIEWED';
  created_at: string;
  chat_thread_id?: string;
}

export interface ApiHealthCondition {
  condition: string;
  severity: string;
  description: string;
}

export interface ApiWeatherSensitivity {
  type: string;
  description: string;
}

export interface ApiUserMedicalDetails {
  blood_type: string;
  height: number;
  weight: number;
  health_conditions: ApiHealthCondition[];
  weather_sensitivities: ApiWeatherSensitivity[];
}

// chat

export interface ApiMessage {
  source: 'webapp' | 'assistant';
  content: string;
  message_id?: string;
  response_type?: ResponseType;
  requested_response_type?: ResponseType;
}

export interface ApiChatResponse {
  chat_thread_id: string;
  messages: ApiMessage[];
}

export interface ApiChatMessageInput {
  message: string;
  requestedResponseType: ResponseType;
  chatThreadId?: string | null;
}

// admin
export interface ApiWeatherAlert {
  weather_alert_id: string;
  zip_code: string;
  message: string;
  created_by: string;
  created_at: string;
  expires_at: string;
  cancelled_at: string | null;
  is_active: boolean;
}

export interface WeatherAlertInput {
  zipCode: string;
  message: string;
  expiresAt: string;
}

export interface WeatherAlertFilters {
  zipCode?: string;
  isActive?: boolean;
}
