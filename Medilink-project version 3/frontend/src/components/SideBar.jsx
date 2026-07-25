import React, { useState } from 'react';
import { Link,useNavigate} from 'react-router-dom';
import logo from '../assets/logo1.png';
import { Toaster } from 'react-hot-toast';
import { FaRegUser, FaBoxesStacked, FaStore, FaBars, FaXmark } from 'react-icons/fa6';
import { FiTruck } from 'react-icons/fi';
import { MdOutlineInventory } from 'react-icons/md';
import { MdExitToApp} from 'react-icons/md';
import { TbDiscount2 } from 'react-icons/tb';
import { LiaFilePrescriptionSolid } from 'react-icons/lia';
import { GrUserWorker } from 'react-icons/gr';
import { BiDollarCircle } from 'react-icons/bi';
import { BsChevronDown } from 'react-icons/bs';
import { RiDashboardFill } from 'react-icons/ri';
import { useDispatch } from 'react-redux';
import {
  signOutUserStart,
  deleteUserSuccess,
  deleteUserFailure
} from '../redux/user/userSlice';
 
export default function SideBar() {
  const [isOpen, setIsOpen] = useState(false);
  const [subMenuOpen, setSubMenuOpen] = useState({});
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      localStorage.removeItem('adminAuthenticated');
      dispatch(signOutUserStart());
      const res = await fetch('./api/auth/signoutEmp');
      const data = await res.json();
      console.log(data);
      if (data.success === false) {
        dispatch(deleteUserFailure(data.message));
        return;
      } 
      dispatch(deleteUserSuccess(data)); 
      navigate('/');
    } catch (error) {
      
      localStorage.removeItem('adminAuthenticated');
      dispatch(deleteUserSuccess(null));
      navigate('/');
    }
  };
  
  const Menus = [
    { title: "User Management", icon: <FaRegUser />, path: '/user-management', submenu: false },
    { title: "Prescription Management", icon: <LiaFilePrescriptionSolid />, path: '/prescription-management', submenu: false },
    { title: "Manage Pharmacies", icon: <FaStore />, path: '/manage-pharmacies', submenu: false },
    { title: "Order Management", icon: <BiDollarCircle />, path: '/admin-orders', submenu: false }
  ];

  const toggleSubMenu = (index) => {
    setSubMenuOpen((prevState) => ({
      ...prevState,
      [index]: !prevState[index],
    }));
  };

  return (
    <>
      <div className="lg:hidden p-4">
        <button onClick={() => setIsOpen(!isOpen)} className="text-2xl">
          {isOpen ? <FaXmark /> : <FaBars />}
        </button>
      </div>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={() => setIsOpen(false)} />
      )}

      <div className={`fixed lg:relative inset-y-0 left-0 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition duration-200 ease-in-out z-50 bg-dark-blue min-h-screen p-5 pt-8 min-w-max`}>
          <Link to='/'>
              <img src={logo} alt="logo" className='mx-auto cursor-pointer' style={{ width: '100px', height: 'auto' }} />
          </Link>
        <ul className='pt-10'>
          {Menus.map((menu, index) => (
            <React.Fragment key={index}>
              <li 
                onClick={() => { navigate(menu.path); setIsOpen(false); }}
                className={`text-white text-sm flex items-center gap-x-6 cursor-pointer p-2 hover:bg-light-white rounded-md ${menu.spacing ? "mt-9" : "mt-2"}`}
              >
                <span className='text-2xl block float-left'>{menu.icon ? menu.icon : <RiDashboardFill />}</span>
                <span className='text-base font-medium flex-1'>{menu.title}</span>
                {menu.submenu && (
                  <BsChevronDown 
                    className={`${subMenuOpen[index] ? 'rotate-180' : ''}`} 
                    onClick={(e) => { e.stopPropagation(); toggleSubMenu(index); }} 
                  />
                )}
              </li>
              {menu.submenu && subMenuOpen[index] && (
                <ul>
                  {menu.submenuItems.map((submenuItem, subIndex) => (
                    <li 
                      key={subIndex} 
                      onClick={() => { navigate(submenuItem.path); setIsOpen(false); }}
                      className="text-paleblue text-sm flex items-center gap-x-4 cursor-pointer p-2 px-5 hover:bg-light-white rounded-md"
                    >
                      <span className="flex-1">{submenuItem.title}</span>
                    </li>
                  ))}
                </ul>
              )}
            </React.Fragment>
          ))}
        </ul>
        <div className="exit p-3 pt-20 h-3">
          <button onClick={() => { handleSignOut(); setIsOpen(false); }} className='flex items-center text-white text-sm gap-x-2 p-2 px-2 bg-light-blue hover:bg-red-700 rounded-md w-full'>
            <MdExitToApp className='text-2xl pl-0' />
            Sign out
          </button>
        </div>
      </div>
      <Toaster />
    </>
  )
}
