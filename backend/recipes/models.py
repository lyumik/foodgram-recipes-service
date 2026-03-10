from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    color = models.CharField(max_length=7, unique=True, verbose_name='Цвет HEX')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(max_length=200, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author_id = models.IntegerField(verbose_name='ID автора')
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/', verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(verbose_name='Время приготовления (мин)')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name