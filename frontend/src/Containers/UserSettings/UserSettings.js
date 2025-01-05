import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { Grid, TextField, Switch, FormControlLabel } from '@mui/material';

const initialSettings = {
    daily_updates: false,
    daily_update_prompt: "",
};

const UserSettings = ({ onChange }) => {
    const dispatch = useDispatch();
    const user = useSelector(state => state.user.user);
    const isLoggedIn = useSelector(state => state.user.loggedIn);
    const isLoading = useSelector(state => state.user.isLoading);
    const currentSettings = useSelector(state => state.user.user_settings);
    const [settings, setSettings] = useState(initialSettings);

    useEffect(() => {
        if (isLoggedIn && user) {
            dispatch(userActions.getUserSettings());
        }
        return () => {
            setSettings(initialSettings);
        };
    }, []);

    useEffect(() => {
        if (!isLoading && currentSettings && Object.keys(currentSettings).length > 0) {
            setSettings(currentSettings);
        }
    }, [isLoading, currentSettings]);

    const handleChange = (e) => {
        const { name, value, checked } = e.target;
        const newValue = name === 'daily_updates' ? checked : value;
        const updatedSettings = { ...settings, [name]: newValue };
        setSettings(updatedSettings);
        onChange(updatedSettings);
    };

    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                <FormControlLabel
                    control={
                        <Switch
                            checked={settings.daily_updates || false}
                            onChange={handleChange}
                            name="daily_updates"
                        />
                    }
                    label="Receive Daily Updates"
                />
            </Grid>
            <Grid item xs={12}>
                <TextField
                    label="Daily Update Prompt"
                    name="daily_update_prompt"
                    value={settings.daily_update_prompt || ''}
                    onChange={handleChange}
                    fullWidth
                    multiline
                    rows={4}
                    disabled={!settings.daily_updates}
                    helperText="Customize your daily update prompt"
                />
            </Grid>
        </Grid>
    );
};

export default UserSettings;
