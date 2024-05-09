import React, { useState } from 'react';
import styles from './Header.module.css';
import AuthComponent from '../AuthComponent/AuthComponent';

export function Header(props) {
    return (
        <div className={styles.bannerContainer}>
            <p>
                Informed
            </p>
            <div className={styles.loginDiv}>
                <AuthComponent />
            </div>
        </div>

    );
}

export default Header;
