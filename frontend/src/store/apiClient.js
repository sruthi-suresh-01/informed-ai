import axios from 'axios';

// Create an Axios instance
const apiClient = axios.create({
  timeout: 5000,
  withCredentials: true, // This is essential to send cookies with each request
  headers: {'Content-Type': 'application/json'}
});

export default apiClient;
