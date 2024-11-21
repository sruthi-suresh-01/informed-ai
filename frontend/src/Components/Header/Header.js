import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';
import AuthComponent from '../AuthComponent/AuthComponent';
import Menu from './Menu';

export function Header(props) {
    return (
        <div className={styles.bannerContainer}>
            <Menu />
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                <p>
                    Informed
                </p>
            </Link>
            <div className={styles.loginDiv}>
                <AuthComponent />
            </div>
        </div>
    );
}

export default Header;
