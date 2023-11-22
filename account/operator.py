from django.apps import apps

from gwlink_manager import settings
from gwlink_manager.common.error import get_exception_traceback

def start():
    logger = settings.get_logger(__name__)

    try:
        User = apps.get_model('account', 'User')
        objects = User.objects.filter(is_superuser=True)

        # register default admin User
        if len(objects) <= 0:
            user = User()
            user.is_superuser = True
            user.is_admin = True
            user.username = 'admin@etri.re.kr'
            user.email = 'admin@etri.re.kr'
            user.name = 'admin'
            user.organization = 'etri'
            password = 'admin1234'
            user.set_password(password)
            user.save()
    except Exception as exc:
        logger.error('Failed in User.save(), caused by ' + get_exception_traceback(exc))
        return



