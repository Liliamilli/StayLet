import { useState } from 'react';
import { Button } from '../ui/button';
import axios from 'axios';
import { 
    FileText, 
    Image as ImageIcon, 
    Download, 
    Trash2, 
    Eye,
    MoreVertical,
    ExternalLink
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-GB', { 
        day: 'numeric', 
        month: 'short', 
        year: 'numeric' 
    });
}

function DocumentCard({ document, onDelete, onPreview }) {
    const [menuOpen, setMenuOpen] = useState(false);
    const [deleting, setDeleting] = useState(false);
    
    const isImage = document.file_type?.startsWith('image/');
    const FileIcon = isImage ? ImageIcon : FileText;
    
    const handleDownload = async () => {
        try {
            const response = await axios.get(
                `${API_URL}/api/documents/${document.id}/download`,
                { responseType: 'blob' }
            );
            
            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = window.document.createElement('a');
            link.href = url;
            link.setAttribute('download', document.original_filename);
            window.document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
        }
    };
    
    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this document?')) return;
        
        setDeleting(true);
        try {
            await axios.delete(`${API_URL}/api/documents/${document.id}`);
            onDelete(document.id);
        } catch (error) {
            console.error('Delete failed:', error);
        } finally {
            setDeleting(false);
            setMenuOpen(false);
        }
    };
    
    return (
        <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:border-slate-300 transition-colors group">
            <div className={`p-2 rounded-lg ${isImage ? 'bg-purple-100' : 'bg-blue-100'}`}>
                <FileIcon className={`w-5 h-5 ${isImage ? 'text-purple-600' : 'text-blue-600'}`} />
            </div>
            
            <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 truncate" title={document.original_filename}>
                    {document.original_filename}
                </p>
                <p className="text-xs text-slate-500">
                    {formatFileSize(document.file_size)} • {formatDate(document.uploaded_at)}
                </p>
            </div>
            
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {isImage && onPreview && (
                    <button
                        onClick={() => onPreview(document)}
                        className="p-1.5 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600"
                        title="Preview"
                    >
                        <Eye className="w-4 h-4" />
                    </button>
                )}
                <button
                    onClick={handleDownload}
                    className="p-1.5 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600"
                    title="Download"
                >
                    <Download className="w-4 h-4" />
                </button>
                <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="p-1.5 hover:bg-red-50 rounded text-slate-400 hover:text-red-600"
                    title="Delete"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}

export default function DocumentList({ documents = [], onDelete, onPreview, emptyMessage = "No documents uploaded" }) {
    if (documents.length === 0) {
        return (
            <div className="text-center py-6 text-sm text-slate-500">
                <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                {emptyMessage}
            </div>
        );
    }
    
    return (
        <div className="space-y-2">
            {documents.map((doc) => (
                <DocumentCard 
                    key={doc.id} 
                    document={doc} 
                    onDelete={onDelete}
                    onPreview={onPreview}
                />
            ))}
        </div>
    );
}
