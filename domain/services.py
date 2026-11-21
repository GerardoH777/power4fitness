from datetime import date, timedelta
from decimal import Decimal


class ReglaNegocioError(Exception):
    pass


def calcular_vencimiento(fecha_inicio: date, duracion_dias: int) -> date:
    if duracion_dias <= 0:
        raise ReglaNegocioError("La duración debe ser mayor a cero.")
    return fecha_inicio + timedelta(days=duracion_dias)


def validar_monto_pago(monto: Decimal, costo_membresia: Decimal) -> bool:
    if monto <= Decimal("0.00"):
        raise ReglaNegocioError("El monto debe ser mayor a cero.")
    if monto < costo_membresia:
        raise ReglaNegocioError("El monto no puede ser menor al costo.")
    return True


def verificar_vigencia_membresia(fecha_vencimiento: date, pagada: bool, fecha_actual: date) -> bool:
    return pagada and fecha_actual <= fecha_vencimiento


def validar_permiso(rol: str, permiso: str) -> bool:
    permisos_recepcionista = {
        "iniciar_sesion",
        "registrar_socio",
        "registrar_pago",
        "registrar_entrada",
    }
    permisos_admin = permisos_recepcionista | {
        "dar_de_baja_socio",
        "administrar_membresias",
        "exportar_reportes",
    }
    if rol == "Administrador":
        return permiso in permisos_admin
    if rol == "Recepcionista":
        return permiso in permisos_recepcionista
    return False


class ServicioAsistencia:
    def __init__(self, membresia_repo, asistencia_repo, reloj):
        self.membresia_repo = membresia_repo
        self.asistencia_repo = asistencia_repo
        self.reloj = reloj

    def registrar_entrada(self, id_socio: int, id_usuario: int):
        hoy = self.reloj.hoy()
        membresia = self.membresia_repo.obtener_activa_por_socio(id_socio)

        if membresia is None or not verificar_vigencia_membresia(
            membresia["fecha_vencimiento"], membresia["pagada"], hoy
        ):
            raise ReglaNegocioError("Membresía vencida o no pagada.")

        if self.asistencia_repo.existe_entrada_en_fecha(id_socio, hoy):
            raise ReglaNegocioError("Ya existe una entrada registrada hoy.")

        return self.asistencia_repo.guardar(
            id_socio=id_socio,
            id_usuario=id_usuario,
            fecha_hora=self.reloj.ahora(),
        )
