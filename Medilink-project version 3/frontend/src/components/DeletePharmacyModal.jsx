import React from 'react';
import { FaTrash } from 'react-icons/fa';

export default function DeletePharmacyModal({
  showDeleteModal,
  setShowDeleteModal,
  selectedPharmacy,
  handleDeleteConfirm
}) {
  if (!showDeleteModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-blue/80 backdrop-blur-sm">
      <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-sm w-full text-center border border-slate-100">
        <div className="bg-red-50 text-red-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
          <FaTrash />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">Delete Pharmacy?</h3>
        <p className="text-slate-500 text-sm mb-6">
          Are you sure you want to delete <span className="font-semibold text-slate-800">{selectedPharmacy?.name}</span>? This action cannot be undone.
        </p>
        <div className="flex justify-center gap-3">
          <button 
            onClick={() => setShowDeleteModal(false)} 
            className="px-4 py-2 text-sm font-semibold text-slate-500 hover:bg-slate-50 rounded-lg border border-slate-200 transition-all"
          >
            Cancel
          </button>
          <button 
            onClick={handleDeleteConfirm} 
            className="px-5 py-2 text-sm font-semibold text-white bg-red-600 hover:bg-red-700 rounded-lg shadow-md transition-all"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
