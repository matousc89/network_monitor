
import ipaddress

class DataValidation():

    def validate_ip_address(self, value):
        try:
            # Zkusíme vytvořit objekt IP adresy
            ip = ipaddress.IPv4Address(value)
            return str(ip)
        except ipaddress.AddressValueError:
            # Pokud selže, vypíšeme chybu
            raise ValueError("Neplatná IPv4 adresa")