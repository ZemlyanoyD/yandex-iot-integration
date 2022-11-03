import logging
from functools import lru_cache
from typing import Optional, Dict, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_TOKEN
from homeassistant.core import DOMAIN
import homeassistant.helpers.config_validation as cv
from homeassistant.data_entry_flow import AbortFlow

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_API_TOKEN): cv.string}
)


class YandexIOTFlowHandler(ConfigFlow, domain=DOMAIN):
    data = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                # Input is valid, set data.
                self.data[CONF_API_TOKEN] = user_input[CONF_API_TOKEN]

                # User is done adding repos, create the config entry.
                return self.async_create_entry(title="Yandex IoT", data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )