# Private Teams Bot

Crea canales de texto y voz, privados para equipos.

## Instalación

Para instalar las bibliotecas requeridas, utiliza el manejador de paquetes [pip](https://pip.pypa.io/en/stable/).

```bash
pip install -r requirements.txt
```

Crea el archivo `.env` con el token de Discord:
```bash
echo DISCORD=<token> > .env
```

## Comandos

Crear un equipo:
```
!team "Nombre Equipo" @User1#1234 @User2#1234 @User3#1234 @User4#1234
```

Eliminar un equipo:
```
!unteam #canal-equipo
```

Sacar a miembro de un equipo:
```
!kick #canal-equipo @User#1234
```

Identificar usuario:
```
!usuario <email>
```

## Licencia
[MIT](LICENSE)
