# Especificación del Módulo: Facturación y Pagos (Junami 2.0)

## 1. Objetivo del Módulo
Gestionar los ingresos de la clínica, el registro de pagos de pacientes, el cálculo de deudas y la liquidación de honorarios. Extraer esta lógica de `app.py` hacia un Blueprint en `rutas/facturacion.py`.

## 2. Rutas y Endpoints a migrar
* `GET /facturacion` - Panel principal de finanzas y estado de cuentas.
* `POST /facturacion/registrar_pago` - Ingreso de un nuevo cobro al sistema.
* *(Cualquier otra ruta referida exclusivamente a cobros, recibos o finanzas)*

## 3. Reglas de Negocio Estrictas (Business Logic)

### 3.1. Restricción de Seguridad por Rol (Crítico)
* La información financiera es confidencial. Si el usuario en sesión (`session['usuario_actual']`) tiene `jerarquia == 'Auxiliar'`, se le debe denegar el acceso y redirigir inmediatamente a `dashboard_personal_bp.dashboard2`.

### 3.2. Carga y Cálculo de Datos
* Importar `cargar_datos` desde `utils.py`.
* Leer los registros necesarios (`pacientes.json`, `sesiones.json` y el archivo de pagos/finanzas si existe).
* Mantener estricta fidelidad a la lógica original que calcula:
  * Deuda total por paciente (sesiones realizadas vs. pagos registrados).
  * Honorarios a liquidar por profesional.
* Al registrar un pago (POST), asegurar la inyección automática de la fecha actual y el usuario que recibe/registra el pago.

## 4. Integración en app.py (Frontend)
* No realizar modificaciones visuales en las plantillas HTML de facturación.
* Eliminar todas las rutas financieras originales de `app.py`.
* Registrar el Blueprint `facturacion_bp`.
* Asegurar mediante `app.add_url_rule` que los enlaces del menú lateral (`url_for('facturacion')`) sigan resolviendo correctamente para no romper la navegación.