import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Grid, TextField, MenuItem, Button, IconButton, Typography } from '@mui/material';
import { AddCircle, RemoveCircle } from '@mui/icons-material';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { RootState } from '../../store/types';
import { UserMedicalDetails, WeatherSensitivity, HealthCondition } from '../../types';
import { AppDispatch } from '../../store/store';

interface HealthUpdateProps {
  onChange: (health: UserMedicalDetails) => void;
}

const bloodTypes = [
  'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
] as const;

const severities = [
  'Mild', 'Moderate', 'Severe'
] as const;

const sensitivityTypes = {
  'rain': 'Rain',
  'temperature': 'Temperature',
  'air_quality': 'Air Quality'
} as const;

const initialHealthDetails: UserMedicalDetails = {
  blood_type: '',
  height: null,
  weight: null,
  health_conditions: [],
  weather_sensitivities: []
};

export const HealthUpdate: React.FC<HealthUpdateProps> = ({ onChange }) => {
  const dispatch = useDispatch<AppDispatch>();
  const user = useSelector((state: RootState) => state.user.user);
  const isLoggedIn = useSelector((state: RootState) => state.user.loggedIn);
  const isLoading = useSelector((state: RootState) => state.user.isLoading);
  const currentUserMedicalDetails = useSelector((state: RootState) => state.user.user_medical_details);
  const [health, setHealth] = useState<UserMedicalDetails>(initialHealthDetails);

  useEffect(() => {
    if(isLoggedIn && user && user.email) {
      dispatch(userActions.getUserMedicalDetails());
    }
    return () => {
      setHealth(initialHealthDetails);
    };
  }, []);

  useEffect(() => {
    if(!isLoading && currentUserMedicalDetails && Object.keys(currentUserMedicalDetails).length > 0) {
      setHealth(currentUserMedicalDetails as UserMedicalDetails);
    }
  }, [isLoading, currentUserMedicalDetails]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    const updatedHealth = {
      ...health,
      [name]: value || ''
    };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleConditionChange = (index: number, field: keyof HealthCondition, value: string) => {
    const updatedConditions = health.health_conditions.map((condition, i) => (
      i === index ? { ...condition, [field]: value } : condition
    ));
    const updatedHealth = { ...health, health_conditions: updatedConditions };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleAddCondition = () => {
    const newCondition: HealthCondition = { condition: '', severity: 'Mild', description: '' };
    const updatedHealth = { ...health, health_conditions: [...health.health_conditions, newCondition] };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleRemoveCondition = (index: number) => {
    const updatedConditions = health.health_conditions.filter((_, i) => i !== index);
    const updatedHealth = { ...health, health_conditions: updatedConditions };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleSensitivityChange = (index: number, field: keyof WeatherSensitivity, value: string) => {
    const updatedSensitivities = health.weather_sensitivities.map((sensitivity, i) => (
      i === index ? { ...sensitivity, [field]: value } : sensitivity
    ));
    const updatedHealth = { ...health, weather_sensitivities: updatedSensitivities };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleAddSensitivity = () => {
    const newSensitivity: WeatherSensitivity = { type: 'rain', description: '' };
    const updatedHealth = {
      ...health,
      weather_sensitivities: [...health.weather_sensitivities, newSensitivity]
    };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleRemoveSensitivity = (index: number) => {
    const updatedSensitivities = health.weather_sensitivities.filter((_, i) => i !== index);
    const updatedHealth = { ...health, weather_sensitivities: updatedSensitivities };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <TextField
          select
          label="Blood Type"
          name="blood_type"
          value={health.blood_type || ''}
          onChange={handleChange}
          fullWidth
        >
          <MenuItem value="">Select blood type</MenuItem>
          {bloodTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type}
            </MenuItem>
          ))}
        </TextField>
      </Grid>
      <Grid item xs={6}>
        <TextField
          label="Height (cm)"
          name="height"
          type="number"
          value={health.height || ''}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          label="Weight (kg)"
          name="weight"
          type="number"
          value={health.weight || ''}
          onChange={handleChange}
          fullWidth
        />
      </Grid>

      <Grid item xs={12}>
        <Typography variant="h6">Weather Sensitivities</Typography>
        {health.weather_sensitivities.map((sensitivity, index) => (
          <Grid container spacing={2} key={index}>
            <Grid item xs={12}>
              <Grid container justifyContent="flex-end">
                <IconButton onClick={() => handleRemoveSensitivity(index)} color="secondary">
                  <RemoveCircle />
                </IconButton>
              </Grid>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                label="Type"
                value={sensitivity.type}
                onChange={(e) => handleSensitivityChange(index, 'type', e.target.value as keyof typeof sensitivityTypes)}
                fullWidth
              >
                {Object.entries(sensitivityTypes).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={sensitivity.description}
                onChange={(e) => handleSensitivityChange(index, 'description', e.target.value)}
                fullWidth
                multiline
                rows={4}
              />
            </Grid>
          </Grid>
        ))}
        <Button onClick={handleAddSensitivity} color="primary" startIcon={<AddCircle />}>
          Add Sensitivity
        </Button>
      </Grid>

      <Grid item xs={12}>
        <Typography variant="h6">Health Conditions</Typography>
        {health.health_conditions.map((condition, index) => (
          <Grid container spacing={2} key={index}>
            <Grid item xs={12}>
              <Grid container justifyContent="flex-end">
                <IconButton onClick={() => handleRemoveCondition(index)} color="secondary">
                  <RemoveCircle />
                </IconButton>
              </Grid>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Condition"
                value={condition.condition}
                onChange={(e) => handleConditionChange(index, 'condition', e.target.value)}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                label="Severity"
                value={condition.severity}
                onChange={(e) => handleConditionChange(index, 'severity', e.target.value)}
                fullWidth
              >
                {severities.map((severity) => (
                  <MenuItem key={severity} value={severity}>
                    {severity}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={condition.description}
                onChange={(e) => handleConditionChange(index, 'description', e.target.value)}
                fullWidth
                multiline
                rows={4}
              />
            </Grid>
          </Grid>
        ))}
        <Button onClick={handleAddCondition} color="primary" startIcon={<AddCircle />}>
          Add Condition
        </Button>
      </Grid>
    </Grid>
  );
};

export default HealthUpdate;
