class PhoneNumber:
    """Class for handling international phone numbers"""

    def __init__(self, number, country_code=None):
        """
        Initialize a new PhoneNumber.

        Args:
            number (str|int): The phone number
            country_code (int|str, optional): The country code. Defaults to None.
        """
        self.number = str(number)
        self.country_code = str(country_code) if country_code is not None else None

    def get_number(self):
        """
        Get the phone number.

        Returns:
            str: The phone number
        """
        return self.number

    def get_country_code(self):
        """
        Get the country code.

        Returns:
            str|None: The country code or None
        """
        return self.country_code

    def get_international_format(self):
        """
        Get the international format of the phone number.

        Returns:
            str: The international format of the phone number
        """
        if self.country_code is None:
            return self.number
        
        return f"+{self.country_code}{self.number}"

    def __str__(self):
        """
        Get the string representation of the phone number.

        Returns:
            str: The string representation of the phone number
        """
        return self.get_international_format() 