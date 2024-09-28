import React, { createContext, useState, useContext, useCallback } from 'react';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

const NotificationContext = createContext();

export const useNotification = () => useContext(NotificationContext);

const Alert = React.forwardRef((props, ref) => {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export const NotificationProvider = ({ children }) => {
  const [notification, setNotification] = useState({ open: false, severity: '', message: '' });

  const showNotification = useCallback(({ severity, message }) => {
    setNotification({ open: true, severity, message });
  }, []);

  const handleClose = useCallback(() => {
    setNotification({ ...notification, open: false });
  }, [notification]);

  return (
    <NotificationContext.Provider value={showNotification}>
      {children}
      <Snackbar open={notification.open} autoHideDuration={6000} onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%' }}>
          {notification.message}
        </Alert>
      </Snackbar>
    </NotificationContext.Provider>
  );
};
