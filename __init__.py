import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)
DOMAIN = "coster_ew50e"
PLATFORMS = [Platform.CLIMATE]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Coster EW-50E component from YAML."""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        conf = config[DOMAIN]
        hass.data[DOMAIN]["yaml_config"] = conf
        
        # Setup platform directly
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(
                Platform.CLIMATE, DOMAIN, conf, config
            )
        )
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
