import * as actionTypes from '../ActionTypes';

export const addNotificationRequest = () => ({
    type: actionTypes.ADD_NOTIFICATION_REQUEST
});

export const addNotificationSuccess = (notification) => ({
    type: actionTypes.ADD_NOTIFICATION_SUCCESS,
    payload: notification
});

export const addNotificationFailure = (error) => ({
    type: actionTypes.ADD_NOTIFICATION_FAILURE,
    payload: error
});

export const cancelNotificationRequest = () => ({
    type: actionTypes.CANCEL_NOTIFICATION_REQUEST
});

export const cancelNotificationSuccess = (notificationId) => ({
    type: actionTypes.CANCEL_NOTIFICATION_SUCCESS,
    payload: notificationId
});

export const cancelNotificationFailure = (error) => ({
    type: actionTypes.CANCEL_NOTIFICATION_FAILURE,
    payload: error
});

export const fetchNotificationsRequest = () => ({
    type: actionTypes.FETCH_NOTIFICATIONS_REQUEST
});

export const fetchNotificationsSuccess = (notifications) => ({
    type: actionTypes.FETCH_NOTIFICATIONS_SUCCESS,
    payload: notifications
});

export const fetchNotificationsFailure = (error) => ({
    type: actionTypes.FETCH_NOTIFICATIONS_FAILURE,
    payload: error
});
