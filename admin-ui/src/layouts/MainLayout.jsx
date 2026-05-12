import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';

const MainLayout = ({ children, activePage, setActivePage }) => {
  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-[#020617] transition-colors duration-500">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      
      {/* Dynamic Background Elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary-500/5 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] -right-[5%] w-[30%] h-[30%] bg-indigo-500/5 blur-[100px] rounded-full" />
      </div>

      <main className="ml-72 flex-1 p-8 relative z-10">
        <div className="max-w-5xl mx-auto animate-in fade-in slide-in-from-top-4 duration-700">
          {children}
        </div>
      </main>
      
      {/* Floating Help / Feedback */}
      <button className="fixed bottom-8 right-8 w-14 h-14 bg-white dark:bg-surface-800 text-slate-900 dark:text-white rounded-2xl flex items-center justify-center shadow-2xl border border-slate-200 dark:border-slate-700 hover:shadow-primary-500/20 hover:-translate-y-1 transition-all group z-50">
        <div className="absolute inset-0 bg-primary-500/10 rounded-2xl scale-0 group-hover:scale-100 transition-transform duration-300" />
        <span className="text-xl font-bold relative z-10 group-hover:text-primary-500 transition-colors">?</span>
      </button>
    </div>
  );
};

export default MainLayout;
