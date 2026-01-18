# Coster EW-50E Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/mattigabrio79/coster_ew50e.svg)](https://github.com/mattigabrio79/coster_ew50e/releases)
[![License](https://img.shields.io/github/license/mattigabrio79/coster_ew50e.svg)](LICENSE)

[🇮🇹 Italiano](#italiano) | [🇬🇧 English](#english)

---

## 🇮🇹 Italiano

### Descrizione

Integrazione personalizzata per Home Assistant che permette di controllare i climatizzatori connessi al webserver **Coster EW-50E** tramite WebSocket in tempo reale.

### Caratteristiche

✅ **Connessione WebSocket in tempo reale** - Aggiornamenti istantanei dello stato  
✅ **Controllo completo** - Accensione/spegnimento, temperatura, modalità, ventola, oscillazione  
✅ **Supporto multi-split** - Gestione di tutti i gruppi configurati (fino a 17)  
✅ **Riconnessione automatica** - Mantiene la connessione stabile  
✅ **Configurazione parametrica** - Personalizza nomi e icone via YAML  
✅ **Integrazione nativa** - Entità Climate standard di Home Assistant  

### Requisiti

- Home Assistant 2023.1 o superiore
- Webserver Coster EW-50E connesso alla rete locale
- Accesso alla rete locale dove si trova il webserver

### Installazione

#### Metodo 1: Installazione Manuale

1. Copia la cartella `coster_ew50e` in `config/custom_components/`:
   ```
   config/
   └── custom_components/
       └── coster_ew50e/
           ├── __init__.py
           ├── climate.py
           └── manifest.json
   ```

2. Aggiungi la configurazione al file `configuration.yaml`:
   ```yaml
   coster_ew50e:
     host: "192.168.1.100"  # IP del tuo webserver EW-50E
     groups:
       13:
         name: "Studio 1"
         icon: "mdi:office-building"
       14:
         name: "Studio 2"
         icon: "mdi:desk"
       15:
         name: "Soggiorno"
         icon: "mdi:sofa"
       # Aggiungi altri gruppi secondo necessità
   ```

3. Riavvia Home Assistant

#### Metodo 2: HACS (quando disponibile)

1. Apri HACS nel tuo Home Assistant
2. Vai su "Integrazioni"
3. Clicca sui tre puntini in alto a destra
4. Seleziona "Repository personalizzati"
5. Aggiungi `https://github.com/mattigabrio79/coster_ew50e`
6. Seleziona "Integrazione" come categoria
7. Clicca su "Installa"

### Configurazione

#### Parametri obbligatori:

- **host**: Indirizzo IP del webserver Coster EW-50E (es. `192.168.50.72`)
- **groups**: Dizionario dei gruppi split da controllare

#### Parametri per ogni gruppo:

- **name**: Nome personalizzato dello split
- **icon**: Icona Material Design Icons (opzionale, default: `mdi:air-conditioner`)

#### Esempio di configurazione completa:

```yaml
coster_ew50e:
  host: "192.168.50.72"
  groups:
    1:
      name: "Magazzino"
      icon: "mdi:warehouse"
    2:
      name: "Ufficio Reception"
      icon: "mdi:desk"
    13:
      name: "Studio Medico 1"
      icon: "mdi:hospital-box"
    14:
      name: "Studio Medico 2"
      icon: "mdi:hospital-box"
    15:
      name: "Sala d'Aspetto"
      icon: "mdi:seat"
```

### Funzionalità supportate

Ogni entità climate supporta:

- **Modalità HVAC**: Off, Heat, Cool, Fan Only, Auto
- **Temperatura**: Impostazione e lettura (16-31°C)
- **Velocità ventola**: Low, Medium-Low, Medium, Medium-High, High, Auto
- **Oscillazione**: On/Off (movimento alette aria)
- **Stato**: Temperatura corrente, temperatura target, modalità attiva

### Risoluzione problemi

#### L'integrazione non si carica

1. Verifica che i file siano nella posizione corretta
2. Controlla che il file si chiami esattamente `__init__.py` (con doppio underscore)
3. Verifica i log di Home Assistant in "Impostazioni" → "Sistema" → "Log"

#### Le entità non appaiono

1. Verifica che l'IP del webserver sia corretto
2. Controlla che il webserver sia raggiungibile dalla rete
3. Verifica che i numeri dei gruppi corrispondano a quelli configurati nel webserver

#### Gli split non rispondono ai comandi

1. Controlla la connessione WebSocket nei log
2. Verifica che il webserver funzioni correttamente accedendo via browser
3. Riavvia l'integrazione o Home Assistant

### Log e Debug

Per abilitare i log dettagliati, aggiungi al `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.coster_ew50e: debug
```

### Supporto

Per segnalare bug o richiedere funzionalità:
- Apri una [Issue su GitHub](https://github.com/mattigabrio79/coster_ew50e/issues)

### Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per i dettagli.

### Crediti

Sviluppato da [@gabrio79](https://github.com/mattigabrio79)

---

## 🇬🇧 English

### Description

Custom integration for Home Assistant that allows you to control air conditioners connected to the **Coster EW-50E** webserver via real-time WebSocket.

### Features

✅ **Real-time WebSocket connection** - Instant status updates  
✅ **Full control** - On/off, temperature, mode, fan speed, swing  
✅ **Multi-split support** - Manage all configured groups (up to 17)  
✅ **Automatic reconnection** - Maintains stable connection  
✅ **Parametric configuration** - Customize names and icons via YAML  
✅ **Native integration** - Standard Home Assistant Climate entities  

### Requirements

- Home Assistant 2023.1 or higher
- Coster EW-50E webserver connected to local network
- Access to the local network where the webserver is located

### Installation

#### Method 1: Manual Installation

1. Copy the `coster_ew50e` folder to `config/custom_components/`:
   ```
   config/
   └── custom_components/
       └── coster_ew50e/
           ├── __init__.py
           ├── climate.py
           └── manifest.json
   ```

2. Add configuration to `configuration.yaml`:
   ```yaml
   coster_ew50e:
     host: "192.168.1.100"  # IP of your EW-50E webserver
     groups:
       13:
         name: "Office 1"
         icon: "mdi:office-building"
       14:
         name: "Office 2"
         icon: "mdi:desk"
       15:
         name: "Living Room"
         icon: "mdi:sofa"
       # Add other groups as needed
   ```

3. Restart Home Assistant

#### Method 2: HACS (when available)

1. Open HACS in your Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add `https://github.com/mattigabrio79/coster_ew50e`
6. Select "Integration" as category
7. Click "Install"

### Configuration

#### Required parameters:

- **host**: IP address of Coster EW-50E webserver (e.g., `192.168.50.72`)
- **groups**: Dictionary of split groups to control

#### Parameters for each group:

- **name**: Custom name for the split unit
- **icon**: Material Design Icon (optional, default: `mdi:air-conditioner`)

#### Complete configuration example:

```yaml
coster_ew50e:
  host: "192.168.50.72"
  groups:
    1:
      name: "Warehouse"
      icon: "mdi:warehouse"
    2:
      name: "Reception Office"
      icon: "mdi:desk"
    13:
      name: "Medical Office 1"
      icon: "mdi:hospital-box"
    14:
      name: "Medical Office 2"
      icon: "mdi:hospital-box"
    15:
      name: "Waiting Room"
      icon: "mdi:seat"
```

### Supported Features

Each climate entity supports:

- **HVAC Modes**: Off, Heat, Cool, Fan Only, Auto
- **Temperature**: Set and read (16-31°C)
- **Fan Speed**: Low, Medium-Low, Medium, Medium-High, High, Auto
- **Swing**: On/Off (air vane movement)
- **Status**: Current temperature, target temperature, active mode

### Troubleshooting

#### Integration doesn't load

1. Verify files are in the correct location
2. Check that the file is named exactly `__init__.py` (with double underscore)
3. Check Home Assistant logs in "Settings" → "System" → "Logs"

#### Entities don't appear

1. Verify the webserver IP is correct
2. Check that the webserver is reachable from the network
3. Verify group numbers match those configured in the webserver

#### Splits don't respond to commands

1. Check WebSocket connection in logs
2. Verify the webserver works correctly by accessing it via browser
3. Restart the integration or Home Assistant

### Logging and Debug

To enable detailed logging, add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.coster_ew50e: debug
```

### Support

To report bugs or request features:
- Open an [Issue on GitHub](https://github.com/mattigabrio79/coster_ew50e/issues)

### License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.

### Credits

Developed by [@gabrio79](https://github.com/gabrio79)

---

## Changelog

### Version 1.0.0 (2026-01-18)

- 🎉 Initial release
- ✅ WebSocket connection with Coster EW-50E
- ✅ Support for all HVAC modes
- ✅ Temperature, fan speed, and swing control
- ✅ Real-time status updates
- ✅ Multi-split support (up to 17 groups)
- ✅ Parametric YAML configuration

---

## Screenshots

### Climate Entity Card
![Climate Card](docs/images/climate-card.png)

### Configuration Example
![Configuration](docs/images/configuration.png)

---

**Star ⭐ this repository if you find it useful!**
