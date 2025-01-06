import React from 'react';
import { ThreeDots } from 'react-loader-spinner';
import styles from './Loader.module.css';

interface LoaderProps {
  color?: string;
  height?: string | number;
  width?: string | number;
  radius?: string | number;
}

export const Loader: React.FC<LoaderProps> = ({
  color = '#4fa94d',
  height = '20',
  width = '20',
  radius = '9'
}) => {
  return (
    <div className={styles.loaderContainer}>
      <ThreeDots
        visible={true}
        height={height}
        width={width}
        color={color}
        radius={radius}
        ariaLabel="three-dots-loading"
        wrapperStyle={{}}
        wrapperClass=""
      />
    </div>
  );
};

export default Loader;
