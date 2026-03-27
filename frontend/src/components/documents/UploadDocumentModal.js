import { useState } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import DocumentUpload from './DocumentUpload';
import ExtractionReview from './ExtractionReview';
import { 
    Upload, 
    ArrowLeft,
    Sparkles
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function UploadDocumentModal({ 
    isOpen, 
    onClose, 
    propertyId,
    complianceRecordId = null,
    onDocumentUploaded,
    onRecordCreated,
    mode = 'upload' // 'upload' = just upload file, 'extract' = upload and create record
}) {
    const [step, setStep] = useState('upload'); // 'upload', 'review'
    const [isExtracting, setIsExtracting] = useState(false);
    const [uploadedDocument, setUploadedDocument] = useState(null);
    const [extractionResult, setExtractionResult] = useState(null);
    const [error, setError] = useState(null);
    
    const resetState = () => {
        setStep('upload');
        setIsExtracting(false);
        setUploadedDocument(null);
        setExtractionResult(null);
        setError(null);
    };
    
    const handleClose = () => {
        resetState();
        onClose();
    };
    
    const handleUploadOnly = async (file) => {
        setError(null);
        setIsExtracting(true);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            if (complianceRecordId) {
                formData.append('compliance_record_id', complianceRecordId);
            }
            
            const response = await axios.post(`${API_URL}/api/documents/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            if (onDocumentUploaded) {
                onDocumentUploaded(response.data);
            }
            handleClose();
        } catch (error) {
            console.error('Upload failed:', error);
            setError(error.response?.data?.detail || 'Upload failed. Please try again.');
        } finally {
            setIsExtracting(false);
        }
    };
    
    const handleUploadWithExtract = async (file) => {
        setError(null);
        setIsExtracting(true);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await axios.post(`${API_URL}/api/documents/upload-and-extract`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            setUploadedDocument(response.data.document);
            setExtractionResult(response.data.extraction);
            setStep('review');
        } catch (error) {
            console.error('Upload/extract failed:', error);
            setError(error.response?.data?.detail || 'Upload failed. Please try again.');
        } finally {
            setIsExtracting(false);
        }
    };
    
    const handleConfirmRecord = async (formData, documentId) => {
        try {
            // Create compliance record
            const recordData = {
                property_id: propertyId,
                title: formData.title,
                category: formData.category,
                issue_date: formData.issue_date || null,
                expiry_date: formData.expiry_date || null,
                notes: formData.notes || null,
                reminder_preference: formData.expiry_date ? '30_days' : 'none'
            };
            
            const recordResponse = await axios.post(`${API_URL}/api/compliance-records`, recordData);
            
            // Link document to the new record
            if (documentId) {
                await axios.put(`${API_URL}/api/documents/${documentId}/link`, null, {
                    params: { compliance_record_id: recordResponse.data.id }
                });
            }
            
            if (onRecordCreated) {
                onRecordCreated(recordResponse.data);
            }
            
            handleClose();
        } catch (error) {
            console.error('Failed to create record:', error);
            throw error;
        }
    };
    
    const handleBack = () => {
        // If we have an uploaded document but user goes back, we should delete it
        if (uploadedDocument) {
            axios.delete(`${API_URL}/api/documents/${uploadedDocument.id}`).catch(console.error);
        }
        resetState();
    };
    
    return (
        <Dialog open={isOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    {step === 'upload' ? (
                        <>
                            <DialogTitle className="flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                {mode === 'extract' ? (
                                    <>
                                        <Sparkles className="w-5 h-5 text-blue-600" />
                                        Upload Document
                                    </>
                                ) : (
                                    <>
                                        <Upload className="w-5 h-5 text-blue-600" />
                                        Attach Document
                                    </>
                                )}
                            </DialogTitle>
                            <DialogDescription>
                                {mode === 'extract' 
                                    ? "Upload a certificate and we'll try to extract the dates automatically."
                                    : "Upload a PDF or image file to attach to this compliance record."}
                            </DialogDescription>
                        </>
                    ) : (
                        <>
                            <DialogTitle style={{ fontFamily: 'Outfit, sans-serif' }}>
                                <button 
                                    onClick={handleBack}
                                    className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-2"
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                    Back
                                </button>
                                Review & Confirm
                            </DialogTitle>
                            <DialogDescription>
                                Please review the extracted information before saving.
                            </DialogDescription>
                        </>
                    )}
                </DialogHeader>
                
                <div className="py-4">
                    {step === 'upload' && (
                        <div className="space-y-4">
                            <DocumentUpload
                                onUpload={mode === 'upload' ? handleUploadOnly : null}
                                onUploadWithExtract={mode === 'extract' ? handleUploadWithExtract : null}
                                isExtracting={isExtracting}
                            />
                            
                            {error && (
                                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                                    {error}
                                </div>
                            )}
                            
                            {mode === 'extract' && (
                                <div className="text-xs text-slate-500 text-center">
                                    <Sparkles className="w-3 h-3 inline mr-1" />
                                    AI-powered extraction • Results may vary • Always verify dates
                                </div>
                            )}
                        </div>
                    )}
                    
                    {step === 'review' && (
                        <ExtractionReview
                            extraction={extractionResult}
                            document={uploadedDocument}
                            onConfirm={handleConfirmRecord}
                            onCancel={handleBack}
                            isCreatingNew={true}
                        />
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
