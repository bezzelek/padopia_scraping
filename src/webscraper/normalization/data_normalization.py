class Normalization:

    def normalize_currency(self, value):
        result = (
            '€' if value == 'EUR'
                   or value == '€'
            else '$' if value == '$'
            else 'лв' if value == 'лв.'
            else '₺' if value == 'TL'
            else None
        )
        return result

    def normalize_currency_iso(self, value):
        currency_to_iso = (
            'EUR' if value == '€'
            else 'USD' if value == '$'
            else 'BGN' if value == 'лв'
            else 'TRY' if value == '₺'
            else None
        )
        return currency_to_iso

    def normalize_advertise_type(self, value):
        result = (
            'Sale' if value == 'Sale'
                      or value == 'sale'
                      or value == 1
                      or value == 'acheter'
                      or value == 'For sale'
                      or value == 'BUY'
            else 'Rent' if value == 'Rent'
                           or value == 'rent'
                           or value == 2
                           or value == 'louer'
                           or value == 'For rent'
                           or value == 'RENT'
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
                      or value == 'Land'
                      or value == 'tarla'
                      or value == 'ticari-imarli'
                      or value == 'muhtelif-arsa'
                      or value == 'bahce'
                      or value == 'zeytinlik'
                      or value == 'sit-alani'
                      or value == 'ciftlik'
                      or value == '3 - Land plot'
            else 'Farmhouse' if value == 'Farmhouse'
                                or value == 'Rustico - Casale'
                                or value == 'çiftlik-evi'
                                or value == 'mustakil'
                                or value == 'koy-evi'
                                or value == 'ciftlik-evi'
            else 'Airspace' if value == 'Airspace'
            else 'Island' if value == 'Island'

            else 'House' if value == 'КЪЩА'
                            or value == 'ВИЛА'
                            or value == 'Rural property'
                            or value == 'House or chalet'
                            or value == 'Casa indipendente'
                            or value == 'Maison'
                            or value == 'Hôtel particulier'
                            or value == 'Manoir'
                            or value == 'Propriété'
                            or value == 'köşk'
                            or value == 'residence'
                            or value == 'dağ-evi'
                            or value == 'yazlık'
                            or value == 'bina'
                            or value == 'yalı (komple)'
                            or value == 'prefabrik'
                            or value == 'devremülk'
                            or value == 'konut-imarli'
                            or value == 'genel'
                            or value == 'bina'
                            or value == 'kosk'
                            or value == '2 - House / Villa'
                            or value == 'HOUSECHALET'
                            or value == 'HOUSE'
                            or value == 'HOUSERURAL_HOUSE'
                            or value == 'HOUSEROW_HOUSE'
            else 'Palace' if value == 'Palace/Castle/Manor'
                             or value == 'Château'
            else 'Penthouse' if value == 'Penthouse'
                                or value == 'Attico - Mansarda'
            else 'Terraced House' if value == 'Terraced House'
                                     or value == 'Terrace'
                                     or value == 'End of Terrace'
            else 'Villa' if value == 'Villa'
                            or value == 'villa-imarli'
                            or value == 'villa'
                            or value == 'HOUSEVILLA'
            else 'Bungalow' if value == 'Bungalow'
            else 'Boathouse' if value == 'Boathouse'
            else 'Detached' if value == 'Detached'
                               or value == 'Detached house'
                               or value == 'müstakil-ev'
            else 'Semi-detached' if value == 'Single-family semi-detached'
                                    or value == 'Semi-D'
            else 'Country house' if value == 'Country house'
                                    or value == 'köy-evi'
                                    or value == 'yazlik'

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
                                or value == 'Appartement'
                                or value == 'daire'
                                or value == 'yalı-dairesi'
                                or value == 'apartman-dairesi'
                                or value == 'toplu-konut-icin'
                                or value == '1 - Apartment'
                                or value == 'FLATAPARTMENT'
            else 'Flat' if value == 'Flat'
                           or value == 'Chambre'
                           or value == 'FLAT'
            else 'Attic' if value == 'Attic'
                            or value == 'FLATATTIC'
            else 'Penthouse' if value == 'Penthouse'
            else 'Duplex apartment' if value == 'Duplex apartment'
                                       or value == 'Duplex'
                                       or value == 'kooperatif'
                                       or value == 'FLATDUPLEX'
            else 'Loft' if value == 'Loft'
                           or value == 'FLATLOFT'
            else 'Studio' if value == 'Studio'
                             or value == 'Study'
                             or value == 'Studio Apartment'
                             or value == 'FLATSTUDY'
            else 'Room' if value == 'Room'
                           or value == 'devremulk'
            else 'Maisonette' if value == 'Maisonette'
            else 'Townhouse' if value == 'Townhouse'
                                or value == 'Villetta a schiera'
            else 'Mixed units' if value == 'Block of apartments/mixed units'
            else 'COVID-19 Accommodation' if value == 'COVID-19 Accommodation'

            else 'Business' if value == 'Business'
                               or value == 'konutticaret-alani'
                               or value == 'ozel-kullanim'
            else 'Office' if value == 'Office'
                             or value == 'buro'
                             or value == 'ОФИС'
                             or value == 'ofis'
                             or value == 'mustakil-isyeri'
            else 'Warehouse' if value == 'Warehouse'
                                or value == 'Storage facilities'

            else 'Bars & Restaurants' if value == 'Bars & Restaurants'
                                         or value == 'kafe--bar'
            else 'Catering' if value == 'Catering (commercial)'
            else 'Hotel' if value == 'Hotel/Resort/Hostel/Guest House'
                            or value == 'Hotel'
                            or value == 'otel'
                            or value == 'turizm-imarli'
                            or value == '5 - Hotel'
            else 'Nightclub' if value == 'Nightclub'
            else 'House of Character' if value == 'House of Character'

            else 'Shop' if value == 'Shop'
                           or value == 'Showroom'
                           or value == 'dukkan--magaza'
            else 'Factory' if value == 'Industrial/Factory (commercial)'
            else 'Commercial' if value == 'Commercial'
                                 or value == 'sanayi-imarli'
                                 or value == 'benzin-istasyonu'
                                 or value == 'atolye'
                                 or value == '4 - Commercial property'
            else 'Education' if value == 'Education (commercial)'

            else 'Parking Space' if value == 'Garage/Parking Space'

            else value
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
