import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Select from 'react-select';
import styles from './Admin.module.css';
import * as adminActions from '../../store/actionCreators/adminActionCreators'

export function Admin() {
    const dispatch = useDispatch();
    const notifications = useSelector(state => state.admin.notifications);
    const [newNotification, setNewNotification] = useState({
        message: '',
        zipCodes: [],
        currentZip: '',
        expiresAt: new Date(Date.now() + 24*60*60*1000)
    });
    const [filters, setFilters] = useState({
        isActive: true,
        zipCode: ''
    });
    const [isInputFocused, setIsFocused] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [debouncedZipCode, setDebouncedZipCode] = useState('');

    const expiryOptions = [
        { value: 1, label: '1 hour', hours: 1 },
        { value: 3, label: '3 hours', hours: 3 },
        { value: 6, label: '6 hours', hours: 6 },
        { value: 12, label: '12 hours', hours: 12 },
        { value: 24, label: '1 day', hours: 24 },
        { value: 48, label: '2 days', hours: 48 },
    ];

    useEffect(() => {
        const timer = setTimeout(() => {
            setFilters(prev => ({
                ...prev,
                zipCode: debouncedZipCode
            }));
        }, 500);

        return () => clearTimeout(timer);
    }, [debouncedZipCode]);

    useEffect(() => {
        dispatch(adminActions.fetchWeatherAlerts({
            isActive: filters.isActive,
            zipCode: filters.zipCode
        }));
    }, [dispatch, filters]);

    const handleAddZipCode = (e) => {
        if (e.key === 'Enter' && e.target.value.trim()) {
            e.preventDefault();
            setNewNotification(prev => ({
                ...prev,
                zipCodes: [...prev.zipCodes, prev.currentZip.trim()],
                currentZip: ''
            }));
        }
    };

    const removeZipCode = (indexToRemove) => {
        setNewNotification(prev => ({
            ...prev,
            zipCodes: prev.zipCodes.filter((_, index) => index !== indexToRemove)
        }));
    };

    const handleAddNotification = () => {
        if (!newNotification.message.trim() || newNotification.zipCodes.length === 0) return;

        dispatch(adminActions.addWeatherAlert({
            ...newNotification,
            zipCode: newNotification.zipCodes[0] // For now, just use the first ZIP code
        }));

        setNewNotification({
            message: '',
            zipCodes: [],
            currentZip: '',
            expiresAt: new Date(Date.now() + 24*60*60*1000)
        });
    };

    const handleExpiryChange = (selectedOption) => {
        const now = new Date();
        const expiryDate = new Date(now.getTime() + selectedOption.hours * 60 * 60 * 1000);

        setNewNotification({
            ...newNotification,
            expiresAt: expiryDate
        });
    };

    const handleCancelNotification = (notificationId) => {
        dispatch(adminActions.cancelWeatherAlert(notificationId));
    };

    const NotificationItem = ({ notification, onDelete }) => {
        const [isExpanded, setIsExpanded] = useState(false);

        const handleClick = (e) => {
            if (e.target.closest('button')) return;
            setIsExpanded(!isExpanded);
        };

        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleString();
        };

        return (
            <div
                className={`${styles.notificationItem} ${isExpanded ? styles.expandedNotification : ''}`}
                onClick={handleClick}
            >
                <div className={styles.notificationDetails}>
                    <span className={styles.notificationText}>
                        {notification.message}
                    </span>
                    <span className={styles.notificationMeta}>
                        ZIP: {notification.zip_code} | Expires: {formatDate(notification.expires_at)}
                    </span>

                    {isExpanded && (
                        <div className={styles.expandedContent}>
                            <span className={styles.expandedMessage}>
                                {notification.message}
                            </span>
                            <div className={styles.metadataGrid}>
                                <span className={styles.metadataLabel}>ID:</span>
                                <span className={styles.metadataValue}>{notification.id}</span>

                                <span className={styles.metadataLabel}>Created At:</span>
                                <span className={styles.metadataValue}>{formatDate(notification.created_at)}</span>

                                <span className={styles.metadataLabel}>Expires At:</span>
                                <span className={styles.metadataValue}>{formatDate(notification.expires_at)}</span>

                                {notification.cancelled_at && (
                                    <>
                                        <span className={styles.metadataLabel}>Cancelled At:</span>
                                        <span className={styles.metadataValue}>{formatDate(notification.cancelled_at)}</span>
                                    </>
                                )}
                            </div>
                        </div>
                    )}
                </div>
                {notification.is_active && (
                    <button
                        onClick={() => onDelete(notification.id)}
                        className={styles.deleteButton}
                    >
                        Delete
                    </button>
                )}
            </div>
        );
    };

    return (
        <div className={styles.adminContainer}>
            <div className={styles.filterContainer}>
                <div className={styles.filters}>
                    <select
                        value={filters.isActive === null ? 'all' : filters.isActive.toString()}
                        onChange={(e) => setFilters({
                            ...filters,
                            isActive: e.target.value === 'all' ? null : e.target.value === 'true'
                        })}
                        className={styles.filterSelect}
                    >
                        <option value="all">All Notifications</option>
                        <option value="true">Active</option>
                        <option value="false">Inactive</option>
                    </select>
                    <input
                        type="text"
                        placeholder="Filter by ZIP code"
                        value={debouncedZipCode}
                        onChange={(e) => setDebouncedZipCode(e.target.value)}
                        className={styles.zipCodeFilter}
                    />
                </div>
                <button
                    onClick={() => setShowAddForm(true)}
                    className={styles.addNewButton}
                >
                    Create
                </button>
            </div>

            {showAddForm && (
                <div className={styles.addNotificationContainer}>
                    <div className={`${styles.inputGroup} ${isInputFocused ? styles.focus : ''}`}>
                        <input
                            type="text"
                            placeholder="Message"
                            className={styles.notificationInput}
                            value={newNotification.message}
                            onChange={(e) => setNewNotification({
                                ...newNotification,
                                message: e.target.value
                            })}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                        />
                        <div className={styles.zipCodeTags}>
                            {newNotification.zipCodes.map((zip, index) => (
                                <span key={index} className={styles.zipTag}>
                                    {zip}
                                    <button
                                        className={styles.removeTag}
                                        onClick={() => removeZipCode(index)}
                                    >
                                        ×
                                    </button>
                                </span>
                            ))}
                            <input
                                type="text"
                                placeholder="Enter ZIP code and press Enter"
                                value={newNotification.currentZip}
                                onChange={(e) => setNewNotification({
                                    ...newNotification,
                                    currentZip: e.target.value
                                })}
                                onKeyPress={handleAddZipCode}
                                style={{ border: 'none', outline: 'none', flex: 1, minWidth: '150px' }}
                            />
                        </div>
                        <Select
                            options={expiryOptions}
                            onChange={handleExpiryChange}
                            defaultValue={expiryOptions[4]}
                            className={styles.expirySelect}
                            placeholder="Select expiry time"
                        />
                    </div>
                    <div className={styles.addFormActions}>
                        <button
                            onClick={handleAddNotification}
                            className={styles.addButton}
                            disabled={!newNotification.message.trim() || newNotification.zipCodes.length === 0}
                        >
                            Add Notification
                        </button>
                        <button
                            onClick={() => setShowAddForm(false)}
                            className={styles.formCancelButton}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            <div className={styles.notificationsList}>
                {notifications.map(notification => (
                    <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onDelete={handleCancelNotification}
                    />
                ))}
            </div>
        </div>
    );
}

export default Admin;
