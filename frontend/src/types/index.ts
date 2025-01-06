

export interface HealthCondition {
    condition: string;
    severity: string;
    description: string;
}
export interface WeatherSensitivity {
    type: string;
    description: string;
}

export interface UserDetails {
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

export interface UserSettings {
    daily_updates: boolean;
    daily_update_prompt: string;
}

export interface UserMedicalDetails {
    blood_type: string;
    height: number;
    weight: number;
    health_conditions: HealthCondition[];
    weather_sensitivities: WeatherSensitivity[];
}

export interface NotificationItem {
    notification_id: string;
    title: string;
    content: string;
    status: 'READY' | 'DELIVERED' | 'VIEWED';
    created_at: string;
    chat_thread_id?: string;
}

export interface User {
    email: string;
    account_type: 'admin' | 'superadmin' | 'user';
    details?: UserDetails;
    is_active?: boolean;
}

export type ResponseType = 'text' | 'audio' | 'text_message';

export interface Message {
    source: 'webapp' | 'assistant';
    content: string;
    message_id?: string;
    response_type?: ResponseType;
    requested_response_type?: ResponseType;
}

export interface WeatherAlert {
    id: string;
    zipCode: string;
    message: string;
    createdBy: string;
    createdAt: string;
    expiresAt: string;
    cancelledAt: string | null;
    isActive: boolean;
  }
