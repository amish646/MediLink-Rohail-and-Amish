import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios'; 
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';
import MedicineItem from '../../components/MedicineItem';
import { useSearchParams } from 'react-router-dom';

export default function InventoryUserPageView() {
    const [userview, setuserview] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [noResults, setNoResults] = useState(false);
    const [recommendedItem, setRecommendedItem] = useState(null);
    const [searchParams] = useSearchParams();
    const [userLoc, setUserLoc] = useState(null);
    const [aiAlternatives, setAiAlternatives] = useState(null);
    const [fetchingAi, setFetchingAi] = useState(false);
    const [roadDistancesCache, setRoadDistancesCache] = useState({});
    const fetchedOrFetching = useRef(new Set());
    const lastUserLoc = useRef(null);

    useEffect(() => {
        if (
            userLoc &&
            (!lastUserLoc.current ||
                userLoc.lat !== lastUserLoc.current.lat ||
                userLoc.lng !== lastUserLoc.current.lng)
        ) {
            fetchedOrFetching.current.clear();
            setRoadDistancesCache({});
            lastUserLoc.current = userLoc;
        }
    }, [userLoc]);

    const fetchAiAlternatives = async (medName) => {
        setFetchingAi(true);
        setAiAlternatives(null);
        try {
            const host = window.location.hostname || 'localhost';
            const response = await axios.get(`http://${host}:8000/api/ai-alternatives/${medName}`);
            if (response.data.status === "Success") {
                setAiAlternatives(response.data);
            }
        } catch (error) {
            console.error("AI alternatives fetch failed", error);
        } finally {
            setFetchingAi(false);
        }
    };

    const calculateDistance = (lat1, lon1, lat2, lon2) => {
        const R = 6371; 
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    };

    const fetchInventory = async () => {
        setLoading(true);
        try {
            
            const host = window.location.hostname || 'localhost';
            const response = await axios.get(`http://${host}:8000/local-inventory`);
            
            if (response.data.status === "Success") {
                const rawData = response.data.data;

                const allItems = rawData.map(item => {
                    const name = item.brand_name ? item.brand_name.trim() : "Unknown";
                    return {
                        _id: item.item_id || item.id || Math.random().toString(),
                        Mname: name,
                        Mquantity: item.quantity,
                        Mprice: item.purchase_price || 0,
                        imageUrl: "https://via.placeholder.com/150",
                        status: 'Active',
                        location: item.pharmacy_name || item.pharmacy_license || 'Cloud',
                        pharmacy_license: item.pharmacy_license || '',
                        lat: parseFloat(item.lat) || 0,
                        lng: parseFloat(item.lng) || 0,
                        distance: null,
                        Mdiscount: item.discount || 0
                    };
                });

                setuserview(allItems);
                
                const query = searchParams.get('search') || '';
                if (query) {
                    performFilter(allItems, query);
                } else {
                    setSearchResults(allItems);
                    setNoResults(false);
                }
            }
        } catch (error) {
            console.error("Fetch Error:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const getGeoLocation = () => {
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        setUserLoc({ lat: pos.coords.latitude, lng: pos.coords.longitude });
                    },
                    (err) => {
                        console.warn("High accuracy geolocation failed/timed out, trying low accuracy...", err);
                        
                        navigator.geolocation.getCurrentPosition(
                            (pos2) => {
                                setUserLoc({ lat: pos2.coords.latitude, lng: pos2.coords.longitude });
                            },
                            (err2) => {
                                console.error("Standard geolocation failed, using default fallback location", err2);
                                setUserLoc({ lat: 33.6844, lng: 73.0479 });
                            },
                            { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
                        );
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
                );
            } else {
                setUserLoc({ lat: 33.6844, lng: 73.0479 });
            }
        };
        getGeoLocation();
        fetchInventory();
    }, []);

    useEffect(() => {
        if (!userLoc || userview.length === 0) return;

        const uniqueLocs = [];
        userview.forEach(item => {
            if (item.lat && item.lng) {
                const key = `${item.lat},${item.lng}`;
                if (!uniqueLocs.includes(key)) {
                    uniqueLocs.push(key);
                }
            }
        });

        uniqueLocs.forEach(async (locStr) => {
            if (fetchedOrFetching.current.has(locStr)) return; 

            fetchedOrFetching.current.add(locStr);

            const [lat, lng] = locStr.split(',').map(Number);
            try {
                const url = `https://router.project-osrm.org/route/v1/driving/${userLoc.lng},${userLoc.lat};${lng},${lat}?overview=false`;
                const res = await axios.get(url);
                if (res.data && res.data.code === "Ok" && res.data.routes && res.data.routes.length > 0) {
                    const dist = res.data.routes[0].distance / 1000;
                    setRoadDistancesCache(prev => ({ ...prev, [locStr]: dist }));
                }
            } catch (e) {
                console.error("OSRM Route API failed for search result location", e);
            }
        });
    }, [userLoc, userview]);

    useEffect(() => {
        if (userview.length > 0) {
            let dataToSort = [...userview];
            
            if (userLoc) {
                dataToSort = dataToSort.map(item => {
                    if (item.lat && item.lng) {
                        const cacheKey = `${item.lat},${item.lng}`;
                        const cachedRoadDist = roadDistancesCache[cacheKey];
                        item.distance = (cachedRoadDist !== undefined && cachedRoadDist !== null)
                            ? cachedRoadDist
                            : calculateDistance(userLoc.lat, userLoc.lng, item.lat, item.lng);
                        item.isRoadDistance = (cachedRoadDist !== undefined && cachedRoadDist !== null);
                    } else {
                        item.distance = Infinity;
                        item.isRoadDistance = false;
                    }
                    return item;
                }).sort((a, b) => a.distance - b.distance);
            }
            
            const query = searchParams.get('search') || '';
            setSearchQuery(query);
            performFilter(dataToSort, query);
        }
    }, [searchParams, userview, userLoc, roadDistancesCache]);

    const performFilter = (data, query) => {
        const lowerQuery = query.toLowerCase().trim();
        
        if (!lowerQuery) {
            setSearchResults(data);
            setNoResults(false);
            setAiAlternatives(null);
            return;
        }

        const filtered = data.filter(item => 
            item.Mname.toLowerCase().includes(lowerQuery)
        );

        if (filtered.length === 0) {
            setNoResults(true);
            setSearchResults([]);
            fetchAiAlternatives(query);
        } else {
            setSearchResults(filtered);
            setNoResults(false);
            setAiAlternatives(null);
        }
    };

    return (
        <div className="bg-sky-50 min-h-screen font-sans">
            <NavigationBar />
            
            <div className="max-w-7xl mx-auto px-4 py-8">
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                        <p className="text-blue-600 font-bold">MediLink Cloud Syncing...</p>
                    </div>
                ) : noResults ? (
                    <div className="space-y-8 max-w-4xl mx-auto font-sans">
                        <div className="bg-white p-8 rounded-2xl shadow-sm text-center border border-gray-100">
                            <p className="text-red-500 font-extrabold text-xl">
                                "{searchQuery}" is not available in our local inventories.
                            </p>
                            <p className="text-slate-400 text-xs mt-1">Our system scanned all registered pharmacy branches in your area.</p>
                        </div>
                        
                        {}
                        <div className="bg-white p-8 rounded-3xl shadow-xl border-2 border-indigo-100 relative overflow-hidden">
                            {}
                            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50/60 rounded-full blur-3xl -mr-16 -mt-16"></div>
                            
                            <div className="relative z-10">
                                <h3 className="text-2xl font-black flex items-center gap-2 text-indigo-900 tracking-tight">
                                    <span className="text-3xl">🧠</span> MediLink AI Alternative Finder
                                </h3>
                                
                                {fetchingAi ? (
                                    <div className="flex flex-col items-center py-12">
                                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4"></div>
                                        <p className="text-sm font-bold text-indigo-600 animate-pulse">Consulting clinical databases and active ingredient logs...</p>
                                    </div>
                                ) : aiAlternatives ? (
                                    <div className="mt-8 space-y-8">
                                        <div className="bg-indigo-50/50 border border-indigo-100 p-5 rounded-2xl">
                                            <p className="text-[10px] text-indigo-500 font-extrabold uppercase tracking-widest">Active Ingredient / Generic Formula</p>
                                            <p className="text-xl font-black text-indigo-950 mt-1">{aiAlternatives.generic_formula}</p>
                                        </div>
                                        
                                        {}
                                        {aiAlternatives.in_stock_alternatives && aiAlternatives.in_stock_alternatives.length > 0 ? (
                                            <div>
                                                <p className="text-sm font-black text-slate-800 uppercase tracking-wide mb-4 flex items-center gap-2">
                                                    <span className="bg-emerald-500 w-2.5 h-2.5 rounded-full inline-block"></span>
                                                    In-Stock alternatives containing {aiAlternatives.generic_formula}:
                                                </p>
                                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                                                    {aiAlternatives.in_stock_alternatives.map((alt, idx) => {
                                                        const origPrice = alt.price;
                                                        const disc = alt.discount;
                                                        const finalPrice = disc > 0 ? (origPrice * (1 - disc / 100)) : origPrice;
                                                        
                                                        return (
                                                            <div key={idx} className="bg-slate-50 border border-slate-200/80 p-5 rounded-2xl flex flex-col justify-between hover:border-indigo-400 transition-all hover:shadow-md">
                                                                <div>
                                                                    <div className="flex justify-between items-start mb-2">
                                                                        <h4 className="font-extrabold text-slate-800 text-base">{alt.brand_name}</h4>
                                                                        {disc > 0 && (
                                                                            <span className="bg-red-100 text-red-700 font-extrabold text-[10px] px-2 py-0.5 rounded-full">{disc}% OFF</span>
                                                                        )}
                                                                    </div>
                                                                    <p className="text-xs text-slate-500 flex items-center gap-1">📍 {alt.pharmacy_name}</p>
                                                                    <p className="text-xs text-slate-600 mt-2 font-bold bg-slate-200/50 inline-block px-2 py-0.5 rounded">Stock: {alt.quantity} units available</p>
                                                                </div>
                                                                <div className="flex justify-between items-center mt-5 border-t border-slate-200 pt-3">
                                                                    <span className="font-black text-slate-900 text-base">Rs {finalPrice.toFixed(2)}</span>
                                                                    <a 
                                                                        href={`/medicine-details/${alt.brand_name}?pharmacy=${encodeURIComponent(alt.pharmacy_license || '')}`}
                                                                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-4 py-2 rounded-xl text-xs transition-colors shadow-sm text-center"
                                                                    >
                                                                        Select Medicine
                                                                    </a>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        ) : aiAlternatives.global_suggestions && aiAlternatives.global_suggestions.length > 0 ? (
                                            <div>
                                                <p className="text-sm font-black text-slate-800 uppercase tracking-wide mb-4 flex items-center gap-2">
                                                    <span className="bg-amber-500 w-2.5 h-2.5 rounded-full inline-block"></span>
                                                    No local stock, but you can request these substitute brands:
                                                </p>
                                                <div className="flex flex-wrap gap-2.5">
                                                    {aiAlternatives.global_suggestions.map((alt, idx) => (
                                                        <span key={idx} className="bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 text-xs font-bold px-4 py-2 rounded-full shadow-sm flex items-center gap-1.5 transition-colors">
                                                            💊 {alt.brand_name}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        ) : (
                                            <p className="text-sm text-slate-500 font-bold py-4">No active substitutes found in FDA or global catalog. Please consult your physician.</p>
                                        )}
                                    </div>
                                ) : (
                                    <p className="text-sm text-slate-500 font-bold py-4">No alternatives resolved. Please search a different brand name.</p>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div>
                        <div className="mb-10 px-2">
                            <h2 className="text-3xl font-black text-slate-800 tracking-tight">
                                {searchQuery ? `Results for "${searchQuery}"` : "MediLink Global Inventory"}
                            </h2>
                            <p className="text-slate-500 mt-1 font-medium">
                                Showing {searchResults.length} verified medicines in your area.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                            {searchResults.map((item) => (
                                <MedicineItem key={item._id} item={item} />
                            ))}
                        </div>
                    </div>
                )}
            </div>
            
            <Footer />
        </div>
    );
}