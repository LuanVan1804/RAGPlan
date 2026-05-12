import UploadCard from '../components/UploadCard';
import { FileUp } from 'lucide-react';

const UploadPage = () => {
  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Thêm <span className="text-primary-500">Tài liệu</span>
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
            Tải lên tài liệu mới để bổ sung kiến thức cho hệ thống RAG.
          </p>
        </div>
        
        <div className="p-2 bg-primary-500/10 rounded-xl">
          <FileUp size={24} className="text-primary-500" />
        </div>
      </div>

      <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
        <UploadCard />
      </div>
    </div>
  );
};

export default UploadPage;
