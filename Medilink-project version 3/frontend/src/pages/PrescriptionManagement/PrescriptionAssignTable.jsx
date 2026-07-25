import React, { useState, useEffect } from 'react';
import { FaSearch } from 'react-icons/fa';
import axios from 'axios';
import toast from 'react-hot-toast';
import SideBar from '../../components/SideBar';

function PrescriptionAssignTable() {
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [deleteId, setDeleteId] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const fetchPrescription = await axios.get('http://192.168.1.11:8000/prescription/read');
            const response = fetchPrescription.data;
            const updatedPrescription = response.prescription.map(promo => {
                if (new Date(promo.expiredAt) < new Date()) {
                    promo.status = 'Inactive';
                    axios.put(`http://192.168.1.11:8000/prescription/update/${promo._id}`, { status: 'Inactive' })
                    .then(response => {
                        console.log('Prescription status updated:', response);
                    })
                    .catch(error => {
                        console.error('Error updating Prescription status:', error);
                    });
                }
                return promo;
            });
            setData(response);
            setSearchResults(updatedPrescription);
        } catch (error) {
            console.log(error);
        }
    };

    const formatDate = (datetimeString) => {
        const date = new Date(datetimeString);
        const formattedDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
        return formattedDate;
    };

    const handleSearch = (e) => {
      e.preventDefault();
      const filtered = data.prescription?.filter(elem => {
          return elem.PrescriptionID.toLowerCase().includes(searchQuery.toLowerCase()) ||
              elem.firstName.toLowerCase().includes(searchQuery.toLowerCase()) ||
              elem.lastName.toLowerCase().includes(searchQuery.toLowerCase()) ||
              elem.MedicationNames.toLowerCase().includes(searchQuery.toLowerCase());
      });
      setSearchResults(filtered || []);
  };

    const handleDeleteConfirmation = (id) => {
        setDeleteId(id);
    };

    const handleDeleteConfirmed = async () => {
        try {
            await axios.delete(`http://192.168.1.11:8000/prescription/delete/${deleteId}`);
            setData(prevState => ({
                ...prevState,
                prescription: (prevState.prescription || []).filter(promo => promo._id !== deleteId)
            }));
            setSearchResults(prevResults => prevResults.filter(promo => promo._id !== deleteId));
            setDeleteId(null);
            toast.success('Prescription deleted successfully!');
        } catch (error) {
            console.log(error);
        }
    };

    const handleCancelDelete = () => {
        setDeleteId(null);
    };

  return (
    <div className='flex'>
        <SideBar />
        <div className='flex-1'>
            <div className='bg-paleblue justify-between flex px-10 py-10'>
                <h1 className='text-4xl font-bold text-blue'>Prescription Management Dashboard</h1>
            </div>
            
            <form  className='px-10 py-5 flex justify-end' onSubmit={handleSearch}>
                <div className='relative'>
                    <input type='text' placeholder='Search...' className='bg-white border-2 border-light-blue rounded-md placeholder-gray focus:outline-none w-56 p-2 pl-10' onChange={(e) => setSearchQuery(e.target.value)} value={searchQuery}/>
                    <FaSearch className='text-gray absolute top-1/2 transform -translate-y-1/2 left-3' />
                </div>
                <button type='submit' className='bg-light-blue border-2 border-light-blue text-white rounded-md w-32 ml-2 hover:bg-blue hover:border-blue transition-all font-semibold'>Search</button>
            </form>

            <div className='px-10'>
                <table className="w-full border-2 border-blue">
                    <thead>
                        <tr className="bg-blue text-white text-left">
                            <th className="border border-blue px-4 py-2">Prescription ID</th>
                            <th className="border border-blue px-4 py-2">First Name</th>
                            <th className="border border-blue px-4 py-2">Last Name</th>
                            <th className="border border-blue px-4 py-2">Medication Name</th>
                            <th className="border border-blue px-4 py-2">Units</th>
                            <th className="border border-blue px-4 py-2">Created At</th>
                            <th className="border border-blue px-4 py-2">Assigned To</th>
                            <th className="border border-blue px-4 py-2">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {searchResults?.map((elem, index) => (
                            <tr key={index} className="bg-paleblue">
                                <td className="border-b-2 border-b-blue px-4 py-2 text-xs font-mono">{elem.PrescriptionID}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">{elem.firstName}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">{elem.lastName}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">{elem.MedicationNames}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">{elem.units}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">{formatDate(elem.createdAt)}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">{elem.status}</td>
                                <td className="border-b-2 border-b-blue px-4 py-2">
                                    <div className='flex text-sm gap-2 px-full'>
                                        {elem.filename && (
                                            <a href={`http://192.168.1.11:8000/uploads/${elem.filename}`} target="_blank" rel="noopener noreferrer">
                                                <button className='bg-[#1e56a0] hover:bg-[#154c8c] text-white transition-all rounded px-4 py-1 font-medium'>View Image</button>
                                            </a>
                                        )}
                                        <button onClick={() => handleDeleteConfirmation(elem._id)} className='bg-red-600 text-white hover:bg-red-700 transition-all rounded px-4 py-1'>Delete</button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {deleteId && (
                <div className="fixed top-0 left-0 flex items-center justify-center w-full h-full bg-dark-blue bg-opacity-90">
                    <div className="bg-white p-8 rounded-lg shadow-lg">
                        <p className="text-lg font-semibold mb-4">Are you sure you want to delete this Prescription?</p>
                        <div className="flex justify-center">
                            <button onClick={handleDeleteConfirmed} className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 mr-2">Delete</button>
                            <button onClick={handleCancelDelete} className="bg-slate-200 text-slate-900 px-4 py-2 rounded-md hover:bg-slate-300 ml-2">Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    </div>
  )
}

export default PrescriptionAssignTable