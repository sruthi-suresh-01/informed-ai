import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Button } from '@mui/material';

const DialogWrapper = ({ open, onClose, title, children, onSave, actions }) => {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm" 
        sx={{
            '.MuiDialogContent-root': {
            paddingTop: '20px !important',
            },
            '.MuiPaper-root': {
              maxHeight: '80vh', // Set your desired max height here
            },
            
        }}
      >
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        {children || <></>}
      </DialogContent>
      {
        actions && Array.isArray(actions) && actions.length > 0 && 
            <DialogActions>
                { 
                    actions.map((action, idx) => {
                        return (<Button key={idx} onClick={action.invoke} color={action.type || "primary"}>
                            {action.text || ''}
                        </Button>)
                    })
                }
            </DialogActions>
      }
    </Dialog>
  );
};

export default DialogWrapper;
