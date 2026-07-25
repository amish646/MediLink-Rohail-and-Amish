import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import axios from 'axios';
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';
import toast from 'react-hot-toast';
import { FaShoppingCart } from 'react-icons/fa';

const medicineInfoMap = {
    paracetamol: {
        usage: "Used to treat mild to moderate pain (from headaches, menstrual periods, toothaches, backaches, osteoarthritis, or cold/flu aches) and to reduce fever.",
        sideEffects: "Rare when taken at recommended doses. May include nausea, allergic reactions, skin rash, or liver damage (in case of overdose)."
    },
    amoxicillin: {
        usage: "A penicillin-type antibiotic used to treat bacterial infections like pneumonia, bronchitis, tonsillitis, and ear/throat/urinary tract infections.",
        sideEffects: "Nausea, vomiting, diarrhea, stomach pain, or allergic reactions (rash/itching)."
    },
    "co-amoxiclav": {
        usage: "A combination antibiotic used to treat bacterial infections of the lungs, middle ear, sinus, skin, and urinary tract.",
        sideEffects: "Diarrhea, nausea, vomiting, skin rash, hives, or yeast infections."
    },
    "mefenamic acid": {
        usage: "An NSAID used for short-term treatment of mild to moderate pain, osteoarthritis, rheumatoid arthritis, and menstrual pain.",
        sideEffects: "Stomach upset, nausea, vomiting, diarrhea, heartburn, or headache."
    },
    "ibuprofen": {
        usage: "An NSAID used to reduce hormones that cause pain and inflammation in the body. Good for toothaches, menstrual cramps, or arthritis.",
        sideEffects: "Upset stomach, mild heartburn, bloating, gas, dizziness, or headache."
    },
    "metronidazole": {
        usage: "An antibiotic/antiprotozoal used to treat bacterial infections of the stomach, joints, skin, and respiratory tract.",
        sideEffects: "Nausea, diarrhea, metallic taste in the mouth, stomach cramps, or dizziness."
    },
    "aspirin": {
        usage: "Used to reduce fever, relieve mild to moderate pain, and as a blood thinner to prevent heart attacks/strokes.",
        sideEffects: "Upset stomach, heartburn, easy bleeding, or ringing in the ears."
    },
    "multivitamins": {
        usage: "Used to provide vitamins that are not taken in through the diet or to treat deficiencies caused by illness or pregnancy.",
        sideEffects: "Constipation, diarrhea, or temporary upset stomach."
    },
    "cetirizine": {
        usage: "An antihistamine used to relieve allergy symptoms such as watery eyes, runny nose, sneezing, hives, and body itching.",
        sideEffects: "Drowsiness, dry mouth, sore throat, or mild fatigue."
    },
    "omeprazole": {
        usage: "A proton pump inhibitor (PPI) that decreases stomach acid to treat GERD, stomach ulcers, and acid reflux.",
        sideEffects: "Headache, stomach pain, nausea, diarrhea, vomiting, or gas."
    },
    "pheniramine": {
        usage: "An antihistamine used to treat allergic conditions such as hay fever, urticaria, food allergies, and runny nose.",
        sideEffects: "Drowsiness, dry mouth, blurred vision, or constipation."
    },
    "salbutamol": {
        usage: "A bronchodilator used to prevent and treat wheezing/shortness of breath caused by asthma or COPD.",
        sideEffects: "Shakiness, tremors, fast heartbeat, headache, or throat irritation."
    },
    "bisoprolol": {
        usage: "A beta-blocker used to treat high blood pressure (hypertension) and protect the heart from failure.",
        sideEffects: "Cold extremities, fatigue, dizziness, headache, or slow heart rate."
    },
    "atorvastatin": {
        usage: "A statin used to prevent cardiovascular disease and lower bad cholesterol/triglycerides in the blood.",
        sideEffects: "Joint pain, stuffy nose, sore throat, muscle pain, or headache."
    },
    "metformin": {
        usage: "An oral diabetes medicine that helps control blood sugar levels for people with type 2 diabetes.",
        sideEffects: "Diarrhea, nausea, vomiting, gas, stomach discomfort, or metallic taste."
    },
    "ciprofloxacin": {
        usage: "A fluoroquinolone antibiotic used to treat bone/joint, abdominal, respiratory, and urinary tract infections.",
        sideEffects: "Nausea, diarrhea, rash, tendonitis, or sunlight sensitivity."
    },
    "clarithromycin": {
        usage: "A macrolide antibiotic used to treat various bacterial infections like strep throat, pneumonia, and skin infections.",
        sideEffects: "Nausea, vomiting, diarrhea, stomach pain, abnormal metallic taste, or headache."
    },
    "sodium alginate": {
        usage: "Used for treating symptoms of gastro-oesophageal reflux, such as acid regurgitation, heartburn, and indigestion.",
        sideEffects: "Flatulence, mild constipation, or allergic reactions (rare)."
    },
    "betahistine": {
        usage: "An anti-vertigo medication prescribed to treat balance disorders and vertigo symptoms associated with Ménière's disease.",
        sideEffects: "Mild stomach upset, nausea, headache, indigestion, or skin rash."
    }
};

const getMedicineDetails = (name, formula) => {
    const key = (formula || name || "").toLowerCase().trim();
    for (const [k, v] of Object.entries(medicineInfoMap)) {
        if (key.includes(k)) {
            return v;
        }
    }
    return {
        usage: "Used to treat symptoms under doctor guidance. Always consult a licensed health professional for appropriate usage guidelines.",
        sideEffects: "Mild gastrointestinal upset, dizziness, or allergic reactions. Consult a doctor if symptoms persist."
    };
};

export default function MedicineDetailsPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const location = useLocation();
    const passedState = location.state || {};
    const selectedPharmacy = searchParams.get('pharmacy');
    const [item, setItem] = useState(null);
    const [branches, setBranches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [userLoc, setUserLoc] = useState(null);

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
    }, []);

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

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                
                const response = await axios.get(`http://192.168.1.11:8000/availability/${id}`);
                
                if (response.data.status === "Empty") {
                    setError(response.data.message);
                } else {
                    setItem(response.data);
                    setBranches(response.data.available_branches);
                    setError(null);
                }
            } catch (err) {
                console.error("Connection Error:", err);
                setError("MediLink server se rabta nahi ho pa raha. Check karein ke backend chal raha hai.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    const handleAddToCart = (branch) => {
        if (!item) return;
        const cart = JSON.parse(localStorage.getItem('userCart') || '[]');
        const existingIdx = cart.findIndex(c => c.medicine_name === item.medicine && c.pharmacy_license === branch.pharmacy_license);
        
        if (existingIdx > -1) {
            if (cart[existingIdx].quantity >= branch.stock_available) {
                toast.error(`Cannot add more than available stock (${branch.stock_available} units)`);
                return;
            }
            cart[existingIdx].quantity += 1;
        } else {
            cart.push({
                medicine_name: item.medicine,
                pharmacy_name: branch.pharmacy_name,
                pharmacy_license: branch.pharmacy_license,
                price: parseFloat(branch.price) || 0,
                discount: parseFloat(branch.discount) || 0,
                quantity: 1,
                stock_available: branch.stock_available,
                lat: parseFloat(branch.lat) || 0,
                lng: parseFloat(branch.lng) || 0
            });
        }
        localStorage.setItem('userCart', JSON.stringify(cart));
        window.dispatchEvent(new Event('cartUpdated'));
        toast.success(`${item.medicine} added to cart!`);
    };

    const handleViewMap = (branch) => {
        if (!branch || !branch.lat || !branch.lng) {
            toast.error("Pharmacy location coordinates not available.");
            return;
        }
        const destLat = parseFloat(branch.lat) || 0;
        const destLng = parseFloat(branch.lng) || 0;
        let url = `https://www.google.com/maps/search/?api=1&query=${destLat},${destLng}`;
        if (userLoc) {
            url = `https://www.google.com/maps/dir/?api=1&origin=${userLoc.lat},${userLoc.lng}&destination=${destLat},${destLng}`;
        }
        window.open(url, '_blank');
    };

    const [roadDistance, setRoadDistance] = useState(
        passedState.distance !== undefined && passedState.distance !== null
            ? passedState.distance
            : null
    );
    const [isRoadDistance, setIsRoadDistance] = useState(
        passedState.isRoadDistance !== undefined ? passedState.isRoadDistance : false
    );

    const selectedBranch = branches.find(branch => {
        if (!selectedPharmacy) return false;
        const lic = (branch.pharmacy_license || branch.license || '').toLowerCase();
        return lic === selectedPharmacy.toLowerCase();
    }) || branches[0];

    useEffect(() => {
        
        if (roadDistance !== null) return;

        if (userLoc && selectedBranch && selectedBranch.lat && selectedBranch.lng) {
            const getRoadDistance = async () => {
                try {
                    const url = `https://router.project-osrm.org/route/v1/driving/${userLoc.lng},${userLoc.lat};${selectedBranch.lng},${selectedBranch.lat}?overview=false`;
                    const res = await axios.get(url);
                    if (res.data && res.data.code === "Ok" && res.data.routes && res.data.routes.length > 0) {
                        setRoadDistance(res.data.routes[0].distance / 1000);
                        setIsRoadDistance(true);
                    }
                } catch (e) {
                    console.error("OSRM Route API failed, falling back to Haversine", e);
                }
            };
            getRoadDistance();
        }
    }, [userLoc, selectedBranch, roadDistance]);

    if (loading) return (
        <div className="flex justify-center items-center h-screen bg-paleblue">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600"></div>
            <p className="ml-4 font-bold text-blue-600">Syncing with Cloud Database...</p>
        </div>
    );

    const details = item ? {
        usage: item.usage && item.usage !== "Not Specified" ? item.usage : getMedicineDetails(item.medicine, item.formula).usage,
        sideEffects: item.side_effects && item.side_effects !== "Not Specified" ? item.side_effects : (item.sideEffects || getMedicineDetails(item.medicine, item.formula).sideEffects)
    } : null;

    return (
        <div className="bg-paleblue min-h-screen">
            <NavigationBar />
            
            <div className='max-w-4xl mx-auto px-6 py-4'>

                {error ? (
                    <div className="bg-white p-10 text-center rounded-2xl shadow-md border-t-4 border-red-500">
                        <p className="text-xl text-red-600 font-bold">{error}</p>
                    </div>
                ) : (
                    <div className='bg-white shadow-xl rounded-2xl overflow-hidden'>
                        {}
                        <div className="bg-blue py-3.5 px-6 text-white flex flex-wrap justify-between items-center gap-2">
                            <h1 className='text-2xl font-black uppercase tracking-tight'>{item.medicine}</h1>
                            <p className='text-lighter-blue italic text-xs'>Generic Formula: {item.formula || 'Not Specified'}</p>
                        </div>

                        <div className='grid grid-cols-1 md:grid-cols-3 gap-0'>
                            {}
                            <div className='p-5 bg-gray-50 border-r-0 md:border-r border-gray-100 flex flex-col items-center justify-start order-2 md:order-1'>
                                <div className="w-full text-left space-y-4">
                                    <div className="bg-green-100 p-3 rounded-lg border border-green-200">
                                        <p className="text-xs text-green-700 font-bold uppercase">Status</p>
                                        <p className="text-sm text-green-800 font-medium italic">MediLink Verified Stock</p>
                                    </div>
                                    
                                    {details && (
                                        <div className="space-y-3 pt-3 border-t border-gray-200">
                                            <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wide">🔍 Clinical Guide</h4>
                                            <div>
                                                <p className="text-xs font-bold text-blue-600 uppercase">Usage:</p>
                                                <p className="text-xs text-gray-600 leading-relaxed mt-0.5">{details.usage}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs font-bold text-red-600 uppercase">Side Effects:</p>
                                                <p className="text-xs text-gray-600 leading-relaxed mt-0.5">{details.sideEffects}</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {}
                            <div className='md:col-span-2 p-5 order-1 md:order-2 border-b md:border-b-0 border-gray-100'>
                                <h3 className='font-bold text-slate-800 text-lg mb-4 flex items-center gap-2'>
                                    <span className="bg-blue-500 w-2.5 h-2.5 rounded-full animate-pulse"></span>
                                    Pharmacy & Ordering Details
                                </h3>

                                {selectedBranch ? (() => {
                                    const origPrice = parseFloat(selectedBranch.price) || 0;
                                    const discVal = parseFloat(selectedBranch.discount) || 0;
                                    const finalPrice = discVal > 0 ? (origPrice * (1 - discVal / 100)) : origPrice;

                                    return (
                                        <div className='bg-slate-50 border border-slate-200 p-4 sm:p-5 rounded-2xl shadow-sm space-y-4'>
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <h4 className='font-extrabold text-slate-800 text-base'>
                                                        📍 {selectedBranch.pharmacy_name}
                                                    </h4>
                                                     {((userLoc && selectedBranch.lat && selectedBranch.lng) || roadDistance !== null) && (() => {
                                                         const isRoad = roadDistance !== null || isRoadDistance;
                                                         const dist = isRoad 
                                                             ? roadDistance 
                                                             : (userLoc ? calculateDistance(userLoc.lat, userLoc.lng, parseFloat(selectedBranch.lat), parseFloat(selectedBranch.lng)) : null);
                                                         if (dist === null) return null;
                                                         return (
                                                             <p className='text-[10px] font-bold text-blue-600 mt-1'>
                                                                 🚗 {dist < 1 ? 'Less than 1 km away' : `${dist.toFixed(1)} km away`} {isRoad ? '(Shortest road path)' : '(Air distance)'}
                                                             </p>
                                                         );
                                                     })()}
                                                </div>
                                                <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${selectedBranch.stock_available > 50 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                                                    {selectedBranch.stock_available > 50 ? 'High Stock' : 'Limited'}
                                                </span>
                                            </div>

                                            {}
                                            <div className="bg-white p-4 rounded-xl border border-slate-200/60 shadow-sm space-y-3.5">
                                                {}
                                                <div className="grid grid-cols-2 gap-4 pb-3 border-b border-slate-100">
                                                    <div>
                                                        <p className="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest">Price</p>
                                                        <div className="mt-1 flex items-baseline gap-1.5 flex-wrap">
                                                            {discVal > 0 ? (
                                                                <>
                                                                    <span className="text-xl font-black text-slate-900">Rs {finalPrice.toFixed(2)}</span>
                                                                    <span className="text-xs text-slate-400 line-through">Rs {origPrice.toFixed(2)}</span>
                                                                </>
                                                            ) : (
                                                                <span className="text-xl font-black text-slate-900">Rs {origPrice.toFixed(2)}</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <p className="text-[9px] text-slate-400 font-extrabold uppercase tracking-widest">Available Stock</p>
                                                        <p className="text-xl font-black text-slate-800 mt-1">{selectedBranch.stock_available} units</p>
                                                    </div>
                                                </div>

                                                {}
                                                <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs">
                                                    <div>
                                                        <p className="text-[9px] text-slate-400 font-bold uppercase">Generic Formula</p>
                                                        <p className="font-semibold text-slate-700 truncate mt-0.5">{selectedBranch.formula || item.formula || 'N/A'}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[9px] text-slate-400 font-bold uppercase">Dosage</p>
                                                        <p className="font-semibold text-slate-700 mt-0.5">{selectedBranch.dosage || 'N/A'}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[9px] text-slate-400 font-bold uppercase">Company (Mfg)</p>
                                                        <p className="font-semibold text-slate-700 truncate mt-0.5">{selectedBranch.manufacturer || 'Unknown'}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[9px] text-slate-400 font-bold uppercase">Expiry Date</p>
                                                        <p className="font-semibold text-slate-700 mt-0.5">{selectedBranch.expiry_date || 'N/A'}</p>
                                                    </div>
                                                </div>
                                            </div>

                                            {}
                                            <div className="flex flex-col sm:flex-row gap-2 pt-1">
                                                <button 
                                                    onClick={() => handleAddToCart(selectedBranch)}
                                                    className='flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-extrabold py-2.5 px-4 rounded-xl transition-all shadow-md hover:shadow-lg text-xs uppercase tracking-wider flex items-center justify-center gap-2 cursor-pointer'
                                                >
                                                    <FaShoppingCart className="text-xs" />
                                                    Add to Cart
                                                </button>
                                                <button 
                                                    onClick={() => handleViewMap(selectedBranch)}
                                                    className='bg-blue-50 hover:bg-blue-100 text-blue-600 font-black py-2.5 px-4 rounded-xl transition-all text-xs uppercase tracking-wider border border-blue-100 cursor-pointer'
                                                >
                                                    View Map
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })() : (
                                    <div className="bg-amber-50 border border-amber-200 p-6 rounded-2xl text-center">
                                        <p className="text-sm font-bold text-amber-800">This medicine is currently out of stock.</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
            <Footer />
        </div>
    );
}