import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import SideBar from './components/SideBar';
import Home from "./pages/Home";
import AdminDashboard from './pages/AdminDashboard';
import InventoryUserPage from './pages/InventoryManagement/InventoryUserPageView';
import MedicineDetailsPage from './pages/InventoryManagement/MedicineDetailsPage';
import DeliveryManagement from './pages/DeliveryManagement/DeliveryManagement';

import SignIn from './pages/UserManagement/SignIn';
import SignUp from './pages/UserManagement/SignUp';
import Profile from './pages/UserManagement/Profile';
import UserTable from './pages/UserManagement/Usertable';
import UserManagement from './pages/UserManagement/UserManagement';
import PrivateRoute from './components/PrivateRoute';
import AdminPrivateRoute from './components/AdminPrivateRoute';
import ManagePharmacies from './pages/PharmacyManagement/ManagePharmacies';
import AdminLogin from './pages/AdminLogin';
import UserPaymentDetails from './pages/UserManagement/UserPaymentDetails';
import OrderHistory from './pages/UserManagement/OrderHistory';
import Prescriptionform from './pages/PrescriptionManagement/PrescriptionForm';
import PrescriptionAssignTable from './pages/PrescriptionManagement/PrescriptionAssignTable';
import AdminOrderManagement from './pages/UserManagement/AdminOrderManagement';

export default function App() {
  return (
    <Router>
      <Toaster position="top-right" reverseOrder={false} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path='/inventory-user' element={<InventoryUserPage />} />
        <Route path='/medicine-details/:id' element={<MedicineDetailsPage />} />
        <Route path='/delivery-management' element={<DeliveryManagement />} />

        { }
        <Route path="/admin-login" element={<AdminLogin />} />

        { }
        <Route element={<AdminPrivateRoute />}>
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          <Route path="/user-management" element={<UserManagement />} />
          <Route path="/user-table" element={<div className="flex"><SideBar /><div className="flex-1"><UserTable /></div></div>} />
          <Route path="/prescription-management" element={<PrescriptionAssignTable />} />
          <Route path="/manage-pharmacies" element={<ManagePharmacies />} />
          <Route path="/admin-orders" element={<AdminOrderManagement />} />
        </Route>

        <Route path='/sign-in' element={<SignIn />} />
        <Route path='/sign-up' element={<SignUp />} />
        <Route path='/user-payment' element={<UserPaymentDetails />} />
        <Route path='/order-history' element={<OrderHistory />} />
        <Route element={<PrivateRoute />}>
          <Route path='/profile' element={<Profile />} />
          <Route path='/prescriptionform' element={<Prescriptionform />} />
        </Route>

      </Routes>
    </Router>
  )
}