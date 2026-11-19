# Guía de modelos y migraciones

Esta guía explica cómo diseñar y modificar los modelos con Flask-SQLAlchemy y cómo mantener actualizada la base de datos mediante Flask-Migrate.

## 1. Conceptos básicos

Un **modelo** es una clase de Python que representa una tabla de la base de datos. Sus atributos definen las columnas y sus restricciones.

Una **migración** es un archivo que describe un cambio en el esquema de la base: crear una tabla, agregar una columna, modificar un índice, etc. Las migraciones permiten que todas las personas del equipo apliquen los mismos cambios sin borrar sus datos.

Es importante distinguir dos operaciones:

- Modificar un modelo cambia el código Python, pero **no modifica automáticamente una base existente**.
- Ejecutar `flask db upgrade` aplica las migraciones pendientes y actualiza la base.

## 2. Crear un modelo

Los modelos se encuentran en `src/proyecto/models/`. Un modelo sencillo tiene esta forma:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.extensions import db


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"
```

En este ejemplo:

- `db.Model` registra la clase como un modelo de SQLAlchemy.
- `__tablename__` define el nombre de la tabla.
- `id` es la clave primaria.
- `String(30)` limita el nombre a 30 caracteres.
- `nullable=False` exige que el nombre tenga un valor.
- `unique=True` impide que dos categorías tengan el mismo nombre.

Las restricciones de la base complementan a las validaciones de los formularios o servicios. No conviene depender únicamente de una de ellas.

### Tipos y valores opcionales

La anotación de Python debe corresponder con la restricción de la columna:

```python
# Obligatorio: no admite None
name: Mapped[str] = mapped_column(String(30), nullable=False)

# Opcional: puede contener NULL
description: Mapped[str | None] = mapped_column(String(200), nullable=True)
```

### Valores predeterminados

Usar `default` cuando la aplicación deba asignar un valor al crear el objeto:

```python
from datetime import datetime, UTC


created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(UTC),
    nullable=False,
)
```

Un valor predeterminado no sustituye a una validación y no modifica los registros ya existentes.

### Registrar el modelo

El modelo debe importarse antes de generar una migración. Si se agrega un archivo nuevo, hay que exportarlo desde `src/proyecto/models/__init__.py`, como se hace con los demás modelos.

Si un modelo no se importa, SQLAlchemy no lo registra y la migración automática puede omitirlo.

### Relaciones entre modelos

Para una relación en la que una categoría tiene muchas preguntas:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Question(db.Model):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id"),
        nullable=False,
    )
    category: Mapped[Category] = relationship(back_populates="questions")
```

Y en `Category`:

```python
questions: Mapped[list[Question]] = relationship(back_populates="category")
```

`category_id` es la columna real que guarda la clave foránea; `category` y `questions` permiten navegar la relación desde Python. Antes de agregar una relación, hay que decidir si el registro hijo puede existir sin el padre y qué debe ocurrir al borrarlo. No usar borrados en cascada sin comprobar ese comportamiento.

## 3. Preparación inicial de las migraciones

Este paso se realiza **una sola vez en el repositorio**, no en cada computadora:

```bash
uv run flask --app proyecto db init
```

El comando crea el directorio `migrations/`. Ese directorio, incluidos los archivos de `migrations/versions/`, debe quedar guardado en Git.

Si el directorio ya existe, no ejecutar `db init` nuevamente.

Para crear la primera migración sobre una base vacía:

```bash
uv run flask --app proyecto db migrate -m "create initial tables"
uv run flask --app proyecto db upgrade
```

## 4. Flujo habitual al modificar modelos

### Paso 1: actualizar la base antes de empezar

Después de descargar cambios del repositorio:

```bash
uv run flask --app proyecto db upgrade
```

Esto aplica las migraciones que todavía no estén aplicadas localmente.

### Paso 2: modificar los modelos

Crear la tabla, agregar la columna o cambiar la relación necesaria. Conviene hacer cambios pequeños y fáciles de describir.

No cambiar manualmente una migración que ya fue compartida y aplicada por otras personas. Para corregir el esquema se crea una migración nueva.

### Paso 3: generar la migración

```bash
uv run flask --app proyecto db migrate -m "add description to category"
```

El mensaje debe explicar brevemente el cambio. El comando genera un archivo nuevo en `migrations/versions/`; no aplica todavía el cambio a la base.

El archivo contiene principalmente:

- `upgrade()`: operaciones necesarias para avanzar.
- `downgrade()`: operaciones para revertir ese cambio, cuando sea posible.

### Paso 4: revisar el archivo generado

Abrir la migración y comprobar que:

- modifica las tablas y columnas esperadas;
- no elimina tablas o columnas que deberían conservarse;
- las restricciones y los tipos sean correctos;
- los cambios detectados en modelos ajenos correspondan realmente a este cambio.

La generación automática compara los modelos con la base, pero no entiende la intención del cambio. Por ejemplo, un renombre puede aparecer como una eliminación seguida de una creación, lo que podría perder datos. En ese caso hay que editar la migración para expresar el renombre antes de aplicarla.

Si la migración no es correcta y todavía no se compartió ni se aplicó, se puede borrar ese archivo nuevo, corregir los modelos y volver a generarla.

### Paso 5: aplicar la migración

```bash
uv run flask --app proyecto db upgrade
```

Para indicar explícitamente que se quiere llegar a la última versión:

```bash
uv run flask --app proyecto db upgrade head
```

### Paso 6: probar y compartir

Ejecutar los tests y comprobar manualmente el comportamiento afectado. Después, incluir en el mismo cambio de Git:

- los modelos modificados;
- la migración generada;
- los tests y demás cambios relacionados.

Nunca subir solamente el modelo: el resto del equipo necesita la migración para actualizar su base.

## 5. Trabajo en equipo

Al recibir cambios de otra persona:

```bash
uv run flask --app proyecto db upgrade
uv run pytest
```

Reglas para evitar problemas:

1. Coordinarse cuando dos ramas modifican modelos al mismo tiempo.
2. No editar ni borrar migraciones ya compartidas.
3. No generar una migración sin revisar primero su contenido.
4. Resolver los conflictos de migraciones antes de crear más ramas del historial.
5. Hacer una copia de seguridad antes de migraciones destructivas en una base con datos importantes.

Si aparecen dos migraciones con la misma revisión anterior, el historial tiene dos cabezas. Hay que revisarlas y unificarlas antes de continuar; no borrar una simplemente para que el comando funcione.

## 6. Base de datos de desarrollo y base de tests

Las bases persistentes de desarrollo y producción se actualizan con migraciones:

```bash
uv run flask --app proyecto db upgrade
```

Los tests usan SQLite en memoria y parten de una base vacía. En ellos se puede crear el esquema directamente:

```python
with app.app_context():
    db.create_all()
```

Y limpiarlo después:

```python
with app.app_context():
    db.drop_all()
```

`create_all()` crea tablas que no existen, pero **no altera tablas existentes**. Por eso es útil para tests descartables, pero no reemplaza a las migraciones en una base persistente.

No hace falta ejecutar todas las migraciones antes de cada test. Sí conviene probar por separado que las migraciones funcionan sobre una base vacía antes de compartir cambios importantes.

## 7. Comandos útiles

```bash
# Aplicar todas las migraciones pendientes
uv run flask --app proyecto db upgrade

# Generar una migración después de modificar modelos
uv run flask --app proyecto db migrate -m "descripción breve"

# Mostrar la revisión actual de la base
uv run flask --app proyecto db current

# Mostrar el historial de migraciones
uv run flask --app proyecto db history

# Volver una revisión hacia atrás, si downgrade está bien definido
uv run flask --app proyecto db downgrade
```

`downgrade` puede eliminar columnas, tablas o datos. No usarlo como sustituto de una copia de seguridad ni ejecutarlo en una base compartida sin revisar antes las operaciones.

## 8. Problemas frecuentes

### «No se detectan cambios»

Comprobar que:

- el modelo nuevo esté importado en `src/proyecto/models/__init__.py`;
- se esté ejecutando el comando con la aplicación y configuración correctas;
- la base tenga aplicadas las migraciones anteriores;
- el cambio realmente modifique el esquema y no solamente métodos de Python.

### «La migración quiere borrar una tabla o columna»

Detenerse y revisarla. Puede deberse a un modelo que no fue importado, una diferencia de configuración o una detección incorrecta. No aplicarla hasta entender el motivo.

### «Mi base no coincide con los modelos»

Consultar la revisión actual:

```bash
uv run flask --app proyecto db current
```

Luego aplicar las migraciones pendientes:

```bash
uv run flask --app proyecto db upgrade
```

Si se modificó la base manualmente, puede ser necesario corregir esa base antes de continuar. Conviene pedir ayuda al equipo en lugar de borrar migraciones o datos.

## 9. Lista de comprobación antes de compartir un cambio

- [ ] Los modelos nuevos están importados y registrados.
- [ ] Las columnas obligatorias y opcionales tienen tipos coherentes.
- [ ] La migración tiene un mensaje descriptivo.
- [ ] Revisé `upgrade()` y `downgrade()`.
- [ ] La migración no contiene borrados inesperados.
- [ ] Ejecuté `flask db upgrade` correctamente.
- [ ] Ejecuté los tests.
- [ ] Incluí los modelos y la migración en el mismo cambio.
