# app/services/intasend_service.py
from ..core.config import settings
import logging
import requests

logger = logging.getLogger(__name__)

class IntaSendService:
    def __init__(self):
        self.publishable_key = settings.INTASEND_PUBLISHABLE_KEY
        self.secret_key = settings.INTASEND_SECRET_KEY
        self.test_mode = settings.INTASEND_ENVIRONMENT == "sandbox"
        self.api_url = settings.INTASEND_API_URL
        
    def initiate_mpesa_stk_push(self, phone_number: str, amount: float, email: str, narrative: str = "Payment"):
        """Initiate M-Pesa STK Push payment using IntaSend"""
        try:
            # Clean phone number
            phone_number = str(phone_number).replace("+", "").strip()
            if not phone_number.startswith("254"):
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
            
            url = f"{self.api_url}v1/payments/mpesa/stk-push/"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "phone_number": phone_number,
                "amount": float(amount),
                "email": email,
                "narrative": narrative,
                "test": self.test_mode
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"IntaSend STK Push failed: {str(e)}")
            raise
    
    def checkout(self, amount: float, email: str, phone_number: str = None, 
                 first_name: str = "", last_name: str = "", currency: str = "KES"):
        """Create a checkout URL for card payments"""
        try:
            url = f"{self.api_url}v1/checkout/"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "amount": float(amount),
                "currency": currency,
                "email": email,
                "test": self.test_mode
            }
            
            if phone_number:
                payload["phone_number"] = phone_number
            if first_name:
                payload["first_name"] = first_name
            if last_name:
                payload["last_name"] = last_name
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"IntaSend checkout failed: {str(e)}")
            raise
    
    def get_payment_status(self, invoice_id: str):
        """Check payment status using invoice/tracking ID"""
        try:
            url = f"{self.api_url}v1/status/{invoice_id}/"
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {str(e)}")
            raise

# Singleton instance
intasend_service = IntaSendService()