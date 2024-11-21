import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";

const api_urls = Constants.apis;
const adminActions = actions.admin;

export const addNotification = (notification) => dispatch => {
    dispatch(adminActions.addNotificationRequest());

    apiClient.post(api_urls.notifications, {
        zip_code: notification.zipCode,
        message: notification.message,
        expires_at: notification.expiresAt
    })
        .then(response => {
            const data = response.data;
            if (data.error) {
                dispatch(adminActions.addNotificationFailure(data.error));
            } else {
                dispatch(adminActions.addNotificationSuccess(data));
            }
        })
        .catch(error => {
            dispatch(adminActions.addNotificationFailure(error.message));
        });
};

export const cancelNotification = (notificationId) => dispatch => {
    dispatch(adminActions.cancelNotificationRequest());

    apiClient.delete(`${api_urls.notifications}/${notificationId}`)
        .then(response => {
            const data = response.data;
            if (data.error) {
                dispatch(adminActions.cancelNotificationFailure(data.error));
            } else {
                dispatch(adminActions.cancelNotificationSuccess(notificationId));
            }
        })
        .catch(error => {
            dispatch(adminActions.cancelNotificationFailure(error.message));
        });
};

export const fetchNotifications = (filters = {}) => dispatch => {
    dispatch(adminActions.fetchNotificationsRequest());

    const params = new URLSearchParams();
    if (filters.zipCode) params.append('zip_code', filters.zipCode);
    if (filters.isActive !== undefined && filters.isActive !== null) params.append('is_active', filters.isActive);

    const url = `${api_urls.notifications}${params.toString() ? '?' + params.toString() : ''}`;

    apiClient.get(url)
        .then(response => {
            const data = response.data;
            if (data.error) {
                dispatch(adminActions.fetchNotificationsFailure(data.error));
            } else {
                dispatch(adminActions.fetchNotificationsSuccess(data));
            }
        })
        .catch(error => {
            dispatch(adminActions.fetchNotificationsFailure(error.message));
        });
};
