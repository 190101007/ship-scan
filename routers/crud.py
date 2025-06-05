import uuid
import qrcode
import time
import cv2  # OpenCV: görüntü işleme, kamera işlemleri
from pyzbar.pyzbar import decode  # pyzbar: qr kodu, barkodu vs çözümleme için
from pydantic import BaseModel, Field
from starlette import status
from models import Shipments, Senders
from fastapi import APIRouter, HTTPException, Depends, Request
from io import BytesIO
from asyncio.windows_events import NULL
from database import db_annotated
from typing import Annotated
from routers.users import get_current_user
from sqlalchemy.orm import defer
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/shipments",
    tags=["SHIPMENTS"],
)

templates = Jinja2Templates(directory="templates")

user_dependency = Annotated[dict, Depends(get_current_user)]


class ShipmentsModel(BaseModel):
    sender_name: str = Field(max_length=100)
    receiver_name: str = Field(max_length=100)
    receiver_phone: str = Field(max_length=12)
    receiver_address: str = Field(max_length=500)


# qr'ı kameradan okuttuğunda sana shipmentsin linkini dönderiyor.
@router.get("/qr_scan", status_code=status.HTTP_200_OK)
async def qr_scan(user: user_dependency):
    # 0: varsayılan kamera. ve kameradan capture adında bir nesne oluşturuyoruz
    capture = cv2.VideoCapture(0)

    # 3: genişlik, 4: uzunluk anlamına gelir ve burada boyut ayarlıyoruz
    capture.set(3, 200)
    capture.set(4, 200)

    # kameranın sürekli açık kalması
    while True:
        # oluşturduğunuz kamera nesnesinden read ile görüntü alıyoruz
        # eğer başarılıysa success=true; okuduğumuz görüntü: frame, artık ekranımız bu
        success, frame = capture.read()

        # (frame)görüntüde qr kod/barkod var mı kontrol
        for obj in decode(frame):
            typi = obj.type  # kodun tipi: qr mı barkod mu (eğer barkodsa tip: EAN13'tür)
            data = obj.data.decode("utf-8")  # okunabilirlik
            time.sleep(5)
            if data != NULL:
                # kameradan bağlantıyı kes, temiz kapama
                capture.release()
                # opencv'nin pencerelerini kapatma
                cv2.destroyAllWindows()

                return RedirectResponse(url=data)

            """         
                        print(f"QR LINKI: {data}")
                        print(type(data)) :::::STR
            """

        # görüntü ekranı gösterilir
        cv2.imshow('frame', frame)

        # waitKey(1): klavyeden veri geldi mi diye bakar ve 1 milisaniye bekler
        # q tuşuna bastığında çıkış yapıyor. ama mutlaka kamera için açılan pencereye odaklandığına dikkat et. yani fare ile en son kamera için açılan pencereye tıklamış ol
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # kameradan bağlantıyı kes, temiz kapama
    capture.release()
    # opencv'nin pencerelerini kapatma
    cv2.destroyAllWindows()


@router.get("/create-form")
async def show_create_form(request: Request, user: user_dependency):
    if user["role"] != "delivery_hub":
        return RedirectResponse(url="/users/login")

    return templates.TemplateResponse(
        "create-shipment.html", {"request": request}
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_shipment(shipment: ShipmentsModel, request: Request, user: user_dependency, db: db_annotated):
    try:
        if user["role"] != "delivery_hub":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bu işlem için yetkiniz yok"
            )

        sender = db.query(Senders).filter(Senders.sender_name == shipment.sender_name).first()

        if sender is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönderici bulunamadı"
            )

        # Generate UUID and create QR code
        sm_uuid = str(uuid.uuid4())
        create_url = f"http://127.0.0.1:8000/shipments/{sm_uuid}"
        new_qr = qrcode.make(create_url)
        buffer = BytesIO()
        new_qr.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        new_shipment = Shipments(
            id=sm_uuid,
            sender_id=sender.id,
            receiver_name=shipment.receiver_name,
            receiver_phone=shipment.receiver_phone,
            receiver_address=shipment.receiver_address,
            shipments_qr_code=qr_bytes
        )

        db.add(new_shipment)
        db.commit()

        return f"oluşturuldu"
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{package_id}", status_code=status.HTTP_200_OK)
async def get_shipment_info(request: Request,user: user_dependency, package_id: str, db: db_annotated):
    package = db.query(Shipments).filter(Shipments.id == package_id).first()
    shipment_info = {
        "receiver_name": package.receiver_name,
        "receiver_phone": package.receiver_phone,
        "receiver_address": package.receiver_address
    }

    # SENDER
    sender = db.query(Senders).join(Shipments, Senders.id == Shipments.sender_id).filter(
        Shipments.id == package_id).first()

    if user["role"] == "delivery_guy" or user["role"] == "delivery_hub":
        shipment_info["sender_phone"] = sender.sender_phone
        if user["role"] == "delivery_hub":
            shipment_info["sender_name"] = sender.sender_name

    return templates.TemplateResponse("read-shipment.html", {"request": request, **shipment_info })




@router.put("/update/{package_id}", status_code=status.HTTP_200_OK)
async def update_shipment(user: user_dependency, db: db_annotated, package_id: str, shipment: ShipmentsModel):
    package = db.query(Shipments).filter(Shipments.id == package_id).options(defer(Shipments.shipments_qr_code)).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    sender = db.query(Senders).filter(Senders.sender_name == shipment.sender_name).first()

    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    package.sender_id = sender.id
    package.receiver_address = shipment.receiver_address
    package.receiver_name = shipment.receiver_name
    package.receiver_phone = shipment.receiver_phone

    db.commit()

    return package

