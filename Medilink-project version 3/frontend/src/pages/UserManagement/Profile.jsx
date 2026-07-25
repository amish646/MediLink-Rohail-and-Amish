import { useSelector, useDispatch } from 'react-redux';
import { useRef, useState, useEffect } from 'react';
import {
  getDownloadURL,
  getStorage,
  ref,
  uploadBytesResumable,
} from 'firebase/storage';
import { app } from '../../firebase';
import {
  updateUserStart,
  updateUserSuccess,
  updateUserFailure,
  deleteUserFailure,
  deleteUserStart,
  deleteUserSuccess,
  signOutUserSuccess,
} from '../../redux/user/userSlice';
import Footer from '../../components/Footer';
import NavigationBar from '../../components/NavigationBar';
import { Link, useNavigate } from 'react-router-dom';
import { FaSignOutAlt } from 'react-icons/fa';

export default function Profile() {
  const fileRef = useRef(null);
  const { currentUser, loading, error } = useSelector((state) => state.user);
  const [file, setFile] = useState(undefined);
  const [filePerc, setFilePerc] = useState(0);
  const [fileUploadError, setFileUploadError] = useState(false);
  const [formData, setFormData] = useState({});
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [expandedOrders, setExpandedOrders] = useState({});

  const dispatch = useDispatch();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      if (!currentUser || !currentUser.email) return;
      setLoadingOrders(true);
      try {
        const response = await fetch(`http://192.168.1.11:8000/api/orders/user/${currentUser.email}`);
        const data = await response.json();
        if (data.status === 'Success') {
          setOrders(data.data);
        }
      } catch (err) {
        console.error("Error fetching orders:", err);
      } finally {
        setLoadingOrders(false);
      }
    };
    fetchOrders();
  }, [currentUser]);

  const toggleOrderExpand = (orderId) => {
    setExpandedOrders(prev => ({
      ...prev,
      [orderId]: !prev[orderId]
    }));
  };

  useEffect(() => {
    if (file) {
      handleFileUpload(file);
    }
  }, [file]);

  const handleFileUpload = (file) => {
    const storage = getStorage(app);
    const fileName = new Date().getTime() + file.name;
    const storageRef = ref(storage, fileName);
    const uploadTask = uploadBytesResumable(storageRef, file);

    uploadTask.on(
      'state_changed',
      (snapshot) => {
        const progress =
          (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        setFilePerc(Math.round(progress));
      },
      (error) => {
        setFileUploadError(true);
      },
      () => {
        getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) =>
          setFormData({ ...formData, avatar: downloadURL })
        );
      }
    );
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!currentUser || !currentUser._id) {
      dispatch(updateUserFailure("User ID not found. Please sign out and sign in again."));
      return;
    }
    try {
      dispatch(updateUserStart());
      const res = await fetch(`http://192.168.1.11:8000/auth/users/${currentUser._id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.status === 'Error') {
        dispatch(updateUserFailure(data.message));
        return;
      }

      dispatch(updateUserSuccess(data.user));
      setUpdateSuccess(true);
    } catch (error) {
      dispatch(updateUserFailure(error.message));
    }
  };

  const handleDeleteUser = async () => {
    if (!window.confirm("Are you sure you want to delete your account? This action cannot be undone.")) return;
    try {
      dispatch(deleteUserStart());
      const res = await fetch(`http://192.168.1.11:8000/auth/users/${currentUser._id}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (data.status === 'Error') {
        dispatch(deleteUserFailure(data.message || data.details));
        return;
      }
      dispatch(deleteUserSuccess(data));
      navigate('/sign-in');
    } catch (error) {
      dispatch(deleteUserFailure(error.message));
    }
  };

  const handleSignOut = () => {
    dispatch(signOutUserSuccess());
    navigate('/sign-in');
  };

  return (
    <div className='bg-paleblue min-h-screen flex flex-col justify-between font-sans'>
      <div>
        <NavigationBar />
        <div className='max-w-7xl mx-auto p-4 sm:p-6 lg:p-8'>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start mt-4 mb-10">
            
            {/* Left Column: Profile Card */}
            <div className="lg:col-span-1 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-md">
              <h1 className='text-2xl font-bold text-center mb-6 text-blue'>Profile Settings</h1>
              <form onSubmit={handleSubmit} className='flex flex-col gap-4'>
                <input
                  onChange={(e) => setFile(e.target.files[0])}
                  type='file'
                  ref={fileRef}
                  hidden
                  accept='image/*'
                />
                <div className='flex flex-col items-center gap-2 mb-4'>
                  <img
                    onClick={() => fileRef.current.click()}
                    src={formData.avatar || currentUser.avatar || 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'}
                    alt='profile'
                    className='rounded-full h-24 w-24 object-cover cursor-pointer border-4 border-lighter-blue hover:border-light-blue hover:opacity-90 shadow-md transition-all'
                  />
                  <p className='text-xs text-center'>
                    {fileUploadError ? (
                      <span className='text-red-600 font-bold'>
                        Error Image upload (image must be less than 2 MB)
                      </span>
                    ) : filePerc > 0 && filePerc < 100 ? (
                      <span className='text-blue font-bold'>{`Uploading ${filePerc}%`}</span>
                    ) : filePerc === 100 ? (
                      <span className='text-green-600 font-bold'>Image uploaded successfully!</span>
                    ) : (
                      <span className='text-slate-400 font-medium'>Click image to change profile photo</span>
                    )}
                  </p>
                </div>
                <input
                  type='text'
                  placeholder='username'
                  defaultValue={currentUser.username}
                  id='username'
                  className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                  onChange={handleChange}
                />
                <input
                  type='email'
                  placeholder='email'
                  id='email'
                  defaultValue={currentUser.email}
                  className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                  onChange={handleChange}
                />
                <input
                  type='tel'
                  placeholder='phone number'
                  pattern='[0-9]{10}'
                  defaultValue={currentUser.phonenumber}
                  id='phonenumber'
                  className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                  onChange={handleChange}
                />
                <input
                  type='text'
                  placeholder='address'
                  defaultValue={currentUser.address}
                  id='address'
                  className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                  onChange={handleChange}
                />
                <input
                  type='password'
                  placeholder='password'
                  onChange={handleChange}
                  id='password'
                  className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                />
                
                 <div className='flex flex-col gap-3 mt-4'>
                  <button
                    disabled={loading}
                    className='w-full bg-blue text-white rounded-lg p-3 uppercase hover:opacity-95 disabled:opacity-80 font-bold transition-all shadow-md'
                  >
                    {loading ? 'Loading...' : 'Update Profile'}
                  </button>

                  <button
                    type='button'
                    onClick={handleSignOut}
                    className='w-full bg-slate-600 text-white p-3 rounded-lg uppercase hover:opacity-95 font-bold transition-all text-xs flex items-center justify-center gap-1.5 cursor-pointer shadow-md'
                  >
                    <FaSignOutAlt /> Log Out
                  </button>

                  <button
                    type='button'
                    onClick={handleDeleteUser}
                    className='w-full bg-red-700 text-white p-3 rounded-lg uppercase hover:opacity-95 font-bold transition-all text-xs cursor-pointer shadow-md'
                  >
                    Delete Account
                  </button>
                </div>
              </form>

              {error && <p className='text-red-700 mt-5 text-center font-semibold'>{error}</p>}
              {updateSuccess && (
                <p className='text-green-700 mt-5 text-center font-semibold'>
                  User is updated successfully!
                </p>
              )}
            </div>

            {/* Right Column: Order History and Tracking */}
            <div className="lg:col-span-2 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-md">
              <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                📦 My Orders & Tracking
              </h2>

              {loadingOrders ? (
                <div className='flex flex-col items-center justify-center py-20'>
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue mb-3"></div>
                  <p className='text-slate-500 font-semibold text-sm'>Loading orders...</p>
                </div>
              ) : orders.length === 0 ? (
                <div className='bg-slate-50 border border-slate-100 p-12 text-center rounded-2xl'>
                  <p className='text-5xl mb-4'>🛒</p>
                  <p className='text-slate-600 font-bold text-lg mb-2'>No orders placed yet</p>
                  <p className='text-slate-400 text-sm'>Medicines you buy on the website will be trackable here.</p>
                </div>
              ) : (
                <div className='flex flex-col gap-6 max-h-[700px] overflow-y-auto pr-2'>
                  {orders.map((order) => {
                    const isExpanded = !!expandedOrders[order.orderId];
                    return (
                      <div key={order.orderId} className='border border-slate-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow bg-white'>
                        {/* Order Header / Main Card Info */}
                        <div 
                          onClick={() => toggleOrderExpand(order.orderId)}
                          className='p-5 bg-slate-50/50 hover:bg-slate-50 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 transition-colors'
                        >
                          <div className='space-y-1'>
                            <div className='flex items-center gap-2'>
                              <span className='font-black text-blue text-base'>{order.orderId}</span>
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                                order.orderStatus === 'Delivered' ? 'bg-green-100 text-green-700' :
                                order.orderStatus === 'Shipped' ? 'bg-indigo-100 text-indigo-700' :
                                order.orderStatus === 'Cancelled' ? 'bg-red-100 text-red-700' :
                                'bg-blue-100 text-blue-700'
                              }`}>
                                {order.orderStatus}
                              </span>
                            </div>
                            <p className='text-xs text-slate-400 font-medium'>Placed on {order.date}</p>
                          </div>

                          <div className='flex items-center gap-4 justify-between sm:justify-end'>
                            <div className='text-left sm:text-right'>
                              <p className='text-[10px] font-bold text-slate-400 uppercase tracking-wider'>Total Bill</p>
                              <p className='text-lg font-black text-slate-800'>Rs {parseFloat(order.amount).toFixed(2)}</p>
                            </div>
                            <button className='text-slate-400 hover:text-slate-600 text-lg transition-transform focus:outline-none'>
                              {isExpanded ? '▲' : '▼'}
                            </button>
                          </div>
                        </div>

                        {/* Order Progress / Tracking Stepper */}
                        <div className="px-5 py-4 border-b border-slate-100">
                          {order.orderStatus === 'Cancelled' ? (
                            <div className="bg-red-50 border border-red-100 rounded-xl p-3.5 flex items-center gap-3">
                              <span className="text-red-500 text-xl">❌</span>
                              <div>
                                <p className="text-red-800 font-extrabold text-xs uppercase">Order Cancelled</p>
                                <p className="text-red-600 text-xs mt-0.5">This order has been cancelled and will not be processed further.</p>
                              </div>
                            </div>
                          ) : (
                            <div className="w-full py-4 px-2 sm:px-6">
                              <div className="flex items-center justify-between relative">
                                {/* Track Line Background */}
                                <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-1 bg-slate-100 rounded-full z-0"></div>
                                
                                {/* Color Track Line based on progress */}
                                <div 
                                  className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-green-500 rounded-full transition-all duration-500 z-0"
                                  style={{ 
                                    width: order.orderStatus === 'Processing' ? '0%' : order.orderStatus === 'Shipped' ? '50%' : '100%' 
                                  }}
                                ></div>

                                {/* Step 1: Processing */}
                                <div className="flex flex-col items-center relative z-10">
                                  <div className={`w-9 h-9 rounded-full flex items-center justify-center border-2 font-bold text-xs transition-all ${
                                    order.orderStatus === 'Processing' ? 'bg-blue border-blue text-white shadow-md scale-110' : 'bg-green-500 border-green-500 text-white shadow-md'
                                  }`}>
                                    {order.orderStatus !== 'Processing' ? '✓' : '🕒'}
                                  </div>
                                  <span className={`text-[10px] font-extrabold mt-1.5 ${order.orderStatus === 'Processing' ? 'text-blue' : 'text-green-600'}`}>Processing</span>
                                </div>

                                {/* Step 2: Shipped */}
                                <div className="flex flex-col items-center relative z-10">
                                  <div className={`w-9 h-9 rounded-full flex items-center justify-center border-2 font-bold text-xs transition-all ${
                                    order.orderStatus === 'Shipped' ? 'bg-blue border-blue text-white shadow-md scale-110' :
                                    order.orderStatus === 'Delivered' ? 'bg-green-500 border-green-500 text-white shadow-md' : 'bg-white border-slate-200 text-slate-400'
                                  }`}>
                                    {order.orderStatus === 'Delivered' ? '✓' : '🚚'}
                                  </div>
                                  <span className={`text-[10px] font-extrabold mt-1.5 ${
                                    order.orderStatus === 'Shipped' ? 'text-blue' :
                                    order.orderStatus === 'Delivered' ? 'text-green-600' : 'text-slate-400'
                                  }`}>Shipped</span>
                                </div>

                                {/* Step 3: Delivered */}
                                <div className="flex flex-col items-center relative z-10">
                                  <div className={`w-9 h-9 rounded-full flex items-center justify-center border-2 font-bold text-xs transition-all ${
                                    order.orderStatus === 'Delivered' ? 'bg-green-500 border-green-500 text-white shadow-md scale-110' : 'bg-white border-slate-200 text-slate-400'
                                  }`}>
                                    🎁
                                  </div>
                                  <span className={`text-[10px] font-extrabold mt-1.5 ${order.orderStatus === 'Delivered' ? 'text-green-600' : 'text-slate-400'}`}>Delivered</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Collapsible Details Panel */}
                        {isExpanded && (
                          <div className='p-5 bg-slate-50/30 border-t border-slate-100 space-y-4 text-xs text-slate-600'>
                            {/* Shipping Details */}
                            <div className='bg-slate-50 p-4 rounded-xl border border-slate-100 flex flex-col sm:flex-row gap-4 justify-between'>
                              <div>
                                <p className="font-extrabold text-slate-500 uppercase tracking-wider text-[9px] mb-1.5">Shipping Address</p>
                                <p className='font-semibold text-slate-800 text-sm'>{order.deliveryAddress}</p>
                              </div>
                              <div className='min-w-[180px]'>
                                <p className="font-extrabold text-slate-500 uppercase tracking-wider text-[9px] mb-1.5">Transaction Info</p>
                                <p><strong className='text-slate-700'>Payment Method:</strong> {order.paymentStatus}</p>
                                <p className='mt-0.5'><strong className='text-slate-700'>Reference:</strong> <span className='font-mono font-bold text-slate-600 bg-slate-200/60 px-1.5 py-0.5 rounded'>{order.transactionId}</span></p>
                              </div>
                            </div>

                            {/* Items List */}
                            <div>
                              <p className="font-extrabold text-slate-500 uppercase tracking-wider text-[9px] mb-2">Order Items ({order.items.length})</p>
                              <div className='border border-slate-100 rounded-xl overflow-hidden bg-white'>
                                <table className="w-full text-left text-xs border-collapse">
                                  <thead>
                                    <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[9px]">
                                      <th className="px-4 py-2">Medicine</th>
                                      <th className="px-4 py-2">Pharmacy</th>
                                      <th className="px-4 py-2 text-center">Qty</th>
                                      <th className="px-4 py-2 text-right">Price</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-slate-100 font-medium">
                                    {order.items.map((item, idx) => (
                                      <tr key={idx} className="hover:bg-slate-50/50">
                                        <td className="px-4 py-2.5 font-bold text-slate-800">{item.medicine_name}</td>
                                        <td className="px-4 py-2.5 text-slate-400">{item.pharmacy_name}</td>
                                        <td className="px-4 py-2.5 text-center text-slate-600">{item.quantity}</td>
                                        <td className="px-4 py-2.5 text-right text-slate-800">Rs {item.price.toFixed(2)}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
