import React, { createContext, useState, useContext, useCallback } from 'react';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';

interface ToastMessage {
  open: boolean;
  severity: AlertProps['severity'];
  message: string;
}

interface ShowToastMessage {
  severity: AlertProps['severity'];
  message: string;
}

type ToastMessageContextType = (message: ShowToastMessage) => void;

const ToastMessageContext = createContext<ToastMessageContextType | undefined>(undefined);

export const useToastMessage = (): ToastMessageContextType => {
  const context = useContext(ToastMessageContext);
  if (context === undefined) {
    throw new Error('useToastMessage must be used within a ToastMessageProvider');
  }
  return context;
};

const Alert = React.forwardRef<HTMLDivElement, AlertProps>((props, ref) => {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

interface ToastMessageProviderProps {
  children: React.ReactNode;
}

export const ToastMessageProvider: React.FC<ToastMessageProviderProps> = ({ children }) => {
  const [toastMessage, setToastMessage] = useState<ToastMessage>({
    open: false,
    severity: 'info',
    message: ''
  });

  const showToastMessage = useCallback(({ severity, message }: ShowToastMessage) => {
    setToastMessage({ open: true, severity, message });
  }, []);

  const handleClose = useCallback(() => {
    setToastMessage(prev => ({ ...prev, open: false }));
  }, []);

  return (
    <ToastMessageContext.Provider value={showToastMessage}>
      {children}
      <Snackbar
        open={toastMessage.open}
        autoHideDuration={6000}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={handleClose}
          severity={toastMessage.severity}
          sx={{ width: '100%' }}
        >
          {toastMessage.message}
        </Alert>
      </Snackbar>
    </ToastMessageContext.Provider>
  );
};
