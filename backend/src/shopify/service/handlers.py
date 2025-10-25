from shopify.domain import events, commands
from shopify.config import DEFAULT_SETTINGS
from shopify.db import events as db_events
from shopify import exceptions

from exchange import hub

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
        )
        uow.commit()


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


def create_business(command: commands.CreateBusiness, uow: UnitOfWork):
    """Create business."""
    with uow:
        owner = uow.accounts.get(command.email)
        if uow.business.check_name_exists(owner.id, command.name):
            raise exceptions.DuplicateBusinessRecord(
                f"You already have a business with the name, {command.name}"
            )
        business = uow.business.create(name=command.name, owner=owner)
        owner.account_type = "business_owner"
        uow.registry.create(
            business_id=business.id,
            owner_id=owner.id,
        )
        uow.commit()


def add_shop(command: commands.AddShop, uow: UnitOfWork):
    """Add shop to business."""
    with uow:
        business = uow.business.get(command.business_id)
        shop = business.add_shop(command.location)
        uow.commit()


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
            shop.location,
            business.name,
        )
        uow.commit()


def create_manager(command: commands.CreateManager, uow: UnitOfWork):
    """Create manager account and assign as shop manager."""
    with uow:
        token = uow.tokenizer.get(token_str=command.token_str, email=command.email)
        if token is None:
            raise exceptions.InvalidInvite("Invalid Token")
        elif token.email != command.email:
            raise exceptions.InvalidInvite("Email Does Not Match")
        elif token.is_valid:
            if uow.accounts.check_email_exists(command.email):
                account = uow.accounts.get(command.email)
            else:
                account = uow.accounts.create(
                    command.firstname,
                    command.lastname,
                    command.email,
                    command.password,
                    account_type="shop_manager",
                )
            business = uow.business.get(token.business_id)
            business.assign_shop_manager(
                token.shop_id, account, permissions=token.permissions
            )
            token.is_valid = False
            token.used = True
            uow.commit()
        else:
            uow.commit()
            raise ValueError("Token Is No Longer Valid.")


def assign_shop_manager(command: commands.AssignManager, uow: UnitOfWork):
    """Assign manager to shop."""
    with uow:
        account = uow.accounts.get(command.account_id)
        business = uow.business.get(token.business_id)
        shop = uow.shops.get(command.shop_id)
        business.assign_shop_manager(command.shop_id, account)
        uow.commit()


def dismiss_shop_manager(command: commands.DismissManager, uow: UnitOfWork):
    """Dismiss current shop manager."""
    with uow:
        manager_registry = uow.registry.get_manager_registry(
            business_id=command.business_id, shop_id=command.shop_id
        )
        manager = manager_registry.account
        business = uow.business.get(command.business_id)
        business.dismiss_shop_manager(command.shop_id)
        uow.session.delete(manager)
        uow.session.delete(manager_registry)
        uow.commit()


def update_setting(command: commands.UpdateSetting, uow: UnitOfWork):
    """Update business setting."""
    with uow:
        try:
            uow.settings.set(
                name=command.name,
                value=command.value,
                entity_id=command.entity_id,
                entity_type="shop",
            )
        except ValueError as err:
            raise exceptions.InvalidSettingKey(str(err))
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


def add_manager_to_shop_view(event: events.AssignedNewManager, uow: UnitOfWork):
    with uow:
        uow.views.add_manager_to_shop(
            event.shop_id, event.manager_name, event.manager_email
        )
        uow.commit()


def remove_manager_from_shop_view(event: events.DismissedManager, uow: UnitOfWork):
    with uow:
        uow.views.remove_manager_from_shop(event.shop_id)
        uow.commit()


def create_and_send_verification_token(
    event: db_events.NewAccountCreated, notifier: EmailNotifier, uow: UnitOfWork
):
    """Create and send verification token after user registration."""
    with uow:
        verification = uow.verification.create(event.email)
        notifier.send_verification_email(
            verification.verification_str, event.firstname, event.lastname, event.email
        )
        uow.commit()


def send_invitation_link(
    event: events.CreatedManagerInviteToken, notifier: EmailNotifier, uow: UnitOfWork
):
    """Send manager invite to manager email."""
    with uow:
        business_name = uow.business.get_business_name(event.business_id)
        notifier.send_invite_email(
            email=event.email, business_name=business_name, token=event.token_str
        )
        uow.tokenizer.mark_as_sent(event.token_str)
        uow.commit()


def delete_invitation_link(cmd: commands.DeleteInviteLink, uow: UnitOfWork):
    with uow:
        uow.tokenizer.delete(cmd.shop_id, cmd.email)
        uow.commit()


def notify_shop_created(event: events.AddedNewShop):
    hub.publish("shop_notifications", "new_shop_added", {"shop_id": str(event.shop_id)})


def notify_shop_deleted(event: events.RemovedShop):
    hub.publish("shop_notifications", "shop_removed", {"shop_id": str(event.shop_id)})


def notify_settings_updates(event: events.UpdatedShopSetting):
    hub.publish(
        "settings_notifications",
        f"{event.tag}_setting_updates",
        {"shop_id": event.shop_id, "name": event.name, "value": event.value},
    )


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
    commands.DeleteInviteLink: [delete_invitation_link],
    commands.UpdateSetting: [update_setting],
}
