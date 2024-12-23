import axios from 'axios';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? "http://localhost:3001" : "",
  timeout: 10000,
  withCredentials: true, // This is essential to send cookies with each request
  headers: {'Content-Type': 'application/json'}
});

// Add a method for blob requests
apiClient.blob = (url, config = {}) => {
    return apiClient.get(url, {
        ...config,
        responseType: 'blob',
        headers: {
            ...config.headers,
            'Accept': 'audio/mpeg',
        }
    });
};

export default apiClient;
