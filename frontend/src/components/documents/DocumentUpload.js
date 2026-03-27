import { useState, useRef } from 'react';
import { Button } from '../ui/button';
import { 
    Upload, 
    FileText, 
    Image as ImageIcon, 
    X, 
    Loader2,
    AlertCircle
} from 'lucide-react';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];

export default function DocumentUpload({ onUpload, onUploadWithExtract, isExtracting = false, disabled = false }) {
    const [dragOver, setDragOver] = useState(false);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const validateFile = (file) => {
        if (!ALLOWED_TYPES.includes(file.type)) {
            return 'File type not allowed. Please upload a PDF, PNG, or JPG file.';
        }
        if (file.size > MAX_FILE_SIZE) {
            return 'File too large. Maximum size is 10MB.';
        }
        return null;
    };

    const handleFile = async (file, withExtract = false) => {
        const validationError = validateFile(file);
        if (validationError) {
            setError(validationError);
            return;
        }
        
        setError(null);
        
        if (withExtract && onUploadWithExtract) {
            await onUploadWithExtract(file);
        } else if (onUpload) {
            await onUpload(file);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file, !!onUploadWithExtract);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setDragOver(false);
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file, !!onUploadWithExtract);
        }
        // Reset input
        e.target.value = '';
    };

    const getFileIcon = (type) => {
        if (type?.startsWith('image/')) {
            return <ImageIcon className="w-8 h-8 text-blue-500" />;
        }
        return <FileText className="w-8 h-8 text-blue-500" />;
    };

    return (
        <div className="w-full">
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`
                    relative border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer
                    ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}
                    ${disabled || isExtracting ? 'opacity-50 cursor-not-allowed' : ''}
                `}
                onClick={() => !disabled && !isExtracting && fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleFileSelect}
                    className="hidden"
                    disabled={disabled || isExtracting}
                />
                
                {isExtracting ? (
                    <div className="flex flex-col items-center gap-3">
                        <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
                        <div>
                            <p className="font-medium text-slate-900">Analyzing document...</p>
                            <p className="text-sm text-slate-500 mt-1">Extracting dates and document type</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-3">
                        <div className="p-3 bg-blue-100 rounded-full">
                            <Upload className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="font-medium text-slate-900">
                                Drop your document here, or <span className="text-blue-600">browse</span>
                            </p>
                            <p className="text-sm text-slate-500 mt-1">
                                PDF, PNG, or JPG up to 10MB
                            </p>
                        </div>
                    </div>
                )}
            </div>
            
            {error && (
                <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                </div>
            )}
        </div>
    );
}
