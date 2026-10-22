#!/usr/bin/env python3
"""
Calculadora Interactiva en Python
Una simple calculadora con interfaz de línea de comandos.
"""


def mostrar_menu():
    """Muestra el menú de opciones."""
    print("\n" + "=" * 40)
    print("        CALCULADORA INTERACTIVA")
    print("=" * 40)
    print("Operaciones disponibles:")
    print("  (+)  Suma")
    print("  (-)  Resta")
    print("  (*)  Multiplicación")
    print("  (/)  División")
    print("  (s)  Salir")
    print("=" * 40)


def sumar(a: float, b: float) -> float:
    """Suma dos números."""
    return a + b


def restar(a: float, b: float) -> float:
    """Resta dos números."""
    return a - b


def multiplicar(a: float, b: float) -> float:
    """Multiplica dos números."""
    return a * b


def dividir(a: float, b: float) -> float:
    """Divide dos números."""
    if b == 0:
        raise ValueError("No se puede dividir entre cero")
    return a / b


def obtener_numero(mensaje: str) -> float:
    """Obtiene un número válido del usuario."""
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("❌ Error: Por favor ingresa un número válido")


def ejecutar_operacion(operacion: str, num1: float, num2: float) -> float | None:
    """Ejecuta la operación solicitada."""
    operaciones = {
        "+": sumar,
        "-": restar,
        "*": multiplicar,
        "/": dividir,
    }

    if operacion not in operaciones:
        print("❌ Operación no válida")
        return None

    try:
        resultado = operaciones[operacion](num1, num2)
        return resultado
    except ValueError as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Función principal - bucle de la calculadora."""
    print("\n¡Bienvenido a la Calculadora Interactiva!")

    while True:
        mostrar_menu()

        operacion = input("\nElige una operación (+, -, *, /, s): ").strip().lower()

        if operacion == "s":
            print("\n👋 ¡Hasta luego!")
            break

        if operacion not in ["+", "-", "*", "/"]:
            print("❌ Operación no válida. Intenta de nuevo.")
            continue

        # Obtener números del usuario
        num1 = obtener_numero("\nIngresa el primer número: ")
        num2 = obtener_numero("Ingresa el segundo número: ")

        # Ejecutar operación
        resultado = ejecutar_operacion(operacion, num1, num2)

        if resultado is not None:
            print(f"\n✅ Resultado: {num1} {operacion} {num2} = {resultado}")


if __name__ == "__main__":
    main()
