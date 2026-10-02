from pathlib import Path

_ROOT = Path(__file__).resolve().parent

LOGO_PATH = _ROOT / "assets" / "logo.png"
LOGO_CANDIDATES = (
    LOGO_PATH,
    _ROOT / "assets" / "logo.jpg",
    _ROOT / "assets" / "logo.jpeg",
    _ROOT / "assets" / "logo.webp",
)

QR_TELEGRAM_PATH = _ROOT / "assets" / "qr_telegram.png"
QR_MAPS_PATH = _ROOT / "assets" / "qr_maps.png"
SIGNATURE_PATH = _ROOT / "assets" / "signature.png"
STAMP_PATH = _ROOT / "assets" / "stamp.png"

SELLER_NAME = "ИП Кадыров Рустам Камильевич"
SELLER_TAGLINE = "Магазин цифровой техники"
SELLER_INN = "382706466702"
SELLER_ACCOUNT = "40802810720001170163"
SELLER_BANK = 'ООО "Банк Точка"'
SELLER_BIK = "044525104"
SELLER_CORR = "30101810745374525104"
SELLER_SIGN = "Индивидуальный предприниматель\nКадыров Рустам Камильевич"

SELLER_FULL = (
    f"{SELLER_NAME}, ИНН {SELLER_INN}, р/с {SELLER_ACCOUNT}, {SELLER_BANK}, БИК {SELLER_BIK}, к/с {SELLER_CORR}"
)


def resolve_logo_path() -> Path | None:
    for path in LOGO_CANDIDATES:
        if path.is_file():
            return path
    return None


def resolve_qr_telegram_path() -> Path | None:
    if QR_TELEGRAM_PATH.is_file():
        return QR_TELEGRAM_PATH
    return None


def resolve_qr_maps_path() -> Path | None:
    if QR_MAPS_PATH.is_file():
        return QR_MAPS_PATH
    return None


def resolve_signature_path() -> Path | None:
    if SIGNATURE_PATH.is_file():
        return SIGNATURE_PATH
    return None


def resolve_stamp_path() -> Path | None:
    if STAMP_PATH.is_file():
        return STAMP_PATH
    return None
