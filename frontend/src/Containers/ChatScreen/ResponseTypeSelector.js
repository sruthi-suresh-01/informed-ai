import React, { useState } from 'react';
import { TextFields, VoiceChat, Message } from '@mui/icons-material';
import { IconButton, Menu, MenuItem } from '@mui/material';
import styles from './ChatScreen.module.css';

const MESSAGE_RESPONSE_TYPES = {
    TEXT: 'text',
    AUDIO: 'audio',
    TEXT_MESSAGE: 'text_message'
};

export function ResponseTypeSelector({ currentType, onTypeChange }) {
    const [menuAnchorEl, setMenuAnchorEl] = useState(null);
    const isMenuOpen = Boolean(menuAnchorEl);

    const openTypeMenu = (event) => {
        setMenuAnchorEl(event.currentTarget);
    };

    const selectResponseType = (type) => {
        if (type && Object.values(MESSAGE_RESPONSE_TYPES).includes(type)) {
            onTypeChange(type);
        }
        setMenuAnchorEl(null);
    };

    return (
        <>
            <IconButton
                onClick={openTypeMenu}
                className={styles.modeToggle}
                aria-controls={isMenuOpen ? 'response-type-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={isMenuOpen ? 'true' : undefined}
                size="large"
            >
                {currentType === MESSAGE_RESPONSE_TYPES.AUDIO ? <VoiceChat /> :
                 currentType === MESSAGE_RESPONSE_TYPES.TEXT_MESSAGE ? <Message /> :
                 <TextFields />}
            </IconButton>
            <Menu
                id="response-type-menu"
                anchorEl={menuAnchorEl}
                open={isMenuOpen}
                onClose={() => selectResponseType()}
                anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'center',
                }}
                transformOrigin={{
                    vertical: 'bottom',
                    horizontal: 'center',
                }}
            >
                <MenuItem
                    onClick={() => selectResponseType(MESSAGE_RESPONSE_TYPES.TEXT)}
                    className={currentType === MESSAGE_RESPONSE_TYPES.TEXT ? styles.selectedMenuItem : ''}
                >
                    <TextFields className={styles.menuIcon} />
                </MenuItem>
                <MenuItem
                    onClick={() => selectResponseType(MESSAGE_RESPONSE_TYPES.AUDIO)}
                    className={currentType === MESSAGE_RESPONSE_TYPES.AUDIO ? styles.selectedMenuItem : ''}
                >
                    <VoiceChat className={styles.menuIcon} />
                </MenuItem>
                <MenuItem
                    onClick={() => selectResponseType(MESSAGE_RESPONSE_TYPES.TEXT_MESSAGE)}
                    className={currentType === MESSAGE_RESPONSE_TYPES.TEXT_MESSAGE ? styles.selectedMenuItem : ''}
                >
                    <Message className={styles.menuIcon} />
                </MenuItem>
            </Menu>
        </>
    );
}

export { MESSAGE_RESPONSE_TYPES };
