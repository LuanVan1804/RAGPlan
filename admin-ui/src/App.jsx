import { useState } from 'react';
import MainLayout from './layouts/MainLayout';
import DocumentsPage from './pages/DocumentsPage';
import UploadPage from './pages/UploadPage';

function App() {
  const [activePage, setActivePage] = useState('documents');

  return (
    <MainLayout activePage={activePage} setActivePage={setActivePage}>
      {activePage === 'documents' && <DocumentsPage />}
      {activePage === 'add-documents' && <UploadPage />}
    </MainLayout>
  );
}

export default App;
