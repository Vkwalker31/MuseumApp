"""
Проверка ролей: superuser (админ), сотрудник, посетитель (зарегистрированный пользователь).
"""
import logging

logger = logging.getLogger('museum')


def is_employee(user):
    """User с регистрацией – сотрудник (есть запись Employee с user=user)."""
    if not user or not user.is_authenticated:
        return False
    return hasattr(user, 'employee_profile') and user.employee_profile is not None


def is_visitor(user):
    """User с регистрацией – посетитель (залогинен, но не сотрудник)."""
    return user and user.is_authenticated and not is_employee(user)


def is_admin(user):
    """Superuser — полный доступ."""
    return user and user.is_authenticated and user.is_superuser
