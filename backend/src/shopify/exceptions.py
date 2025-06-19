class OperationalError(Exception):
    """
    Group of known errors that may occur during
    command execution or event handling.
    """

    pass


class EmailAlreadyRegistered(OperationalError):
    pass


class DuplicateBusinessRecord(OperationalError):
    pass


class ShopAlreadyHasManager(OperationalError):
    pass


class DuplicateShopRecord(OperationalError):
    pass


class VerificationError(OperationalError):
    pass


class InvalidSettingKey(OperationalError):
    pass


class NoActiveManger(OperationalError):
    pass


class InvalidInvite(OperationalError):
    pass


class ShopNotFound(OperationalError):
    pass


class UnresolvedError(Exception):
    """Non operational exceptions not handled"""

    pass
