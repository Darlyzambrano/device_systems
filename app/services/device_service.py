from typing import Optional

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceUpdate

ALLOWED_DEVICE_TYPES = {"laptop", "tablet", "proyector", "camara", "router", "monitor"}


class DeviceService:
    def __init__(self, db: Session):
        self.db = db

    def list_devices(
        self,
        device_type: Optional[str] = None,
        is_available: Optional[bool] = None,
        brand: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Device]:
        query = self.db.query(Device)
        if device_type:
            self._validate_device_type(device_type)
            query = query.filter(Device.device_type == device_type)
        if is_available is not None:
            query = query.filter(Device.is_available == is_available)
        if brand:
            query = query.filter(Device.brand.ilike(f"%{brand}%"))
        if search:
            query = query.filter(
                or_(
                    Device.name.ilike(f"%{search}%"),
                    Device.serial_number.ilike(f"%{search}%"),
                    Device.brand.ilike(f"%{search}%"),
                )
            )
        return query.order_by(Device.name.asc()).all()

    def get_device(self, device_id: int) -> Device:
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        return device

    def create_device(self, data: DeviceCreate) -> Device:
        self._validate_device_type(data.device_type)
        if self._serial_exists(data.serial_number):
            raise HTTPException(
                status_code=400,
                detail=f"El número de serie {data.serial_number} ya está registrado",
            )
        device = Device(**data.model_dump())
        self.db.add(device)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Número de serie duplicado")
        self.db.refresh(device)
        return device

    def update_device(self, device_id: int, data: DeviceUpdate) -> Device:
        device = self.get_device(device_id)
        self._validate_device_type(data.device_type)
        if self._serial_exists(data.serial_number, exclude_id=device_id):
            raise HTTPException(status_code=400, detail="Número de serie duplicado")
        for field, value in data.model_dump().items():
            setattr(device, field, value)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Número de serie duplicado")
        self.db.refresh(device)
        return device

    def patch_device(self, device_id: int, data: DevicePatch) -> Device:
        patch_data = data.model_dump(exclude_unset=True)
        if not patch_data:
            raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar")
        device = self.get_device(device_id)
        if "device_type" in patch_data:
            self._validate_device_type(patch_data["device_type"])
        if "serial_number" in patch_data and self._serial_exists(
            patch_data["serial_number"], exclude_id=device_id
        ):
            raise HTTPException(status_code=400, detail="Número de serie duplicado")
        for field, value in patch_data.items():
            setattr(device, field, value)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Número de serie duplicado")
        self.db.refresh(device)
        return device

    def delete_device(self, device_id: int) -> None:
        device = self.get_device(device_id)
        self.db.delete(device)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar: el dispositivo tiene préstamos asociados",
            )

    def _serial_exists(self, serial: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(Device).filter(Device.serial_number == serial)
        if exclude_id:
            query = query.filter(Device.id != exclude_id)
        return query.first() is not None

    def _validate_device_type(self, device_type: str) -> None:
        if device_type not in ALLOWED_DEVICE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo no permitido: {device_type}. Válidos: {', '.join(sorted(ALLOWED_DEVICE_TYPES))}",
            )
