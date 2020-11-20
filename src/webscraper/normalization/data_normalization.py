class Normalization:

    def __init__(self):
        pass

    def normalize_currency(self, value):
        result = (
            '€' if value == 'EUR'
            else '$' if value == '$'
            else 'лв' if value == 'лв.'
            else 'Other'
        )
        return result

    def normalize_advertise_type(self, value):
        result = (
            'Sale' if value == 1
            else 'Rent' if value == 2
            else 'Other'
        )
        return result

    def normalize_property_type(self, value):
        result = (
            'Land' if value == 'ПАРЦЕЛ'
                      or value == 'ЗЕМЕДЕЛСКА ЗЕМЯ'
            else 'House' if value == 'КЪЩА'
                            or value == 'ВИЛА'
            else 'Apartment' if value == '1-СТАЕН'
                                or value == '2-СТАЕН'
                                or value == '3-СТАЕН'
                                or value == '3-СТАЕН'
                                or value == '4-СТАЕН'
                                or value == 'МНОГОСТАЕН'
                                or value == 'МЕЗОНЕТ'
                                or value == 'АТЕЛИЕ, ТАВАН'
            else 'Office' if value == 'ОФИС'
            else 'Other'
        )
        return result

    def normalize_month(self, value):
        result = (
            'January' if value == 'януари'
            else 'February' if value == 'февруари'
            else 'March' if value == 'март'
            else 'April' if value == 'април'
            else 'May' if value == 'може'
            else 'June' if value == 'юни'
            else 'July' if value == 'юли'
            else 'August' if value == 'август'
            else 'September' if value == 'септември'
            else 'October' if value == 'октомври'
            else 'November' if value == 'ноември'
            else 'December' if value == 'декември'
            else 'Undefined'
        )
        return result

    def get_slug(self, value):
        property_address_lower = value.lower()
        dot = '.'
        for symbol in property_address_lower:
            if symbol in dot:
                property_address_lower = property_address_lower.replace(symbol, " ") or property_address_lower
        address_lower = ' '.join(property_address_lower.split())
        punctuation = "!@#$%^&*()_-+<>?:,;"
        for symbol in address_lower:
            if symbol in punctuation:
                address_lower = address_lower.replace(symbol, "") or None
        result = address_lower.replace(" ", "-")
        return result

    def get_letters(self, string):
        result = ''.join([number for number in string if not number.isdigit()]).strip()
        return result

    def get_digits(self, string):
        result = ''.join([number for number in string if number.isdigit()])
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
        value_len = len(value)
        if value_len > 0:
            result = value
        else:
            result = None
        return result

