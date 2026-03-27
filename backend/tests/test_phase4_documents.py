"""
Phase 4 Document Upload and Extraction Tests
Tests document upload, download, delete, and AI extraction endpoints
"""
import pytest
import requests
import os
import io
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "bugtest@staylet.com"
TEST_PASSWORD = "Test1234!"


class TestDocumentEndpoints:
    """Document upload, download, delete, and extraction tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        self.token = data["token"]
        self.user_id = data["user"]["id"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        # Get or create a test property
        props_response = self.session.get(f"{BASE_URL}/api/properties")
        assert props_response.status_code == 200
        props = props_response.json()
        
        if props:
            self.property_id = props[0]["id"]
        else:
            # Create a test property
            prop_response = self.session.post(f"{BASE_URL}/api/properties", json={
                "name": "TEST_Document_Property",
                "address": "123 Test Street",
                "postcode": "SW1A 1AA",
                "uk_nation": "England",
                "property_type": "apartment",
                "bedrooms": 2
            })
            assert prop_response.status_code == 200
            self.property_id = prop_response.json()["id"]
        
        yield
        
        # Cleanup: Delete test documents and properties created during tests
        # (Documents are cleaned up in individual tests)
    
    # ==================== Constants Endpoint Tests ====================
    
    def test_constants_include_file_upload_config(self):
        """Test that constants endpoint returns allowed_file_types and max_file_size"""
        response = self.session.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        
        data = response.json()
        assert "allowed_file_types" in data, "allowed_file_types missing from constants"
        assert "max_file_size" in data, "max_file_size missing from constants"
        
        # Verify allowed types
        allowed_types = data["allowed_file_types"]
        assert "application/pdf" in allowed_types
        assert "image/png" in allowed_types
        assert "image/jpeg" in allowed_types
        
        # Verify max file size is 10MB
        assert data["max_file_size"] == 10 * 1024 * 1024
        print("PASS: Constants endpoint returns file upload configuration")
    
    # ==================== Document Upload Tests ====================
    
    def test_upload_pdf_document(self):
        """Test uploading a PDF document"""
        # Create a simple PDF-like file (just for testing the endpoint accepts PDF mime type)
        pdf_content = b"%PDF-1.4 test content"
        files = {
            'file': ('test_document.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        # Remove Content-Type header for multipart upload
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["original_filename"] == "test_document.pdf"
        assert data["file_type"] == "application/pdf"
        assert data["file_size"] > 0
        
        # Cleanup
        doc_id = data["id"]
        delete_response = requests.delete(
            f"{BASE_URL}/api/documents/{doc_id}",
            headers=headers
        )
        assert delete_response.status_code == 200
        
        print("PASS: PDF document upload works correctly")
    
    def test_upload_png_image(self):
        """Test uploading a PNG image"""
        # Create a minimal PNG file
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {
            'file': ('test_image.png', io.BytesIO(png_content), 'image/png')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert data["original_filename"] == "test_image.png"
        assert data["file_type"] == "image/png"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/documents/{data['id']}", headers=headers)
        
        print("PASS: PNG image upload works correctly")
    
    def test_upload_jpg_image(self):
        """Test uploading a JPG image"""
        # Create a minimal JPEG file
        jpg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9teletext\xff\xd9'
        files = {
            'file': ('test_image.jpg', io.BytesIO(jpg_content), 'image/jpeg')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert data["original_filename"] == "test_image.jpg"
        assert data["file_type"] == "image/jpeg"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/documents/{data['id']}", headers=headers)
        
        print("PASS: JPG image upload works correctly")
    
    def test_upload_invalid_file_type_rejected(self):
        """Test that invalid file types are rejected"""
        # Try to upload a text file
        txt_content = b"This is a text file"
        files = {
            'file': ('test.txt', io.BytesIO(txt_content), 'text/plain')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "not allowed" in response.json().get("detail", "").lower()
        
        print("PASS: Invalid file type correctly rejected")
    
    def test_upload_with_compliance_record_link(self):
        """Test uploading a document linked to a compliance record"""
        # First create a compliance record
        record_response = self.session.post(f"{BASE_URL}/api/compliance-records", json={
            "property_id": self.property_id,
            "title": "TEST_Gas Safety Certificate",
            "category": "gas_safety",
            "expiry_date": "2026-12-31"
        })
        assert record_response.status_code == 200
        record_id = record_response.json()["id"]
        
        # Upload document with compliance_record_id
        pdf_content = b"%PDF-1.4 gas safety cert"
        files = {
            'file': ('gas_safety.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        data = {
            'compliance_record_id': record_id
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        doc_data = response.json()
        assert doc_data["compliance_record_id"] == record_id
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/documents/{doc_data['id']}", headers=headers)
        self.session.delete(f"{BASE_URL}/api/compliance-records/{record_id}")
        
        print("PASS: Document upload with compliance record link works")
    
    # ==================== Upload and Extract Tests ====================
    
    def test_upload_and_extract_endpoint(self):
        """Test upload-and-extract endpoint returns document and extraction suggestions"""
        # Create a PDF with gas safety in the name
        pdf_content = b"%PDF-1.4 gas safety certificate content"
        files = {
            'file': ('gas_safety_certificate_2025.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload-and-extract",
            files=files,
            headers=headers,
            timeout=60  # AI extraction may take time
        )
        
        assert response.status_code == 200, f"Upload-and-extract failed: {response.text}"
        
        data = response.json()
        
        # Verify document is returned
        assert "document" in data
        assert data["document"]["original_filename"] == "gas_safety_certificate_2025.pdf"
        
        # Verify extraction result is returned
        assert "extraction" in data
        extraction = data["extraction"]
        
        # Extraction should have suggestions (even if empty or from filename)
        assert "suggestions" in extraction or "success" in extraction
        
        # Cleanup
        doc_id = data["document"]["id"]
        requests.delete(f"{BASE_URL}/api/documents/{doc_id}", headers=headers)
        
        print("PASS: Upload-and-extract endpoint returns document and extraction data")
    
    # ==================== Document Download Tests ====================
    
    def test_download_document(self):
        """Test downloading an uploaded document"""
        # Upload a document first
        pdf_content = b"%PDF-1.4 downloadable content"
        files = {
            'file': ('download_test.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        upload_response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # Download the document
        download_response = requests.get(
            f"{BASE_URL}/api/documents/{doc_id}/download",
            headers=headers
        )
        
        assert download_response.status_code == 200
        assert download_response.content == pdf_content
        assert "application/pdf" in download_response.headers.get("content-type", "")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/documents/{doc_id}", headers=headers)
        
        print("PASS: Document download works correctly")
    
    def test_download_nonexistent_document(self):
        """Test downloading a non-existent document returns 404"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/documents/nonexistent-id/download",
            headers=headers
        )
        
        assert response.status_code == 404
        print("PASS: Non-existent document download returns 404")
    
    # ==================== Document Delete Tests ====================
    
    def test_delete_document(self):
        """Test deleting a document removes it from database and disk"""
        # Upload a document first
        pdf_content = b"%PDF-1.4 to be deleted"
        files = {
            'file': ('delete_test.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        upload_response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # Delete the document
        delete_response = requests.delete(
            f"{BASE_URL}/api/documents/{doc_id}",
            headers=headers
        )
        
        assert delete_response.status_code == 200
        assert "deleted" in delete_response.json().get("message", "").lower()
        
        # Verify document is gone
        get_response = requests.get(
            f"{BASE_URL}/api/documents/{doc_id}",
            headers=headers
        )
        assert get_response.status_code == 404
        
        print("PASS: Document delete removes file from database")
    
    def test_delete_nonexistent_document(self):
        """Test deleting a non-existent document returns 404"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.delete(
            f"{BASE_URL}/api/documents/nonexistent-id",
            headers=headers
        )
        
        assert response.status_code == 404
        print("PASS: Non-existent document delete returns 404")
    
    # ==================== Link Document Tests ====================
    
    def test_link_document_to_compliance_record(self):
        """Test linking an uploaded document to a compliance record"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create a compliance record
        record_response = self.session.post(f"{BASE_URL}/api/compliance-records", json={
            "property_id": self.property_id,
            "title": "TEST_EICR Certificate",
            "category": "eicr",
            "expiry_date": "2030-12-31"
        })
        assert record_response.status_code == 200
        record_id = record_response.json()["id"]
        
        # Upload a document (not linked)
        pdf_content = b"%PDF-1.4 eicr cert"
        files = {
            'file': ('eicr.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # Link document to compliance record
        link_response = requests.put(
            f"{BASE_URL}/api/documents/{doc_id}/link",
            params={"compliance_record_id": record_id},
            headers=headers
        )
        
        assert link_response.status_code == 200
        assert "linked" in link_response.json().get("message", "").lower()
        
        # Verify link by getting compliance record documents
        docs_response = requests.get(
            f"{BASE_URL}/api/compliance-records/{record_id}/documents",
            headers=headers
        )
        assert docs_response.status_code == 200
        docs = docs_response.json()
        assert len(docs) >= 1
        assert any(d["id"] == doc_id for d in docs)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/documents/{doc_id}", headers=headers)
        self.session.delete(f"{BASE_URL}/api/compliance-records/{record_id}")
        
        print("PASS: Document linking to compliance record works")
    
    def test_link_document_to_nonexistent_record(self):
        """Test linking document to non-existent compliance record returns 404"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Upload a document
        pdf_content = b"%PDF-1.4 test"
        files = {
            'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # Try to link to non-existent record
        link_response = requests.put(
            f"{BASE_URL}/api/documents/{doc_id}/link",
            params={"compliance_record_id": "nonexistent-record-id"},
            headers=headers
        )
        
        assert link_response.status_code == 404
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/documents/{doc_id}", headers=headers)
        
        print("PASS: Linking to non-existent record returns 404")
    
    # ==================== Get Compliance Record Documents Tests ====================
    
    def test_get_compliance_record_documents(self):
        """Test getting all documents for a compliance record"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create a compliance record
        record_response = self.session.post(f"{BASE_URL}/api/compliance-records", json={
            "property_id": self.property_id,
            "title": "TEST_Insurance Policy",
            "category": "insurance"
        })
        assert record_response.status_code == 200
        record_id = record_response.json()["id"]
        
        # Upload two documents linked to the record
        doc_ids = []
        for i in range(2):
            pdf_content = f"%PDF-1.4 insurance doc {i}".encode()
            files = {
                'file': (f'insurance_{i}.pdf', io.BytesIO(pdf_content), 'application/pdf')
            }
            data = {'compliance_record_id': record_id}
            
            upload_response = requests.post(
                f"{BASE_URL}/api/documents/upload",
                files=files,
                data=data,
                headers=headers
            )
            assert upload_response.status_code == 200
            doc_ids.append(upload_response.json()["id"])
        
        # Get documents for the record
        docs_response = requests.get(
            f"{BASE_URL}/api/compliance-records/{record_id}/documents",
            headers=headers
        )
        
        assert docs_response.status_code == 200
        docs = docs_response.json()
        assert len(docs) == 2
        
        # Cleanup
        for doc_id in doc_ids:
            requests.delete(f"{BASE_URL}/api/documents/{doc_id}", headers=headers)
        self.session.delete(f"{BASE_URL}/api/compliance-records/{record_id}")
        
        print("PASS: Get compliance record documents works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
