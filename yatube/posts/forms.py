from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите какой-нибудь текст, ну пожалуйста 😥')
        self.fields['group'].empty_label = (
            'Нажмите сюда, чтобы выбрать группу')

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Пост:',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Напишите пост и нажмите "Добавить"',
            'group': 'Выбирать группу не обязательно',
        }
