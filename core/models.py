# core/models.py - Exemplo básico
from django.db import models

class Inscricao(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    empresa = models.CharField(max_length=100, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    mensagem = models.TextField(blank=True)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome} - {self.email}"