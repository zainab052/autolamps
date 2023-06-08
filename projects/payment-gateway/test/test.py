import unittest
from config import TestConfig
from gateway import create_app, db
from gateway.models import TransactionHeader,TransactionLine,MpesaTransaction

class MpesaModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_transaction_insert(self):
        transaction = TransactionHeader(transaction_type='paybill',uiid='1231',)
        db.session.add(transaction)
        db.session.commit()

if __name__ == '__main__':
    unittest.main(verbosity=2)