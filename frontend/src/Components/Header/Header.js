import React, { useState } from 'react';
import styles from './Header.module.css';
import AuthComponent from '../AuthComponent/AuthComponent';
import Menu from './Menu';
export function Header(props) {
    
    return (
        <div className={styles.bannerContainer}>
            <Menu />
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
