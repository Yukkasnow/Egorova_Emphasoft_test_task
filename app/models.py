from tortoise import fields
from tortoise.models import Model


class Users(Model):
    id = fields.IntField(pk=True)
    super_user = fields.BooleanField(default=False)
    user_name = fields.CharField(max_length=50, unique=True)
    first_name = fields.CharField(max_length=100)
    last_name = fields.CharField(max_length=100)
    password = fields.CharField(max_length=100)
    is_active = fields.BooleanField(default=True)
