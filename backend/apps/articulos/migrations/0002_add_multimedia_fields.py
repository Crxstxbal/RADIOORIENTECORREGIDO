# Generated manually - Add multimedia support fields

import apps.articulos.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def generate_category_slugs(apps, schema_editor):
    """Genera slugs para las categorías existentes"""
    Categoria = apps.get_model('articulos', 'Categoria')
    for categoria in Categoria.objects.all():
        if not categoria.slug:
            categoria.slug = slugify(categoria.nombre)
            # Asegurar que sea único
            original_slug = categoria.slug
            counter = 1
            while Categoria.objects.filter(slug=categoria.slug).exists():
                categoria.slug = f"{original_slug}-{counter}"
                counter += 1
            categoria.save()


class Migration(migrations.Migration):

    dependencies = [
        ('articulos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Agregar slug a Categoria (primero sin unique)
        migrations.AddField(
            model_name='categoria',
            name='slug',
            field=models.SlugField(blank=True, max_length=60, default=''),
        ),
        
        # Generar slugs para categorías existentes
        migrations.RunPython(generate_category_slugs, reverse_code=migrations.RunPython.noop),
        
        # Hacer el campo slug único
        migrations.AlterField(
            model_name='categoria',
            name='slug',
            field=models.SlugField(blank=True, max_length=60, unique=True),
        ),
        
        # Agregar campos multimedia a Articulo
        migrations.AddField(
            model_name='articulo',
            name='imagen_portada',
            field=models.ImageField(
                blank=True,
                help_text='Imagen destacada del artículo (JPG, PNG, máx 5MB)',
                null=True,
                upload_to=apps.articulos.models.upload_to_articulos_imagen,
                verbose_name='Imagen de portada'
            ),
        ),
        migrations.AddField(
            model_name='articulo',
            name='video_url',
            field=models.URLField(
                blank=True,
                help_text='YouTube, Vimeo, etc. (opcional)',
                null=True,
                verbose_name='URL de video'
            ),
        ),
        migrations.AddField(
            model_name='articulo',
            name='archivo_adjunto',
            field=models.FileField(
                blank=True,
                help_text='PDF, Word, Excel, etc. (opcional, máx 10MB)',
                null=True,
                upload_to=apps.articulos.models.upload_to_articulos_archivo,
                verbose_name='Archivo adjunto'
            ),
        ),
        migrations.AddField(
            model_name='articulo',
            name='fecha_actualizacion',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='Última actualización'
            ),
        ),
        migrations.AddField(
            model_name='articulo',
            name='vistas',
            field=models.PositiveIntegerField(
                default=0,
                verbose_name='Vistas'
            ),
        ),
        
        # Modificar relación categoria para permitir NULL
        migrations.AlterField(
            model_name='articulo',
            name='categoria',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='articulos',
                to='articulos.categoria',
                verbose_name='Categoría'
            ),
        ),
        
        # Crear tabla de comentarios
        migrations.CreateModel(
            name='ComentarioArticulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
                ('articulo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comentarios',
                    to='articulos.articulo'
                )),
                ('autor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comentarios_articulos',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Comentario',
                'verbose_name_plural': 'Comentarios',
                'db_table': 'comentario_articulo',
                'ordering': ['-fecha_creacion'],
            },
        ),
        
        # Agregar índices si no existen
        migrations.AddIndex(
            model_name='articulo',
            index=models.Index(fields=['publicado'], name='articulo_publica_f53dc7_idx'),
        ),
        migrations.AddIndex(
            model_name='articulo',
            index=models.Index(fields=['slug'], name='articulo_slug_1d29b5_idx'),
        ),
        migrations.AddIndex(
            model_name='articulo',
            index=models.Index(fields=['autor'], name='articulo_autor_i_9d8dd0_idx'),
        ),
        migrations.AddIndex(
            model_name='articulo',
            index=models.Index(fields=['categoria'], name='articulo_categor_ae1160_idx'),
        ),
        migrations.AddIndex(
            model_name='articulo',
            index=models.Index(fields=['-fecha_publicacion'], name='articulo_fecha_p_111db5_idx'),
        ),
    ]
