# core/base_module.py
from abc import ABC, abstractmethod

class BaseThreat(ABC):
    """Interfaz obligatoria para todos los scripts de simulación de amenazas."""
    
    @abstractmethod
    def ejecutar(self) -> None:
        """Lanza la simulación del malware."""
        pass

    @abstractmethod
    def limpiar(self) -> None:
        """Revierte los efectos del malware (opción --clean)."""
        pass


class BaseDefense(ABC):
    """Interfaz obligatoria para todos los scripts de respuesta y defensa."""
    
    @abstractmethod
    def analizar_y_mitigar(self) -> None:
        """Ejecuta el escaneo, detección y restauración."""
        pass