import { FaChevronDown, FaList, FaSearch, FaShoppingCart } from 'react-icons/fa';
import { LuPhoneCall } from "react-icons/lu";
import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import mainlogo from '../assets/logo1.png';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import LocationButton from '../components/LocationButton';
import toast from 'react-hot-toast';
import { signOutUserSuccess } from '../redux/user/userSlice';
import CartDrawer from './CartDrawer';

export default function NavigationBar() {
    const { currentUser } = useSelector((state) => state.user);
    const [isOpen, setIsOpen] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [showPopup, setShowPopup] = useState(false);
        const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

    const navigate = useNavigate();
    const location = useLocation();
    const isHomePage = location.pathname === '/';
    const dispatch = useDispatch();
    const [searchTerm, setSearchTerm] = useState('');
    const [cartItems, setCartItems] = useState([]);
    const [isCartOpen, setIsCartOpen] = useState(false);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (!event.target.closest('.profile-dropdown-container')) {
                setIsProfileDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    useEffect(() => {
        const syncCart = () => {
            const stored = JSON.parse(localStorage.getItem('userCart') || '[]');
            setCartItems(stored);
        };
        window.addEventListener('cartUpdated', syncCart);
        syncCart();
        return () => window.removeEventListener('cartUpdated', syncCart);
    }, []);

    const updateCartQuantity = (index, newQty) => {
        if (newQty <= 0) {
            removeCartItem(index);
            return;
        }
        const updated = [...cartItems];
        if (newQty > updated[index].stock_available) {
            toast.error(`Only ${updated[index].stock_available} units available in stock.`);
            return;
        }
        updated[index].quantity = newQty;
        localStorage.setItem('userCart', JSON.stringify(updated));
        setCartItems(updated);
        window.dispatchEvent(new Event('cartUpdated'));
    };

    const removeCartItem = (index) => {
        const updated = [...cartItems];
        const removedItem = updated[index];
        updated.splice(index, 1);
        localStorage.setItem('userCart', JSON.stringify(updated));
        setCartItems(updated);
        window.dispatchEvent(new Event('cartUpdated'));
        toast.success(`${removedItem.medicine_name} removed from cart`);
    };

    const calculateCartTotal = () => {
        return cartItems.reduce((total, item) => {
            const finalPrice = item.price * (1 - item.discount / 100);
            return total + (finalPrice * item.quantity);
        }, 0);
    };

    const handleCheckout = () => {
        setIsCartOpen(false);
        navigate('/user-payment');
    };

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    }

    const togglePopup = () => {
        setShowPopup(!showPopup);
    }

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        if (searchTerm.trim()) {
            navigate(`/inventory-user?search=${searchTerm.trim()}`);
        }
    };

    const handleLogout = () => {
        dispatch(signOutUserSuccess());
        navigate('/sign-in');
    };

    return (
        <div className="w-full bg-transparent font-sans">
            { }
            <div className="max-w-7xl mx-auto px-4 py-3 md:py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                { }
                <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
                    <div className="flex items-center justify-between w-full sm:w-auto">
                        <Link to="/" className="flex-shrink-0">
                            <img src={mainlogo} alt="logo" className="w-[60px] md:w-[70px] h-auto cursor-pointer" />
                        </Link>
                        { }
                        <div className="flex items-center gap-3 md:hidden">
                            { }
                            <button
                                onClick={() => setIsCartOpen(true)}
                                className="relative p-2 text-slate-700 hover:text-blue-600 transition-colors flex items-center justify-center bg-white border-2 border-slate-200 rounded-full w-10 h-10 shadow-sm"
                            >
                                <FaShoppingCart className="text-lg text-slate-600" />
                                {cartItems.length > 0 && (
                                    <span className="absolute -top-1 -right-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-[9px] font-extrabold w-5 h-5 rounded-full flex items-center justify-center border border-white shadow-md animate-pulse">
                                        {cartItems.reduce((acc, curr) => acc + curr.quantity, 0)}
                                    </span>
                                )}
                            </button>
                            { }
                            {currentUser && (
                                <Link
                                    to="/profile"
                                    className="focus:outline-none cursor-pointer flex items-center"
                                >
                                    <img className="rounded-full h-9 w-9 object-cover border-2 border-pink-500 hover:opacity-90 transition-opacity" src={currentUser.avatar || 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'} alt="profile" />
                                </Link>
                            )}
                            { }
                            <button
                                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                                className="p-2 text-slate-700 hover:text-blue-600 bg-white border-2 border-slate-200 rounded-lg shadow-sm font-bold"
                            >
                                <span className="text-xl">☰</span>
                            </button>
                        </div>
                    </div>

                    { }
                    <form className="flex w-full sm:w-auto text-sm" onSubmit={handleSearchSubmit}>
                        <div className="relative flex-grow sm:flex-grow-0">
                            <input
                                type="text"
                                placeholder="medicines near me"
                                className="bg-white border-2 border-blue rounded-md placeholder-gray focus:outline-none w-full sm:w-56 p-2 pl-10"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                            <FaSearch className="text-gray absolute top-1/2 transform -translate-y-1/2 left-3" />
                        </div>
                        <button type="submit" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-md px-6 sm:px-10 ml-2 hover:bg-blue hover:border-blue transition-all cursor-pointer">Search</button>
                    </form>
                </div>

                { }
                <div className={`w-full md:w-auto ${isMobileMenuOpen ? 'block' : 'hidden'} md:block`}>
                    <button onClick={togglePopup} type="button" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white flex items-center rounded-md pr-6 pl-6 pt-3 pb-3 text-sm w-full md:w-auto justify-center shadow-md">
                        <LocationButton />
                    </button>
                </div>
            </div>

            { }
            <div className={`max-w-7xl mx-auto px-4 ${isMobileMenuOpen ? 'block' : 'hidden'} md:block`}>

                { }
                <div className="md:hidden flex flex-col gap-3 py-3 border-t border-slate-200">
                    <Link
                        to="/"
                        onClick={() => setIsMobileMenuOpen(false)}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-5 rounded-lg flex items-center justify-center gap-2 shadow-md transition-all text-sm uppercase tracking-wide w-full text-center"
                    >
                        <span>🏠</span> Home
                    </Link>

                    {currentUser ? (
                        <>
                            <Link
                                to="/profile"
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-5 rounded-lg flex items-center justify-center gap-2 shadow-md transition-all text-sm uppercase tracking-wide w-full text-center"
                            >
                                View Profile
                            </Link>
                            <button
                                onClick={() => { handleLogout(); setIsMobileMenuOpen(false); }}
                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-5 rounded-lg flex items-center justify-center gap-2 shadow-md transition-all text-sm uppercase tracking-wide w-full text-center cursor-pointer"
                            >
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/sign-in"
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="w-full"
                            >
                                <button
                                    type="button"
                                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-5 rounded-lg flex items-center justify-center gap-2 shadow-md transition-all text-sm uppercase tracking-wide w-full text-center cursor-pointer"
                                >
                                    Login
                                </button>
                            </Link>
                            <Link
                                to="/sign-up"
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="w-full"
                            >
                                <button
                                    type="button"
                                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-5 rounded-lg flex items-center justify-center gap-2 shadow-md transition-all text-sm uppercase tracking-wide w-full text-center cursor-pointer"
                                >
                                    Register
                                </button>
                            </Link>
                        </>
                    )}
                </div>

                { }
                <div className="hidden md:flex md:flex-row md:justify-between md:items-center py-2 md:py-3 border-t md:border-t-0 border-slate-200 gap-3">
                    { }
                    <div className="flex flex-row items-center gap-3">
                        <Link to="/" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold px-5 py-2.5 rounded-lg flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all text-sm uppercase tracking-wide">
                            <span>🏠</span> Home
                        </Link>

                        <div className="relative inline-block text-center w-full md:w-auto">
                            <button onClick={toggleMenu} className="text-slate-700 hover:text-blue-600 flex items-center justify-center gap-1.5 p-2.5 font-semibold text-sm transition-all w-full md:w-auto bg-slate-50 md:bg-transparent rounded-lg border md:border-0 border-slate-200">
                                <FaList className="text-base" />
                                <span>Menu</span>
                                <FaChevronDown className="text-xs" />
                            </button>
                            {isOpen && (
                                <div className="bg-white border border-slate-200 absolute left-0 right-0 md:right-auto z-50 mt-2 md:w-48 rounded-lg shadow-xl" role="menu">
                                    <div className="py-1" role="none">
                                        <Link to="/admin-login" onClick={() => { setIsOpen(false); }} className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 font-medium transition-colors" role="menuitem">Admin Login</Link>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    { }
                    <div className="flex flex-row items-center gap-3 md:gap-4 border-t md:border-t-0 border-slate-100 pt-3 md:pt-0">
                        { }
                        <button
                            onClick={() => setIsCartOpen(true)}
                            className="relative p-2 text-slate-700 hover:text-blue-600 transition-colors flex items-center justify-center bg-white border-2 border-slate-200 rounded-full w-10 h-10 shadow-sm hover:shadow-md cursor-pointer"
                        >
                            <FaShoppingCart className="text-lg text-slate-600" />
                            {cartItems.length > 0 && (
                                <span className="absolute -top-1 -right-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-[9px] font-extrabold w-5 h-5 rounded-full flex items-center justify-center border border-white shadow-md animate-pulse">
                                    {cartItems.reduce((acc, curr) => acc + curr.quantity, 0)}
                                </span>
                            )}
                        </button>

                        {currentUser ? (
                            <Link
                                to="/profile"
                                className="focus:outline-none cursor-pointer flex items-center"
                            >
                                <img className="rounded-full h-9 w-9 object-cover border-2 border-pink-500 hover:opacity-90 transition-opacity" src={currentUser.avatar || 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'} alt="profile" />
                            </Link>
                        ) : (
                            <div className="flex flex-row gap-2 w-full md:w-auto">
                                <Link to="/sign-in" className="w-full md:w-auto">
                                    <button type="button" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-md p-2 px-6 flex text-sm hover:bg-slate-100 transition-all justify-center w-full cursor-pointer">Login</button>
                                </Link>
                                <Link to="/sign-up" className="w-full md:w-auto">
                                    <button type="button" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-md p-2 px-6 flex text-sm hover:bg-green-700 transition-all justify-center w-full cursor-pointer">Register</button>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
            <CartDrawer
                isCartOpen={isCartOpen}
                setIsCartOpen={setIsCartOpen}
                cartItems={cartItems}
                updateCartQuantity={updateCartQuantity}
                removeCartItem={removeCartItem}
                calculateCartTotal={calculateCartTotal}
                handleCheckout={handleCheckout}
            />
        </div>
    );
}