import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

interface BlobConfig extends AxiosRequestConfig {
  headers?: {
    Accept?: string;
    [key: string]: string | undefined;
  };
}

// Create an Axios instance with custom methods
interface CustomAxiosInstance extends AxiosInstance {
  blob: (url: string, config?: BlobConfig) => Promise<any>;
}

// Create an Axios instance
const apiClient: CustomAxiosInstance = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? "http://localhost:3001" : "",
  timeout: 10000,
  withCredentials: true, // This is essential to send cookies with each request
  headers: {'Content-Type': 'application/json'}
}) as CustomAxiosInstance;

// Add a method for blob requests
apiClient.blob = (url: string, config: BlobConfig = {}) => {
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
