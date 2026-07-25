import { useNavigate } from 'react-router-dom';
import mainbanner from '../assets/Main-banner.png';
import NavigationBar from '../components/NavigationBar';
import img1 from '../assets/banner-1.png';
import img2 from '../assets/banner-2.png';
import Footer from '../components/Footer';

export default function Home() {
  const navigate = useNavigate(); 

  const handleClick = () => {
    navigate('/prescriptionform'); 
  };

  return (
    <div className="bg-paleblue">
      {}
      <div className="absolute w-full z-10 bg-transparent">
        <NavigationBar />
      </div>

      <div className="relative bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 md:from-transparent md:to-transparent min-h-[70vh] md:min-h-0 flex md:block">
        <img className="hidden md:block w-full h-screen object-cover" src={mainbanner} alt="main-banner" />
        
        {}
        <div className="relative md:absolute inset-0 max-w-7xl mx-auto p-6 pt-44 pb-12 md:pt-0 md:pb-0 md:mt-56 flex flex-col items-center md:items-start text-center md:text-left justify-start">
          <h1 className="max-w-xl text-3xl sm:text-4xl md:text-5xl leading-tight font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-orange-300">
            Search and Buy <br className="hidden sm:inline" /> from nearest Pharmacies
          </h1>
          <p className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-orange-300 mt-3 text-lg md:text-xl font-semibold">
            Buy prescribed drugs to better manage your health
          </p>
          
          {}
          <button
            onClick={handleClick} 
            type="button" 
            className="bg-gradient-to-r from-pink-500 to-orange-300 text-white rounded-md px-6 py-3.5 mt-8 hover:opacity-90 transition-all font-bold shadow-md cursor-pointer"
          >
            Upload Prescription
          </button>
          
        </div>
      </div>
      
      {}
      <div className="flex flex-col md:flex-row max-w-7xl mx-auto justify-between mt-14 mb-14 gap-5 px-4">
        <img src={img1} alt="Banner 1" className="object-cover w-full md:w-1/2 h-auto rounded-xl shadow-sm" />
        <img src={img2} alt="Banner 2" className="object-cover w-full md:w-1/2 h-auto rounded-xl shadow-sm" />
      </div>
      
      <Footer />
    </div>
  );
}