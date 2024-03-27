"""Support for Audi Connect."""

from datetime import timedelta
import voluptuous as vol
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import utcnow
from homeassistant import config_entries
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_RESOURCES,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from homeassistant.util.unit_system import (
    US_CUSTOMARY_SYSTEM,
)

from .audi_account import AudiAccount

from .const import (
    DOMAIN,
    CONF_REGION,
    CONF_MUTABLE,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    RESOURCES,
    COMPONENTS,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=timedelta(minutes=DEFAULT_UPDATE_INTERVAL),
                ): vol.All(
                    cv.time_period,
                    vol.Clamp(min=timedelta(minutes=MIN_UPDATE_INTERVAL)),
                ),
                vol.Optional(CONF_NAME, default={}): cv.schema_with_slug_keys(
                    cv.string
                ),
                vol.Optional(CONF_RESOURCES): vol.All(
                    cv.ensure_list, [vol.In(RESOURCES)]
                ),
                vol.Optional(CONF_REGION): cv.string,
                vol.Optional(CONF_MUTABLE, default=True): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    if hass.config_entries.async_entries(DOMAIN):
        return True

    if DOMAIN not in config:
        return True

    names = config[DOMAIN].get(CONF_NAME)
    if len(names) == 0:
        return True

    data = {}
    data[CONF_USERNAME] = config[DOMAIN].get(CONF_USERNAME)
    data[CONF_PASSWORD] = config[DOMAIN].get(CONF_PASSWORD)
    data[CONF_SCAN_INTERVAL] = config[DOMAIN].get(CONF_SCAN_INTERVAL).seconds / 60
    data[CONF_REGION] = config[DOMAIN].get(CONF_REGION)

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=data
        )
    )

    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    """Set up the Audi Connect component."""
    hass.data[DOMAIN]["devices"] = set()

    account = config_entry.data.get(CONF_USERNAME)

    unit_system = "metric"
    if hass.config.units is US_CUSTOMARY_SYSTEM:
        unit_system = "imperial"

    if account not in hass.data[DOMAIN]:
        data = hass.data[DOMAIN][account] = AudiAccount(
            hass, config_entry, unit_system=unit_system
        )
        data.init_connection()
    else:
        data = hass.data[DOMAIN][account]

    return await data.update(utcnow())


async def async_unload_entry(hass, config_entry):
    account = config_entry.data.get(CONF_USERNAME)

    data = hass.data[DOMAIN][account]

    for component in COMPONENTS:
        await hass.config_entries.async_forward_entry_unload(
            data.config_entry, component
        )

    del hass.data[DOMAIN][account]

    return True

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
     """Migrate an old config entry."""
     if config_entry.version == 1:

        new = {**config_entry.data}
        hass.config_entries.async_update_entry(config_entry, data=new, minor_version=0, version=2)

        _LOGGER.debug("Migration to version %s.%s successful", config_entry.version, config_entry.minor_version)

        device_registry = await dr.async_get(hass)
        for entry_id, device in device_registry.devices.items():
            if device.domain == DOMAIN and "identifiers" in device.config_entries:
                old_identifier = device.config_entries["identifiers"][0]
                if (
                    old_identifier[1] == self._instrument.vehicle_name
                ):  # Überprüfen, ob alter Identifier verwendet wird
                    _LOGGER.info(
                        "Migriere Gerät %s (%s) auf neuen Identifier",
                        device.name,
                        device.id,
                    )
                    new_identifier = (DOMAIN, self._instrument.vehicle_vin)
                    try:
                        device_registry.async_update_device(
                            entry_id, device_id=new_identifier["id"]
                        )
                        _LOGGER.info("Migration für Gerät %s erfolgreich", device.name)
                    except Exception as e:
                        _LOGGER.error(
                            "Migration für Gerät %s fehlgeschlagen: %s", device.name, e
                        )
                else:
                    _LOGGER.info(
                        "Keine Migration notwendig für Gerät %s (%s) auf neuen Identifier",
                        device.name,
                        device.id,
                    )

    return True

    async def async_remove_config_entry_device(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_entry: dr.DeviceEntry,
    ) -> bool:
        """Remove a config entry device."""

    return True
