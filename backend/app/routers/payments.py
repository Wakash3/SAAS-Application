from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.payment import MpesaTransaction
from ..models.sale import Sale
from ..services.mpesa_service import mpesa_service

router = APIRouter(prefix="/payments", tags=["payments"])


class STKRequest(BaseModel):
    sale_id: str
    phone: str
    amount: float


@router.post("/mpesa/stk")
async def initiate_stk(
    payload: STKRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    result = await mpesa_service.stk_push(
        phone=payload.phone,
        amount=payload.amount,
        reference=payload.sale_id[:10],
        desc="Msingi POS Payment",
    )

    if result.get("ResponseCode") != "0":
        raise HTTPException(400, result.get("errorMessage", "STK push failed"))

    tx = MpesaTransaction(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        sale_id=payload.sale_id,
        checkout_request_id=result["CheckoutRequestID"],
        phone_number=payload.phone,
        amount=payload.amount,
        status="pending",
    )
    db.add(tx)
    db.commit()
    return {"checkout_request_id": result["CheckoutRequestID"]}


@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    stk = body.get("Body", {}).get("stkCallback", {})
    checkout_id = stk.get("CheckoutRequestID")
    result_code = stk.get("ResultCode")

    tx = db.query(MpesaTransaction).filter(
        MpesaTransaction.checkout_request_id == checkout_id
    ).first()

    if not tx:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    if result_code == 0:
        items = stk.get("CallbackMetadata", {}).get("Item", [])
        receipt = next((i["Value"] for i in items if i["Name"] == "MpesaReceiptNumber"), None)
        tx.status = "paid"
        tx.mpesa_receipt_number = receipt
        tx.raw_callback = body

        if tx.sale_id:
            sale = db.query(Sale).filter(Sale.id == tx.sale_id).first()
            if sale:
                sale.payment_status = "paid"
                sale.mpesa_receipt = receipt
    else:
        tx.status = "failed"

    db.commit()
    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.get("/mpesa/status/{checkout_request_id}")
async def poll_status(
    checkout_request_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    tx = db.query(MpesaTransaction).filter(
        MpesaTransaction.checkout_request_id == checkout_request_id,
        MpesaTransaction.tenant_id == tenant_id,
    ).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    return {"status": tx.status, "receipt": tx.mpesa_receipt_number}