import React from 'react';
import { useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';
import AuthComponent from '../AuthComponent/AuthComponent';
import Menu from './Menu';
import * as chatActions from '../../store/actionCreators/chatActionCreators';

export function Header(props) {
    const dispatch = useDispatch();
    return (
        <div className={styles.bannerContainer}>
            <Menu />
            <Link to="/chat" style={{ textDecoration: 'none', color: 'inherit' }} onClick={() => dispatch(chatActions.setCurrentChatThreadId(null))}>
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
