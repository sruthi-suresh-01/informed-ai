import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Grid, TextField, Switch, FormControlLabel } from '@mui/material';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { RootState } from '../../store/types';
import { UserSettings } from '../../types';
import { AppDispatch } from '../../store/store';


interface UserSettingsProps {
  onChange: (settings: UserSettings) => void;
}

const initialSettings: UserSettings = {
  daily_updates: false,
  daily_update_prompt: "",
};

export const UserSettingsUpdate: React.FC<UserSettingsProps> = ({ onChange }) => {
  const dispatch = useDispatch<AppDispatch>();
  const user = useSelector((state: RootState) => state.user.user);
  const isLoggedIn = useSelector((state: RootState) => state.user.loggedIn);
  const isLoading = useSelector((state: RootState) => state.user.isLoading);
  const currentSettings = useSelector((state: RootState) => state.user.user_settings);
  const [settings, setSettings] = useState<UserSettings>(initialSettings);

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
      setSettings(currentSettings as UserSettings);
    }
  }, [isLoading, currentSettings]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, checked } = e.target as HTMLInputElement;
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

export default UserSettingsUpdate;
