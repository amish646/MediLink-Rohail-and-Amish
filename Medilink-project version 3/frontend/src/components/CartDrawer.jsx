import React from 'react';

export default function CartDrawer({
  isCartOpen,
  setIsCartOpen,
  cartItems,
  updateCartQuantity,
  removeCartItem,
  calculateCartTotal,
  handleCheckout
}) {
  if (!isCartOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden font-sans">
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity cursor-pointer" 
        onClick={() => setIsCartOpen(false)}
      ></div>
      
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col">
          <div className="flex-1 py-6 overflow-y-auto px-4 sm:px-6">
            <div className="flex items-start justify-between border-b border-gray-200 pb-5">
              <h2 className="text-xl font-black text-slate-800 flex items-center gap-2">
                <span>🛒</span> Your MediLink Cart
              </h2>
              <button 
                onClick={() => setIsCartOpen(false)} 
                className="text-gray-400 hover:text-gray-500 font-extrabold text-2xl"
              >
                &times;
              </button>
            </div>
            
            <div className="mt-8">
              {cartItems.length === 0 ? (
                <div className="text-center py-20">
                  <p className="text-5xl mb-4">🛒</p>
                  <p className="text-gray-500 font-medium">Your cart is empty.</p>
                  <button 
                    onClick={() => setIsCartOpen(false)} 
                    className="mt-4 text-blue-600 font-bold hover:underline"
                  >
                    Start shopping
                  </button>
                </div>
              ) : (
                <div className="flow-root">
                  <ul className="-my-6 divide-y divide-gray-200">
                    {cartItems.map((cartItem, idx) => {
                      const originalPrice = cartItem.price * cartItem.quantity;
                      const discountedPrice = (cartItem.price * (1 - cartItem.discount / 100)) * cartItem.quantity;
                      return (
                        <li key={idx} className="py-6 flex">
                          <div className="flex-1 flex flex-col">
                            <div>
                              <div className="flex justify-between text-base font-bold text-gray-900">
                                <h3>{cartItem.medicine_name}</h3>
                                <p className="ml-4">
                                  {cartItem.discount > 0 ? (
                                    <span>
                                      <span className="text-xs text-gray-400 line-through mr-2">Rs {originalPrice.toFixed(2)}</span>
                                      <span className="text-green-600">Rs {discountedPrice.toFixed(2)}</span>
                                    </span>
                                  ) : (
                                    <span>Rs {originalPrice.toFixed(2)}</span>
                                  )}
                                </p>
                              </div>
                              <p className="mt-1 text-xs text-gray-500">📍 {cartItem.pharmacy_name}</p>
                              {cartItem.discount > 0 && (
                                <span className="bg-red-50 text-red-500 text-[10px] font-bold px-1.5 py-0.5 rounded">
                                  {cartItem.discount}% Off applied
                                </span>
                              )}
                            </div>
                            <div className="flex-1 flex items-end justify-between text-sm mt-4">
                              <div className="flex items-center border border-gray-300 rounded-md">
                                <button 
                                  onClick={() => updateCartQuantity(idx, cartItem.quantity - 1)}
                                  className="px-2.5 py-1 bg-gray-100 hover:bg-gray-200 font-bold text-gray-700 transition-colors"
                                >
                                  -
                                </button>
                                <span className="px-3.5 py-1 font-semibold text-gray-800">{cartItem.quantity}</span>
                                <button 
                                  onClick={() => updateCartQuantity(idx, cartItem.quantity + 1)}
                                  className="px-2.5 py-1 bg-gray-100 hover:bg-gray-200 font-bold text-gray-700 transition-colors"
                                >
                                  +
                                </button>
                              </div>
                              <div className="flex">
                                <button 
                                  onClick={() => removeCartItem(idx)}
                                  type="button" 
                                  className="font-bold text-red-600 hover:text-red-500 text-xs transition-colors"
                                >
                                  Remove
                                </button>
                              </div>
                            </div>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
            </div>
          </div>
          
          {cartItems.length > 0 && (
            <div className="border-t border-gray-200 py-6 px-4 sm:px-6 bg-gray-50">
              <div className="flex justify-between text-base font-bold text-gray-900">
                <p>Subtotal</p>
                <p>Rs {calculateCartTotal().toFixed(2)}</p>
              </div>
              <div className="mt-6">
                <button 
                  onClick={handleCheckout}
                  className="w-full flex justify-center items-center px-6 py-3 border border-transparent rounded-lg shadow-md text-sm font-bold text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition-all cursor-pointer"
                >
                  Checkout & Payment
                </button>
              </div>
              <div className="mt-4 flex justify-center text-sm text-center text-gray-500">
                <p>
                  or{' '}
                  <button 
                    type="button" 
                    className="text-blue-600 font-bold hover:underline cursor-pointer" 
                    onClick={() => setIsCartOpen(false)}
                  >
                    Continue Shopping<span aria-hidden="true"> &rarr;</span>
                  </button>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
