import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { Grid, TextField, MenuItem, Button, IconButton, Typography } from '@mui/material';
import { AddCircle, RemoveCircle } from '@mui/icons-material';

import * as userActions from '../../store/actionCreators/userActionCreators'


const bloodTypes = [
  'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
];

const severities = [
  'Mild', 'Moderate', 'Severe'
];

const sensitivityTypes = {
  'rain': 'Rain', 
  'temperature': 'Temperature', 
  'air_quality': 'Air Quality' 
}

const initialHealthDetails = {
  blood_type: '',
  height: '',
  weight: '',
  health_conditions: [],
  weather_sensitivities: []
};

const HealthUpdate = ({ onChange }) => {
  const dispatch = useDispatch();
  const user = useSelector(state => state.user.user)
  const isLoggedIn = useSelector(state => state.user.loggedIn)
  const isLoading = useSelector(state => state.user.isLoading)
  const currentUserMedicalDetails = useSelector(state => state.user.user_medical_details)
  const [health, setHealth] = useState(initialHealthDetails);

  useEffect(() => {
    if(isLoggedIn && user && user.username) {
        dispatch(userActions.getUserMedicalDetails({ username: user.username}))
    }
    return () => {
        // Cleanup on App unmount if needed
        setHealth(initialHealthDetails)
    };
  }, []);

  useEffect(() => {
    if(!isLoading && currentUserMedicalDetails && Object.keys(currentUserMedicalDetails).length > 0 ) {
      setHealth(currentUserMedicalDetails)
    }
    return () => {
        // Cleanup on App unmount if needed
    };
  }, [isLoading, currentUserMedicalDetails]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updatedHealth = { ...health, [name]: value };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleConditionChange = (index, field, value) => {
    const updatedConditions = health.health_conditions.map((condition, i) => (
      i === index ? { ...condition, [field]: value } : condition
    ));
    const updatedHealth = { ...health, health_conditions: updatedConditions };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleAddCondition = () => {
    const newCondition = { condition: '', severity: 'Mild', description: '' };
    const updatedHealth = { ...health, health_conditions: [...health.health_conditions, newCondition] };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleRemoveCondition = (index) => {
    const updatedConditions = health.health_conditions.filter((_, i) => i !== index);
    const updatedHealth = { ...health, health_conditions: updatedConditions };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleSensitivityChange = (index, field, value) => {
    const updatedSensitivities = health.weather_sensitivities.map((sensitivity, i) => (
      i === index ? { ...sensitivity, [field]: value } : sensitivity
    ));
    const updatedHealth = { ...health, weather_sensitivities: updatedSensitivities };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleAddSensitivity = () => {
    const newSensitivity = { type: 'rain', description: '' };
    const updatedHealth = { ...health, weather_sensitivities: [...health.weather_sensitivities, newSensitivity] };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  const handleRemoveSensitivity = (index) => {
    const updatedSensitivities = health.weather_sensitivities.filter((_, i) => i !== index);
    const updatedHealth = { ...health, weather_sensitivities: updatedSensitivities };
    setHealth(updatedHealth);
    onChange(updatedHealth);
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} >
        <TextField
          select
          label="Blood Type"
          name="blood_type"
          value={health.blood_type}
          onChange={handleChange}
          fullWidth
        >
          {bloodTypes.map((type, index) => (
            <MenuItem key={index} value={type}>
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
          value={health.height}
          onChange={handleChange}
          fullWidth
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          label="Weight (kg)"
          name="weight"
          type="number"
          value={health.weight}
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
                name="type"
                value={sensitivity.type}
                onChange={(e) => handleSensitivityChange(index, 'type', e.target.value)}
                fullWidth
              >
                {Object.keys(sensitivityTypes).map((type, index) => (
                  <MenuItem key={index} value={type}>
                    {sensitivityTypes[type]}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                name="description"
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
                name="condition"
                value={condition.condition}
                onChange={(e) => handleConditionChange(index, 'condition', e.target.value)}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                label="Severity"
                name="severity"
                value={condition.severity}
                onChange={(e) => handleConditionChange(index, 'severity', e.target.value)}
                fullWidth
              >
                {severities.map((severity, index) => (
                  <MenuItem key={index} value={severity}>
                    {severity}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                name="description"
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
