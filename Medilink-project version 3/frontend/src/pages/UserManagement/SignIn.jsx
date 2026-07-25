import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  signInStart,
  signInSuccess,
  signInFailure,
} from '../../redux/user/userSlice';
import NavigationBar from '../../components/NavigationBar';
import Footer from '../../components/Footer';
import img01 from '../../assets/login-rafiki.png';
import axios from 'axios'; 

export default function SignIn() {
  const [formData, setFormData] = useState({});
  const { loading, error } = useSelector((state) => state.user);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      dispatch(signInStart());

      const res = await axios.post('http://192.168.1.11:8000/auth/login', {
        email: formData.email,
        password: formData.password,
      });

      const data = res.data;

      if (data.status === "Error") {
        dispatch(signInFailure(data.message));
        return;
      }

      dispatch(signInSuccess(data.user));
      navigate('/');
      
    } catch (error) {
      
      const errorMessage = error.response?.data?.message || "Server connection failed";
      dispatch(signInFailure(errorMessage));
    }
  };

  return (
    <div className='bg-paleblue'>
      <NavigationBar />
      <div className='p-3 w-auto mx-auto'>
        <div className="max-w-md mx-auto mt-4 mb-10 sm:mt-6 sm:mb-12">
          <h1 className='text-3xl text-center font-semibold mt-2 mb-4 sm:mt-3 sm:mb-5 text-blue'>Sign In</h1>
          <div className='p-6 sm:p-10 bg-paleblue mx-4 my-2 sm:mx-0 rounded-3xl border-2 border-light-blue shadow-sm'>
            <form onSubmit={handleSubmit} className='flex flex-col gap-4'>
              <input
                type='email'
                placeholder='email'
                className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                id='email'
                required
                onChange={handleChange}
              />
              <input
                type='password'
                placeholder='password'
                className='border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue'
                id='password'
                required
                onChange={handleChange}
              />

              <button
                disabled={loading}
                className='bg-blue text-white p-3 rounded-lg uppercase hover:opacity-95 disabled:opacity-80 font-bold transition-all'
              >
                {loading ? 'Authenticating...' : 'Sign In'}
              </button>
            </form>
          </div>

          <div className='flex flex-col items-center mx-auto mt-4 mb-8'>
            <div className='flex gap-2 justify-center'>
              <p>Don't have an account?</p>
              <Link to={'/sign-up'}>
                <span className='text-light-blue font-bold'>Sign up</span>
              </Link>
            </div>
            {error && <p className='text-red-500 mt-5 font-medium text-center'>{error}</p>}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}