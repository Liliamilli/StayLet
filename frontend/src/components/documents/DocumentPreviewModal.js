import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import axios from 'axios';
import { 
    X, 
    Download, 
    ChevronLeft, 
    ChevronRight,
    FileText,
    Loader2,
    ZoomIn,
    ZoomOut,
    RotateCw
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function DocumentPreviewModal({ isOpen, onClose, document, documents = [], onNavigate }) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [zoom, setZoom] = useState(1);
    const [rotation, setRotation] = useState(0);

    const isImage = document?.file_type?.startsWith('image/');
    const isPdf = document?.file_type === 'application/pdf';
    
    // Find current index in documents array for navigation
    const currentIndex = documents.findIndex(d => d.id === document?.id);
    const hasPrev = currentIndex > 0;
    const hasNext = currentIndex < documents.length - 1;

    useEffect(() => {
        if (isOpen && document) {
            loadPreview();
        }
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [isOpen, document?.id]);

    const loadPreview = async () => {
        setLoading(true);
        setError(null);
        setZoom(1);
        setRotation(0);
        
        try {
            const response = await axios.get(
                `${API_URL}/api/documents/${document.id}/download`,
                { responseType: 'blob' }
            );
            
            const url = URL.createObjectURL(response.data);
            setPreviewUrl(url);
        } catch (err) {
            console.error('Failed to load preview:', err);
            setError('Failed to load document preview');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        try {
            const response = await axios.get(
                `${API_URL}/api/documents/${document.id}/download`,
                { responseType: 'blob' }
            );
            
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

    const handlePrev = () => {
        if (hasPrev && onNavigate) {
            onNavigate(documents[currentIndex - 1]);
        }
    };

    const handleNext = () => {
        if (hasNext && onNavigate) {
            onNavigate(documents[currentIndex + 1]);
        }
    };

    const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.25, 3));
    const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.25, 0.5));
    const handleRotate = () => setRotation(prev => (prev + 90) % 360);

    if (!document) return null;

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl max-h-[90vh] p-0 overflow-hidden" data-testid="document-preview-modal">
                {/* Accessible title for screen readers */}
                <DialogTitle className="sr-only">
                    Document Preview: {document?.original_filename}
                </DialogTitle>
                
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-3 border-b bg-slate-50">
                    <div className="flex items-center gap-3 min-w-0">
                        <FileText className="w-5 h-5 text-slate-400 flex-shrink-0" />
                        <span className="font-medium text-slate-900 truncate" title={document.original_filename}>
                            {document.original_filename}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {isImage && (
                            <>
                                <button
                                    onClick={handleZoomOut}
                                    className="p-1.5 hover:bg-slate-200 rounded"
                                    title="Zoom out"
                                >
                                    <ZoomOut className="w-4 h-4 text-slate-600" />
                                </button>
                                <span className="text-sm text-slate-500 w-12 text-center">{Math.round(zoom * 100)}%</span>
                                <button
                                    onClick={handleZoomIn}
                                    className="p-1.5 hover:bg-slate-200 rounded"
                                    title="Zoom in"
                                >
                                    <ZoomIn className="w-4 h-4 text-slate-600" />
                                </button>
                                <button
                                    onClick={handleRotate}
                                    className="p-1.5 hover:bg-slate-200 rounded"
                                    title="Rotate"
                                >
                                    <RotateCw className="w-4 h-4 text-slate-600" />
                                </button>
                                <div className="w-px h-5 bg-slate-300 mx-1" />
                            </>
                        )}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleDownload}
                            className="h-8"
                        >
                            <Download className="w-4 h-4 mr-1" />
                            Download
                        </Button>
                    </div>
                </div>

                {/* Preview Content */}
                <div className="relative flex-1 bg-slate-900 min-h-[400px] max-h-[calc(90vh-120px)] overflow-auto flex items-center justify-center">
                    {loading && (
                        <div className="flex flex-col items-center gap-3 text-slate-400">
                            <Loader2 className="w-8 h-8 animate-spin" />
                            <span>Loading preview...</span>
                        </div>
                    )}
                    
                    {error && (
                        <div className="flex flex-col items-center gap-3 text-slate-400">
                            <FileText className="w-12 h-12" />
                            <span>{error}</span>
                            <Button variant="outline" size="sm" onClick={handleDownload}>
                                Download instead
                            </Button>
                        </div>
                    )}
                    
                    {!loading && !error && previewUrl && (
                        <>
                            {isImage && (
                                <img
                                    src={previewUrl}
                                    alt={document.original_filename}
                                    className="max-w-full max-h-full object-contain transition-transform duration-200"
                                    style={{ 
                                        transform: `scale(${zoom}) rotate(${rotation}deg)`,
                                        transformOrigin: 'center center'
                                    }}
                                    data-testid="preview-image"
                                />
                            )}
                            
                            {isPdf && (
                                <iframe
                                    src={previewUrl}
                                    title={document.original_filename}
                                    className="w-full h-full min-h-[500px] bg-white"
                                    data-testid="preview-pdf"
                                />
                            )}
                            
                            {!isImage && !isPdf && (
                                <div className="flex flex-col items-center gap-3 text-slate-400">
                                    <FileText className="w-12 h-12" />
                                    <span>Preview not available for this file type</span>
                                    <Button variant="outline" size="sm" onClick={handleDownload}>
                                        Download to view
                                    </Button>
                                </div>
                            )}
                        </>
                    )}

                    {/* Navigation arrows */}
                    {documents.length > 1 && (
                        <>
                            {hasPrev && (
                                <button
                                    onClick={handlePrev}
                                    className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
                                    data-testid="prev-document-btn"
                                >
                                    <ChevronLeft className="w-6 h-6" />
                                </button>
                            )}
                            {hasNext && (
                                <button
                                    onClick={handleNext}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
                                    data-testid="next-document-btn"
                                >
                                    <ChevronRight className="w-6 h-6" />
                                </button>
                            )}
                        </>
                    )}
                </div>

                {/* Footer with document count */}
                {documents.length > 1 && (
                    <div className="px-4 py-2 border-t bg-slate-50 text-center text-sm text-slate-500">
                        {currentIndex + 1} of {documents.length}
                    </div>
                )}
            </DialogContent>
        </Dialog>
    );
}
