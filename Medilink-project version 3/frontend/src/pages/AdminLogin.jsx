import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NavigationBar from '../components/NavigationBar';
import Footer from '../components/Footer';
import { FaLock, FaUserShield, FaEye, FaEyeSlash } from 'react-icons/fa';
import toast, { Toaster } from 'react-hot-toast';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setLoading(true);

    setTimeout(() => {
      const cleanEmail = email.trim().toLowerCase();
      const cleanPassword = password.trim().toLowerCase();

      const isAdminEmail = cleanEmail === 'admin';
      const isAdminPassword = cleanPassword === 'admin';

      if (isAdminEmail && isAdminPassword) {
        localStorage.setItem('adminAuthenticated', 'true');
        toast.success('Admin Authenticated Successfully!');
        setLoading(false);
        navigate('/admin-dashboard');
      } else {
        toast.error('Invalid Admin Credentials! Use username "admin" and password "admin"');
        setLoading(false);
      }
    }, 1200);
  };

  return (
    <div className="bg-paleblue min-h-screen flex flex-col justify-between">
      <Toaster position="top-right" reverseOrder={false} />
      <NavigationBar />

      <div className="flex-1 flex items-center justify-center p-6 my-10">
        <div className="w-full max-w-md bg-white border border-light-blue rounded-3xl shadow-xl overflow-hidden transform transition-all duration-300 hover:shadow-2xl">
          { }
          <div className="bg-gradient-to-r from-purple-600 to-pink-500 p-8 text-center text-white relative">
            <div className="absolute top-0 right-0 left-0 bottom-0 bg-black opacity-10 pointer-events-none"></div>
            <div className="mx-auto bg-white/20 w-16 h-16 rounded-full flex items-center justify-center mb-3 backdrop-blur-sm shadow-inner">
              <FaUserShield className="text-white text-3xl" />
            </div>
            <h1 className="text-2xl font-bold tracking-wide">MediLink Admin Portal</h1>
            <p className="text-purple-100 text-sm mt-1">Authorized Personnel Only</p>
          </div>

          { }
          <form onSubmit={handleLogin} className="p-8 space-y-6">
            { }

            <div className="space-y-2">
              <label className="text-sm font-semibold text-blue block">Admin Username / Email</label>
              <div className="relative">
                <input
                  type="text"
                  className="w-full border border-gray-300 p-3 pl-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-blue block">Security Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}

                  className="w-full border border-gray-300 p-3 pl-4 pr-12 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-purple-600 transition-colors"
                >
                  {showPassword ? <FaEyeSlash size={18} /> : <FaEye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-500 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg hover:shadow-purple-500/30 hover:opacity-95 active:scale-[0.98] transition-all duration-200 disabled:opacity-75 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <FaLock className="text-sm" />
                  <span>Authenticate Admin</span>
                </>
              )}
            </button>
          </form>

          { }
          <div className="px-8 pb-8 text-center">
            <p className="text-xs text-gray-400">
              By logging in, you agree to comply with system security policies. All actions are logged.
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
