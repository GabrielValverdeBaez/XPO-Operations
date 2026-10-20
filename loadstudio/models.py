from __future__ import annotations
from datetime import date as Date, time as Time
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, field_serializer, model_validator

class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_assignment=True)

class Place(Model):
    country: str | None = None
    postcode: str | None = None
    locality: str | None = None
    center: str | None = None

class Window(Model):
    date: Date | None = None
    start: Time | None = None
    end: Time | None = None
    # Times are local to each site. No silent timezone conversion.
    timezone: str | None = None

    @model_validator(mode='after')
    def ordered(self):
        if self.end and not self.start:
            raise ValueError('Indicar inicio antes del fin de la ventana')
        if self.start and self.end and self.end < self.start:
            raise ValueError('Ventana nocturna: separar fechas, no invertir horas')
        return self

class Load(Model):
    reference: str | None = Field(default=None, max_length=64)
    customer: str | None = Field(default=None, max_length=160)
    origin: Place = Field(default_factory=Place)
    destination: Place = Field(default_factory=Place)
    pickup: Window = Field(default_factory=Window)
    delivery: Window = Field(default_factory=Window)
    service: Literal['FTL','GROUPAGE','RIGID'] | None = None
    service_code: str | None = None
    vehicle: str | None = None
    body: str | None = None
    weight_kg: Decimal | None = Field(default=None, ge=0, le=1000000)
    linear_meters: Decimal | None = Field(default=None, ge=0, le=100)
    pallets: int | None = Field(default=None, ge=0, le=2000)
    euro_pallets_confirmed: StrictBool = False
    palletized: StrictBool | None = None
    adr: StrictBool | None = None
    goods_es: str | None = Field(default=None, max_length=240)
    goods_en: str | None = Field(default=None, max_length=240)
    client_price_eur: Decimal | None = Field(default=None, ge=0, le=1000000, decimal_places=2)
    distance_km: Decimal | None = Field(default=None, gt=0, le=10000)
    # Output prices are calculated separately: never accept unproven market quotes.
    options: dict[str, StrictBool | None] = Field(default_factory=dict)
    blocked_fields: list[str] = Field(default_factory=list, max_length=50)
    stop_count: int = Field(default=2, ge=2, le=20)
    source_hash: str | None = None

    @field_validator('weight_kg','linear_meters','client_price_eur','distance_km')
    @classmethod
    def finite(cls, value):
        if value is not None and not value.is_finite(): raise ValueError('Numero no finito')
        return value.normalize() if value is not None else None

    @field_serializer('weight_kg','linear_meters','client_price_eur','distance_km',when_used='json')
    def plain_decimal(self,value,info):
        if value is None:return None
        return format(value,'.2f' if info.field_name=='client_price_eur' else 'f')

    @model_validator(mode='after')
    def dates_ordered(self):
        if self.pickup.date and self.delivery.date and self.delivery.date < self.pickup.date:
            raise ValueError('La descarga no puede ser anterior a la recogida')
        allowed={'pallet_exchange','gps','top','side','rear','refrigerated_ok','low_side_ok','same_specialty','alert'}
        if self.options.keys()-allowed: raise ValueError('Opcion Wtransnet desconocida')
        return self

class Issue(Model):
    field: str
    message: str
    severity: Literal['error','warning'] = 'warning'

class ParseRequest(Model):
    text: str = Field(max_length=250000)
    mode: Literal['auto','fote','text'] = 'auto'

class RenderRequest(Model):
    load: Load
    reviewed: StrictBool = False

class Rules(Model):
    revision: int = Field(ge=1)
    notes: dict[str, str]
    enabled: dict[str, StrictBool]
    reason: str = Field(min_length=3, max_length=300)

class CorridorRate(Model):
    id: str = Field(min_length=1, max_length=64, pattern=r'^[A-Za-z0-9_-]+$')
    origin_country: str
    origin_prefix: str = Field(min_length=2, max_length=5)
    destination_country: str
    destination_prefix: str = Field(min_length=2, max_length=5)
    service: Literal['FTL','GROUPAGE','RIGID']
    vehicle: str
    adr: StrictBool
    base_eur: Decimal = Field(ge=0, le=100000)
    per_km_eur: Decimal = Field(default=Decimal(0), ge=0, le=100)
    extras_eur: Decimal = Field(default=Decimal(0), ge=0, le=100000)
    max_weight_kg: Decimal = Field(gt=0, le=100000)
    max_linear_meters: Decimal = Field(gt=0, le=100)
    valid_from: Date
    valid_until: Date
    source: str = Field(min_length=5, max_length=500)

    @model_validator(mode='after')
    def ordered(self):
        if self.valid_until < self.valid_from: raise ValueError('Fechas de tarifa invertidas')
        return self
