"""Individuazione IPv4 LAN senza servizi esterni o dipendenze aggiuntive."""
import ipaddress
import socket

_PRIVATE_NETWORKS = tuple(ipaddress.IPv4Network(value) for value in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
))


def validate_lan_ip(value):
    """Restituisce un IPv4 RFC1918 canonico; solleva ValueError altrimenti.

    value: indirizzo testuale, senza porta. Non accetta hostname, loopback,
    indirizzi pubblici, link-local o IPv6. Non verifica la presenza sul PC.
    """
    try:
        address = ipaddress.IPv4Address(value)
    except (ipaddress.AddressValueError, TypeError) as exc:
        raise ValueError("Specificare un indirizzo IPv4 della rete privata") from exc
    if not any(address in network for network in _PRIVATE_NETWORKS):
        raise ValueError("Sono ammessi solo IPv4 privati 10.x, 172.16-31.x o 192.168.x")
    return str(address)


def detect_lan_ips():
    """Restituisce IPv4 privati ordinati risolti per il nome di questo PC.

    Non invia richieste a Internet. La risoluzione del nome non garantisce
    l'elenco completo delle interfacce: restituisce [] se non disponibile.
    L'indirizzo manuale viene comunque verificato con bind da select_lan_ip.
    """
    try:
        entries = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET,
                                     socket.SOCK_STREAM)
    except OSError:
        return []
    addresses = set()
    for entry in entries:
        try:
            addresses.add(validate_lan_ip(entry[4][0]))
        except ValueError:
            continue
    return sorted(addresses, key=ipaddress.IPv4Address)


def require_local_ip(value):
    """Valida value e verifica con bind che appartenga al PC; restituisce l'IP.

    Non apre un server, non sceglie la porta applicativa e non modifica il
    firewall. Solleva ValueError per indirizzi non privati o non assegnati.
    """
    address = validate_lan_ip(value)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((address, 0))
    except OSError as exc:
        raise ValueError(f"Indirizzo {address} non utilizzabile su questo PC: {exc}") from exc
    return address


def select_lan_ip(value=None, prompt=input, report=print):
    """Restituisce un IP locale verificato, esplicito, unico o scelto dall'utente.

    value: override manuale facoltativo. prompt/report: callback console.
    Nessuna scelta automatica tra piu' interfacce (VPN incluse). Se il
    rilevamento fallisce richiede l'IP manuale; input invalido produce ValueError.
    """
    if value is not None:
        return require_local_ip(value)
    addresses = detect_lan_ips()
    if len(addresses) == 1:
        return require_local_ip(addresses[0])
    if addresses:
        report("Piu' indirizzi privati disponibili; scegli quello della rete Wi-Fi/LAN:")
        for index, address in enumerate(addresses, 1):
            report(f"  {index}) {address}")
        choice = prompt("Numero oppure indirizzo IPv4 manuale: ").strip()
        if choice.isdecimal() and 1 <= int(choice) <= len(addresses):
            return require_local_ip(addresses[int(choice) - 1])
    else:
        report("IP LAN non rilevato automaticamente.")
        choice = prompt("Indirizzo IPv4 del PC sulla rete Wi-Fi/LAN: ").strip()
    return require_local_ip(choice)
