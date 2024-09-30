import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import * as userActions from '../../store/actionCreators/userActionCreators'

import { Grid, TextField, MenuItem } from '@mui/material';

const initialUserDetails = {
    first_name: "",
    last_name: "",
    age: "",
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    zip_code: "",
    country: "",
    phone_number: "",
    ethnicity: "",
    languages: [
      { name: "spanish", is_preferred: false },
      { name: "english", is_preferred: true }
    ]
  }
const languages =  [
    { name: "spanish", is_preferred: false },
    { name: "english", is_preferred: true }
]

const ethnicities = [
    'Hispanic',
    'White',
    'Black',
    'Asian',
    'Native American',
    'Pacific Islander',
    'Other'
];

const states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

const UserUpdate = ({ onChange }) => {
    const dispatch = useDispatch();
    const user = useSelector(state => state.user.user)
    const isLoggedIn = useSelector(state => state.user.loggedIn)
    const isLoading = useSelector(state => state.user.isLoading)
    const currentUserDetails = useSelector(state => state.user.user_details)
    const [userDetails, setUserDetails] = useState(initialUserDetails);

    useEffect(() => {
        if(isLoggedIn && user && user.username) {
            dispatch(userActions.getUserDetails({ username: user.username}))
        }
        return () => {
            // Cleanup on App unmount if needed
            setUserDetails(initialUserDetails)
        };
    }, []);

    useEffect(() => {
        if(!isLoading && currentUserDetails && Object.keys(currentUserDetails).length > 0 ) {
            setUserDetails(currentUserDetails)
        }
        return () => {
            // Cleanup on App unmount if needed
        };
    }, [isLoading, currentUserDetails]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        const updatedUser = { ...userDetails, [name]: value };
        setUserDetails(updatedUser);
        onChange(updatedUser);
    };

    return (
    <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
            <TextField
            label="First Name"
            name="first_name"
            value={userDetails.first_name}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12} sm={6}>
            <TextField
            label="Last Name"
            name="last_name"
            value={userDetails.last_name}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12}>
            <TextField
            label="Age"
            name="age"
            type="number"
            value={userDetails.age}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12}>
            <TextField
            label="Address Line 1"
            name="address_line1"
            value={userDetails.address_line1}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12}>
            <TextField
            label="Address Line 2"
            name="address_line2"
            value={userDetails.address_line2}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12} sm={6}>
            <TextField
            label="City"
            name="city"
            value={userDetails.city}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12} sm={6}>
            <TextField
            select
            label="State"
            name="state"
            value={userDetails.state}
            onChange={handleChange}
            fullWidth
            >
            {states.map((state, index) => (
                <MenuItem key={index} value={state}>
                {state}
                </MenuItem>
            ))}
            </TextField>
        </Grid>
        <Grid item xs={12} sm={6}>
            <TextField
            label="Zip Code"
            name="zip_code"
            value={userDetails.zip_code}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12} sm={6}>
            <TextField
            label="Country"
            name="country"
            value={userDetails.country}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12}>
            <TextField
            label="Phone Number"
            name="phone_number"
            value={userDetails.phone_number}
            onChange={handleChange}
            fullWidth
            />
        </Grid>
        <Grid item xs={12}>
            <TextField
            select
            label="Ethnicity"
            name="ethnicity"
            value={userDetails.ethnicity}
            onChange={handleChange}
            fullWidth
            >
            {ethnicities.map((ethnicity, index) => (
                <MenuItem key={index} value={ethnicity}>
                {ethnicity}
                </MenuItem>
            ))}
            </TextField>
        </Grid>
        <Grid item xs={12}>
            <TextField
            select
            label="Preferred Language"
            name="preferred_language"
            value={userDetails.languages && userDetails.languages.find(lang => lang.is_preferred)?.name || ''}
            onChange={(e) => {
                const preferredLanguage = e.target.value;
                const updatedLanguages = userDetails.languages && userDetails.languages.map(lang =>
                ({ ...lang, is_preferred: lang.name === preferredLanguage })
                );
                const updatedUser = { ...userDetails, languages: updatedLanguages };
                setUserDetails(updatedUser);
                onChange(updatedUser);
            }}
            fullWidth
            >
            {languages.map((language, index) => (
                <MenuItem key={index} value={language.name}>
                {language.name}
                </MenuItem>
            ))}
            </TextField>
        </Grid>
    </Grid>
    );
};

export default UserUpdate;
