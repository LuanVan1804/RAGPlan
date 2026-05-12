import React, { useState } from 'react';
import MainLayout from './layouts/MainLayout';
import DocumentsPage from './pages/DocumentsPage';

function App() {
  const [activePage, setActivePage] = useState('documents');

  return (
    <MainLayout activePage={activePage} setActivePage={setActivePage}>
      {activePage === 'documents' && <DocumentsPage />}
    </MainLayout>
  );
}

export default App;
