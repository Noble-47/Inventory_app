from shopify.service.uow import UnitOfWork
from shopify.domain import events, commands
from shopify.db import handlers

# command handlers

def create_account(command: commands.CreateAccount, uow: UnitOfWork):
    with uow:
        uow.accounts.create(
            command.firstname, command.lastname, command.email, command.password
        )
        uow.commit()
    return accounts


def verify_account(command: commands.VerifyAccount, uow:UnitOfWork):
    with uow:
        verification = uow.verification.get(command.verification_str)
        if verification is None:
            raise ValueError("Invalid Token")
        elif verification.email != command.email:
            raise ValueError("Email Does Not Match")
        else:
            account = uow.accounts.get(verification.email)
            account.is_verified = True
            verification.is_valid = False
        uow.commit()
    return verification


def create_business(command: commands.CreateBusiness, uow: UnitOfWork):
    with uow:
        owner = uow.accounts.get(owner_id)
        business = uow.business.create(name=command.name, owner=owner)
        uow.registry.create(
            entity_id=business.id,
            entity_name=business.name,
            entity_type=EntityType.business,
            account_id=owner.id,
            permissions="*"
        )
        uow.commit()
    return business


def add_shop(command: commands.AddShop, uow: UnitOfWork):
    with uow:
        business = uow.business.get(command.business_id)
        #shop = uow.shop.create(command.location)
        business.add_shop(command.location)
        uow.commit()
    return shop

def remove_shop(command: commands.RemoveShop, uow: UnitOfWork):
    with uow:
        business = uow.business.get(command.business_id)
        business.remove(command.shop_id)
        uow.commit()


def create_assignment_token(command: commands.CreateAssignmentToken, uow: UnitOfWork):
    with uow:
        token = uow.tokenizer.create(
            command.email, command.permissions, command.business_id, command.shop_id
        )
        uow.commit()
    return token


def create_manager(command: commands.CreateManager, uow: UnitOfWork):
    with uow:
        token = uow.tokenizer.get(command.token_str)
        if token is None:
            raise ValueError("Invalid Token")
        elif token.email != command.email:
            raise ValueError("Email Does Not Match")
        else:
            account = uow.accounts.create(
                command.firstname, command.lastname, command.email, command.password
            )
            business = uow.business.get(token.business_id)
            business.assign_shop_manager(
                token.shop_id, account, permissions=token.decoded["permissions"]
            )
            uow.registry.create(
                entity_id=token.shop_id,
                entity_name=token.decoded['location'],
                entity_type=EntityType.shop,
                account_id=account.id,
                permissions=command.permissions
            )
            token.is_valid = False
            token.used = True
        uow.commit()
    return account


def assign_shop_manager(command: commands.AssignManager, uow: UnitOfWork):
    with uow:
        account = uow.accounts.get(command.account_id)
        business = uow.business.get(token.business_id)
        shop = uow.shops.get(command.shop_id)
        manager = business.assign_shop_manager(command.shop_id, account)
        uow.registry.create(
            entity_id = shop.id,
            entity_name = shop.location,
            entity_type = EntityType.shop,
            account_id = account.id,
            permissions = command.permissions
        )
        uow.commit()
    return manager


def dismiss_shop_manager(command: commands.DismissManager, uow: UnitOfWork):
    with uow:
        business = uow.business.get(command.busines_id)
        business.dismiss_shop_manager(command.shop_id)
        registry = uow.registry.get(entity_id=command.shop_id)
        registry.account_id = None
        uow.commit()

def update_setting(command:commands.UpdateSetting, uow:UnitOfWork):
    setting_db = db.Setting(session)
    setting_db.set(command.name, command.value, command.entity_id)
    session.commit()

# Event handlers

def log_audit(event: events.Event, uow: UnitOfWork):
    with uow:
        uow.audit.add(event)
        uow.commit()


COMMAND_HANDLERS = {
    commands.CreateAccount : [create_account],
    commands.VerifyAccount : [verify_account],
    commands.CreateBusiness : [create_business],
    commands.AddShop : [add_shop],
    commands.CreateAssignmentToken : [create_assignment_token],
    commands.CreateManager : [create_manager],
    commands.AssignManager : [assign_shop_manager],
    commands.DismissManager : [dismiss_shop_manager],
    commands.UpdateSetting : [update_setting]
}

EVENT_HANDLERS = {
    events.AddedNewShop : [log_audit],
    events.RemovedShop : [log_audit],
    events.AssignedNewManager : [log_audit],
    events.DismissedManager : [log_audit],
    events.CreatedManagerInviteToken : [log_audit],
}

