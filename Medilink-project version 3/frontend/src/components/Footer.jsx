import React from 'react'
import { FaFacebook, FaInstagram, FaTwitter } from 'react-icons/fa'

export default function () {
  return (
<div>
    <footer className="flex flex-col items-center bg-zinc-50 text-center text-surface dark:bg-dark-blue dark:text-white lg:text-left">
        <div className="container max-w-7xl py-10 px-6 md:px-8">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div className="">
                    <h5 className="mb-2 font-bold">About</h5>
                    <ul className="mb-0 list-none">
                        <li>
                            <a href="#!">Terms and Conditions</a>
                        </li>
                    </ul>
                </div>
                <div className="">
                    <h5 className="mb-2 font-bold">Customer Service</h5>
                    <ul className="mb-6 list-none">
                        <li>
                            <a href="#!">Contact Us</a>
                        </li>
                    </ul>
                    <h5 className="mb-2 font-bold">Phone</h5>
                    <p className="mb-6 list-none">03011061902</p>
                    <h5 className="mb-2 font-bold">Email</h5>
                    <p className="mb-0 list-none">aamish646@gmail.com</p>
                </div>
                <div className="">
                    <h5 className="mb-2 font-bold">MEDILINK</h5>
                    <p className="mb-6 list-none">IT department <br/> Quaid-e-Azam University.</p>
                </div>
                <div className="flex flex-col items-center lg:items-start">
                    <div className='flex gap-2 mb-2 place-items-center justify-center lg:justify-start'>
                        <FaInstagram className='text-lg'/> 
                        <a href='#!' className="mb-0 list-none">Instagram</a>
                    </div>
                    <div className='flex gap-2 mb-2 place-items-center justify-center lg:justify-start'>
                        <FaFacebook className='text-lg'/> 
                        <a href='#!' className="mb-0 list-none">Facebook</a>
                    </div>
                    <h5 className="mb-2 font-bold mt-2">Rohail & Co Limited</h5>
                    <p className="mb-6 list-none">Delivery all across Pakistan.</p>
                </div>
            </div>
        </div>
        <div className="w-full  
           bg-gradient-to-r from-purple-600 to-pink-600  p-4 text-center">Medilink Pharmacy System : All Rights Reserved.</div>
    </footer>
</div>
  )
}
