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
    firstName: string;
    lastName: string;
    age: number;
    addressLine1: string;
    addressLine2: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
    phoneNumber: string;
    ethnicity: string;
    language: string;
}

export interface UserSettings {
    dailyUpdates: boolean;
    dailyUpdatePrompt: string;
}

export interface UserMedicalDetails {
    bloodType: string;
    height: number;
    weight: number;
    healthConditions: HealthCondition[];
    weatherSensitivities: WeatherSensitivity[];
}

export interface NotificationItem {
    notificationId: string;
    title: string;
    content: string;
    status: 'READY' | 'DELIVERED' | 'VIEWED';
    createdAt: string;
    chatThreadId?: string;
}

export interface User {
    email: string;
    accountType: 'admin' | 'superadmin' | 'user';
    details?: UserDetails;
    isActive?: boolean;
}

export type ResponseType = 'text' | 'audio' | 'text_message';

export interface Message {
    source: 'webapp' | 'assistant';
    content: string;
    messageId?: string;
    responseType?: ResponseType;
    requestedResponseType?: ResponseType;
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
