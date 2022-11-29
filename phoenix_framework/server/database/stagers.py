"""The Stagers Model"""
import importlib
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Session, relationship

from phoenix_framework.server import AVAILABLE_KITS

from .base import Base

if TYPE_CHECKING:
    from phoenix_framework.server.commander import Commander
    from phoenix_framework.server.kits.base_stager import (BasePayload,
                                                           BaseStager)

    from .devices import DeviceModel
    from .listeners import ListenerModel


class StagerModel(Base):
    """The Stagers Model"""

    __tablename__ = "Stagers"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    payload_type: str = Column(String(100))
    encoding: str = Column(String(10))
    random_size: bool = Column(Boolean)
    timeout: int = Column(Integer)
    delay: int = Column(Integer)
    different_address = Column(String(100))
    options: dict = Column(MutableDict.as_mutable(JSON), default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    listener_id: int = Column(Integer, ForeignKey("Listeners.id"))
    listener: "ListenerModel" = relationship("ListenerModel", back_populates="stagers")
    devices: list["DeviceModel"] = relationship("DeviceModel", back_populates="stager")

    def to_dict(
        self,
        commander: "Commander",
        show_listener: bool = True,
        show_devices: bool = True,
    ) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "payload_type": self.payload_type,
            "encoding": self.encoding,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "delay": self.delay,
            "different_address": self.different_address,
            "options": self.options,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "listener": self.listener.to_dict(commander, show_stagers=False)
            if show_listener
            else self.listener.id,
            "devices": [
                device.to_dict(commander, show_listener=False)
                for device in self.devices
            ]
            if show_devices
            else [device.id for device in self.devices],
        }

    @staticmethod
    def get_class_from_type(type: str) -> "BaseStager":
        """Return the stager class based on its type."""
        type = type.replace("-", "_")
        if type not in AVAILABLE_KITS:
            raise ValueError(f"Stager '{type}' isn't available.")
        try:
            stager = importlib.import_module(
                "phoenix_framework.server.kits." + type.replace("-", "_") + ".stager"
            ).Stager
        except ModuleNotFoundError as e:
            raise FileNotFoundError(f"Stager '{type}' doesn't exist.") from e
        else:
            return stager

    @property
    def stager_class(self) -> "BaseStager":
        """Returns the stager class."""
        return self.get_class_from_type(self.listener.type)

    @property
    def payload_class(self) -> "BasePayload":
        """Returns the payload class."""
        return self.stager_class.payloads[self.payload_type]

    @staticmethod
    def get_all_classes() -> list["BaseStager"]:
        """Get all stager classes."""
        return [StagerModel.get_class_from_type(stager) for stager in AVAILABLE_KITS]

    def edit(self, data: dict):
        """Edit the stager"""
        options = (
            self.stager_class.options
        )  # so we dont have to get the class multiple times
        for key, value in data.items():
            if hasattr(self, key):
                if value == str(getattr(self, key)):
                    continue
                option = options.get_option(key)
                if not option.editable:
                    raise ValueError(f"Option '{key}' is not editable.")
                value = option.validate_data(value)
                setattr(self, key, value)
            else:
                if key in self.options:
                    if value == self.options[key]:
                        continue
                    option = options.get_option(key)
                    if not option.editable:
                        raise ValueError(f"Option '{key}' is not editable.")
                    value = option.validate_data(value)
                    self.options[key] = value
                else:
                    raise KeyError(f"{key} is not a valid key")

    @classmethod
    def create_from_data(cls, data: dict):
        """Create the stager using custom validated data"""
        standard = []
        # gets standard values present in every stager and remove them to only leave options
        for st_value in [
            "name",
            "listener",
            "payload_type",
            "encoding",
            "random_size",
            "timeout",
            "delay",
            "different_address",
        ]:
            standard.append(data.pop(st_value))
        return cls(
            name=standard[0],
            listener=standard[1],
            payload_type=standard[2],
            encoding=standard[3],
            random_size=standard[4],
            timeout=standard[5],
            delay=standard[6],
            different_address=standard[7],
            options=data,
        )

    @classmethod
    def add(cls, data: dict, session: Session) -> "StagerModel":
        """Add a stager to the database"""
        stager = cls.create_from_data(data)
        session.add(stager)
        session.commit()
        return stager
