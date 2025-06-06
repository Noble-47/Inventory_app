from shopify.domain import events, commands
from shopify.config import DEFAULT_SETTINGS
from shopify.db import events as db_events
from shopify import exceptions

from shopify.service.uow import UnitOfWork
from shopify.notification.email import EmailNotifier

# command handlers


def create_account(command: commands.CreateAccount, uow: UnitOfWork):
    """Create account."""
    with uow:
        if uow.accounts.check_email_exists(command.email):
            raise exceptions.EmailAlreadyRegistered("Email Already Registered.")

        account = uow.accounts.create(
            command.firstname,
            command.lastname,
            command.email,
            command.password,
            type="owner",
        )
        uow.commit()
    return account


def verify_account(command: commands.VerifyAccount, uow: UnitOfWork):
    """Verify user email."""
    with uow:
        verification = uow.verification.get(command.verification_str)
        if verification is None:
            raise exceptions.VerificationError("Token doesn't exists")
        elif not verification.is_valid:
            raise exceptions.VerificationError(verification.invalid_cause)
        else:
            account = uow.accounts.get(verification.email)
            account.is_verified = True
            verification.is_valid = False
        uow.commit()
    return verification


def create_business(command: commands.CreateBusiness, uow: UnitOfWork):
    """Create business."""
    with uow:
        owner = uow.accounts.get(command.email)
        if uow.business.check_name_exists(owner.id, command.name):
            raise exceptions.DuplicateBusinessRecord(
                f"You already have a business with the name, {command.name}"
            )
        business = uow.business.create(name=command.name, owner=owner)
        uow.registry.create(
            business_id=business.id,
            owner_id=owner.id,
        )
        uow.commit()
    return business


def add_shop(command: commands.AddShop, uow: UnitOfWork):
    """Add shop to business."""
    with uow:
        business = uow.business.get(command.business_id)
        # shop = uow.shop.create(command.location)
        shop = business.add_shop(command.location)
        uow.commit()
    return shop


def remove_shop(command: commands.RemoveShop, uow: UnitOfWork):
    """Remove shop from business."""
    with uow:
        business = uow.business.get(command.business_id)
        business.remove_shop(command.shop_id)
        uow.commit()


def create_assignment_token(command: commands.CreateAssignmentToken, uow: UnitOfWork):
    """Create manager invite token."""
    with uow:
        business = uow.business.get(command.business_id)
        shop = business.search_registry(command.shop_id)
        token = uow.tokenizer.create(
            command.email,
            command.permissions,
            command.business_id,
            shop.shop_id,
            business.name,
            shop.location,
        )
        uow.commit()
    return token


def create_manager(command: commands.CreateManager, uow: UnitOfWork):
    """Create manager account and assign as shop manager."""
    with uow:
        token = uow.tokenizer.get(command.token_str)
        if token is None:
            raise ValueError("Invalid Token")
        elif token.email != command.email:
            raise ValueError("Email Does Not Match")
        elif token.is_valid:
            account = uow.accounts.create(
                command.firstname, command.lastname, command.email, command.password
            )
            business = uow.business.get(token.business_id)
            business.assign_shop_manager(
                token.shop_id, account, permissions=token.decoded["permissions"]
            )
            token.is_valid = False
            token.used = True
            uow.commit()
        else:
            uow.commit()
            raise ValueError("Token is no more valid.")
    return account


def assign_shop_manager(command: commands.AssignManager, uow: UnitOfWork):
    """Assign manager to shop."""
    with uow:
        account = uow.accounts.get(command.account_id)
        business = uow.business.get(token.business_id)
        shop = uow.shops.get(command.shop_id)
        manager = business.assign_shop_manager(command.shop_id, account)
        uow.commit()
    return manager


def dismiss_shop_manager(command: commands.DismissManager, uow: UnitOfWork):
    """Dismiss current shop manager."""
    with uow:
        business = uow.business.get(command.busines_id)
        business.dismiss_shop_manager(command.shop_id)
        # registry = uow.registry.get(entity_id=command.shop_id)
        # registry.account_id = None
        uow.commit()


def update_setting(command: commands.UpdateSetting, uow: UnitOfWork):
    """Update business setting."""
    with uow:
        uow.settings.set(
            name=command.name,
            value=command.value,
            entity_id=command.entity_id,
            entity_type="business",
        )
        uow.session.commit()


# Event handlers


def log_audit(event: events.Event, uow: UnitOfWork):
    """Log domain events as business history."""
    with uow:
        uow.audit.add(event)
        uow.commit()


def add_business_to_views(event: events.NewBusinessCreated, uow: UnitOfWork):
    """Update business_view table."""
    with uow:
        uow.views.add_business(
            event.business_id, event.name, event.owner_email, event.owner_name
        )
        uow.commit()


def setup_new_business(event: events.NewBusinessCreated, uow: UnitOfWork):
    """Apply default settings to business."""
    with uow:
        for setting in DEFAULT_SETTINGS:
            uow.settings.set(
                entity_id=event.business_id,
                name=setting["name"],
                value=setting["default"],
                entity_type="business",
            )
        uow.commit()


def add_shop_to_views(event: events.AddedNewShop, uow: UnitOfWork):
    """Update shop_view table."""
    with uow:
        uow.views.add_shop(event.business_id, event.shop_id, event.shop_location)
        uow.commit()


def remove_shop_from_views(event: events.RemovedShop, uow: UnitOfWork):
    """Update shop_view table."""
    with uow:
        uow.views.delete_shop(event.business_id, event.location)
        uow.commit()


def create_and_send_verification_token(
    event: db_events.NewAccountCreated, notifier: EmailNotifier, uow: UnitOfWork
):
    """Create and send verification token after user registration."""
    with uow:
        verification = uow.verification.create(event.email)
        notifier.send_verification_token(
            verification.verification_str, event.firstname, event.lastname, event.email
        )
        uow.commit()


COMMAND_HANDLERS = {
    commands.CreateAccount: [create_account],
    commands.VerifyAccount: [verify_account],
    commands.CreateBusiness: [create_business],
    commands.AddShop: [add_shop],
    commands.RemoveShop: [remove_shop],
    commands.CreateAssignmentToken: [create_assignment_token],
    commands.CreateManager: [create_manager],
    commands.AssignManager: [assign_shop_manager],
    commands.DismissManager: [dismiss_shop_manager],
    commands.UpdateSetting: [update_setting],
}

EVENT_HANDLERS = {
    events.AddedNewShop: [log_audit],
    events.RemovedShop: [log_audit],
    events.AssignedNewManager: [log_audit],
    events.DismissedManager: [log_audit],
    events.CreatedManagerInviteToken: [log_audit],
}
