from __future__ import annotations

import logging

import requests
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA,
                                            LightEntity)
from homeassistant.const import CONF_API_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

Bulb = "devices.types.light"
Socket = "devices.types.socket"
Switch = "devices.types.switch"
Thermostat = "devices.types.thermostat"
AC = "devices.types.thermostat.ac"
MediaDevice = "devices.types.media_device"
MediaDeviceTV = "devices.types.media_device.tv"
MediaDeviceTVBox = "devices.types.media_device.tv_box"
MediaDeviceReceiver = "devices.types.media_device.receiver"
KitchenThings = "devices.types.cooking"
KitchenThingsCoffeeMaker = "devices.types.cooking.coffee_maker"
KitchenThingsKettle = "devices.types.cooking.kettle"
KitchenThingsMultiCooker = "devices.types.cooking.multicooker"
Openable = "devices.types.openable"
OpenableCurtain = "devices.types.openable.curtain"
Humidifier = "devices.types.humidifier"
Purifier = "devices.types.purifier"
VecuumCleaner = "devices.types.socket"
WashingMachine = "devices.types.washing_machine"
DishWasher = "devices.types.dishwasher"
Iron = "devices.types.iron"
Sensor = "devices.types.sensor"
Other = "devices.types.other"

DevicesNames = {
    Bulb: {
        "en": "Bulb",
        "ru": "Лампа"
    },
    Socket: {
        "en": "Socket",
        "ru": "Розетка"
    },
    Switch: {
        "en": "Switch",
        "ru": "Выключатель"
    },
    Thermostat: {
        "en": "Thermostat",
        "ru": "Термостат"
    },
    AC: {
        "en": "AC",
        "ru": "Кондиционер"
    },
    MediaDevice: {
        "en": "MediaDevice",
        "ru": "Устройство воспроизведения"
    },
    MediaDeviceTV: {
        "en": "TV",
        "ru": "Телевизор"
    },
    MediaDeviceTVBox: {
        "en": "TV box",
        "ru": "ТВ приставка"
    },
    MediaDeviceReceiver: {
        "en": "TV Receiver",
        "ru": "Тв приемник"
    },
    KitchenThings: {
        "en": "Kitchen device",
        "ru": "Кухонное устройство"
    },
    KitchenThingsKettle: {
        "en": "Kettle",
        "ru": "Чайник"
    },
    KitchenThingsCoffeeMaker: {
        "en": "Coffee maker",
        "ru": "Кофеварка"
    },
    KitchenThingsMultiCooker: {
        "en": "Multi cooker",
        "ru": "Мультиварка"
    },
    Openable: {
        "en": "Openable device",
        "ru": "Открывающееся устройство"
    },
    OpenableCurtain: {
        "en": "Curtain",
        "ru": "Шторка"
    },
    Humidifier: {
        "en": "Humidifier",
        "ru": "Увлажнитель"
    },
    Purifier: {
        "en": "Purifier",
        "ru": "Очиститель воздуха"
    },
    VecuumCleaner: {
        "en": "Vacuum cleaner",
        "ru": "Пылесос"
    },
    WashingMachine: {
        "en": "Washing machine",
        "ru": "Стиральная машина"
    },
    DishWasher: {
        "en": "Dish washer",
        "ru": "Посудомойка"
    },
    Iron: {
        "en": "Iron",
        "ru": "Утюг"
    },
    Sensor: {
        "en": "Sensor",
        "ru": "Датчик"
    },
    Other: {
        "en": "Other",
        "ru": "Другое"
    }
}
TYPE_RANGE = "devices.capabilities.range"
BRIGHTNESS_STATE_INSTANCE = "brightness"
EnabledState = "devices.capabilities.on_off"

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_TOKEN): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    token = config[CONF_API_TOKEN]

    # Setup connection with devices/cloud
    hub = Hub(token)

    # Verify that passed in configuration works
    if hub.is_invalid_token():
        _LOGGER.error("Could not connect to AwesomeLight hub")
        return

    # Add devices
    add_entities(AwesomeLight(light) for light in hub.lights())


class AwesomeLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, light) -> None:
        """Initialize an AwesomeLight."""
        self._light = light
        self._name = light.name
        self._state = None
        self._brightness = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs) -> None:
        """Instruct the light to turn on.
        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.turn_on()

    def turn_off(self, **kwargs) -> None:
        """Instruct the light to turn off."""
        self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
        self._state = self._light.is_on()
        self._brightness = self._light.brightness


class Light:
    def __init__(self, name, state, brightness, token, yandex_device_id):
        self.yandex_device_id = yandex_device_id
        self.name = name
        self.state = state
        self.brightness = brightness
        self.token = token

    def turn_on(self):
        payload = {
            "payload": {
                "devices": [
                    {
                        "id": self.yandex_device_id,
                        "capabilities": [
                            {
                                "type": EnabledState,
                                "retrievable": True,
                                "parameters": {
                                    "instance": "on",
                                    "value": True
                                }
                            }
                        ]
                    }
                ]
            }
        }

        res = requests.post(f"https://api.iot.yandex.net/v1.0/user/devices/action",
                            headers={
                                "Authorization": f"Bearer {self.token}"},
                            json=payload)

        if res.status_code < 400:
            self.state = True

    def turn_off(self):
        payload = {
            "payload": {
                "devices": [
                    {
                        "id": self.yandex_device_id,
                        "capabilities": [
                            {
                                "type": EnabledState,
                                "retrievable": True,
                                "parameters": {
                                    "instance": "on",
                                    "value": False
                                }
                            }
                        ]
                    }
                ]
            }
        }

        res = requests.post(f"https://api.iot.yandex.net/v1.0/user/devices/action",
                            headers={
                                "Authorization": f"Bearer {self.token}"},
                            json=payload)
        if res.status_code < 400:
            self.state = False

    def is_on(self):
        return self.state

    def update(self):
        res = requests.get(f"https://api.iot.yandex.net/v1.0/devices/{self.yandex_device_id}",
                           headers={
                               "Authorization": f"Bearer {self.token}"})
        res_json = res.json()
        self.name = res_json["name"]
        enabled = False
        brightness = None
        for capability in res_json["capabilities"]:
            if capability["type"] == EnabledState:
                enabled = capability["state"]["value"]
            if capability["type"] == TYPE_RANGE:
                if capability["state"]["instance"] == BRIGHTNESS_STATE_INSTANCE:
                    brightness = int(255 / 100 * capability["state"]["instance"]["value"])
        self.state = enabled
        self.brightness = brightness


class Hub:
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token

    def is_invalid_token(self):
        res = requests.get("https://api.iot.yandex.net/v1.0/user/info",
                           headers={"Authorization": f"Bearer {self.bearer_token}"})
        if res.status_code >= 400:
            return True
        return False

    def lights(self):
        res = requests.get("https://api.iot.yandex.net/v1.0/user/info",
                           headers={
                               "Authorization": f"Bearer {self.bearer_token}"})
        res_json = res.json()
        lights = []
        for item in res_json["devices"]:
            if item["type"] == Bulb:
                brightness = None
                enabled = False
                for capability in item["capabilities"]:
                    if capability["type"] == TYPE_RANGE:
                        if capability["state"]["instance"] == BRIGHTNESS_STATE_INSTANCE:
                            brightness = int(255 / 100 * capability["state"]["instance"]["value"])
                    if capability["type"] == EnabledState:
                        enabled = capability["state"]["value"]
                lights.append(Light(item["name"], enabled, brightness, self.bearer_token, item["id"]))

        return lights