import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import PersonIcon from '@mui/icons-material/Person';

import HealthUpdate from '../../Containers/HealthUpdate/HealthUpdate';
import UserUpdate from '../../Containers/UserUpdate/UserUpdate';
import DialogWrapper from '../DialogWrapper/DialogWrapper';
import { useNotification } from '../../Containers/HOCLayout/NotificationContext';
import styles from './Header.module.css';

import * as userActions from '../../store/actionCreators/userActionCreators'


const menuItems = [
    {
        code: 'profile',
        label: 'Profile',
        dialog: true,
        dialogProps: {
            title: "Update User Details",
            success_msg: "User details updated successfully!",
        }
    },
    {
        code: 'health_details',
        label: 'Health Details',
        dialogProps: {
            title: "Update Health Details",
            success_msg: "User details updated successfully!",
        }
    },
    // {
    //     code: 'dependants',
    //     label: 'Dependants',
    // },
]
const initialDialogFormState = {"profile": {}, "health_details": {}}
export function Menu(props) {
    const dispatch = useDispatch();
    const user = useSelector(state => state.user.user)
    const [open, setOpen] = useState(false);
    const [dialogFormState, setDialogFormState] = useState(initialDialogFormState);
    const [isDialogOpen, openDialog] = useState(false);
    const [selectedMenuItem, selectMenuItem] = useState('');
    const showNotification = useNotification()
    const toggleDrawer = (newOpen) => () => {
        setOpen(newOpen);
    };

    const handleDialogClose = () => {
        selectMenuItem('')
        openDialog(false)
    }

    useEffect(() => {
        if(selectedMenuItem) {
            openDialog(true)
        }

    }, [selectedMenuItem]);

    useEffect(() => {
        // if(isLoggedIn && user && user.username) {
        //     dispatch(userActions.getUserDetails({ username: user.username}))
        // }
        return () => {
            // Cleanup on App unmount if needed
            setDialogFormState(initialDialogFormState)
        };
    }, []);

    const handleDialogFormChange = (updatedFormState) => {
        const newDialogForm = dialogFormState
        if(selectedMenuItem == "profile") {
            newDialogForm["profile"] = { ...updatedFormState }
        } else if(selectedMenuItem == "health_details") {
            newDialogForm["health_details"] = { ...updatedFormState }
        }
        setDialogFormState(newDialogForm)
    }

    const handleOnSave = () => {
        switch(selectedMenuItem) {
            case "profile":
                dispatch(userActions.setUserDetails({ username: user.username, payload: dialogFormState[selectedMenuItem]}))
                break;
            case 'health_details':
                dispatch(userActions.setUserMedicalDetails({ username: user.username, payload: dialogFormState[selectedMenuItem]}))
                break

        }
            

        showNotification({ severity: 'success', message: menuItems.find((item) => item.code == selectedMenuItem)?.dialogProps?.success_msg });
        handleDialogClose()
    }

    const DrawerList = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)}>
        <List>
        {menuItems.map((item, index) => (
            <ListItem key={item.code} disablePadding>
            <ListItemButton onClick={() => {
                selectMenuItem(item.code)
            }}>
                <ListItemIcon>
                {index % 2 === 0 ? <PersonIcon /> : <HealthAndSafetyIcon />}
                </ListItemIcon>
                <ListItemText primary={item.label} />
            </ListItemButton>
            </ListItem>
        ))}
        </List>
        {/* <Divider />
        <List>
        {['All mail', 'Trash', 'Spam'].map((text, index) => (
            <ListItem key={text} disablePadding>
            <ListItemButton>
                <ListItemIcon>
                {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
                </ListItemIcon>
                <ListItemText primary={text} />
            </ListItemButton>
            </ListItem>
        ))}
        </List> */}
    </Box>
    );

    return (
        <div className={styles.headerMenu}>
            <div onClick={toggleDrawer(true)} className={styles.menu_button}>
                <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="100" height="100" viewBox="0 0 256 256">
                    <g fill="#ffffff" fillRule="nonzero" stroke="none" strokeWidth="1" strokeLinecap="butt" strokeLinejoin="miter" strokeMiterlimit="10" strokeDasharray="" strokeDashoffset="0" fontFamily="none" fontWeight="none" fontSize="none" textAnchor="none" style={{ mixBlendMode: 'normal' }}>
                    <g transform="scale(8.53333, 8.53333)">
                        <path d="M3,7c-0.36064,-0.0051 -0.69608,0.18438 -0.87789,0.49587c-0.18181,0.3115 -0.18181,0.69676 0,1.00825c0.18181,0.3115 0.51725,0.50097 0.87789,0.49587h24c0.36064,0.0051 0.69608,-0.18438 0.87789,-0.49587c0.18181,-0.3115 0.18181,-0.69676 0,-1.00825c-0.18181,-0.3115 -0.51725,-0.50097 -0.87789,-0.49587zM3,14c-0.36064,-0.0051 -0.69608,0.18438 -0.87789,0.49587c-0.18181,0.3115 -0.18181,0.69676 0,1.00825c0.18181,0.3115 0.51725,0.50097 0.87789,0.49587h24c0.36064,0.0051 0.69608,-0.18438 0.87789,-0.49587c0.18181,-0.3115 0.18181,-0.69676 0,-1.00825c-0.18181,-0.3115 -0.51725,-0.50097 -0.87789,-0.49587zM3,21c-0.36064,-0.0051 -0.69608,0.18438 -0.87789,0.49587c-0.18181,0.3115 -0.18181,0.69676 0,1.00825c0.18181,0.3115 0.51725,0.50097 0.87789,0.49587h24c0.36064,0.0051 0.69608,-0.18438 0.87789,-0.49587c0.18181,-0.3115 0.18181,-0.69676 0,-1.00825c-0.18181,-0.3115 -0.51725,-0.50097 -0.87789,-0.49587z"></path>
                    </g>
                    </g>
                </svg>
            </div>
            <Drawer open={open} onClose={toggleDrawer(false)}>
        {DrawerList}
      </Drawer>
        <DialogWrapper
            open={isDialogOpen}
            title={menuItems.find((item) => item.code == selectedMenuItem)?.dialogProps?.title || ''}
            actions={[
                {
                    type: "primary",
                    text: "Cancel",
                    invoke: () => {
                        handleDialogClose()
                    }
                },
                {
                    type: "primary",
                    text: "Save",
                    invoke: handleOnSave
                },
            ]}
        >
            {
                selectedMenuItem == 'profile' &&
                <UserUpdate onChange={handleDialogFormChange}/>
            }
            {
                selectedMenuItem == 'health_details' &&
                <HealthUpdate onChange={handleDialogFormChange}/>
            }
            {
                selectedMenuItem == 'dependants' &&
                <UserUpdate onChange={handleDialogFormChange}/>
            }
            
        </DialogWrapper>

        </div>
    );
}

export default Menu;
