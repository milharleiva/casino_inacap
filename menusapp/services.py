from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from django.conf import settings
from transbank.common.integration_type import IntegrationType

def initialize_transbank_sdk():
    
    if not hasattr(Transaction, 'is_configured') or not Transaction.is_configured:
        try:
           
            Transaction.configure_for_integration(
                settings.TRANSBANK_COMMERCE_CODE, settings.TRANSBANK_API_KEY)
           
            Transaction.is_configured = True
            print("Transbank SDK configured successfully.")
        except TransbankError as e:
            
            print(f"Error al configurar Transbank SDK: {str(e)}")

class TransbankService:
    @staticmethod
    def iniciar_transaccion(monto, orden_compra, sesion_id, url_retorno):
        
        initialize_transbank_sdk()
        
        try:
            response = Transaction.create(
                buy_order=orden_compra,
                session_id=sesion_id,
                amount=monto,
                return_url=url_retorno
            )
            return response.url, response.token
        except TransbankError as e:
            print(f"Error al iniciar transacción: {str(e)}")
            return None, None

    @staticmethod
    def confirmar_transaccion(token):
        
        initialize_transbank_sdk()
        
        try:
            result = Transaction.commit(token=token)
            return result
        except TransbankError as e:
            print(f"Error al confirmar transacción: {e.message}")
            return None
