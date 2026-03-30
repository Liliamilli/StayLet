      import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Home,
  Pencil,
  Plus,
  AlertCircle,
  Clock,
  CheckCircle2,
  FileX,
  Calendar,
  Trash2,
  Upload,
  FileText,
  Paperclip,
  Eye,
  Image as ImageIcon
} from 'lucide-react';
import PropertyModal from '../components/properties/PropertyModal';
import ComplianceRecordModal from '../components/compliance/ComplianceRecordModal';
import BulkComplianceModal from '../components/compliance/BulkComplianceModal';
import UploadDocumentModal from '../components/documents/UploadDocumentModal';
import DocumentPreviewModal from '../components/documents/DocumentPreviewModal';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const statusConfig = {
  compliant: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    icon: CheckCircle2,
    label: 'Compliant'
  },
  expiring_soon: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    icon: Clock,
    label: 'Due Soon'
  },
  overdue: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    icon: AlertCircle,
    label: 'Overdue'
  },
  missing: {
    bg: 'bg-slate-50',
    text: 'text-slate-600',
    border: 'border-slate-200',
    icon: FileX,
    label: 'Missing'
  }
};

const categoryLabels = {
  gas_safety: 'Gas Safety Certificate',
  eicr: 'EICR',
  epc: 'EPC',
  insurance: 'Insurance',
  fire_risk_assessment: 'Fire Risk Assessment',
  pat_testing: 'PAT Testing',
  legionella: 'Legionella Risk Assessment',
  smoke_co_alarms: 'Smoke / CO Alarms',
  licence: 'Licence',
  custom: 'Custom'
};

function Compliance
