from homeassistant import core, config_entries
from homeassistant.core import DOMAIN


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Yandex IoT integration component."""
    # @TODO: Add setup code.
    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light")
    )
    return True
