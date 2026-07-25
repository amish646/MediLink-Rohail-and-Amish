import React from 'react';
import { FaEdit, FaWindowClose } from 'react-icons/fa';

export default function EditPharmacyModal({
  showEditModal,
  setShowEditModal,
  formData,
  handleInputChange,
  handleEditSubmit
}) {
  if (!showEditModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-blue/80 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100">
        <div className="bg-gradient-to-r from-light-blue to-blue text-white px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <FaEdit /> Edit Pharmacy Details
          </h2>
          <button onClick={() => setShowEditModal(false)} className="hover:text-red-200 transition-all">
            <FaWindowClose className="text-xl" />
          </button>
        </div>
        
        <form onSubmit={handleEditSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Pharmacy Name</label>
            <input 
              type="text" 
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-light-blue focus:ring-1 focus:ring-light-blue"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">License Number</label>
            <input 
              type="text" 
              name="license_no"
              value={formData.license_no}
              onChange={handleInputChange}
              className="w-full border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-light-blue focus:ring-1 focus:ring-light-blue"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Latitude</label>
              <input 
                type="number" 
                step="0.000001"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                className="w-full border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-light-blue focus:ring-1 focus:ring-light-blue"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Longitude</label>
              <input 
                type="number" 
                step="0.000001"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                className="w-full border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-light-blue focus:ring-1 focus:ring-light-blue"
                required
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button 
              type="button" 
              onClick={() => setShowEditModal(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-500 hover:bg-slate-50 rounded-lg border border-slate-200 transition-all"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="px-5 py-2 text-sm font-semibold text-white bg-light-blue hover:bg-blue rounded-lg shadow-md transition-all"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
