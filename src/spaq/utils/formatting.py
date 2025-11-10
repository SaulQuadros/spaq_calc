def fmt_lpm(x: float) -> str:
    return f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
