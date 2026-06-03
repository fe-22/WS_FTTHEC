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


class CRMPublicRegistrationForm(forms.Form):
    empresa = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nome da empresa"}
        ),
    )
    nome = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nome completo"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "seu@email.com"}
        )
    )
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "(11) 99999-9999"}
        ),
    )
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


class CRMAccessProvisionForm(forms.Form):
    username = forms.CharField(
        label="Usuario ou e-mail",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "usuario@empresa.com ou admin",
                "autocomplete": "username",
            }
        ),
    )
    email = forms.EmailField(
        label="E-mail para envio",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "usuario@empresa.com",
                "autocomplete": "email",
            }
        ),
    )
    nome = forms.CharField(
        label="Nome",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nome do usuario"}
        ),
    )
    empresa = forms.CharField(
        label="Empresa",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Empresa vinculada"}
        ),
    )
    telefone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "(11) 99999-9999"}
        ),
    )
    make_staff = forms.BooleanField(
        label="Permitir administrar acessos",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    send_email = forms.BooleanField(
        label="Tentar enviar a senha por e-mail",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if "@" in username:
            return username.lower()
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        return email.lower()


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
