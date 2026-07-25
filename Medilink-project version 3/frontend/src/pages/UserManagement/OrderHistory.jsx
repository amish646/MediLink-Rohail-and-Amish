import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';

export default function OrderHistory() {
    const { currentUser } = useSelector((state) => state.user);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrders = async () => {
            if (!currentUser || !currentUser.email) {
                setLoading(false);
                return;
            }
            try {
                const response = await fetch(`http://192.168.1.11:8000/api/orders/user/${currentUser.email}`);
                const data = await response.json();
                if (data.status === 'Success') {
                    setOrders(data.data);
                }
            } catch (err) {
                console.error("Error fetching order history:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, [currentUser]);

    return (
        <div className='bg-sky-50 min-h-screen flex flex-col font-sans'>
            <NavigationBar />
            
            <div className='max-w-6xl mx-auto w-full p-6 flex-1'>
                <h1 className='text-3xl font-black text-slate-800 tracking-tight my-7'>My Orders</h1>
                
                {loading ? (
                    <div className='flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-slate-100 shadow-sm'>
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-3"></div>
                        <p className='text-slate-500 font-semibold text-sm'>Loading order history...</p>
                    </div>
                ) : orders.length === 0 ? (
                    <div className='bg-white p-12 text-center rounded-2xl border border-slate-100 shadow-sm'>
                        <p className='text-5xl mb-4'>📦</p>
                        <p className='text-gray-500 font-bold text-lg'>You haven't placed any orders yet.</p>
                    </div>
                ) : (
                    <div className='bg-white shadow-sm border border-slate-100 rounded-2xl overflow-hidden'>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 border-b border-slate-100">
                                    <tr className="text-slate-500 font-bold text-xs uppercase tracking-wider">
                                        <th className="px-6 py-4">Order ID</th>
                                        <th className="px-6 py-4">Date Ordered</th>
                                        <th className="px-6 py-4">Items</th>
                                        <th className="px-6 py-4">Payment Status</th>
                                        <th className="px-6 py-4">Transaction ID</th>  
                                        <th className="px-6 py-4 text-right">Amount</th>
                                        <th className="px-6 py-4 text-center">Status</th>  
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {orders.map((order, index) => (
                                        <tr key={index} className="hover:bg-slate-50/50 transition-colors">
                                            <td className="px-6 py-4 font-black text-blue-600">{order.orderId}</td>
                                            <td className="px-6 py-4 text-slate-500">{order.date}</td>
                                            <td className="px-6 py-4">
                                                <div className="space-y-1">
                                                    {order.items.map((item, idx) => (
                                                        <p key={idx} className="font-medium text-slate-700">
                                                            {item.medicine_name} <span className="text-slate-400 font-normal">({item.quantity}x)</span>
                                                        </p>
                                                    ))}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase ${order.paymentStatus.includes('Paid') ? 'bg-green-50 text-green-600 border border-green-100' : 'bg-amber-50 text-amber-600 border border-amber-100'}`}>
                                                    {order.paymentStatus}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 font-mono text-slate-400 text-xs">{order.transactionId}</td>
                                            <td className="px-6 py-4 font-black text-slate-800 text-right">Rs {parseFloat(order.amount).toFixed(2)}</td>
                                            <td className="px-6 py-4 text-center">
                                                <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase border ${
                                                    order.orderStatus === 'Delivered' ? 'bg-green-50 text-green-600 border-green-100' :
                                                    order.orderStatus === 'Shipped' ? 'bg-indigo-50 text-indigo-600 border-indigo-100' :
                                                    order.orderStatus === 'Cancelled' ? 'bg-red-50 text-red-600 border-red-100' :
                                                    'bg-blue-50 text-blue-600 border-blue-100'
                                                }`}>
                                                    {order.orderStatus}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
            
            <Footer />   
        </div>
    );
}
