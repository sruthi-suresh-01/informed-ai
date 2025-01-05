import React, { createContext, useState, useContext, useCallback } from 'react';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

const ToastMessageContext = createContext();

export const useToastMessage = () => useContext(ToastMessageContext);

const Alert = React.forwardRef((props, ref) => {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export const ToastMessageProvider = ({ children }) => {
  const [toastMessage, setToastMessage] = useState({ open: false, severity: '', message: '' });

  const showToastMessage = useCallback(({ severity, message }) => {
    setToastMessage({ open: true, severity, message });
  }, []);

  const handleClose = useCallback(() => {
    setToastMessage({ ...toastMessage, open: false });
  }, [toastMessage]);

  return (
    <ToastMessageContext.Provider value={showToastMessage}>
      {children}
      <Snackbar open={toastMessage.open} autoHideDuration={6000} onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleClose} severity={toastMessage.severity} sx={{ width: '100%' }}>
          {toastMessage.message}
        </Alert>
      </Snackbar>
    </ToastMessageContext.Provider>
  );
};
