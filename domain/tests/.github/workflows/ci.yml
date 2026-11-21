from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from domain.services import (
    ReglaNegocioError,
    ServicioAsistencia,
    calcular_vencimiento,
    validar_monto_pago,
    validar_permiso,
    verificar_vigencia_membresia,
)


def test_calcular_vencimiento_30_dias():
    # Arrange
    inicio = date(2026, 11, 1)
    dias = 30

    # Act
    resultado = calcular_vencimiento(inicio, dias)

    # Assert
    assert resultado == date(2026, 12, 1)


def test_verificar_vigencia_en_fecha_limite():
    # Arrange
    vencimiento = date(2026, 11, 20)
    hoy = date(2026, 11, 20)

    # Act
    vigente = verificar_vigencia_membresia(vencimiento, True, hoy)

    # Assert
    assert vigente is True


def test_validar_monto_menor_al_costo_falla():
    # Arrange
    monto = Decimal("200.00")
    costo = Decimal("500.00")

    # Act & Assert
    with pytest.raises(ReglaNegocioError):
        validar_monto_pago(monto, costo)


def test_recepcionista_no_puede_dar_de_baja_socio():
    # Arrange
    rol = "Recepcionista"

    # Act
    permitido = validar_permiso(rol, "dar_de_baja_socio")

    # Assert
    assert permitido is False


def test_registrar_entrada_rechaza_membresia_vencida_con_mock():
    # Arrange
    membresia_repo = MagicMock()
    asistencia_repo = MagicMock()
    reloj = MagicMock()

    reloj.hoy.return_value = date(2026, 11, 21)
    membresia_repo.obtener_activa_por_socio.return_value = {
        "fecha_vencimiento": date(2026, 11, 20),
        "pagada": True,
    }
    servicio = ServicioAsistencia(membresia_repo, asistencia_repo, reloj)

    # Act & Assert
    with pytest.raises(ReglaNegocioError):
        servicio.registrar_entrada(id_socio=1, id_usuario=2)

    asistencia_repo.guardar.assert_not_called()


def test_registrar_entrada_evita_duplicado_mismo_dia_con_mock():
    # Arrange
    membresia_repo = MagicMock()
    asistencia_repo = MagicMock()
    reloj = MagicMock()

    reloj.hoy.return_value = date(2026, 11, 20)
    reloj.ahora.return_value = datetime(2026, 11, 20, 9, 0, 0)
    membresia_repo.obtener_activa_por_socio.return_value = {
        "fecha_vencimiento": date(2026, 12, 20),
        "pagada": True,
    }
    asistencia_repo.existe_entrada_en_fecha.return_value = True
    servicio = ServicioAsistencia(membresia_repo, asistencia_repo, reloj)

    # Act & Assert
    with pytest.raises(ReglaNegocioError):
        servicio.registrar_entrada(id_socio=1, id_usuario=2)

    asistencia_repo.guardar.assert_not_called()
