import { Dispatch } from 'redux';
import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";
import { UserAction } from '../types';
import { User, UserDetails, NotificationItem, UserSettings, UserMedicalDetails } from '../../types';
import {
  UserRegistrationInput,
  UserLoginInput,
  NotificationUpdateInput,
  ApiUserDetails,
  ApiUserSettings,
  ApiNotificationItem,
  ApiUserMedicalDetails
} from './types';
import { transformRequestToSnakeCase, transformResponseToCamelCase } from '../../utils/apiUtils';

const api_urls = Constants.apis;
const userActions = actions.user;

interface ApiResponse<T> {
  user?: User;
  notifications?: any[];
  error?: string;
  data?: T;
}

export const registerUser = ({ email, firstName, lastName }: UserRegistrationInput) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.registerUserRequest());

    if (email) {
      const payload = transformRequestToSnakeCase({ email, firstName, lastName });
      apiClient.post<ApiResponse<User>>(api_urls.register, payload)
        .then(response => {
          const data = response.data;
          if(data.user) {
            const transformedUser = transformResponseToCamelCase(data.user);
            dispatch(userActions.registerUserSuccess(transformedUser));
          }
        })
        .catch(error => {
          dispatch(userActions.registerUserFailure(error.message));
        });
    } else {
      dispatch(userActions.registerUserFailure("Email is required"));
    }
};

export const login = ({ email, password }: UserLoginInput) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.loginRequest());

    if (email) {
      const payload = transformRequestToSnakeCase({ email, password });
      apiClient.post<ApiResponse<{ user: User }>>(api_urls.login, payload)
        .then(response => {
          const data = response.data;
          const transformedUser = transformResponseToCamelCase(data.user);
          dispatch(userActions.loginSuccess(transformedUser));
        })
        .catch(error => {
          dispatch(userActions.loginFailure(error.message));
        });
    } else {
      dispatch(userActions.loginFailure("Email is required"));
    }
};

export const logout = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.logoutRequest());

    apiClient.get<ApiResponse<any>>(api_urls.logout)
      .then(response => {
        const data = response.data;
        dispatch(userActions.logoutSuccess(data));
      })
      .catch(error => dispatch(userActions.logoutFailure(error.message)));
};

export const verifyLogin = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.verifyLoginRequest());

    apiClient.get<ApiResponse<{ user: User }>>(api_urls.verifyLogin)
      .then(response => {
        const data = response.data;
        if(data.user) {
          const transformedUser = transformResponseToCamelCase(data.user);
          dispatch(userActions.verifyLoginSuccess(transformedUser));
        }
      })
      .catch(error => {
        dispatch(userActions.verifyLoginFailure(error.message));
      });
};

export const getUserDetails = () =>
  (dispatch: Dispatch<UserAction>) => {
    apiClient.get<ApiResponse<ApiUserDetails>>(api_urls.getUserDetails)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data as ApiUserDetails);
        dispatch(userActions.getUserDetailsSuccess(transformedData));
      })
      .catch(error => dispatch(userActions.getUserDetailsFailure(error.message)));
};

export const setUserDetails = ({ payload }: { payload: UserDetails }) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.setUserDetailsRequest());

    const apiPayload = transformRequestToSnakeCase(payload);
    apiClient.post<ApiResponse<ApiUserDetails>>(api_urls.setUserDetails, apiPayload)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data as ApiUserDetails);
        dispatch(userActions.setUserDetailsSuccess(transformedData));
      })
      .catch(error => {
        dispatch(userActions.setUserDetailsFailure(error.message));
      });
};

export const getUserMedicalDetails = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.getUserMedicalDetailsRequest());

    apiClient.get<ApiResponse<ApiUserMedicalDetails>>(api_urls.getUserMedicalDetails)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data as ApiUserMedicalDetails);
        dispatch(userActions.getUserMedicalDetailsSuccess(transformedData));
      })
      .catch(error => dispatch(userActions.getUserMedicalDetailsFailure(error.message)));
};

export const setUserMedicalDetails = ({ payload }: { payload: UserMedicalDetails }) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.setUserMedicalDetailsRequest());

    const apiPayload = transformRequestToSnakeCase(payload);
    apiClient.post<ApiResponse<ApiUserMedicalDetails>>(api_urls.setUserMedicalDetails, apiPayload)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data as ApiUserMedicalDetails) as UserMedicalDetails;
        dispatch(userActions.setUserMedicalDetailsSuccess(transformedData));
      })
      .catch(error => {
        dispatch(userActions.setUserMedicalDetailsFailure(error.message));
      });
};

export const getUserSettings = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.getUserSettingsRequest());

    apiClient.get<ApiResponse<ApiUserSettings>>(api_urls.getUserSettings)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data as ApiUserSettings) as UserSettings;
        dispatch(userActions.getUserSettingsSuccess(transformedData));
      })
      .catch(error => dispatch(userActions.getUserSettingsFailure(error.message)));
};

export const setUserSettings = ({ payload }: { payload: UserSettings }) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.setUserSettingsRequest());

    const apiPayload = transformRequestToSnakeCase(payload);
    apiClient.post<ApiResponse<ApiUserSettings>>(api_urls.setUserSettings, apiPayload)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data as ApiUserSettings) as UserSettings;
        dispatch(userActions.setUserSettingsSuccess(transformedData));
      })
      .catch(error => dispatch(userActions.setUserSettingsFailure(error.message)));
};

export const fetchNotifications = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.fetchNotificationsRequest());

    apiClient.get<ApiResponse<{ notifications: ApiNotificationItem[] }>>(api_urls.fetchNotifications)
      .then(response => {
        const data = response.data;
        if(data.notifications) {
          const transformedNotifications = data.notifications.map(notification =>
            transformResponseToCamelCase(notification)
          );
          dispatch(userActions.fetchNotificationsSuccess(transformedNotifications));
        }
      })
      .catch(error => dispatch(userActions.fetchNotificationsFailure(error.message)));
};

export const updateNotificationStatus = ({ notification_ids, status }: NotificationUpdateInput) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.updateNotificationStatusRequest());

    const payload = transformRequestToSnakeCase({ notificationIds: notification_ids, status });
    apiClient.put<ApiResponse<{ notifications: ApiNotificationItem[] }>>(
      api_urls.updateNotificationStatus,
      payload
    )
      .then(response => {
        const data = response.data;
        if(data.notifications) {
          const transformedNotifications = data.notifications.map(notification =>
            transformResponseToCamelCase(notification)
          );
          dispatch(userActions.updateNotificationStatusSuccess(transformedNotifications));
        }
      })
      .catch(error => dispatch(userActions.updateNotificationStatusFailure(error.message)));
};
