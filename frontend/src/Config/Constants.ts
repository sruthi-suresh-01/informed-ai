interface ApiEndpoints {
  addUserMessage: string;
  getChatThread: string;
  register: string;
  login: string;
  logout: string;
  verifyLogin: string;
  getUserDetails: string;
  setUserDetails: string;
  getUserMedicalDetails: string;
  setUserMedicalDetails: string;
  weatherAlerts: string;
  fetchNotifications: string;
  updateNotificationStatus: string;
  getUserSettings: string;
  setUserSettings: string;
}

interface AppConstants {
  apis: ApiEndpoints;
}

export const Constants: AppConstants = {
  "apis": {
    "addUserMessage": "api/v1/chat",
    "getChatThread": "api/v1/chat",
    "register": "api/v1/user/register",
    "login": "api/v1/user/login",
    "logout": "api/v1/user/logout",
    "verifyLogin": "api/v1/user/me",
    "getUserDetails": "api/v1/user/details",
    "setUserDetails": "api/v1/user/details",
    "getUserMedicalDetails": "api/v1/user/medical-details",
    "setUserMedicalDetails": "api/v1/user/medical-details",
    "weatherAlerts": "/api/v1/admin/weather-alerts",
    "fetchNotifications": "/api/v1/notifications/",
    "updateNotificationStatus": "/api/v1/notifications/",
    "getUserSettings": "/api/v1/user/settings",
    "setUserSettings": "/api/v1/user/settings"
  }
};
