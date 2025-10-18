# Generated manually - Initial state from blog app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Crear modelo Categoria (tabla ya existe)
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'db_table': 'categoria',
                'ordering': ['nombre'],
            },
        ),
        # Crear modelo Articulo (tabla ya existe con campos básicos)
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True)),
                ('contenido', models.TextField(verbose_name='Contenido')),
                ('resumen', models.TextField(blank=True, null=True, verbose_name='Resumen')),
                ('imagen_url', models.URLField(blank=True, max_length=500, null=True)),
                ('publicado', models.BooleanField(default=False, verbose_name='Publicado')),
                ('destacado', models.BooleanField(default=False, verbose_name='Destacado')),
                ('fecha_publicacion', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articulos', to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articulos', to='articulos.categoria', verbose_name='Categoría')),
            ],
            options={
                'verbose_name': 'Artículo',
                'verbose_name_plural': 'Artículos',
                'db_table': 'articulo',
                'ordering': ['-fecha_publicacion', '-fecha_creacion'],
            },
        ),
    ]
