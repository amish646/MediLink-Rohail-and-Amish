import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import SideBar from '../../components/SideBar';

export default function AdminOrderManagement() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState('All');

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const response = await axios.get('http://192.168.1.11:8000/api/orders');
            if (response.data.status === 'Success') {
                setOrders(response.data.data);
            } else {
                toast.error("Failed to load orders from database");
            }
        } catch (error) {
            console.error("Connection error:", error);
            toast.error("Could not reach backend API server");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const handleStatusChange = async (orderId, newStatus) => {
        try {
            const response = await axios.put(`http://192.168.1.11:8000/api/orders/${orderId}`, {
                orderStatus: newStatus
            });
            if (response.data.status === 'Success') {
                toast.success(`Order ${orderId} marked as ${newStatus}`);
                fetchOrders(); 
            } else {
                toast.error("Failed to update order status");
            }
        } catch (error) {
            console.error("Update error:", error);
            toast.error("Error communicating status update to server");
        }
    };

    const filteredOrders = statusFilter === 'All' 
        ? orders 
        : orders.filter(o => o.orderStatus === statusFilter);

    return (
        <div className='flex min-h-screen bg-sky-50 font-sans'>
            <SideBar />
            
            <div className='flex-1 p-8 overflow-x-hidden'>
                <div className='flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4'>
                    <div>
                        <h1 className='text-3xl font-black text-slate-800 tracking-tight'>Order Management</h1>
                        <p className='text-slate-500 text-sm mt-1'>Process user orders, track transaction records, and coordinate deliveries.</p>
                    </div>

                    <div className='flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm'>
                        <span className='text-xs font-bold text-slate-500 uppercase'>Filter:</span>
                        <select 
                            value={statusFilter} 
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className='outline-none text-sm font-bold text-slate-700 bg-transparent cursor-pointer'
                        >
                            <option value="All">All Statuses</option>
                            <option value="Processing">Processing</option>
                            <option value="Shipped">Shipped</option>
                            <option value="Delivered">Delivered</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                    </div>
                </div>

                {loading ? (
                    <div className='flex flex-col items-center justify-center py-24'>
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-3"></div>
                        <p className='text-blue-600 font-bold text-sm'>Syncing MongoDB transaction logs...</p>
                    </div>
                ) : filteredOrders.length === 0 ? (
                    <div className='bg-white p-12 text-center rounded-2xl border border-slate-200/60 shadow-sm'>
                        <p className='text-4xl mb-3'>📦</p>
                        <p className='text-slate-500 font-bold text-base'>No orders found for the selected status.</p>
                    </div>
                ) : (
                    <div className='grid grid-cols-1 gap-6'>
                        {filteredOrders.map((order) => (
                            <div key={order.orderId} className='bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6 flex flex-col md:flex-row justify-between gap-6 hover:shadow-md transition-shadow'>
                                
                                {}
                                <div className='space-y-4 flex-1'>
                                    <div className='flex flex-wrap items-center gap-3'>
                                        <span className='text-base font-black text-blue-600'>{order.orderId}</span>
                                        <span className='text-xs text-slate-400 font-medium'>Placed on {order.date}</span>
                                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase border ${
                                            order.paymentStatus.includes('COD') 
                                                ? 'bg-amber-50 text-amber-600 border-amber-100' 
                                                : 'bg-green-50 text-green-600 border-green-100'
                                        }`}>
                                            {order.paymentStatus}
                                        </span>
                                    </div>

                                    {}
                                    <div className='bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs text-slate-600 leading-relaxed'>
                                        <p className="font-bold text-slate-500 uppercase tracking-wider text-[9px] mb-1">Shipping & Delivery Details</p>
                                        <p><strong className="text-slate-800">Email:</strong> {order.userEmail}</p>
                                        <p className='mt-0.5'><strong className="text-slate-800">Address:</strong> {order.deliveryAddress}</p>
                                        <p className='mt-0.5'><strong className="text-slate-800">Txn/Ref ID:</strong> <span className='font-mono font-bold text-slate-500'>{order.transactionId}</span></p>
                                    </div>

                                    {}
                                    <div>
                                        <h4 className='font-bold text-slate-700 text-xs uppercase tracking-wider mb-2'>Ordered Medicines:</h4>
                                        <div className='space-y-2'>
                                            {order.items.map((item, idx) => (
                                                <div key={idx} className='flex justify-between items-center text-xs border-b border-slate-50 pb-1.5 max-w-xl'>
                                                    <div>
                                                        <span className='font-bold text-slate-800'>{item.medicine_name}</span>
                                                        <span className='text-slate-400 text-[10px] ml-2'>({item.pharmacy_name})</span>
                                                    </div>
                                                    <span className='text-slate-500 font-semibold'>{item.quantity} x Rs {item.price.toFixed(2)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {}
                                <div className='flex flex-col justify-between items-start md:items-end min-w-max border-t md:border-t-0 md:border-l border-slate-100 pt-4 md:pt-0 md:pl-6 gap-4'>
                                    <div className='text-left md:text-right'>
                                        <p className='text-xs font-bold text-slate-400 uppercase tracking-wider'>Total Bill</p>
                                        <p className='text-2xl font-black text-green-600 mt-0.5'>Rs {parseFloat(order.amount).toFixed(2)}</p>
                                    </div>

                                    <div className='space-y-2 w-full'>
                                        <label className='block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1'>Update Order Status</label>
                                        <div className='flex items-center gap-2'>
                                            <select 
                                                value={order.orderStatus} 
                                                onChange={(e) => handleStatusChange(order.orderId, e.target.value)}
                                                className={`text-xs font-bold px-3 py-2 rounded-xl outline-none border cursor-pointer ${
                                                    order.orderStatus === 'Delivered' ? 'bg-green-50 text-green-600 border-green-200' :
                                                    order.orderStatus === 'Shipped' ? 'bg-indigo-50 text-indigo-600 border-indigo-200' :
                                                    order.orderStatus === 'Cancelled' ? 'bg-red-50 text-red-600 border-red-200' :
                                                    'bg-blue-50 text-blue-600 border-blue-200'
                                                }`}
                                            >
                                                <option value="Processing">Processing</option>
                                                <option value="Shipped">Shipped</option>
                                                <option value="Delivered">Delivered</option>
                                                <option value="Cancelled">Cancelled</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
