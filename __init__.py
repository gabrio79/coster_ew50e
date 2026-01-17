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


# custom_components/coster_ew50e/climate.py
import asyncio
import json
import logging
import xml.etree.ElementTree as ET
from datetime import timedelta
from typing import Any, Dict, Optional

import aiohttp
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "coster_ew50e"
SCAN_INTERVAL = timedelta(seconds=30)

# Mapping modalità Coster -> Home Assistant
MODE_MAP = {
    "HEAT": HVACMode.HEAT,
    "COOL": HVACMode.COOL,
    "FAN": HVACMode.FAN_ONLY,
    "AUTO": HVACMode.AUTO,
    "DRY": HVACMode.DRY,
}

MODE_MAP_REVERSE = {v: k for k, v in MODE_MAP.items()}

FAN_SPEED_MAP = {
    "LOW": "low",
    "MID1": "medium-low",
    "MID2": "medium",
    "MID3": "medium-high",
    "HIGH": "high",
    "AUTO": "auto",
}


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[dict] = None,
):
    """Set up the Coster EW-50E climate devices."""
    
    if discovery_info is None:
        discovery_info = config
    
    host = discovery_info.get("host")
    groups = discovery_info.get("groups", {})
    
    if not host or not groups:
        _LOGGER.error("Missing host or groups configuration")
        return False
    
    # Crea un coordinatore WebSocket condiviso
    coordinator = CosterWebSocketCoordinator(hass, host)
    
    # Crea le entità climate per ogni gruppo configurato
    entities = []
    for group_id, group_config in groups.items():
        entity = CosterClimate(
            coordinator,
            group_id,
            group_config.get("name", f"Split {group_id}"),
            group_config.get("icon", "mdi:air-conditioner"),
        )
        entities.append(entity)
    
    async_add_entities(entities, True)
    
    # Avvia il coordinatore WebSocket
    await coordinator.connect()
    
    return True


class CosterWebSocketCoordinator:
    """Coordinatore per gestire la connessione WebSocket con EW-50E."""
    
    def __init__(self, hass: HomeAssistant, host: str):
        """Initialize the coordinator."""
        self.hass = hass
        self.host = host
        self.ws = None
        self.session = None
        self.token = None
        self.data = {}
        self.listeners = []
        self._running = False
        
    async def connect(self):
        """Connetti al WebSocket."""
        if self._running:
            return
        
        self._running = True
        self.hass.async_create_task(self._maintain_connection())
    
    async def _maintain_connection(self):
        """Mantieni la connessione WebSocket attiva."""
        while self._running:
            try:
                await self._connect_websocket()
            except Exception as e:
                _LOGGER.error(f"WebSocket error: {e}")
                await asyncio.sleep(10)
    
    async def _connect_websocket(self):
        """Connetti e gestisci il WebSocket."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        # Prima ottieni il token da una richiesta HTTP
        await self._get_token()
        
        if not self.token:
            _LOGGER.error("Failed to get authentication token")
            await asyncio.sleep(30)
            return
        
        ws_url = f"wss://{self.host}/b_xmlproc/?token={self.token}"
        
        try:
            async with self.session.ws_connect(
                ws_url,
                ssl=False,
                heartbeat=30
            ) as ws:
                self.ws = ws
                _LOGGER.info("WebSocket connected")
                
                # Invia richiesta iniziale per tutti i gruppi
                await self._request_all_groups()
                
                # Loop di ricezione messaggi
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await self._handle_message(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        _LOGGER.error(f"WebSocket error: {ws.exception()}")
                        break
                        
        except Exception as e:
            _LOGGER.error(f"WebSocket connection error: {e}")
        finally:
            self.ws = None
            await asyncio.sleep(5)
    
    async def _get_token(self):
        """Ottieni il token JWT dal server."""
        try:
            async with self.session.get(
                f"https://{self.host}/",
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                # Il token è nell'URL del WebSocket mostrato nella pagina
                # Per semplicità, lo estraiamo dai cookie o headers
                # In alternativa, possiamo usare un token fisso se funziona
                
                # Metodo semplificato: usa cookie di sessione
                cookies = self.session.cookie_jar.filter_cookies(f"https://{self.host}")
                
                # Se non funziona, prova a fare il parsing della pagina HTML
                # per estrarre il token dal JavaScript
                text = await resp.text()
                
                # Cerca il pattern del token nel codice JavaScript
                import re
                match = re.search(r'token=([A-Za-z0-9._-]+)', text)
                if match:
                    self.token = match.group(1)
                    _LOGGER.info("Token extracted successfully")
                else:
                    _LOGGER.warning("Token not found in page, using session cookies")
                    
        except Exception as e:
            _LOGGER.error(f"Failed to get token: {e}")
    
    async def _request_all_groups(self):
        """Richiedi i dati di tutti i gruppi."""
        request_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<Packet>
<Command>getRequest</Command>
<DatabaseManager>
"""
        
        # Aggiungi tutti i gruppi (1-17)
        for group_id in range(1, 18):
            request_xml += f'<Mnet Group="{group_id}" Drive="*" Mode="*" SetTemp="*" InletTemp="*" FanSpeed="*" AirDirection="*" ErrorSign="*" />\n'
        
        request_xml += """</DatabaseManager>
</Packet>"""
        
        if self.ws and not self.ws.closed:
            await self.ws.send_str(request_xml)
            _LOGGER.debug("Sent data request for all groups")
    
    async def _handle_message(self, message: str):
        """Gestisci i messaggi ricevuti dal WebSocket."""
        try:
            # Parse XML
            root = ET.fromstring(message)
            command = root.find("Command")
            
            if command is not None and command.text == "getResponse":
                # Estrai i dati dei gruppi
                db_manager = root.find("DatabaseManager")
                if db_manager is not None:
                    for mnet in db_manager.findall("Mnet"):
                        group_id = mnet.get("Group")
                        if group_id:
                            self.data[group_id] = dict(mnet.attrib)
                    
                    # Notifica tutti i listener
                    for listener in self.listeners:
                        listener()
            
            elif command is not None and command.text == "notifyRequest":
                # Aggiornamento singolo gruppo
                db_manager = root.find("DatabaseManager")
                if db_manager is not None:
                    for mnet in db_manager.findall("Mnet"):
                        group_id = mnet.get("Group")
                        if group_id and group_id in self.data:
                            # Aggiorna solo i campi presenti
                            self.data[group_id].update(dict(mnet.attrib))
                            
                            # Notifica i listener
                            for listener in self.listeners:
                                listener()
                                
        except Exception as e:
            _LOGGER.error(f"Error parsing message: {e}")
    
    def add_listener(self, listener):
        """Aggiungi un listener per gli aggiornamenti."""
        self.listeners.append(listener)
    
    def remove_listener(self, listener):
        """Rimuovi un listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    async def set_group_state(self, group_id: str, **kwargs):
        """Imposta lo stato di un gruppo."""
        set_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<Packet>
<Command>setRequest</Command>
<DatabaseManager>
<Mnet Group="{group_id}" """
        
        for key, value in kwargs.items():
            set_xml += f'{key}="{value}" '
        
        set_xml += """/>
</DatabaseManager>
</Packet>"""
        
        if self.ws and not self.ws.closed:
            await self.ws.send_str(set_xml)
            _LOGGER.debug(f"Sent set command for group {group_id}: {kwargs}")
            
            # Richiedi un refresh dei dati
            await asyncio.sleep(1)
            await self._request_all_groups()
    
    async def close(self):
        """Chiudi la connessione."""
        self._running = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()


class CosterClimate(ClimateEntity):
    """Rappresenta un climatizzatore Coster."""
    
    def __init__(
        self,
        coordinator: CosterWebSocketCoordinator,
        group_id: str,
        name: str,
        icon: str,
    ):
        """Initialize the climate device."""
        self._coordinator = coordinator
        self._group_id = group_id
        self._name = name
        self._icon = icon
        self._attr_unique_id = f"coster_ew50e_group_{group_id}"
        
        # Supporta modalità e funzionalità
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.SWING_MODE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.FAN_ONLY,
            HVACMode.AUTO,
        ]
        
        self._attr_fan_modes = list(FAN_SPEED_MAP.values())
        self._attr_swing_modes = ["on", "off"]
        
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = 16
        self._attr_max_temp = 31
        self._attr_target_temperature_step = 0.5
        
        # Aggiungi listener al coordinatore
        self._coordinator.add_listener(self._handle_coordinator_update)
    
    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name
    
    @property
    def icon(self):
        """Return the icon."""
        return self._icon
    
    @property
    def available(self):
        """Return True if entity is available."""
        return self._group_id in self._coordinator.data
    
    @property
    def current_temperature(self):
        """Return the current temperature."""
        data = self._coordinator.data.get(self._group_id, {})
        temp = data.get("InletTemp", "0")
        try:
            return float(temp)
        except (ValueError, TypeError):
            return None
    
    @property
    def target_temperature(self):
        """Return the target temperature."""
        data = self._coordinator.data.get(self._group_id, {})
        temp = data.get("SetTemp", "0")
        try:
            return float(temp)
        except (ValueError, TypeError):
            return None
    
    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        data = self._coordinator.data.get(self._group_id, {})
        drive = data.get("Drive", "OFF")
        
        if drive == "OFF":
            return HVACMode.OFF
        
        mode = data.get("Mode", "AUTO")
        return MODE_MAP.get(mode, HVACMode.AUTO)
    
    @property
    def fan_mode(self):
        """Return current fan mode."""
        data = self._coordinator.data.get(self._group_id, {})
        speed = data.get("FanSpeed", "AUTO")
        return FAN_SPEED_MAP.get(speed, "auto")
    
    @property
    def swing_mode(self):
        """Return current swing mode."""
        data = self._coordinator.data.get(self._group_id, {})
        direction = data.get("AirDirection", "HORIZONTAL")
        return "on" if direction != "HORIZONTAL" else "off"
    
    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            await self._coordinator.set_group_state(
                self._group_id,
                SetTemp=str(int(temperature))
            )
    
    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self._coordinator.set_group_state(
                self._group_id,
                Drive="OFF"
            )
        else:
            coster_mode = MODE_MAP_REVERSE.get(hvac_mode, "AUTO")
            await self._coordinator.set_group_state(
                self._group_id,
                Drive="ON",
                Mode=coster_mode
            )
    
    async def async_set_fan_mode(self, fan_mode: str):
        """Set new fan mode."""
        # Reverse lookup
        coster_speed = None
        for key, value in FAN_SPEED_MAP.items():
            if value == fan_mode:
                coster_speed = key
                break
        
        if coster_speed:
            await self._coordinator.set_group_state(
                self._group_id,
                FanSpeed=coster_speed
            )
    
    async def async_set_swing_mode(self, swing_mode: str):
        """Set new swing mode."""
        direction = "AUTO" if swing_mode == "on" else "HORIZONTAL"
        await self._coordinator.set_group_state(
            self._group_id,
            AirDirection=direction
        )
    
    async def async_turn_on(self):
        """Turn the entity on."""
        await self._coordinator.set_group_state(
            self._group_id,
            Drive="ON"
        )
    
    async def async_turn_off(self):
        """Turn the entity off."""
        await self._coordinator.set_group_state(
            self._group_id,
            Drive="OFF"
        )
    
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
    
    async def async_update(self):
        """Update the entity."""
        # Il coordinatore gestisce già gli aggiornamenti automatici
        pass
    
    async def async_will_remove_from_hass(self):
        """Clean up before removing."""
        self._coordinator.remove_listener(self._handle_coordinator_update)
