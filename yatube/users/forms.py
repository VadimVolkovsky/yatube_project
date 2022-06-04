from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


# class ChangingPasswordForm(PasswordChangeForm):
#     class Meta(PasswordChangeForm):
#         model = User
#         help_texts = {
#              'old_password': 'Здесь надо вспомнить свой старый пароль'
#         }
