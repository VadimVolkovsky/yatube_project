from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель, добавляет дату создания"""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
