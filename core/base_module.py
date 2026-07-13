from abc import ABC, abstractmethod
import argparse

class BaseLabModule(ABC):
    """Clase base abstracta que define la estructura obligatoria de cada módulo del laboratorio."""

    def __init__(self, nombre: str, codigo: str):
        self.nombre = nombre
        self.codigo = codigo

    @abstractmethod
    def simular(self) -> None:
        """Lógica principal que ejecuta la simulación de la amenaza."""
        pass

    @abstractmethod
    def defender(self) -> None:
        """Lógica principal que ejecuta las contramedidas o mitigación."""
        pass

    @abstractmethod
    def revertir(self) -> None:
        """Equivalente a --clean. Deja el entorno de pruebas exactamente como estaba."""
        pass

    def ejecutar_cli(self) -> None:
        """Manejador común de argumentos por si los scripts se lanzan directamente."""
        parser = argparse.ArgumentParser(description=f"Módulo {self.codigo}: {self.nombre}")
        parser.add_argument("--simular", action="store_true", help="Ejecuta la simulación")
        parser.add_argument("--defender", action="store_true", help="Ejecuta la defensa")
        parser.add_argument("--clean", action="store_true", help="Limpia los efectos del módulo")
        
        args = parser.parse_args()
        
        if args.clean:
            self.revertir()
        elif args.defender:
            self.defender()
        elif args.simular:
            self.simular()
        else:
            # Comportamiento por defecto al llamarlo plano
            self.simular()