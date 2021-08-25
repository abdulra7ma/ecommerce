from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment


class PayPalClient:
    def __init__(self):
        self.client_id = "Ad7qtEj_UfFsvAXCw87ymMqgVI0_ieXy22zaVIvozJ_YUCEdWYHgTpeZSUZifXRuZ6xXo-wWSCvY-4Ff"
        self.client_secret = "ECEh7Guu8UEyR-0kk2rUK0RpETa0DSRucnIi0LSi6jIDD7Jfm7SLhFLGmZah-BSo3lQwtwPjaN_wlUfr"
        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)