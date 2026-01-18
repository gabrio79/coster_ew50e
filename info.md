# Coster EW-50E Integration

Integrazione per Home Assistant che permette di controllare i climatizzatori connessi al webserver **Coster EW-50E** tramite WebSocket in tempo reale.

## ✨ Caratteristiche

- ✅ **Connessione WebSocket in tempo reale** - Aggiornamenti istantanei dello stato
- ✅ **Controllo completo** - Accensione/spegnimento, temperatura, modalità, ventola, oscillazione
- ✅ **Supporto multi-split** - Gestione di tutti i gruppi configurati (fino a 17)
- ✅ **Riconnessione automatica** - Mantiene la connessione stabile
- ✅ **Configurazione parametrica** - Personalizza nomi e icone via YAML
- ✅ **Integrazione nativa** - Entità Climate standard di Home Assistant

## 📦 Installazione

### Via HACS (Raccomandato)

1. Apri HACS nel tuo Home Assistant
2. Vai su "Integrazioni"
3. Clicca sui tre puntini in alto a destra → "Repository personalizzati"
4. Aggiungi questo URL: `https://github.com/gabrio79/coster_ew50e`
5. Seleziona "Integrazione" come categoria
6. Cerca "Coster EW-50E" e clicca "Installa"
7. Riavvia Home Assistant

### Installazione Manuale

1. Scarica questa repository
2. Copia la cartella `custom_components/coster_ew50e` nella tua cartella `config/custom_components/`
3. Riavvia Home Assistant

## ⚙️ Configurazione

Aggiungi al tuo `configuration.yaml`:

```yaml
coster_ew50e:
  host: "192.168.1.100"  # IP del tuo webserver EW-50E
  groups:
    13:
      name: "Soggiorno"
      icon: "mdi:sofa"
    14:
      name: "Camera da Letto"
      icon: "mdi:bed"
    15:
      name: "Studio"
      icon: "mdi:desk"
```

### Parametri

- **host** *(obbligatorio)*: Indirizzo IP del webserver Coster EW-50E
- **groups** *(obbligatorio)*: Dizionario dei gruppi split da controllare
  - **name**: Nome personalizzato dello split
  - **icon**: Icona Material Design (opzionale, default: `mdi:air-conditioner`)

## 🎮 Funzionalità Supportate

Ogni entità climate supporta:

- **Modalità HVAC**: Off, Heat, Cool, Fan Only, Auto
- **Temperatura**: Impostazione e lettura (16-31°C, step 0.5°C)
- **Velocità ventola**: Low, Medium-Low, Medium, Medium-High, High, Auto
- **Oscillazione**: On/Off (movimento alette aria)
- **Stato in tempo reale**: Temperatura corrente e target

## 🐛 Risoluzione Problemi

### L'integrazione non si carica
- Verifica che i file siano nella posizione corretta
- Controlla i log in "Impostazioni" → "Sistema" → "Log"
- Assicurati che il file si chiami `__init__.py` (con doppio underscore)

### Le entità non appaiono
- Verifica l'IP del webserver nel `configuration.yaml`
- Controlla che il webserver sia raggiungibile dalla rete
- Verifica i numeri dei gruppi configurati

### Debug
Abilita i log dettagliati in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.coster_ew50e: debug
```

## 📝 Documentazione Completa

Per la documentazione completa, troubleshooting avanzato e maggiori informazioni, visita il [README completo](https://github.com/gabrio79/coster_ew50e).

## 💬 Supporto

- 🐛 [Segnala un bug](https://github.com/gabrio79/coster_ew50e/issues)
- 💡 [Richiedi una funzionalità](https://github.com/gabrio79/coster_ew50e/issues)

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT.

---

**Se trovi utile questa integrazione, lascia una ⭐ al repository!**
