# Sitio Q&A

Sitio de preguntas y respuestas hecho en Flask.
UNRC 2026.

## Ejecución
1. Clonar el repositorio
```bash
git clone https://github.com/lau-luna/proyecto-isi
```
2. Hacer upgrade de las migraciones
```bash
uv run flask --app proyecto db upgrade head
```
3. Correr tests
```bash
uv run pytest -vv
```
4. Levantar la aplicación
```bash
uv run flask --app proyecto run
```

Actualmente cuenta con mocks de datos para mostrar el funcionamiento de la aplicación. Están definidos en `src/seeds.py` y se ejecutan con `seed_all()` en la app factory cuando se ejecuta la aplicación. Esto ocurre la primera vez que se hace `flask run`, cargándose una única vez en la base de datos.

## Integrantes

- Lautaro Eduardo Eber Luna
- Hugo Rodrigo Saavedra Diaz
- Juan Pablo Ollo
- Catalina Gnesutta

## Documentación

La documentación del proyecto se encuentra en la carpeta [docs](docs/).

### Entregables

- [Justificación de patrones](docs/deliverables/pattern-justification.md)
- [Diagrama de clases — fuente PlantUML](docs/deliverables/class-diagram.puml)

![Diagrama de clases final](docs/deliverables/class-diagram.png)

## Librerías

- Jinja2
- SQLAlchemy
- Pytest
- Alembic
- Ruff

## A futuro

Se podría guardar el cuerpo de las preguntas y respuestas en formato Markdown como opción para brindar un cuerpo detallado con todas las características que provee un `.md`.

Librerías interesantes:

- [OverType](https://overtype.dev/)
- [md-block](https://md-block.verou.me/)

Dockerizar.
