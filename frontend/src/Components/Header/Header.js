import React from 'react';
import { useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';
import UserMenu from '../UserMenu/UserMenu';
import Menu from './Menu';
import * as chatActions from '../../store/actionCreators/chatActionCreators';
import Notification from '../Notification/Notification';

export function Header(props) {
    const dispatch = useDispatch();
    return (
        <div className={styles.bannerContainer}>
            <div className={styles.leftSection}>
                <Menu />
            </div>
            <Link to="/chat" style={{ textDecoration: 'none', color: 'inherit' }} onClick={() => dispatch(chatActions.setCurrentChatThreadId(null))}>
                <p>
                    Informed
                </p>
            </Link>
            <div className={styles.rightSection}>
                <div className={styles.notificationDiv}>
                    <Notification />
                </div>
                <div className={styles.loginDiv}>
                    <UserMenu />
                </div>
            </div>

        </div>
    );
}

export default Header;
