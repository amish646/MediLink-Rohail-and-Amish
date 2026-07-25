import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MdNotifications } from 'react-icons/md';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

const NotificationBell = () => {
    const [notificationCount, setNotificationCount] = useState(0);
    const navigate = useNavigate();
    const POLLING_INTERVAL = 5000;

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const response = await axios.get('http://localhost:3000/api/notification');
                const notifications = response.data.notifications || [];
                setNotificationCount(notifications.length);

                notifications.forEach((notification) => {
                    toast.success(notification.message);
                });
            } catch (error) {
                console.error('Error fetching notifications:', error);
                
            }
        };

        const interval = setInterval(fetchNotifications, POLLING_INTERVAL);

        return () => clearInterval(interval); 
    }, []); 

    const handleBellClick = () => {
        setNotificationCount(0); 
        navigate('/orders'); 
    };

    return (
        <button onClick={handleBellClick} className="relative">
            <MdNotifications size={24} className="text-gray-600" />
            {notificationCount > 0 && (
                <span className="absolute top-0 right-0 bg-red-600 text-white rounded-full px-2 py-1 text-xs">
                    {notificationCount}
                </span>
            )}
        </button>
    );
};

export default NotificationBell;
