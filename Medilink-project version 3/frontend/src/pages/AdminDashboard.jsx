import { BrowserRouter as Router } from 'react-router-dom';
import SideBar from '../components/SideBar';

export default function AdminDashboard() {
    return (
        <div className='flex'>
            <SideBar />
            <div className='flex-1 flex flex-col justify-center items-center'>
                <h1 className='text-5xl font-bold text-dark-blue'>Welcome to Admin Dashboard</h1>
            </div>
        </div>
    )
}
