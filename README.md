# Private Teams Bot

Crea canales de texto y voz, privados para equipos.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the package.

```bash
pip install -r requirements.txt
```

Crea el archivo `.env` con el token de Discord:
```bash
echo DISCORD=<token> > .env
```

## Commands

Crear un equipo:
```
!team "Nombre Equipo" @User1#1234 @User2#1234 @User3#1234 @User4#1234
```

Eliminar un equipo:
```
!unteam "Nombre Equipo"
```

Sacar a miembro de un equipo:
```
!kick "Nombre Equipo" @User#1234
```

## License
[MIT](LICENSE)
