import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import { FaSearch, FaPlus, FaEdit, FaTrash, FaMapMarkerAlt, FaStore, FaWindowClose } from 'react-icons/fa';
import SideBar from '../../components/SideBar';
import AddPharmacyModal from '../../components/AddPharmacyModal';
import EditPharmacyModal from '../../components/EditPharmacyModal';
import DeletePharmacyModal from '../../components/DeletePharmacyModal';

export default function ManagePharmacies() {
  const [pharmacies, setPharmacies] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    license_no: '',
    latitude: '',
    longitude: ''
  });
  const [selectedPharmacy, setSelectedPharmacy] = useState(null);

  useEffect(() => {
    fetchPharmacies();
  }, []);

  const fetchPharmacies = async () => {
    try {
      const response = await axios.get('http://192.168.1.11:8000/pharmacies');
      if (response.data.status === 'Success') {
        setPharmacies(response.data.data);
        setSearchResults(response.data.data);
      } else {
        toast.error('Failed to load pharmacies');
      }
    } catch (error) {
      console.error('Error fetching pharmacies:', error);
      toast.error('Error connecting to backend');
    }
  };

  useEffect(() => {
    const filtered = pharmacies.filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.license_no.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setSearchResults(filtered);
  }, [searchQuery, pharmacies]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.license_no || !formData.latitude || !formData.longitude) {
      toast.error('All fields are required');
      return;
    }
    
    const payload = {
      name: formData.name,
      license_no: formData.license_no,
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude)
    };

    if (isNaN(payload.latitude) || isNaN(payload.longitude)) {
      toast.error('Latitude and Longitude must be valid numbers');
      return;
    }

    try {
      const res = await axios.post('http://192.168.1.11:8000/pharmacies', payload);
      if (res.data.status === 'Success') {
        toast.success('Pharmacy registered successfully');
        setShowAddModal(false);
        setFormData({ name: '', license_no: '', latitude: '', longitude: '' });
        fetchPharmacies();
      } else {
        toast.error(res.data.message || 'Failed to register pharmacy');
      }
    } catch (error) {
      console.error(error);
      toast.error('Error adding pharmacy');
    }
  };

  const handleEditClick = (pharmacy) => {
    setSelectedPharmacy(pharmacy);
    const coords = pharmacy.location?.coordinates || [0, 0];
    setFormData({
      name: pharmacy.name,
      license_no: pharmacy.license_no,
      longitude: coords[0],
      latitude: coords[1]
    });
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.license_no || !formData.latitude || !formData.longitude) {
      toast.error('All fields are required');
      return;
    }

    const payload = {
      name: formData.name,
      license_no: formData.license_no,
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude)
    };

    if (isNaN(payload.latitude) || isNaN(payload.longitude)) {
      toast.error('Latitude and Longitude must be valid numbers');
      return;
    }

    try {
      const res = await axios.put(`http://192.168.1.11:8000/pharmacies/${selectedPharmacy._id}`, payload);
      if (res.data.status === 'Success') {
        toast.success('Pharmacy updated successfully');
        setShowEditModal(false);
        setFormData({ name: '', license_no: '', latitude: '', longitude: '' });
        setSelectedPharmacy(null);
        fetchPharmacies();
      } else {
        toast.error(res.data.message || 'Failed to update pharmacy');
      }
    } catch (error) {
      console.error(error);
      toast.error('Error updating pharmacy');
    }
  };

  const handleDeleteClick = (pharmacy) => {
    setSelectedPharmacy(pharmacy);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      const res = await axios.delete(`http://192.168.1.11:8000/pharmacies/${selectedPharmacy._id}`);
      if (res.data.status === 'Success') {
        toast.success('Pharmacy deleted successfully');
        setShowDeleteModal(false);
        setSelectedPharmacy(null);
        fetchPharmacies();
      } else {
        toast.error(res.data.message || 'Failed to delete pharmacy');
      }
    } catch (error) {
      console.error(error);
      toast.error('Error deleting pharmacy');
    }
  };

  return (
    <div className='flex min-h-screen bg-slate-50'>
      <SideBar />
      <Toaster position="top-right" />
      <div className='flex-1 flex flex-col'>
        {}
        <div className='bg-paleblue justify-between flex items-center px-10 py-8 border-b border-lighter-blue'>
          <div>
            <h1 className='text-4xl font-bold text-blue flex items-center gap-3'>
              <FaStore className='text-light-blue' />
              Manage Pharmacies
            </h1>
            <p className='text-gray text-sm mt-1'>View and coordinate branches available in the cloud database</p>
          </div>
          
          <button 
            onClick={() => {
              setFormData({ name: '', license_no: '', latitude: '', longitude: '' });
              setShowAddModal(true);
            }} 
            className="bg-light-blue hover:bg-blue text-white font-semibold transition-all py-2.5 px-5 rounded-lg flex items-center gap-2 shadow-md hover:shadow-lg transform active:scale-95 duration-200"
          >
            <FaPlus className='text-sm' />
            <span>Add Pharmacy</span>
          </button>
        </div>

        {}
        <div className='px-10 pt-8 flex gap-6'>
          <div className='bg-lighter-blue border border-light-blue rounded-2xl w-80 p-6 shadow-sm flex items-center justify-between'>
            <div>
              <p className='text-dark-blue font-medium text-sm uppercase tracking-wider'>Registered Branches</p>
              <p className='text-dark-blue text-3xl font-extrabold mt-1'>{pharmacies.length}</p>
            </div>
            <div className='bg-white p-3 rounded-full shadow-inner text-light-blue text-2xl'>
              <FaStore />
            </div>
          </div>
        </div>

        {}
        <div className='px-10 py-6 flex justify-end'>
          <div className='relative w-80'>
            <input 
              type='text' 
              placeholder='Search by name or license...' 
              className='bg-white border-2 border-lighter-blue focus:border-light-blue rounded-lg placeholder-gray focus:outline-none w-full p-2.5 pl-10 transition-all duration-300 text-sm shadow-sm'
              onChange={(e) => setSearchQuery(e.target.value)} 
              value={searchQuery}
            />
            <FaSearch className='text-gray absolute top-1/2 transform -translate-y-1/2 left-3.5 text-sm' />
          </div>
        </div>

        {}
        <div className='px-10 pb-12 flex-1'>
          {searchResults.length === 0 ? (
            <div className='flex flex-col items-center justify-center p-12 bg-white rounded-2xl border-2 border-dashed border-lighter-blue h-96'>
              <FaStore className='text-6xl text-slate-300 mb-4' />
              <p className='text-slate-500 font-semibold text-lg'>No pharmacies found</p>
              <p className='text-slate-400 text-sm mt-1'>Try adding a new branch or refine your search query.</p>
            </div>
          ) : (
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
              {searchResults.map((pharmacy) => {
                const coords = pharmacy.location?.coordinates || [0.0, 0.0];
                const lng = coords[0];
                const lat = coords[1];
                
                return (
                  <div 
                    key={pharmacy._id}
                    className='bg-white border border-slate-100 rounded-2xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1.5 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden'
                  >
                    {}
                    <div className='absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-light-blue to-blue'></div>
                    
                    <div>
                      <div className='flex justify-between items-start mb-4'>
                        <div className='bg-paleblue p-2.5 rounded-xl text-blue text-xl group-hover:scale-110 transition-all duration-300'>
                          <FaStore />
                        </div>
                        <span className='bg-lighter-blue text-blue font-semibold text-xs px-2.5 py-1 rounded-full uppercase tracking-wider border border-light-blue/20'>
                          {pharmacy.license_no}
                        </span>
                      </div>
                      
                      <h3 className='text-lg font-bold text-dark-blue group-hover:text-blue transition-colors duration-300 line-clamp-1'>
                        {pharmacy.name}
                      </h3>
                      
                      <div className='mt-4 space-y-2 border-t border-slate-50 pt-4 text-sm'>
                        <div className='flex items-center text-slate-600 gap-2'>
                          <FaMapMarkerAlt className='text-light-blue text-xs shrink-0' />
                          <span className='font-medium text-slate-400 w-16 shrink-0'>Latitude:</span>
                          <span className='font-mono text-dark-blue'>{lat.toFixed(4)}</span>
                        </div>
                        <div className='flex items-center text-slate-600 gap-2'>
                          <FaMapMarkerAlt className='text-light-blue text-xs shrink-0' />
                          <span className='font-medium text-slate-400 w-16 shrink-0'>Longitude:</span>
                          <span className='font-mono text-dark-blue'>{lng.toFixed(4)}</span>
                        </div>
                      </div>
                    </div>

                    <div className='mt-6 pt-4 border-t border-slate-100 flex items-center justify-between gap-3'>
                      <a 
                        href={`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className='text-xs font-semibold text-blue hover:text-light-blue underline flex items-center gap-1 transition-all'
                      >
                        View Map
                      </a>
                      
                      <div className='flex items-center gap-2'>
                        <button 
                          onClick={() => handleEditClick(pharmacy)}
                          className='p-2 text-slate-400 hover:text-blue hover:bg-slate-50 rounded-lg transition-all border border-transparent hover:border-slate-100'
                          title="Edit Pharmacy"
                        >
                          <FaEdit className='text-sm' />
                        </button>
                        <button 
                          onClick={() => handleDeleteClick(pharmacy)}
                          className='p-2 text-slate-400 hover:text-red-600 hover:bg-red-50/50 rounded-lg transition-all border border-transparent hover:border-red-100'
                          title="Delete Pharmacy"
                        >
                          <FaTrash className='text-sm' />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
      <AddPharmacyModal
        showAddModal={showAddModal}
        setShowAddModal={setShowAddModal}
        formData={formData}
        handleInputChange={handleInputChange}
        handleAddSubmit={handleAddSubmit}
      />

      <EditPharmacyModal
        showEditModal={showEditModal}
        setShowEditModal={setShowEditModal}
        formData={formData}
        handleInputChange={handleInputChange}
        handleEditSubmit={handleEditSubmit}
      />

      <DeletePharmacyModal
        showDeleteModal={showDeleteModal}
        setShowDeleteModal={setShowDeleteModal}
        selectedPharmacy={selectedPharmacy}
        handleDeleteConfirm={handleDeleteConfirm}
      />
    </div>
  );
}
