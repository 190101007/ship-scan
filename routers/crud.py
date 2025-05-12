import uuid
import qrcode
import time
import cv2  # OpenCV: görüntü işleme, kamera işlemleri
from pyzbar.pyzbar import decode  # pyzbar: qr kodu, barkodu vs çözümleme için
from pydantic import BaseModel, Field
from models import Shipments, Senders
from fastapi import APIRouter, HTTPException, Request
from io import BytesIO
from asyncio.windows_events import NULL
from database import db_annotated

router = APIRouter(
    prefix="/shipments",
    tags=["SHIPMENTS"],
)

class ShipmentsModel(BaseModel):
    sender_name: str = Field(max_length=100)
    receiver_name: str = Field(max_length=100)
    receiver_phone: str = Field(max_length=12)
    receiver_address: str = Field(max_length=500)


@router.get("/qr_scan")
async def qr_scan(db: db_annotated):
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
            print(f"QR OKUNDU: {data}")
            print(type(data))
            time.sleep(5)
            if data != NULL:
                # kameradan bağlantıyı kes, temiz kapama
                capture.release()
                # opencv'nin pencerelerini kapatma
                cv2.destroyAllWindows()
                return data

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


@router.post("/add")
async def add_shipment(db: db_annotated, shipment: ShipmentsModel):
    # sender name'i alıp db'deki eşleşen veriyi bulup id'sini alıyoruz. böylece foreign key ile bağlanmış oluyor
    sender = db.query(Senders).filter(Senders.sender_name == shipment.sender_name).first()
    if sender is None:
        raise HTTPException(status_code=404, detail="Gönderici bulunamadı.")

    # uuid ile (link için) id'yi komplike hale getiriyoruz
    sm_uuid = uuid.uuid4()
    sm_uuid = str(uuid.uuid4())
    # uuid ile ürettiğimiz id'yi linkte kullanıyoruz ve sonra qr'a gömeceğiz
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


@router.get("/{package_id}")
async def get_shipment(db: db_annotated, package_id: str):
    find = db.query(Shipments).filter(Shipments.id == package_id).first()
    # http://127.0.0.1:8000/package/d86196b1-67d4-427f-9075-9ddd1f50099f
    return find.receiver_name, find.sender_id, find.receiver_phone, find.receiver_address


@router.get("/get_all")
async def get_all_shipments(db: db_annotated):
    return db.query(Shipments.receiver_address).all()


