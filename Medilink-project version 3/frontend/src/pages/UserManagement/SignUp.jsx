import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';
import img01 from '../../assets/Sign-up-2.png';
import axios from 'axios'; 

export default function SignUp() {
  const [formData, setFormData] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      
      const res = await axios.post('http://192.168.1.11:8000/auth/register', {
        name: formData.username, 
        email: formData.email,
        password: formData.password,
        phonenumber: formData.phonenumber || "",
        address: formData.address || ""
      });

      if (res.data.status === "Success") {
        setLoading(false);
        setError(null);
        alert("Registration Successful! Please login.");
        navigate('/sign-in');
      } else {
        setLoading(false);
        setError(res.data.message || "Registration failed");
      }
    } catch (error) {
      setLoading(false);
      
      setError(error.response?.data?.details || "Server se rabta nahi ho saka");
    }
  };

  return (
    <div className='bg-paleblue'>
      <NavigationBar />
      <div className='p-3 w-auto mx-auto'>
        <div className="max-w-md mx-auto mt-1 mb-6 sm:mt-3 sm:mb-8">
          <h1 className='text-2xl text-center font-semibold my-2 sm:my-3 text-blue'>Sign Up</h1>
          <div className='p-4 sm:p-6 bg-paleblue mx-4 my-1 sm:mx-0 rounded-2xl border-2 border-light-blue shadow-sm'>
            <form onSubmit={handleSubmit} className='flex flex-col gap-2.5'>
              <input
                type='text'
                placeholder='username'
                className='border py-2 px-3 text-sm rounded-md focus:outline-none focus:ring-2 focus:ring-blue'
                id='username'
                required
                onChange={handleChange}
              />
              <input
                type='email'
                placeholder='email'
                className='border py-2 px-3 text-sm rounded-md focus:outline-none focus:ring-2 focus:ring-blue'
                id='email'
                required
                onChange={handleChange}
              />
              {}
              <input
                type='text'
                placeholder='phone number'
                className='border py-2 px-3 text-sm rounded-md focus:outline-none focus:ring-2 focus:ring-blue'
                id='phonenumber'
                onChange={handleChange}
              />
              <input
                type='text'
                placeholder='address'
                className='border py-2 px-3 text-sm rounded-md focus:outline-none focus:ring-2 focus:ring-blue'
                id='address'
                onChange={handleChange}
              />
              <input
                type='password'
                placeholder='password'
                className='border py-2 px-3 text-sm rounded-md focus:outline-none focus:ring-2 focus:ring-blue'
                id='password'
                required
                onChange={handleChange}
              />

              <button
                disabled={loading}
                className='bg-blue text-white py-2.5 px-3 rounded-md uppercase hover:opacity-95 disabled:opacity-80 transition-all font-bold text-sm'
              >
                {loading ? 'Processing...' : 'Sign Up'}
              </button>
            </form>
            {error && <p className='text-red-500 mt-3 text-center font-medium text-xs'>{error}</p>}
          </div>
          
          <div className='flex flex-col items-center mx-auto mt-2 mb-4 gap-1 text-sm'>
            <div className='flex gap-2 justify-center'>
              <p>Have an account?</p>
              <Link to={'/sign-in'}>
                <span className='text-light-blue font-bold'>Sign in</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}