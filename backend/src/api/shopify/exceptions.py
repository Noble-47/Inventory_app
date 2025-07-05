class UnsupportedSettingException(Exception):
    def __init__(self, values: list):
        self.values = values
