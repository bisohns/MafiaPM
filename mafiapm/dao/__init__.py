from mafiapm.model import User


class UserDAO(User):

    @classmethod
    async def get_user(cls, user_id):
        user = await cls.get_or_404(user_id)
        return user
