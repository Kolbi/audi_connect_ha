from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
)

from .const import DOMAIN, SIGNAL_STATE_UPDATED


class AudiEntity(Entity):
    """Base class for all entities."""

    def __init__(self, data, instrument):
        """Initialize the entity."""
        self._data = data
        self._instrument = instrument
        self._vin = self._instrument.vehicle_name
        self._component = self._instrument.component
        self._attribute = self._instrument.attr

    async def async_added_to_hass(self):
        """Register update dispatcher."""
        async_dispatcher_connect(
            self.hass, SIGNAL_STATE_UPDATED, self.async_schedule_update_ha_state
        )

    @property
    def icon(self):
        """Return the icon."""
        return self._instrument.icon

    @property
    def _entity_name(self):
        return self._instrument.name

    @property
    def _vehicle_name(self):
        return self._instrument.vehicle_name

    @property
    def name(self):
        """Return full name of the entity."""
        return "{} {}".format(self._vehicle_name, self._entity_name)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        return True

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        return dict(
            self._instrument.attributes,
            model=self._instrument.vehicle_model,
            model_year=self._instrument.vehicle_model_year,
            model_family=self._instrument.vehicle_model_family,
            title=self._instrument.vehicle_name,
            csid=self._instrument.vehicle_csid,
            vin=self._instrument.vehicle_vin,
        )

    @property
    def unique_id(self):
        return self._instrument.full_name

    @property
    def migrate_device_identifiers(self): # Migrate device identifiers
    dev_reg = dr.async_get(hass)
    devices: list[dr.DeviceEntry] = dr.async_entries_for_config_entry(
        dev_reg, entry.entry_id
    )
    for device in devices:
        old_identifier = dict(device.identifiers).get(
            DOMAIN
        )  # list(next(iter(device.identifiers)))
        if old_identifier == self._instrument.vehicle_name:
            new_identifier = {(DOMAIN, self._instrument.vehicle_vin)}
            _LOGGER.debug(
                "migrate identifier '%s' to '%s'", device.identifiers, new_identifier
            )
            dev_reg.async_update_device(device.id, new_identifiers=new_identifier)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._instrument.vehicle_vin)},
            "manufacturer": "Audi",
            "model": self._instrument.vehicle_model_family,
            "name": self._vehicle_name,
        }
