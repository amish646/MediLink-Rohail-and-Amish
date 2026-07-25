import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { toast } from 'react-hot-toast';
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';

export default function PrescriptionForm() {
    const navigate = useNavigate();
    const { currentUser } = useSelector((state) => state.user);
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [scannedMedicines, setScannedMedicines] = useState([]);
    const [hasScanned, setHasScanned] = useState(false);
    const [scannedFileUrl, setScannedFileUrl] = useState('');
    const [ocrStatus, setOcrStatus] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleAddToCart = (medicineName, branch) => {
        const cart = JSON.parse(localStorage.getItem('userCart') || '[]');
        const existingIdx = cart.findIndex(c => c.medicine_name === medicineName && c.pharmacy_license === branch.pharmacy_license);
        
        if (existingIdx > -1) {
            if (cart[existingIdx].quantity >= branch.stock_available) {
                toast.error(`Cannot add more than available stock (${branch.stock_available} units)`);
                return;
            }
            cart[existingIdx].quantity += 1;
        } else {
            cart.push({
                medicine_name: medicineName,
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
        toast.success(`${medicineName} added to cart!`);
    };

    const handleDone = async () => {
        if (!file) {
            toast.error("Please upload a prescription first.");
            return;
        }

        if (!currentUser) {
            toast.error("You must be signed in to upload a prescription.");
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('email', currentUser.email || '');
        formData.append('username', currentUser.username || '');
        formData.append('phone', currentUser.phonenumber || '');
        formData.append('address', currentUser.address || '');

        try {
            const res = await axios.post('http://192.168.1.11:8000/prescription/upload-ocr', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (res.data.status === "Success") {
                toast.success('Prescription uploaded and scanned successfully!');
                setScannedFileUrl(res.data.file_url);
                setScannedMedicines(res.data.medicines || []);
                setOcrStatus(res.data.ocr_status || '');
                setHasScanned(true);
            } else {
                toast.error('Upload failed: ' + res.data.message);
            }
        } catch (error) {
            console.error("Upload error:", error);
            toast.error('Error uploading or scanning prescription. Is backend running?');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-paleblue min-h-screen flex flex-col justify-between font-sans">
            <NavigationBar />
            
            {!hasScanned ? (
                <div className="flex-grow flex justify-center items-center p-6 bg-gray-50">
                    <div className="bg-white w-full max-w-3xl rounded-lg border border-gray-300 shadow-sm">
                        <div className="p-10">
                            <h2 className="text-2xl font-bold text-[#1e56a0] mb-2 text-left">Upload Prescription</h2>
                            <p className="text-gray-500 text-[16px] mb-8 text-left">
                                To place an order please upload picture of your prescription
                            </p>

                            <div className="relative w-[140px] h-[110px] flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-md bg-[#fcfcfc] hover:bg-gray-50 transition-all cursor-pointer">
                                <input 
                                    type="file" 
                                    className="absolute inset-0 opacity-0 cursor-pointer" 
                                    onChange={handleFileChange}
                                    accept="image/*"
                                />
                                <svg className="w-10 h-10 text-[#1e56a0] mb-1" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19.35 10.04A7.49 7.49 0 0012 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 000 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
                                </svg>
                                <span className="text-sm text-gray-600 font-medium">Browse files</span>
                            </div>

                            {file && (
                                <div className="mt-4 flex items-center gap-2">
                                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                                        Selected: {file.name}
                                    </span>
                                </div>
                            )}
                        </div>

                        <div className="p-4 bg-white flex justify-end border-t border-gray-100">
                            <button 
                                onClick={handleDone}
                                disabled={loading}
                                className={`px-10 py-2 rounded text-white font-semibold transition-all ${
                                    file ? 'bg-[#8ca1cc] hover:bg-[#7a92c2]' : 'bg-[#b8c5e0] cursor-not-allowed'
                                }`}
                            >
                                {loading ? 'Processing Scan...' : 'Scan & Upload'}
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex-grow flex justify-center items-stretch p-6 bg-gray-50">
                    <div className="bg-white w-full max-w-6xl rounded-2xl border border-gray-200 shadow-xl overflow-hidden flex flex-col md:flex-row">
                        {/* Left Side: Prescription Preview */}
                        <div className="md:w-1/2 bg-slate-900 flex flex-col justify-between p-6 text-white min-h-[400px] md:min-h-0 border-r border-gray-200">
                            <div>
                                <h3 className="text-lg font-black tracking-tight mb-2 text-sky-400">📄 Uploaded Prescription</h3>
                                <p className="text-slate-400 text-xs">Scanned via MediLink Multimodal AI OCR</p>
                            </div>
                            
                            <div className="flex-grow flex items-center justify-center my-6">
                                {scannedFileUrl && (
                                    <img 
                                        src={`http://192.168.1.11:8000${scannedFileUrl}`}
                                        alt="Prescription Scan" 
                                        className="max-h-[450px] w-auto object-contain rounded-lg border-2 border-slate-700 shadow-2xl"
                                    />
                                )}
                            </div>

                            <div className="text-center">
                                <button
                                    onClick={() => {
                                        setHasScanned(false);
                                        setFile(null);
                                        setScannedMedicines([]);
                                        setOcrStatus('');
                                    }}
                                    className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold px-6 py-2.5 rounded-xl text-xs transition-colors border border-slate-700 shadow-sm"
                                >
                                    🔄 Upload & Scan Another
                                </button>
                            </div>
                        </div>

                        {/* Right Side: Scan Results */}
                        <div className="md:w-1/2 p-6 md:p-8 flex flex-col justify-between bg-white max-h-[700px] overflow-y-auto">
                            <div>
                                <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-100">
                                    <div>
                                        <h2 className="text-2xl font-black text-[#1e56a0] tracking-tight">💊 Scan Results</h2>
                                        <p className="text-slate-400 text-xs mt-1">We found {scannedMedicines.length} medicines in your prescription</p>
                                    </div>
                                    <button 
                                        onClick={() => navigate('/user-payment')}
                                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-extrabold px-5 py-2.5 rounded-xl text-xs shadow-md transition-all uppercase tracking-wider flex items-center gap-1.5 cursor-pointer"
                                    >
                                        Checkout ➜
                                    </button>
                                </div>

                                <div className="space-y-6">
                                    {ocrStatus === 'KeyMissing' ? (
                                        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 text-amber-800 space-y-2.5">
                                            <p className="font-extrabold text-sm flex items-center gap-1.5">
                                                ⚠️ Gemini API Key Missing
                                            </p>
                                            <p className="text-xs leading-relaxed text-slate-600">
                                                The prescription was uploaded successfully, but the automatic OCR scanning could not be performed because the Gemini API key is missing in the backend.
                                            </p>
                                            <p className="text-xs leading-relaxed text-slate-600 font-medium">
                                                Please configure the <strong className="text-amber-800">GEMINI_API_KEY</strong> environment variable, or define <strong className="text-amber-800">"gemini_key"</strong> in your backend's <code>pharmacy_config.json</code> file, and restart the backend server.
                                            </p>
                                        </div>
                                    ) : scannedMedicines.length === 0 ? (
                                        <div className="text-center py-10">
                                            <p className="text-slate-400 font-medium">No medicines could be identified automatically.</p>
                                            <p className="text-slate-400 text-xs mt-1">Please try uploading a clearer image or search medicines manually.</p>
                                        </div>
                                    ) : (
                                        scannedMedicines.map((med, idx) => (
                                            <div key={idx} className="bg-slate-50 border border-slate-200/80 rounded-2xl p-5 shadow-sm space-y-4 hover:shadow-md transition-all">
                                                <div className="flex justify-between items-start flex-wrap gap-2">
                                                    <div>
                                                        <h3 className="font-extrabold text-slate-800 text-lg uppercase tracking-tight">{med.name}</h3>
                                                        <p className="text-xs text-slate-500 italic mt-0.5">Generic: {med.generic_formula}</p>
                                                    </div>
                                                    <span className={`text-[10px] px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
                                                        med.status === 'Available' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                                                    }`}>
                                                        {med.status}
                                                    </span>
                                                </div>

                                                {med.status === 'Available' ? (
                                                    <div className="space-y-3">
                                                        <p className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">Available Pharmacy Branches:</p>
                                                        <div className="grid grid-cols-1 gap-3">
                                                            {med.available_branches.map((branch, bIdx) => {
                                                                const origPrice = parseFloat(branch.price) || 0;
                                                                const discVal = parseFloat(branch.discount) || 0;
                                                                const finalPrice = discVal > 0 ? (origPrice * (1 - discVal / 100)) : origPrice;
                                                                
                                                                return (
                                                                    <div key={bIdx} className="bg-white border border-slate-100 p-3.5 rounded-xl shadow-xs flex justify-between items-center flex-wrap gap-2 hover:border-[#1e56a0] transition-all">
                                                                        <div>
                                                                            <p className="font-bold text-slate-800 text-sm">📍 {branch.pharmacy_name}</p>
                                                                            <p className="text-[10px] text-slate-500 mt-1">Stock: {branch.stock_available} units • Expiry: {branch.expiry_date}</p>
                                                                            <div className="mt-1.5 flex items-baseline gap-1.5">
                                                                                {discVal > 0 ? (
                                                                                    <>
                                                                                        <span className="text-sm font-black text-slate-900">Rs {finalPrice.toFixed(2)}</span>
                                                                                        <span className="text-xs text-slate-400 line-through">Rs {origPrice.toFixed(2)}</span>
                                                                                        <span className="bg-red-100 text-red-700 font-extrabold text-[8px] px-1.5 py-0.5 rounded-full">{discVal}% OFF</span>
                                                                                    </>
                                                                                ) : (
                                                                                    <span className="text-sm font-black text-slate-900">Rs {origPrice.toFixed(2)}</span>
                                                                                )}
                                                                            </div>
                                                                        </div>
                                                                        <button
                                                                            onClick={() => handleAddToCart(med.name, branch)}
                                                                            className="bg-blue hover:bg-[#1e56a0] text-white font-extrabold px-4 py-2 rounded-xl text-xs transition-colors flex items-center gap-1 cursor-pointer"
                                                                        >
                                                                            🛒 Add to Cart
                                                                        </button>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="space-y-3 pt-2 border-t border-slate-200/60">
                                                        {med.in_stock_alternatives && med.in_stock_alternatives.length > 0 ? (
                                                            <>
                                                                <p className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider flex items-center gap-1.5">
                                                                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                                                                    Alternative Brands In Stock:
                                                                </p>
                                                                <div className="grid grid-cols-1 gap-3">
                                                                    {med.in_stock_alternatives.map((alt, bIdx) => {
                                                                        const origPrice = parseFloat(alt.price) || 0;
                                                                        const discVal = parseFloat(alt.discount) || 0;
                                                                        const finalPrice = discVal > 0 ? (origPrice * (1 - discVal / 100)) : origPrice;

                                                                        return (
                                                                            <div key={bIdx} className="bg-white border border-amber-100 p-3.5 rounded-xl shadow-xs flex justify-between items-center flex-wrap gap-2 hover:border-amber-400 transition-all">
                                                                                <div>
                                                                                    <p className="font-extrabold text-amber-950 text-sm">💊 {alt.brand_name}</p>
                                                                                    <p className="text-[10px] text-slate-500 mt-1">📍 {alt.pharmacy_name} • Stock: {alt.quantity} units</p>
                                                                                    <div className="mt-1.5 flex items-baseline gap-1.5">
                                                                                        {discVal > 0 ? (
                                                                                            <>
                                                                                                <span className="text-sm font-black text-slate-900">Rs {finalPrice.toFixed(2)}</span>
                                                                                                <span className="text-xs text-slate-400 line-through">Rs {origPrice.toFixed(2)}</span>
                                                                                            </>
                                                                                        ) : (
                                                                                            <span className="text-sm font-black text-slate-900">Rs {origPrice.toFixed(2)}</span>
                                                                                        )}
                                                                                    </div>
                                                                                </div>
                                                                                <button
                                                                                    onClick={() => handleAddToCart(alt.brand_name, {
                                                                                        pharmacy_name: alt.pharmacy_name,
                                                                                        pharmacy_license: alt.pharmacy_license,
                                                                                        price: alt.price,
                                                                                        discount: alt.discount,
                                                                                        stock_available: alt.quantity,
                                                                                        lat: 0.0,
                                                                                        lng: 0.0
                                                                                    })}
                                                                                    className="bg-amber-600 hover:bg-amber-700 text-white font-extrabold px-4 py-2 rounded-xl text-xs transition-colors flex items-center gap-1 cursor-pointer"
                                                                                >
                                                                                    🛒 Add Alternative
                                                                                </button>
                                                                            </div>
                                                                        );
                                                                    })}
                                                                </div>
                                                            </>
                                                        ) : med.global_suggestions && med.global_suggestions.length > 0 ? (
                                                            <>
                                                                <p className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">Suggested Substitute Brands (Unavailable Locally):</p>
                                                                <div className="flex flex-wrap gap-2 pt-1">
                                                                    {med.global_suggestions.map((sug, bIdx) => (
                                                                        <span key={bIdx} className="bg-slate-100 border border-slate-200 text-slate-600 font-bold px-3 py-1 rounded-full text-xs">
                                                                            💊 {sug.brand_name}
                                                                        </span>
                                                                    ))}
                                                                </div>
                                                            </>
                                                        ) : (
                                                            <p className="text-xs text-slate-400 italic">No in-stock generic alternatives found. Please contact support or consult your doctor.</p>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            <Footer />
        </div>
    );
}