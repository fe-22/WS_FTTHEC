import json

from django.test import TestCase
from django.urls import reverse


class ChatbotResponseTests(TestCase):
    def test_responde_empresas_e_segmentos_que_podem_usar_erp(self):
        response = self.client.post(
            reverse("chatbot_api"),
            data=json.dumps(
                {
                    "message": "Em quais empresas posso usar ERP?",
                    "session_id": "segmentos-test",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["error"])
        self.assertIn("Comercio e varejo", payload["response"])
        self.assertIn("Industria", payload["response"])
