import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/types';
import styles from './HOCLayout.module.css';
import Header from '../../Components/Header/Header';
import { ToastMessageProvider } from './ToastMessageContext';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { AppDispatch } from '../../store/store';

interface HOCLayoutProps {
  children: React.ReactNode;
}

export const HOCLayout: React.FC<HOCLayoutProps> = React.memo(function HOCLayout({ children }) {
    const dispatch = useDispatch<AppDispatch>();
    const user = useSelector((state: RootState) => state.user.user);

    useEffect(() => {
        if(!user) {
            dispatch(userActions.verifyLogin());
        }
    }, []);

    useEffect(() => {
        if (user) {
            // Initial fetch
            dispatch(userActions.fetchNotifications());

            const intervalId = setInterval(() => {
                dispatch(userActions.fetchNotifications());
            }, 10000);

            return () => clearInterval(intervalId);
        }
    }, [user, dispatch]);

    return (
        <div className="p-6 max-w-sm mx-auto bg-white rounded-xl shadow-md flex items-center space-x-4">
            <ToastMessageProvider>
                <div className={styles.layout}>
                    <Header />
                    <div className={styles.contentContainer}>
                        {children}
                    </div>
                </div>
            </ToastMessageProvider>
        </div>
    );
});

export default HOCLayout;
