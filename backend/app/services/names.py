def clean_name(value: str) -> str:
    # Nome da mostrare: spazi ai bordi tolti e spazi interni ridotti a uno solo.
    return " ".join(value.split())


def name_key(value: str) -> str:
    # Chiave per l'unicità: stesso nome ripulito, senza distinguere maiuscole e
    # minuscole. casefold() gestisce anche accenti e lettere speciali ("Straße" -> "strasse").
    return clean_name(value).casefold()