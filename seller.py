from pathlib import Path

_ROOT = Path(__file__).resolve().parent

LOGO_PATH = _ROOT / "assets" / "logo.png"
LOGO_CANDIDATES = (
    LOGO_PATH,
    _ROOT / "assets" / "logo.jpg",
    _ROOT / "assets" / "logo.jpeg",
    _ROOT / "assets" / "logo.webp",
)

SELLER_NAME = "ИП Клименко Андрей Игоревич"
SELLER_TAGLINE = "Магазин игровых приставок! PlayStation, Nintendo, Oculus, Steam, Xbox"
SELLER_INN = "772580198140"
SELLER_ACCOUNT = "40802810120000970922"
SELLER_BANK = 'ООО "Банк Точка"'
SELLER_BIK = "044525104"
SELLER_CORR = "30101810745374525104"
SELLER_SIGN = "Индивидуальный предприниматель\nКлименко Андрей Игоревич"

SELLER_FULL = (
    f"{SELLER_NAME}, ИНН {SELLER_INN}, р/с {SELLER_ACCOUNT}, {SELLER_BANK}, БИК {SELLER_BIK}, к/с {SELLER_CORR}"
)


def resolve_logo_path() -> Path | None:
    for path in LOGO_CANDIDATES:
        if path.is_file():
            return path
    return None
