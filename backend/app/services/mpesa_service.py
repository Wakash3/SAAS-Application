import httpx
import base64
from datetime import datetime
from ..core.config import settings


class MpesaService:
    @property
    def base_url(self):
        return (
            "https://api.safaricom.co.ke"
            if settings.MPESA_ENVIRONMENT == "production"
            else "https://sandbox.safaricom.co.ke"
        )

    async def get_token(self) -> str:
        creds = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        async with httpx.AsyncClient() as c:
            r = await c.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {creds}"},
            )
            return r.json()["access_token"]

    def _password(self, ts: str) -> str:
        raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{ts}"
        return base64.b64encode(raw.encode()).decode()

    def _normalize_phone(self, phone: str) -> str:
        phone = phone.strip()
        if phone.startswith("0"):
            return "254" + phone[1:]
        if phone.startswith("+"):
            return phone[1:]
        return phone

    async def stk_push(self, phone: str, amount: float, reference: str, desc: str) -> dict:
        token = await self.get_token()
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        phone = self._normalize_phone(phone)
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "BusinessShortCode": settings.MPESA_SHORTCODE,
                    "Password": self._password(ts),
                    "Timestamp": ts,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": int(amount),
                    "PartyA": phone,
                    "PartyB": settings.MPESA_SHORTCODE,
                    "PhoneNumber": phone,
                    "CallBackURL": settings.MPESA_CALLBACK_URL,
                    "AccountReference": reference,
                    "TransactionDesc": desc,
                },
            )
            return r.json()

    async def query_status(self, checkout_request_id: str) -> dict:
        token = await self.get_token()
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.base_url}/mpesa/stkpushquery/v1/query",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "BusinessShortCode": settings.MPESA_SHORTCODE,
                    "Password": self._password(ts),
                    "Timestamp": ts,
                    "CheckoutRequestID": checkout_request_id,
                },
            )
            return r.json()


mpesa_service = MpesaService()