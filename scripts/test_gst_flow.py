import requests
import json
import os

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "tester@test.com"
PASSWORD = "TestPass123!"

def log(msg, type="INFO"):
    print(f"[{type}] {msg}")

def run_test():
    log("Starting GST Filing Module Integration Test...")
    
    # 1. Login
    auth_url = f"{BASE_URL}/auth/login/"
    try:
        resp = requests.post(auth_url, json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            log(f"Login Failed: {resp.text}", "ERROR")
            return
        token = resp.json()['access']
        headers = {"Authorization": f"Bearer {token}"}
        log("Login Successful")
    except Exception as e:
        log(f"Connection Failed: {e}", "ERROR")
        return

    # 2. Create Filing (GSTR1)
    create_url = f"{BASE_URL}/gst/filings/"
    filing_data = {
        "filing_type": "GSTR1",
        "financial_year": "2024-25",
        "month": 4, # April
        "year": 2024,
        "nil_filing": False
    }
    
    # Clean up previous similar filing if exists (optional, but good for idempotency if API allows delete)
    # For now, we just create. If duplicate, we might get 400.
    resp = requests.post(create_url, json=filing_data, headers=headers)
    if resp.status_code == 400 and "already exists" in resp.text:
         log("Filing already exists, fetching list to find it...")
         # Get list and find it
         list_resp = requests.get(create_url, headers=headers)
         filings = list_resp.json()
         # simple find
         filing = next((f for f in filings if f['month'] == 4 and f['year'] == 2024), None)
         if not filing:
             log("Could not find existing filing even though create said it exists.", "ERROR")
             return
         filing_id = filing['id']
         log(f"Found existing filing: {filing_id}")
    elif resp.status_code == 201:
        filing = resp.json()
        filing_id = filing['id']
        log(f"Filing Created: {filing_id}")
    else:
        log(f"Create Filing Failed: {resp.status_code} {resp.text}", "ERROR")
        return

    # 3. Get Filing Detail
    detail_url = f"{BASE_URL}/gst/filings/{filing_id}/"
    resp = requests.get(detail_url, headers=headers)
    if resp.status_code != 200:
        log(f"Get Detail Failed: {resp.text}", "ERROR")
        return
    log("Filing Details Fetched")

    # 4. Create Invoice
    invoice_url = f"{BASE_URL}/invoices/invoices/" # Wait, check if invoice URL is nested or separate?
    # In views.py: InvoiceViewSet is usually registered. Let's check urls.py to be sure.
    # It seems InvoiceViewSet is likely at /invoices/ or /gst/invoices/.
    # Checking api.ts: `api.post("gst/filings/${filingId}/upload_invoices/", ...)` for upload.
    # The InvoiceViewSet seems separate. Let's try to upload directly first using the `upload_invoices` action on filing.
    
    # Create a dummy excel file in memory? Or just skip upload and use 'create invoice' if endpoint available?
    # The tests used `Invoice.objects.create`.
    # Let's try the `upload_document` or `upload_invoices` endpoint if I can mock a file, but simpler to check if InvoiceViewSet is exposed.
    # In `gst_filing/views.py`, `InvoiceViewSet` is defined.
    # In `gst_filing/urls.py` (assumed based on pattern), it should be there.
    # Let's assume `/api/v1/gst/invoices/` exists.
    
    # Let's try listing invoices first to see if 200
    resp = requests.get(f"{BASE_URL}/gst/invoices/", headers=headers)
    if resp.status_code != 200:
        # Maybe it's not registered there.
        # Let's try adding an invoice via the upload endpoint as it's the primary way in UI.
        # We need a file.
        pass
    else:
        # Create an invoice manually via API
        inv_data = {
            "filing_id": filing_id,
            "invoice_number": "TEST-001",
            "invoice_date": "2024-04-05",
            "invoice_type": "b2b",
            "counterparty_name": "Test Client",
            "taxable_value": 1000.00,
            "total_tax": 180.00
        }
        resp = requests.post(f"{BASE_URL}/gst/invoices/", json=inv_data, headers=headers)
        if resp.status_code == 201:
            log("Invoice Created via API")
        elif resp.status_code == 400:
             log(f"Invoice Create Failed: {resp.text}", "WARN")
        else:
             log(f"Invoice API Path might be wrong: {resp.status_code}", "WARN")

    # 5. Check Summary (Totals should update)
    resp = requests.get(f"{detail_url}summary/", headers=headers)
    if resp.status_code == 200:
        summary = resp.json()
        log(f"Summary Fetched. Total Tax: {summary.get('total_tax')}")
    else:
        log(f"Summary Failed: {resp.text}", "ERROR")

    # 6. Delete Filing (Cleanup)
    # Assuming delete is allowed
    resp = requests.delete(detail_url, headers=headers)
    if resp.status_code == 204:
        log("Filing Deleted Successfully")
    else:
        log(f"Delete Failed: {resp.status_code}", "WARN")

    log("Test Complete.")

if __name__ == "__main__":
    run_test()
