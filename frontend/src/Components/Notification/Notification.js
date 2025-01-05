import React, { useState, useMemo, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { IconButton, Menu, MenuItem, Badge } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import styles from './Notification.module.css';
import { formatDistanceToNow } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import * as chatActions from '../../store/actionCreators/chatActionCreators'
import * as userActions from '../../store/actionCreators/userActionCreators';

const Notification = () => {
  const dispatch = useDispatch();
  const [anchorEl, setAnchorEl] = useState(null);
  const notifications = useSelector(state => state.user.notifications);
  const navigate = useNavigate();

  const unreadCount = useMemo(() =>
    notifications.filter(n => n.status === 'DELIVERED' || n.status === 'READY').length,
    [notifications]
  );

  useEffect(() => {
    if (notifications.length > 0) {
      console.log("notifications", notifications);
      const readyNotifications = notifications
        .filter(n => n.status === 'READY')
        .map(n => n.notification_id);

      if (readyNotifications.length > 0) {
        dispatch(userActions.updateNotificationStatus({
          notification_ids: readyNotifications,
          status: 'DELIVERED'
        }));
      }
    }
  }, [notifications, dispatch]);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);

    const unreadNotifications = notifications
      .filter(n => n.status !== 'VIEWED')
      .map(n => n.notification_id);

    if (unreadNotifications.length > 0) {
      dispatch(userActions.updateNotificationStatus({
        notification_ids: unreadNotifications,
        status: 'VIEWED'
      }));
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const formatTimeAgo = (timestamp) => {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  };

  const handleNotificationClick = (notification) => {
    if (notification.chat_thread_id) {
      dispatch(chatActions.setCurrentChatThreadId(notification.chat_thread_id, true));
      navigate(`/chat?id=${notification.chat_thread_id}`);
      handleClose();
    }
  };

  return (
    <div className={styles.notificationComponent}>
      <IconButton onClick={handleClick}>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {notifications.length === 0 ? (
          <MenuItem disabled>No notifications</MenuItem>
        ) : (
          notifications.map((notification) => (
            <MenuItem
              key={notification.notification_id}
              className={notification.status === 'VIEWED' ? styles.readNotification : styles.unreadNotification}
              onClick={() => handleNotificationClick(notification)}
            >
              <div>
                <div className={styles.notificationContent}>
                  <span className={styles.notificationTitle}>{notification.title}: </span>
                  {notification.content}
                </div>
                <div className={styles.notificationTime}>
                  {formatTimeAgo(notification.created_at)}
                </div>
              </div>
            </MenuItem>
          ))
        )}
      </Menu>
    </div>
  );
};

export default Notification;
