import React from 'react';
import { Link } from 'react-router-dom';

export default function MedicineItem({ item }) {
    
    if (item.status === 'Expired') {
        return null;
    }

    return (
        <Link 
            to={`/medicine-details/${item.Mname}?pharmacy=${encodeURIComponent(item.pharmacy_license || '')}`} 
            state={{ distance: item.distance, isRoadDistance: item.isRoadDistance }}
            className="block"
        >
            <div className="relative border-t-indigo-400 border-light-blue flex flex-col justify-between w-full rounded-2xl min-h-[140px] border-2 p-4 hover:shadow-xl transition-all cursor-pointer bg-white">
                {item.Mdiscount > 0 && (
                    <div className="absolute top-2 right-2 bg-gradient-to-r from-red-500 to-pink-500 text-white text-[9px] font-extrabold px-2 py-0.5 rounded-full shadow-md animate-pulse z-10">
                        {item.Mdiscount}% OFF
                    </div>
                )}
                <div className="flex flex-col h-full justify-between gap-3"> 
                    <div className="flex flex-col gap-1 w-full">
                        {}
                        <p className="text-sm font-extrabold text-slate-800 leading-tight line-clamp-2">
                            {item.Mname}
                        </p>
                        
                        <p className="text-xs text-light-blue font-bold">
                            Stock: {item.Mquantity} units
                        </p>
                    </div>

                    {}
                    <div className="flex flex-col gap-1.5 mt-auto">
                        <div className="flex flex-wrap gap-1 items-center justify-between">
                            <span className="text-[9px] text-green-700 font-extrabold bg-green-50 px-2 py-0.5 rounded-full inline-block truncate max-w-full">
                                📍 {item.location || 'Cloud'}
                            </span>
                            {item.distance !== null && item.distance !== Infinity && (
                                <span className="text-[9px] text-blue-700 font-extrabold bg-blue-50 px-2 py-0.5 rounded-full inline-block">
                                    {item.distance < 1 ? '<1 km' : `${item.distance.toFixed(1)} km`} {item.isRoadDistance ? '🚗' : ''}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}