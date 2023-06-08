from datetime import datetime

from itsdangerous import Serializer, BadSignature, SignatureExpired
from gateway import create_app as app
from gateway import db
from gateway import ma


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(100))
    phone_no = db.Column(db.String(100))
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(50))

    def __init__(self, email, confirmed,
                 phone_number,
                 paid=False, admin=False, confirmed_on=None):
        self.email = email
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        # self.hash_password = pwd_context.encrypt(password)
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.phone_number = phone_number

    # def hash_password(self, password):
    #     self.password_hash = pwd_context.encrypt(password)
    #
    # def verify_password(self, password):
    #     return pwd_context.verify(password, self.password_hash)
    #
    # def generate_auth_token(self, expiration=60000):
    #     s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    #     return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class MpesaTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(10), nullable=True,)
    transaction_id = db.Column(db.String(10), nullable=True)
    transaction_time = db.Column(
        db.DateTime, index=True, default=datetime.utcnow)
    uiid = db.Column(db.String(100), nullable=False, unique=True)
    trasnction_amount = db.Column(db.String(50))
    business_short_code = db.Column(db.String(50))
    bill_ref = db.Column(db.String(20))
    msisdn = db.Column(db.String(50))
    first_name = db.Column(db.String(20))
    middle_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    transaction_header_id = db.Column(
        db.Integer, db.ForeignKey('transaction_header.id'), nullable=True)

    def __init__(self, **kwargs):
        super(MpesaTransaction, self).__init__(**kwargs)


class TransactionHeader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String())
    uiid = db.Column(db.String(100), nullable=False, unique=True)
    time_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    time_modefied = db.Column(db.DateTime, nullable=True,)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_on = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    mpesa_transaction = db.relationship(
        'MpesaTransaction', backref='transaction_header', lazy=True, uselist=False)
    transaction_line = db.relationship(
        'TransactionLine', backref='transaction_header', lazy=True)

    def __init__(self, **kwargs):
        super(TransactionHeader, self).__init__(**kwargs)


class TransactionLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    loan_id = db.Column(db.Integer)
    transaction_header_id = db.Column(db.Integer, db.ForeignKey(
        'transaction_header.id'), nullable=False)

    def __init__(self, **kwargs):
        super(TransactionLine, self).__init__(**kwargs)


class Setup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100))


class MpesaTransactionSchema(ma.ModelSchema):
    """docstring for ClassName"""
    class Meta:
        model = MpesaTransaction


class TransactionLineSchema(ma.ModelSchema):

    class Meta:
        model = TransactionLine


class TransactionHeaderSchema(ma.ModelSchema):
    transaction_line = ma.Nested(TransactionLineSchema, many=True)
    mpesa_transaction = ma.Nested(MpesaTransactionSchema, many=False)

    class Meta:
        fields = ('transaction_type', 'completed', 'uiid',
                  'transaction_line', 'mpesa_transaction')
        model = TransactionHeader()
