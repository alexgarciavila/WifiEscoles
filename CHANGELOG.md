# Changelog

## [1.2.4] - 2026-01-01

### Afegit

- **Atribució i agraïments**: Afegida secció al README reconeixent l'ús del component **WLANSetEAPUserData** desenvolupat per Simon Rozman ([rozmansi/WLANSetEAPUserData](https://github.com/rozmansi/WLANSetEAPUserData)). Aquest component és essencial per configurar credencials d'usuari EAP per a connexions WLAN a Windows.

---

## [1.2.3] - 2025-12-25

### Canviat

- **Internacionalització completa en català**: Tots els missatges de sortida, logs i excepcions ara utilitzen el sistema de traduccions centralitzat.
- Els docstrings i comentaris romanen en castellà per a mantenibilitat del codi

### Arreglat

- **Botó de desconnexió**: Solucionat error `AttributeError` quan es clicava el botó de desconnectar.
- **Bloqueig de la GUI durant desconnexió**: La desconnexió ara s'executa en un fil de fons, evitant que l'aplicació es pengi durant uns segons.
- **Finestra de CMD en desconnectar**: Ocultada la finestra de terminal que apareixia breument durant l'operació de desconnexió..
- **Consistència de traduccions**: Centralitzades totes les traduccions a `translations.py`, eliminant textos hardcodejats.

---

## [1.2.2]

### Arreglat

- **Gestió d'avisos de permisos de Windows**: Els missatges d'avís de permisos d'ubicació o elevació ja no es tracten com a errors crítics. La connexió WiFi es considera exitosa encara que Windows mostri aquests avisos, ja que la connexió s'estableix correctament.
- **Verificació de connexió més permissiva**: Si la verificació automàtica de la connexió falla per restriccions de permisos de Windows, l'aplicació informa que la connexió pot haver-se establert correctament en lloc de mostrar un error.
- **Codificació de caràcters en logs**: Millorada la decodificació de la sortida dels comandos de Windows. Ara els logs mostren correctament els caràcters especials (accentuats, ñ, etc.) en lloc de mostrar-los corruptes (tipus "ubicaci├│n").

---

## [1.2.1] - 2025-12-16

### Arreglat

- **Arxiu Wifi.json no trobat a l'executable**: Solucionat l'error que impedia trobar `Wifi.json` en executar `WifiEduca.exe`.
- **Ruta de favorits en executable**: Corregit el path de `fav.json`, assegurant que els favorits es guardin a la ubicació correcta.

---

## [1.2.0] - 2025-12-16

### Afegit

- **Sistema de Favorits**: Els usuaris poden marcar centres com a favorits per accedir-hi més ràpidament.
  - Icona ⭐ al costat de cada centre per marcar/desmarcar favorits
  - Botó toggle al header per alternar entre vista "Tots els centres" i "Només favorits"
  - Persistència automàtica dels favorits a `Json/fav.json`
  - Cerca dins de favorits quan el mode favorits està actiu
  - Auto-neteja de favorits obsolets (centres eliminats del catàleg)

### Canviat

- **Missatges d'error millorats**: Els errors de xarxa (netsh) ara mostren missatges genèrics a l'usuari i els detalls tècnics es registren als logs.
  - L'usuari veu: "Error de xarxa. Revisa els logs per a més detalls."
  - Els logs contenen el detall tècnic complet per a depuració

### Arreglat

- **Error de permisos d'ubicació**: L'avís "Los comandos de shell de red necesitan permiso de ubicación..." ja no es mostra com a error, ja que la connexió funciona correctament.

---

## [1.1.0] - 2025-12-13

### Afegit

- **Tema Fosc**: Interfície amb tema fosc permanent per millorar la visibilitat i reduir la fatiga visual.
  - Tema fosc aplicat a tots els components de la GUI
  - No depèn de la configuració del sistema operatiu

---

## [1.0.0] - Versió inicial

### Afegit

- Connexió automàtica a la xarxa WiFi `gencat_ENS_EDU`
- Gestió de credencials per centre educatiu
- Cerca de centres per codi o nom
- Instal·lació automàtica del perfil WiFi
- Configuració de credencials EAP
- Verificació de connexió
