import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Button } from '@mui/material';

interface DialogAction {
  text: string;
  invoke: () => void;
  type?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

interface DialogWrapperProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children?: React.ReactNode;
  onSave?: () => void;
  actions?: DialogAction[];
}

export const DialogWrapper: React.FC<DialogWrapperProps> = ({
  open,
  onClose,
  title,
  children,
  onSave,
  actions
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      sx={{
        '.MuiDialogContent-root': {
          paddingTop: '20px !important',
        },
        '.MuiPaper-root': {
          maxHeight: '80vh',
        },
      }}
    >
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        {children}
      </DialogContent>
      {actions?.length > 0 && (
        <DialogActions>
          {actions.map((action, idx) => (
            <Button
              key={idx}
              onClick={action.invoke}
              color={action.type || 'primary'}
            >
              {action.text}
            </Button>
          ))}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default DialogWrapper;
