DATABASE_NAME = "currency_rates.db"

NB_RSS_URL = "https://nationalbank.kz/rss/rates_all.xml"
NB_UPDATE_TIME = "09:00"
NB_TIMEZONE = "Asia/Almaty"

PRIORITY_CURRENCY_PAIRS = [
    ("USD", "KZT"),
    ("EUR", "KZT"),
    ("RUB", "KZT")
]

CURRENCY_RATE_TYPES = [
    "Курс покрытия",
    "Курс конвертации для физических лиц",
    "Курсы конвертации для проведения операций по платежным карточкам",
    "Курсы конвертации для МП",
    "Курс аффинированного драгоценного металла в слитках",
    "Курс по безналичной конвертации"
]

ALL_CURRENCIES = [
    "USD", "EUR", "RUB", "GBP", "XAU", "CHF", "CAD", "AED", 
    "CNY", "AUD", "JPY", "SEK", "KGS", "CZK", "TRY", "KZT"
]

LOYALTY_UNITS = [
    "ST1F", "ST1J", "ST2F", "ST2J", 
    "LG1F", "LG1J", "LG2F", "LG2J"
]

LOYALTY_UNIT_DESCRIPTIONS = {
    "ST1F": "стандартный курс для физических лиц",
    "ST1J": "стандартный курс для юридических лиц",
    "ST2F": "стандартный курс 2 для физических лиц",
    "ST2J": "стандартный курс 2 для юридических лиц",
    "LG1F": "льготный курс 1 для физических лиц",
    "LG1J": "льготный курс 1 для юридических лиц",
    "LG2F": "льготный курс 2 для физических лиц",
    "LG2J": "льготный курс 2 для юридических лиц"
}

STATUS_SANCTIONED = "санкционировано"
STATUS_UNSANCTIONED = "не санкционировано"
STATUS_WITH_REMARKS = "есть замечание"

AUTO_TIME_OFFSET_MINUTES = 7
