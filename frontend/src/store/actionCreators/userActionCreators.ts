import { Dispatch } from 'redux';
import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";
import { UserAction } from '../types';
import { User, UserDetails } from '../../types';
const api_urls = Constants.apis;
const userActions = actions.user;

interface UserRegistrationInput {
  email: string;
  first_name: string;
  last_name: string;
}

interface UserLoginInput {
  email: string;
  password: string;
}

interface NotificationUpdateInput {
  notification_ids: string[];
  status: string;
}

interface ApiResponse<T> {
  user?: User;
  notifications?: any[];
  error?: string;
  data?: T;
}

export const registerUser = ({ email, first_name, last_name }: UserRegistrationInput) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.registerUserRequest());

    if (email) {
      apiClient.post<ApiResponse<User>>(api_urls.register, { email, first_name, last_name })
        .then(response => {
          const data = response.data;
          if (data.error) {
            dispatch(userActions.registerUserFailure(data.error));
          } else if(data.user) {
            dispatch(userActions.registerUserSuccess(data.user));
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
      apiClient.post<ApiResponse<{ user: User }>>(api_urls.login, { email, password })
        .then(response => {
          const data = response.data;
          if (data.error) {
            dispatch(userActions.loginFailure(data.error));
          } else if(data?.user) {
            dispatch(userActions.loginSuccess(data.user));
          }
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
        if (data.error) {
          dispatch(userActions.logoutFailure(data.error));
        } else {
          dispatch(userActions.logoutSuccess(data));
        }
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
          dispatch(userActions.verifyLoginSuccess(data.user));
        }
      })
      .catch(error => {
        dispatch(userActions.verifyLoginFailure(error.message));
      });
};

export const getUserDetails = () =>
  (dispatch: Dispatch<UserAction>) => {
    apiClient.get<ApiResponse<UserDetails>>(api_urls.getUserDetails)
      .then(response => {
        const data = response.data;
        if (data.error) {
          dispatch(userActions.getUserDetailsFailure(data.error));
        } else {
          dispatch(userActions.getUserDetailsSuccess(data));
        }
      })
      .catch(error => dispatch(userActions.getUserDetailsFailure(error.message)));
};

export const setUserDetails = ({ payload }: { payload: UserDetails }) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.setUserDetailsRequest());

    apiClient.post<ApiResponse<UserDetails>>(api_urls.setUserDetails, payload)
      .then(response => {
        const data = response.data;
        if (data.error) {
          dispatch(userActions.setUserDetailsFailure(data.error));
        } else {
          dispatch(userActions.setUserDetailsSuccess(data));
        }
      })
      .catch(error => {
        dispatch(userActions.setUserDetailsFailure(error.message));
      });
};

export const getUserMedicalDetails = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.getUserMedicalDetailsRequest());

    apiClient.get<ApiResponse<any>>(api_urls.getUserMedicalDetails)
      .then(response => {
        const data = response.data;
        if (data.error) {
          dispatch(userActions.getUserMedicalDetailsFailure(data.error));
        } else {
          dispatch(userActions.getUserMedicalDetailsSuccess(data));
        }
      })
      .catch(error => dispatch(userActions.getUserMedicalDetailsFailure(error.message)));
};

export const setUserMedicalDetails = ({ payload }: { payload: any }) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.setUserMedicalDetailsRequest());

    apiClient.post<ApiResponse<any>>(api_urls.setUserMedicalDetails, payload)
      .then(response => {
        const data = response.data;
        if (data.error) {
          dispatch(userActions.setUserMedicalDetailsFailure(data.error));
        } else {
          dispatch(userActions.setUserMedicalDetailsSuccess(data));
        }
      })
      .catch(error => {
        dispatch(userActions.setUserMedicalDetailsFailure(error.message));
      });
};

export const getUserSettings = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.getUserSettingsRequest());

    apiClient.get<ApiResponse<any>>(api_urls.getUserSettings)
      .then(response => {
        dispatch(userActions.getUserSettingsSuccess(response.data));
      })
      .catch(error => dispatch(userActions.getUserSettingsFailure(error.message)));
};

export const setUserSettings = ({ payload }: { payload: any }) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.setUserSettingsRequest());

    apiClient.post<ApiResponse<any>>(api_urls.setUserSettings, payload)
      .then(response => {
        dispatch(userActions.setUserSettingsSuccess(response.data));
      })
      .catch(error => dispatch(userActions.setUserSettingsFailure(error.message)));
};

export const fetchNotifications = () =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.fetchNotificationsRequest());

    apiClient.get<ApiResponse<{ notifications: any[] }>>(api_urls.fetchNotifications)
      .then(response => {
        const data = response.data;
        if(data.notifications) {
          dispatch(userActions.fetchNotificationsSuccess(data.notifications));
        }
      })
      .catch(error => dispatch(userActions.fetchNotificationsFailure(error.message)));
};

export const updateNotificationStatus = ({ notification_ids, status }: NotificationUpdateInput) =>
  (dispatch: Dispatch<UserAction>) => {
    dispatch(userActions.updateNotificationStatusRequest());

    apiClient.put<ApiResponse<{ notifications: any[] }>>(api_urls.updateNotificationStatus, { notification_ids, status })
      .then(response => {
        const data = response.data;
        if(data.notifications) {
          dispatch(userActions.updateNotificationStatusSuccess(data.notifications));
        }
      })
      .catch(error => dispatch(userActions.updateNotificationStatusFailure(error.message)));
};
