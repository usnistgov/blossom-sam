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
    swid_tags = db.relationship('SwidTag', lazy=True,
                                backref=db.backref('system', lazy=True),
                                cascade='all, delete')

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    passwd = db.Column(db.String, nullable=False)

    tokens = db.relationship('AdminToken', lazy=True,
                             backref=db.backref('admin', lazy=True),
                             cascade='all, delete')

class AdminToken(db.Model):
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'),
                         nullable=False, primary_key=True)
    issued = db.Column(db.Time(timezone=True), server_default=db.func.now(),
                       nullable=False)
    token = db.Column(db.String, nullable=False)

class Application(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', 'version', 'arch', 'os'),
    )

    app_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    version = db.Column(db.String, nullable=False)
    arch = db.Column(db.String, nullable=False)
    os = db.Column(db.String, nullable=False)
    blossom_id = db.Column(db.String, nullable=False)

    keys = db.relationship('Key', lazy='selectin',
                           backref=db.backref('application', lazy='selectin'),
                           cascade='all, delete')
    swid_tags = db.relationship('SwidTag', lazy=True,
                                backref=db.backref('application',
                                                   lazy='selectin'),
                                cascade='all, delete')

class Key(db.Model):
    key_id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.app_id'),
                       nullable=False)
    data = db.Column(db.Binary, nullable=False)
    expiration = db.Column(db.String, nullable=False)
    lease_date = db.Column(db.String, nullable=True)

    leased_to = db.Column(db.Integer, db.ForeignKey('system.system_id'),
                          nullable=True)

class SwidTag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.app_id'),
                       nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('system.system_id'),
                          nullable=False)
    key_id = db.Column(db.Integer, db.ForeignKey('key.key_id'), nullable=False)
    swid_tag = db.Column(db.String, nullable=False)
