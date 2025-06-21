# GitHub Copilot Instructions

## Contexto del Proyecto
Siempre debes tener en cuenta el contexto completo del proyecto al generar sugerencias. Analiza los archivos existentes y las estructuras actuales antes de proponer cambios. No asumas una solución genérica sin antes revisar la arquitectura existente.

## Reglas de trabajo

1. **Referencia obligatoria al archivo en modo ask**:
   - Toda sugerencia debe incluir explícitamente:
     - Ruta completa del archivo (`path/to/file`)
     - Nombre del archivo
     - Código que se debe crear o modificar
   - Formato sugerido para los cambios:
     ```
     Apply to: path/to/file.ext
     ```

2. **Prioridad en reutilización**:
   - Antes de sugerir crear un nuevo archivo, revisa si puede modificarse o reutilizarse uno ya existente.
   - La creación de nuevos archivos solo está permitida si:
     - Existe una justificación clara por *best practices* o arquitectura.
     - No hay un archivo existente adecuado para la funcionalidad requerida.

3. **Organización y arquitectura**:
   - Respeta y extiende la arquitectura actual del proyecto.
   - Si el proyecto sigue una estructura por dominios, capas, o módulos, adáptate a dicha estructura.
   - Cualquier propuesta de refactorización mayor debe explicar por qué mejora el diseño actual.

4. **Formato de respuesta preferido aplica unicamente para modo "ASK" no para modo Agent**:
   - Respuestas concisas, claras y orientadas a la acción.
   - Estructura preferida:
     ```
     Apply to: path/to/file.js

     Código:
     (código sugerido aquí)

     Justificación:
     (si aplica, breve explicación del cambio o por qué se reutiliza/modifica un archivo)
     ```

## Buenas prácticas
- Utiliza comentarios en el código para marcar zonas nuevas o modificadas.
- Si detectas código duplicado o funcionalidad similar, sugiere consolidación.
- Siempre escribe código limpio y legible, siguiendo los estándares del lenguaje o framework en uso.

## Tono y estilo
- El enfoque debe ser técnico y profesional, sin explicaciones innecesarias si el código es autoexplicativo.
- Resalta únicamente lo esencial para aplicar los cambios correctamente.

---
