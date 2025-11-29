# 📶 WiFi Connector - Centres Educatius de Catalunya

Aplicació per connectar-se fàcilment a la xarxa WiFi **gencat_ENS_EDU** dels centres educatius de Catalunya.

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue?logo=windows)
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)
![License](https://img.shields.io/badge/License-GPLv3-blue)

## 🎯 Per a què serveix?

Aquesta aplicació simplifica la connexió a la xarxa WiFi dels centres educatius catalans. En lloc de configurar manualment les credencials i el perfil de xarxa, només cal:

1. **Seleccionar** el teu centre educatiu de la llista
2. **Fer clic** a "Connectar"
3. **Llest!** Ja estàs connectat

## ✨ Característiques

- 🖥️ Interfície gràfica senzilla i moderna
- 🔍 Cerca ràpida de centres per nom o codi
- 🔐 Gestió segura de credencials
- ⚡ Connexió automàtica en un sol clic
- 📦 Disponible com executable (no cal instal·lar Python)

## 🚀 Començar

### Opció 1: Executable (Recomanat)

Descarrega l'executable i l'arxiu de credencials:

```
📁 La meva carpeta/
   ├── WifiEduca.exe
   └── 📁 Json/
       └── wifi.json
```

Fes doble clic a `WifiEduca.exe` i ja pots connectar-te!

### Opció 2: Des del codi font

```powershell
# Clona el repositori
git clone <repository-url>
cd WifiEscoles

# Crea i activa l'entorn virtual
python -m venv venv
.\venv\Scripts\activate

# Instal·la les dependències
pip install -r requirements.txt

# Executa l'aplicació
python main.py
```

## ⚙️ Configuració

### Arxiu de credencials (`Json/wifi.json`)

Crea un arxiu JSON amb les credencials dels centres:

```jso del co
[
  {
    "Codi": "08012345",
    "Centre": "Institut Example Barcelona",
    "Usuari": "W08012345",
    "Contrasenya": "la_teva_contrasenya"
  }
]
```

> ⚠️ **Important**: Aquest arxiu conté informació sensible. No el comparteixis!

## 📋 Requisits

- **Sistema Operatiu**: Windows 10 o Windows 11
- **Xarxa**: Cal estar dins del rang de la xarxa WiFi del centre
- **Permisos**: No requereix permisos d'administrador

## 🛠️ Per a desenvolupadors

### Generar l'executable

```powershell
.\venv\Scripts\Activate.ps1
python -m PyInstaller build_exe.spec --clean
```

L'executable es generarà a `dist/WifiEduca.exe`

### Executar els tests

```powershell
.\venv\Scripts\Activate.ps1
pytest --cov=wifi_connector
```

## 📝 Llicència

Aquest projecte està llicenciat sota la [GNU General Public License v3.0](LICENSE).

## 🤝 Contribucions

Les contribucions són benvingudes! Obre un issue per reportar problemes o suggerir millores.
