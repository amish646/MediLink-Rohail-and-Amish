import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';
import OrderInvoice from '../../components/OrderInvoice';

export default function UserPaymentDetails() {
    const navigate = useNavigate();
    const { currentUser } = useSelector((state) => state.user);
    const [cartItems, setCartItems] = useState([]);
    const [paymentMethod, setPaymentMethod] = useState('Card'); 
    
    const [value, setValue] = useState({
        firstName: '',
        lastName: '',
        email: '',
        phoneNumber: '',
        address: '',
        city: '',
        postalCode: '',
        state: '',
        cardNumber: '',
        cardName: '',
        cardExpiry: '',
        cardCvv: '',
        bankRefNo: ''
    });

    useEffect(() => {
        const stored = JSON.parse(localStorage.getItem('userCart') || '[]');
        setCartItems(stored);
        if (stored.length === 0) {
            toast.error("Your cart is empty. Please add medicines first!");
            navigate('/inventory-user');
        }
    }, [navigate]);

    useEffect(() => {
        if (currentUser) {
            setValue(prev => ({
                ...prev,
                firstName: currentUser.username || '',
                email: currentUser.email || ''
            }));
        }
    }, [currentUser]);

    const handleChange = (e) => {
        const { name, value: val } = e.target;
        setValue(prevState => ({
            ...prevState,
            [name]: val
        }));
    };    

    const calculateSubtotal = () => {
        return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    };

    const calculateTotalDiscount = () => {
        return cartItems.reduce((total, item) => {
            const discVal = item.price * (item.discount / 100);
            return total + (discVal * item.quantity);
        }, 0);
    };

    const deliveryCharge = 150;
    const subtotal = calculateSubtotal();
    const totalDiscount = calculateTotalDiscount();
    const finalTotal = subtotal - totalDiscount + deliveryCharge;

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!value.firstName || !value.lastName || !value.email || !value.phoneNumber || !value.address || !value.city) {
            toast.error("Please fill in all required delivery details.");
            return;
        }

        if (paymentMethod === 'Card') {
            if (!value.cardNumber || !value.cardExpiry || !value.cardCvv) {
                toast.error("Please complete your debit card details.");
                return;
            }
            if (value.cardNumber.replace(/\s/g, '').length < 16) {
                toast.error("Card number must be 16 digits.");
                return;
            }
            if (value.cardCvv.length < 3) {
                toast.error("CVV must be 3 digits.");
                return;
            }
        }

        if (paymentMethod === 'Bank') {
            if (!value.bankRefNo) {
                toast.error("Please enter your 6-digit Bank Transfer Transaction Reference Number.");
                return;
            }
        }

        const orderId = 'ML-' + Math.floor(100000 + Math.random() * 900000);
        
        const payload = {
            orderId,
            date: new Date().toLocaleString(),
            amount: finalTotal,
            paymentStatus: paymentMethod === 'COD' ? 'Pending (COD)' : (paymentMethod === 'Bank' ? 'Paid (Bank Transfer)' : 'Paid (Debit Card)'),
            transactionId: paymentMethod === 'COD' ? 'N/A' : (paymentMethod === 'Bank' ? `BANK-REF-${value.bankRefNo}` : 'TXN-' + Math.floor(10000000 + Math.random() * 90000000)),
            orderStatus: 'Processing',
            items: cartItems.map(c => ({
                medicine_name: c.medicine_name,
                pharmacy_name: c.pharmacy_name,
                pharmacy_license: c.pharmacy_license,
                price: parseFloat(c.price) || 0.0,
                discount: parseFloat(c.discount) || 0.0,
                quantity: parseInt(c.quantity) || 1
            })),
            deliveryAddress: `${value.address}, ${value.city}, ${value.state}`,
            userEmail: value.email
        };

        const postOrder = async () => {
            try {
                
                await axios.post('http://192.168.1.11:8000/api/orders', payload);
                
                const localOrder = {
                    ...payload,
                    amount: payload.amount.toFixed(2)
                };
                const existingOrders = JSON.parse(localStorage.getItem('orderHistory') || '[]');
                localStorage.setItem('orderHistory', JSON.stringify([localOrder, ...existingOrders]));

                localStorage.removeItem('userCart');
                window.dispatchEvent(new Event('cartUpdated'));

                toast.success(`Order Placed Successfully! ID: ${orderId}. Redirecting to home page in 5 seconds...`, {
                    duration: 5000
                });
                setTimeout(() => {
                    navigate('/');
                }, 5000);
            } catch (err) {
                console.error("Order submission failed:", err);
                toast.error("Failed to place order. Check if server is running.");
            }
        };

        postOrder();
    };

    if (cartItems.length === 0) {
        return (
            <div className="bg-sky-50 min-h-screen">
                <NavigationBar />
                <div className="flex flex-col items-center justify-center py-20 font-sans">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p className="text-blue-600 font-bold">Redirecting to inventory...</p>
                </div>
                <Footer />
            </div>
        );
    }

    return (
        <div className='bg-sky-50 min-h-screen font-sans'>
            <NavigationBar />
            
            <div className='max-w-6xl mx-auto p-6'>
                <h1 className='text-3xl font-black text-slate-800 tracking-tight mb-2'>
                    Secure Checkout & Payment
                </h1>
                <div className='mb-8 text-xs sm:text-sm text-slate-500 space-y-1'>
                    <p className='flex items-center gap-1.5'>
                        <span>💡</span> <em>Note: Online order will be processed from the nearest pharmacy from user's location.</em>
                    </p>
                    <p className='flex items-center gap-1.5 font-semibold text-slate-600 pl-5'>
                        <span>🚚</span> Delivery charges Applied
                    </p>
                </div>

                <div className='grid grid-cols-1 lg:grid-cols-3 gap-8'>
                    {}
                    <div className='lg:col-span-2 space-y-6'>
                        <form onSubmit={handleSubmit} className='space-y-6'>
                            
                            {}
                            <div className='bg-white p-6 rounded-2xl shadow-sm border border-slate-100'>
                                <h3 className='text-lg font-bold text-slate-800 border-b pb-3 mb-5 flex items-center gap-2'>
                                    <span>📍</span> Delivery Information
                                </h3>
                                
                                <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>First Name *</label>
                                        <input 
                                            type="text" 
                                            name="firstName" 
                                            value={value.firstName} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Last Name *</label>
                                        <input 
                                            type="text" 
                                            name="lastName" 
                                            value={value.lastName} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Email Address *</label>
                                        <input 
                                            type="email" 
                                            name="email" 
                                            value={value.email} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Contact Number *</label>
                                        <input 
                                            type="tel" 
                                            name="phoneNumber" 
                                            value={value.phoneNumber} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                            required
                                        />
                                    </div>
                                    <div className="sm:col-span-2">
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Complete Street Address *</label>
                                        <textarea 
                                            name="address" 
                                            rows="2"
                                            value={value.address} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                            required
                                        ></textarea>
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>City *</label>
                                        <input 
                                            type="text" 
                                            name="city" 
                                            value={value.city} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Postal / ZIP Code</label>
                                        <input 
                                            type="text" 
                                            name="postalCode" 
                                            value={value.postalCode} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                        />
                                    </div>
                                    <div>
                                        <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>State / Province</label>
                                        <input 
                                            type="text" 
                                            name="state" 
                                            value={value.state} 
                                            onChange={handleChange} 
                                            className='w-full border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all' 
                                        />
                                    </div>
                                </div>
                            </div>

                            {}
                            <div className='bg-white p-6 rounded-2xl shadow-sm border border-slate-100'>
                                <h3 className='text-lg font-bold text-slate-800 border-b pb-3 mb-5 flex items-center gap-2'>
                                    <span>💳</span> Payment Method
                                </h3>

                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                                    <label className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${paymentMethod === 'Card' ? 'border-blue-500 bg-blue-50/50' : 'border-slate-100 hover:border-slate-200'}`}>
                                        <input 
                                            type="radio" 
                                            name="paymentMethod" 
                                            checked={paymentMethod === 'Card'} 
                                            onChange={() => setPaymentMethod('Card')}
                                            className="accent-blue-600 w-4 h-4"
                                        />
                                        <div>
                                            <p className="font-bold text-slate-800 text-sm">Debit Card</p>
                                            <p className="text-[10px] text-slate-500 mt-0.5">Visa/MasterCard checkout</p>
                                        </div>
                                    </label>
                                    
                                    <label className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${paymentMethod === 'Bank' ? 'border-blue-500 bg-blue-50/50' : 'border-slate-100 hover:border-slate-200'}`}>
                                        <input 
                                            type="radio" 
                                            name="paymentMethod" 
                                            checked={paymentMethod === 'Bank'} 
                                            onChange={() => setPaymentMethod('Bank')}
                                            className="accent-blue-600 w-4 h-4"
                                        />
                                        <div>
                                            <p className="font-bold text-slate-800 text-sm">Bank Transfer</p>
                                            <p className="text-[10px] text-slate-500 mt-0.5">Meezan Bank Direct Deposit</p>
                                        </div>
                                    </label>

                                    <label className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${paymentMethod === 'COD' ? 'border-blue-500 bg-blue-50/50' : 'border-slate-100 hover:border-slate-200'}`}>
                                        <input 
                                            type="radio" 
                                            name="paymentMethod" 
                                            checked={paymentMethod === 'COD'} 
                                            onChange={() => setPaymentMethod('COD')}
                                            className="accent-blue-600 w-4 h-4"
                                        />
                                        <div>
                                            <p className="font-bold text-slate-800 text-sm">Cash on Delivery</p>
                                            <p className="text-[10px] text-slate-500 mt-0.5">Pay in cash on delivery</p>
                                        </div>
                                    </label>
                                </div>

                                {paymentMethod === 'Card' && (
                                    <div className="space-y-4 bg-slate-50 p-5 rounded-2xl border border-slate-100 animate-fadeIn">
                                        <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg mb-2 text-xs text-blue-700">
                                            💡 Card transactions are processed securely via <strong>Meezan Bank Merchant Services</strong>.<br />
                                            Settled directly to Merchant Account: <strong>Amish Ali (Acc: 03310105909173)</strong>.
                                        </div>
                                        <div>
                                            <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Cardholder Name</label>
                                            <input 
                                                type="text" 
                                                name="cardName" 
                                                placeholder="e.g. John Doe"
                                                value={value.cardName} 
                                                onChange={handleChange} 
                                                className='w-full bg-white border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all'
                                            />
                                        </div>
                                        <div>
                                            <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Card Number</label>
                                            <input 
                                                type="text" 
                                                name="cardNumber" 
                                                placeholder="1234 5678 9012 3456"
                                                maxLength="19"
                                                value={value.cardNumber.replace(/\s?/g, '').replace(/(\d{4})/g, '$1 ').trim()} 
                                                onChange={handleChange} 
                                                className='w-full bg-white border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all'
                                            />
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Expiry Date</label>
                                                <input 
                                                    type="text" 
                                                    name="cardExpiry" 
                                                    placeholder="MM/YY"
                                                    maxLength="5"
                                                    value={value.cardExpiry} 
                                                    onChange={handleChange} 
                                                    className='w-full bg-white border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all'
                                                />
                                            </div>
                                            <div>
                                                <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>CVV / CVC</label>
                                                <input 
                                                    type="password" 
                                                    name="cardCvv" 
                                                    placeholder="123"
                                                    maxLength="3"
                                                    value={value.cardCvv} 
                                                    onChange={handleChange} 
                                                    className='w-full bg-white border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all'
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {paymentMethod === 'Bank' && (
                                    <div className="space-y-4 bg-emerald-50/50 p-5 rounded-2xl border border-emerald-100 animate-fadeIn text-slate-700">
                                        <div className="bg-emerald-100 border border-emerald-200 p-3 rounded-lg text-xs text-emerald-800">
                                            Please transfer <strong>Rs {finalTotal.toFixed(2)}</strong> from your bank application using the details below:
                                        </div>
                                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-semibold">
                                            <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                                                <p className="text-slate-400 font-bold uppercase tracking-wider text-[9px] mb-1">Bank Name</p>
                                                <p className="text-slate-800 font-bold text-sm">Meezan Bank</p>
                                            </div>
                                            <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                                                <p className="text-slate-400 font-bold uppercase tracking-wider text-[9px] mb-1">Account Title</p>
                                                <p className="text-slate-800 font-bold text-sm">Amish Ali</p>
                                            </div>
                                            <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                                                <p className="text-slate-400 font-bold uppercase tracking-wider text-[9px] mb-1">Account Number</p>
                                                <p className="text-slate-800 font-black text-sm select-all">03310105909173</p>
                                            </div>
                                        </div>
                                        <div>
                                            <label className='block text-xs font-bold text-slate-500 uppercase mb-1.5'>Transaction Reference Number (Ref ID) *</label>
                                            <input 
                                                type="text" 
                                                name="bankRefNo" 
                                                placeholder="e.g. 123456"
                                                maxLength="10"
                                                value={value.bankRefNo} 
                                                onChange={handleChange} 
                                                className='w-full bg-white border-2 border-slate-200 focus:border-blue-500 outline-none rounded-xl p-3 text-sm transition-all'
                                                required
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>

                            {}
                            <button 
                                type="submit" 
                                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg transition-all text-center cursor-pointer uppercase tracking-wider text-sm"
                            >
                                {paymentMethod === 'Card' ? 'Pay & Place Order' : 'Confirm Cash on Delivery Order'}
                            </button>
                        </form>
                    </div>

                    {}
                    <OrderInvoice
                        cartItems={cartItems}
                        subtotal={subtotal}
                        totalDiscount={totalDiscount}
                        deliveryCharge={deliveryCharge}
                        finalTotal={finalTotal}
                    />
                </div>
            </div>
            
            <Footer />
        </div>
    );
}
