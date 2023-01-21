from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    MAX_LENGHT_WORD = 128
    MAX_LENGHT_TEXT = 2048

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': ('Текст'),
            'group': ('Группа'),
        }
        help_texts = {
            'text': ('Текст нового поста'),
            'group': ('Группа, к которой будет относиться пост'),
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) > self.MAX_LENGHT_TEXT:
            raise forms.ValidationError(
                '%(value)s',
                code='max_lenght_text',
                params={'value': ('Ваш текст очень большой,'
                                  'пожалуйста сократите его.')}
            )
        for word in data.split():
            if len(word) > self.MAX_LENGHT_WORD:
                raise forms.ValidationError(
                    '%(value)s',
                    code='max_lenght_word',
                    params={'value': ('В вашем посте слишком'
                            ' длинное слово, пожалуйста замените')}
                )
        return data
