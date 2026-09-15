# Manual de Usuario KairOs

El Manual de Usuario completo, ilustrado con capturas de pantalla reales anotadas paso a paso con recuadros rojos y números guía, se encuentra alojado en:

👉 **[docs/manual_usuario/MANUAL_DE_USUARIO.md](../docs/manual_usuario/MANUAL_DE_USUARIO.md)**

---

## 📸 Capturas de Pantalla Anotadas

Todas las capturas del sistema se encuentran organizadas en:
👉 **[docs/manual_usuario/capturas/](../docs/manual_usuario/capturas/)**

## 🔄 Actualización Automatizada

Si alguna vista o ruta (por ejemplo, `/espacios/mapa` o cualquier modal) es refactorizada o cambia de diseño, ejecute el siguiente comando para re-generar todas las capturas con sus recuadros actualizados en vivo:

```bash
python scripts/generar_manual_capturas.py
```

## 📄 Exportación a Documento Word (.docx)

Para compilar este manual o la documentación completa a un documento Word profesional:

```bash
python scripts/exportar_documentacion_word.py
```
