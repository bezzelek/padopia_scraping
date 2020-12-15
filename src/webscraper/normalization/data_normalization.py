class Normalization:

    def normalize_currency(self, value):
        result = (
            '€' if value == 'EUR'
                   or value == '€'
            else '$' if value == '$'
            else 'лв' if value == 'лв.'
            else 'Other'
        )
        return result

    def normalize_advertise_type(self, value):
        result = (
            'Sale' if value == 'Sale'
                      or value == 'sale'
                      or value == 1
            else 'Rent' if value == 'Rent'
                           or value == 'rent'
                           or value == 2
            else 'Auction' if value == 'auction'
            else 'Other'
        )
        return result

    def normalize_property_type(self, value):
        result = (
            'Land' if value == 'Farm/Land'
                      or value == 'Land/Plot/Site'
                      or value == 'Site'
                      or value == 'ПАРЦЕЛ'
                      or value == 'ЗЕМЕДЕЛСКА ЗЕМЯ'
            else 'Farmhouse' if value == 'Farmhouse'
                                or value == 'Rustico - Casale'
            else 'Airspace' if value == 'Airspace'

            else 'House' if value == 'КЪЩА'
                            or value == 'ВИЛА'
                            or value == 'Rural property'
                            or value == 'House or chalet'
                            or value == 'Casa indipendente'
            else 'Palace' if value == 'Palace/Castle/Manor'
            else 'Penthouse' if value == 'Penthouse'
                                or value == 'Attico - Mansarda'
            else 'Terraced House' if value == 'Terraced House'
                                     or value == 'Terrace'
                                     or value == 'End of Terrace'
            else 'Villa' if value == 'Villa'
            else 'Bungalow' if value == 'Bungalow'
            else 'Boathouse' if value == 'Boathouse'
            else 'Detached' if value == 'Detached'
            else 'Semi-detached' if value == 'Single-family semi-detached'
                                    or value == 'Semi-D'
            else 'Country house' if value == 'Country house'

            else 'Parking Space' if value == 'Garage/Parking Space'

            else 'Flat' if value == 'Flat'
            else 'Attic' if value == 'Attic'
            else 'Apartment' if value == 'Apartment'
                                or value == '1-СТАЕН'
                                or value == '2-СТАЕН'
                                or value == '3-СТАЕН'
                                or value == '3-СТАЕН'
                                or value == '4-СТАЕН'
                                or value == 'МНОГОСТАЕН'
                                or value == 'МЕЗОНЕТ'
                                or value == 'АТЕЛИЕ, ТАВАН'
                                or value == 'Intermediate floors'
                                or value == 'Ground floor'
                                or value == 'Planta baja'
                                or value == 'Appartamento'
            else 'Penthouse' if value == 'Penthouse'
            else 'Duplex apartment' if value == 'Duplex apartment'
                                       or value == 'Duplex'
            else 'Loft' if value == 'Loft'
            else 'Studio' if value == 'Studio'
                             or value == 'Study'
                             or value == 'Studio Apartment'
            else 'Room' if value == 'Room'
            else 'Maisonette' if value == 'Maisonette'
            else 'Townhouse' if value == 'Townhouse'
                                or value == 'Villetta a schiera'
            else 'Mixed units' if value == 'Block of apartments/mixed units'
            else 'COVID-19 Accommodation' if value == 'COVID-19 Accommodation'

            else 'Office' if value == 'Office'
                             or value == 'ОФИС'
            else 'Warehouse' if value == 'Warehouse'
                                or value == 'Storage facilities'

            else 'Bars & Restaurants' if value == 'Bars & Restaurants'
            else 'Catering' if value == 'Catering (commercial)'
            else 'Hotel' if value == 'Hotel/Resort/Hostel/Guest House'
            else 'Nightclub' if value == 'Nightclub'
            else 'House of Character' if value == 'House of Character'

            else 'Shop' if value == 'Shop'
                           or value == 'Showroom'
            else 'Factory' if value == 'Industrial/Factory (commercial)'
            else 'Commercial' if value == 'Commercial'
            else 'Education' if value == 'Education (commercial)'

            else 'Other'
        )
        return result

    def normalize_month(self, value):
        result = (
            'January' if value == 'януари'
                         or value == 'Jan'
            else 'February' if value == 'февруари'
                               or value == 'Feb'
            else 'March' if value == 'март'
                            or value == 'Mar'
            else 'April' if value == 'април'
                            or value == 'Apr'
            else 'May' if value == 'може'
                          or value == 'May'
            else 'June' if value == 'юни'
                           or value == 'June'
            else 'July' if value == 'юли'
                           or value == 'July'
            else 'August' if value == 'август'
                             or value == 'Aug'
            else 'September' if value == 'септември'
                                or value == 'Sept'
            else 'October' if value == 'октомври'
                              or value == 'Oct'
            else 'November' if value == 'ноември'
                               or value == 'Nov'
            else 'December' if value == 'декември'
                               or value == 'Dec'
            else 'Undefined'
        )
        return result

    def get_no_punctuation(self, value):
        punctuation = """!.@#$%^&*('")_-+<>?:,;"""
        for symbol in value:
            if symbol in punctuation:
                value = value.replace(symbol, "")
            else:
                value = value
        return value

    def get_slug(self, value):
        property_address_lower = value.lower()
        dot = '.'
        for symbol in property_address_lower:
            if symbol in dot:
                property_address_lower = property_address_lower.replace(symbol, " ") or property_address_lower
        address_lower = ' '.join(property_address_lower.split())
        punctuation = """!@#$%^&*('")_-+<>?:,;"""
        for symbol in address_lower:
            if symbol in punctuation:
                address_lower = address_lower.replace(symbol, "") or None
        result = address_lower.replace(" ", "-")
        return result

    def get_letters(self, string):
        if string is not None:
            result = ''.join([number for number in string if not number.isdigit()]).strip()
        else:
            result = None
        return result

    def get_digits(self, string):
        if string is not None:
            result = ''.join([number for number in string if number.isdigit()])
        else:
            result = None
        return result

    def get_no_spaces(self, value):
        result = ' '.join(value.split())
        return result

    def get_no_tags(self, value):
        result = ''.join(value).strip()
        return result

    def get_text(self, source_str, str_start, str_end):
        result = ''.join(
            element.split(str_end)[0]
            for element in source_str.split(str_start)[1:]
        )
        return result

    def get_list(self, source_str, str_start, str_end):
        result = [
            element.split(str_end)[0]
            for element in source_str.split(str_start)
        ]
        return result

    def check_if_exists(self, value):
        if value is not None:
            value_len = len(value)
            if value_len > 0:
                result = value
            else:
                result = None
            return result
        else:
            return None

    def get_if_element_in(self, elements_list, start_str, end_str, exist):
        for element in elements_list:
            if exist in element:
                result = self.get_text(element, start_str, end_str)
                return result

    def get_shorter(self, long_string, limiter):
        item = long_string.index(limiter)
        result = long_string[:item + len(limiter)]
        return result
