from django.forms import CharField, Form, TextInput


class LoginForm(Form):
    pin = CharField(
        min_length=12,
        max_length=12,
        widget=TextInput(
            attrs={
                "placeholder": "PIN",
                "class": "input1",
                "type": "text",
            }
        )
    )

    password = CharField(
        max_length=255,
        widget=TextInput(
            attrs={
                "placeholder": "Password",
                "class": "input2",
                "type": "password",
            }
        )
    )
