import React, { useState } from 'react';

function LocationButton() {
  const [location, setLocation] = useState({ 
    latitude: null, 
    longitude: null, 
    error: null 
  });
  const [loading, setLoading] = useState(false);

  const getLocation = () => {
    setLoading(true); 
    setLocation({ latitude: null, longitude: null, error: null }); 

    if (navigator.geolocation) {
      
      navigator.geolocation.getCurrentPosition(
        
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            error: null
          });
          setLoading(false); 
        },
        
        (error) => {
          let errorMessage = "Location can't be accessed !";
          if (error.code === error.PERMISSION_DENIED) {
            errorMessage = "Access Denied!";
          } else if (error.code === error.TIMEOUT) {
            errorMessage = "Timeout!";
          }
          setLocation({
            latitude: null,
            longitude: null,
            error: errorMessage
          });
          setLoading(false); 
        },
        
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } 
  };

  return (
    <div>
      
      {}
      <button
        onClick={getLocation}
        disabled={loading}
        className={`
          ${loading 
          }
        `}
      >
        {loading ? 'Finding location' : '📍 Enable Location'}
      </button>

      {}
      <div className="text-sm">
        {location.error && (
          <p className="text-red-600 font-medium">❌ Error: {location.error}</p>
        )}

      </div>
    </div>
  );
}

export default LocationButton;