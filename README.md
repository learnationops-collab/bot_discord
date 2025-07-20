# Guía de Ramas y Colaboración en el Proyecto del Bot de Discord

¡Bienvenidos al equipo de desarrollo del bot de Discord de Neurocogniciones! Para asegurar un flujo de trabajo eficiente, organizado y colaborativo, utilizaremos un modelo de ramificación (branching) basado en **GitHub Flow** con una rama de integración (`develop`).

Esta guía explica las ramas que usaremos y cómo interactuar con ellas.

## 1. Ramas Principales

Tenemos dos ramas principales que son cruciales para el ciclo de vida del bot:

### `main`

* **Propósito:** Esta rama contiene siempre la **versión más estable y funcional del bot**. Es la rama que se considera lista para producción (es decir, la que debería estar corriendo el bot en su entorno principal).
* **Estado:** Siempre debe estar en un estado desplegable y libre de errores críticos.
* **Interacción:** **Nunca se trabaja directamente en esta rama.** Los cambios solo se fusionan en `main` desde la rama `develop` a través de una Pull Request (PR) una vez que un conjunto de características ha sido probado y validado.

### `develop`

* **Propósito:** Esta es nuestra **rama de integración principal para el desarrollo**. Aquí es donde se consolidan todas las nuevas características y correcciones de errores antes de que estén listas para ser liberadas a `main`.
* **Estado:** Debería ser una versión relativamente estable, adecuada para pruebas internas o para un entorno de *staging*. Puede contener funcionalidades en desarrollo que aún no están en `main`.
* **Interacción:** Todas las ramas de características (`feature/`) y correcciones de errores (`bugfix/`) se fusionan en `develop`. Antes de empezar a trabajar en una nueva tarea, siempre debes basar tu nueva rama en la versión más reciente de `develop`.

## 2. Ramas de Trabajo (Temporales)

Estas ramas se crean para tareas específicas y se eliminan una vez que su trabajo ha sido fusionado.

### `feature/nombre-de-la-caracteristica`

* **Propósito:** Se utilizan para desarrollar **nuevas funcionalidades** o mejoras significativas en el bot. Cada nueva característica debe tener su propia rama `feature`.
* **Convención de Nombres:** `feature/` seguido de una descripción corta y concisa de la característica, usando guiones (`-`) en lugar de espacios (ej., `feature/gestion-recursos-db`, `feature/comando-ticket`).
* **Creación:** Siempre se crean a partir de `develop`.
* **Flujo de Trabajo:**
    1.  Asegúrate de que tu rama `develop` local esté actualizada:
        ```bash
        git checkout develop
        git pull origin develop
        ```
    2.  Crea tu nueva rama de característica y cámbiate a ella:
        ```bash
        git checkout -b feature/nombre-de-la-caracteristica
        ```
    3.  Trabaja en tu código, haz commits pequeños y frecuentes con mensajes descriptivos.
    4.  Sube tu rama a GitHub regularmente:
        ```bash
        git push -u origin feature/nombre-de-la-caracteristica
        ```
    5.  Cuando la característica esté completa y probada localmente, abre una **Pull Request** de tu `feature/` branch a `develop`.

### `bugfix/descripcion-del-bug`

* **Propósito:** Se utilizan para corregir **errores específicos** en el bot.
* **Convención de Nombres:** `bugfix/` seguido de una descripción corta del error (ej., `bugfix/fix-limpiar-comando`).
* **Creación:** Siempre se crean a partir de `develop`. Si es un *bug crítico en producción* que no puede esperar la próxima liberación de `develop`, se podría considerar un `hotfix/` directamente de `main` (pero esto es menos común y se discute con el equipo).
* **Flujo de Trabajo:** Similar a las ramas de característica, se trabaja, se hacen commits, se sube la rama y se abre una Pull Request a `develop`.

## 3. Flujo de Trabajo General (GitHub Flow)

1.  **Clonar el Repositorio:** Si aún no lo has hecho, clona el proyecto:
    ```bash
    git clone [https://github.com/tu-usuario/nombre-del-repositorio.git](https://github.com/tu-usuario/nombre-del-repositorio.git)
    cd nombre-del-repositorio
    ```

2.  **Mantener `main` y `develop` Actualizadas:**
    * Siempre que empieces a trabajar o después de que se fusionen cambios importantes, actualiza tus ramas principales locales:
        ```bash
        git checkout main
        git pull origin main
        git checkout develop
        git pull origin develop
        ```

3.  **Crear una Rama para tu Trabajo:** Para cada tarea (nueva característica o corrección de error), crea una rama desde `develop`:
    ```bash
    git checkout develop
    git pull origin develop # Asegúrate de tener lo último de develop
    git checkout -b feature/tu-tarea-aqui # O bugfix/tu-tarea-aqui
    ```

4.  **Desarrollar y Hacer Commits:**
    * Realiza tus cambios en el código.
    * Añade los archivos modificados: `git add .` (o `git add nombre-del-archivo.py`)
    * Confirma tus cambios con un mensaje descriptivo:
        ```bash
        git commit -m "Descripción concisa de lo que se hizo"
        ```
    * Sube tus cambios a tu rama en GitHub:
        ```bash
        git push -u origin feature/tu-tarea-aqui
        ```

5.  **Abrir una Pull Request (PR):**
    * Una vez que tu trabajo en la rama está completo y probado localmente, ve a GitHub.
    * Verás un botón o mensaje sugiriendo abrir una PR desde tu rama a `develop`.
    * Asegúrate de que la PR apunte de `feature/tu-tarea-aqui` a `develop`.
    * Proporciona una descripción clara de los cambios y cualquier información relevante.

6.  **Revisión de Código y Resolución de Conflictos:**
    * Otros miembros del equipo revisarán tu PR. Pueden solicitar cambios o dejar comentarios.
    * Si hay conflictos de fusión (merge conflicts), deberás resolverlos en tu rama local y volver a subir los cambios antes de que la PR pueda ser fusionada.

7.  **Fusión (Merge):**
    * Una vez que la PR es aprobada y los conflictos resueltos, se fusionará en `develop`.
    * **¡Importante!** Después de que tu PR sea fusionada, puedes eliminar tu rama local y remota (GitHub te dará la opción en la interfaz de la PR).

8.  **Actualizar tu Entorno Local:** Después de cada fusión en `develop`, asegúrate de actualizar tu rama `develop` local antes de empezar una nueva tarea.

## Consejos Adicionales para la Colaboración

* **Comunicación:** Mantén una comunicación constante con el equipo sobre lo que estás trabajando, cualquier problema que encuentres o si necesitas ayuda.
* **Issues de GitHub:** Utiliza la sección "Issues" en GitHub para rastrear tareas, errores y discusiones. Asigna issues a los colaboradores para mayor claridad.
* **Commits Pequeños:** Haz commits pequeños y frecuentes. Esto facilita la revisión de código y la resolución de conflictos.
* **Pruebas:** Si es posible, ejecuta pruebas locales antes de abrir una PR para asegurarte de que tus cambios no rompan la funcionalidad existente.

¡Esperamos que esta guía sea útil para tu trabajo colaborativo en el bot! Si tienes alguna pregunta, no dudes en consultarla con el equipo.