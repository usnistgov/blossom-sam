try:
    from service.sam import db
except:
    from sam import db

class System(db.Model):
    system_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    token = db.Column(db.String, nullable=False, unique=True)

    keys = db.relationship('Key', lazy=True,
                           backref=db.backref('system', lazy=True),
                           cascade='all, delete')

class Application(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', 'version', 'arch', 'os'),
    )

    app_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    version = db.Column(db.String, nullable=False)
    arch = db.Column(db.String, nullable=False)
    os = db.Column(db.String, nullable=False)

    keys = db.relationship('Key', lazy=True,
                           backref=db.backref('application', lazy=True),
                           cascade='all, delete')

class Key(db.Model):
    key_id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.app_id'),
                       nullable=False)
    data = db.Column(db.Binary, nullable=False)
    leased_to = db.Column(db.Integer, db.ForeignKey('system.system_id'),
                          nullable=True)
