from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Inscricao


class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['nome', 'email', 'telefone', 'empresa', 'cargo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da empresa'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu cargo'}),
        }


class CRMUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Seu usuario"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Crie uma senha"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirme a senha"}
        )


class CRMInviteCreateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "novo.usuario"}
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ja existe.")
        return username


class CRMInviteSetPasswordForm(forms.Form):
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Crie uma senha"}
        ),
    )
    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirme a senha"}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("As senhas nao conferem.")
        return cleaned_data
