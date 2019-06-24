from gino.ext.sanic import Gino


db = Gino()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode())

    def __str__(self):
        return "{}<{}>".format(self.name, self.id)

    def __repr__(self):
        return self.__str__()
