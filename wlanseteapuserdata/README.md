# WLANSetEAPUserData Directory

Este directorio debe contener el ejecutable `WLANSetEAPUserData.exe`.

## Descarga

Puedes obtener este ejecutable de:
- GitHub: https://github.com/karpetrosyan/WLANSetEAPUserData
- O compilarlo desde el código fuente

## Uso

El script `profile_connector.py` buscará el ejecutable en:
```
wlanseteapuserdata/WLANSetEAPUserData.exe
```

## Sintaxis

```
WLANSetEAPUserData.exe <SSID> <interface_index> <credentials_xml> /i
```

Ejemplo:
```
WLANSetEAPUserData.exe gencat_ENS_EDU 1 xml/credentials.xml /i
```

## Notas

- El índice de interfaz `1` corresponde a la primera interfaz inalámbrica
- El flag `/i` indica importar las credenciales al sistema
- Requiere permisos de administrador para ejecutarse
