from decimal import Decimal, ROUND_HALF_UP

from num2words import num2words


def _plural(n: int, one: str, few: str, many: str) -> str:
    n100 = abs(n) % 100
    n10 = abs(n) % 10
    if 11 <= n100 <= 19:
        return many
    if n10 == 1:
        return one
    if 2 <= n10 <= 4:
        return few
    return many


def format_money(amount) -> str:
    value = Decimal(str(amount)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


def format_money_rub(amount) -> str:
    return f"{format_money(amount)} ₽"


def amount_in_words(amount, *, capitalize: bool = True, kopecks_as_words: bool = False) -> str:
    value = Decimal(str(amount)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP)
    rubles = int(value)
    kopecks = int((value - rubles) * 100)

    rubles_text = num2words(rubles, lang="ru")
    rub_word = _plural(rubles, "рубль", "рубля", "рублей")
    kop_word = _plural(kopecks, "копейка", "копейки", "копеек")

    if kopecks_as_words:
        kop_text = num2words(kopecks, lang="ru")
        text = f"{rubles_text} {rub_word} {kop_text} {kop_word}"
    else:
        text = f"{rubles_text} {rub_word} {kopecks:02d} {kop_word}"

    if capitalize:
        return text[:1].upper() + text[1:]
    return text


def items_word(count: int) -> str:
    return _plural(count, "наименование", "наименования", "наименований")


def receipt_summary(count: int, amount) -> str:
    count_words = num2words(count, lang="ru", gender="n")
    money = amount_in_words(amount, capitalize=False, kopecks_as_words=True)
    return f"Всего {count_words} {items_word(count)} на сумму {money}"
