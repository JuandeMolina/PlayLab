# utils.py


def format_duration_ms(milliseconds: int) -> str:
    if milliseconds < 0:
        return "Duración inválida"

    total_seconds = milliseconds // 1000

    # Calcula las unidades de tiempo
    days = total_seconds // (24 * 3600)
    remaining_seconds = total_seconds % (24 * 3600)

    hours = remaining_seconds // 3600
    remaining_seconds %= 3600

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    parts = []

    # Añade cada parte a la lista solo si su valor es mayor que cero
    if days > 0:
        parts.append(f"{days} día{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hora{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minuto{'s' if minutes > 1 else ''}")

    # Los segundos se añaden si son mayores que cero, O si todas las unidades anteriores son cero (para el caso de 0 segundos o solo segundos)
    if (
        seconds > 0 or not parts
    ):  # Corregido para que "0 segundos" se muestre si la duración es 0 ms, o si es solo segundos.
        parts.append(f"{seconds} segundo{'s' if seconds > 1 else ''}")

    # Une las partes en una cadena legible
    if not parts:
        return "0 segundos"  # Caso para una duración de 0 milisegundos

    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} y {parts[1]}"
    else:
        # Para más de dos partes, une todas menos la última con comas,
        # y la última con " y "
        return ", ".join(parts[:-1]) + f" y {parts[-1]}"
