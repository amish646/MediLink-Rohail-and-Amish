import React from 'react';

export default function OrderInvoice({
  cartItems,
  subtotal,
  totalDiscount,
  deliveryCharge,
  finalTotal
}) {
  return (
    <div>
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 sticky top-6">
        <h3 className="text-lg font-bold text-slate-800 border-b pb-3 mb-5 flex items-center gap-2">
          <span>🧾</span> Order Invoice
        </h3>

        <div className="divide-y divide-slate-100 max-h-64 overflow-y-auto mb-6 pr-2">
          {cartItems.map((cartItem, idx) => {
            const finalPrice = cartItem.price * (1 - cartItem.discount / 100);
            return (
              <div key={idx} className="py-3 flex justify-between items-start text-xs">
                <div>
                  <p className="font-bold text-slate-800">{cartItem.medicine_name}</p>
                  <p className="text-[10px] text-slate-400">Qty: {cartItem.quantity} &times; Rs {cartItem.price.toFixed(2)}</p>
                  {cartItem.discount > 0 && (
                    <span className="text-[9px] text-red-500 font-extrabold bg-red-50 px-1 py-0.5 rounded">{cartItem.discount}% OFF</span>
                  )}
                </div>
                <p className="font-bold text-slate-800">
                  Rs {(finalPrice * cartItem.quantity).toFixed(2)}
                </p>
              </div>
            );
          })}
        </div>

        <div className="space-y-3 pt-4 border-t border-slate-100 text-xs">
          <div className="flex justify-between text-slate-500">
            <span>Subtotal</span>
            <span>Rs {subtotal.toFixed(2)}</span>
          </div>
          {totalDiscount > 0 && (
            <div className="flex justify-between text-red-500">
              <span>Total Discount</span>
              <span>-Rs {totalDiscount.toFixed(2)}</span>
            </div>
          )}
          <div className="flex justify-between text-slate-500">
            <span>Delivery Charges</span>
            <span>Rs {deliveryCharge.toFixed(2)}</span>
          </div>
          
          <div className="flex justify-between text-base font-black text-slate-800 pt-3 border-t border-slate-100">
            <span>Total Payable</span>
            <span className="text-green-600">Rs {finalTotal.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
