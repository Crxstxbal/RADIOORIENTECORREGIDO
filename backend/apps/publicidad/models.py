from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from PIL import Image

# ==========================
# Modelos existentes
# ==========================

class Publicidad(models.Model):
    """Publicidad base normalizada"""
    TIPO_CHOICES = [
        ('WEB', 'Web'),
        ('RADIAL', 'Radial'),
    ]
    
    nombre_cliente = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    archivo_media = models.URLField(max_length=500, blank=True, null=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publicidades')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'publicidad'
        verbose_name = 'Publicidad'
        verbose_name_plural = 'Publicidades'
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['tipo']),
            models.Index(fields=['activo']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
                name='publicidad_fechas_validas'
            )
        ]
    
    def __str__(self):
        return f"{self.nombre_cliente} - {self.get_tipo_display()}"

class PublicidadWeb(models.Model):
    """Publicidad web específica"""
    UBICACION_CHOICES = [
        ('banner_superior', 'Banner Superior'),
        ('lateral', 'Lateral'),
        ('footer', 'Footer'),
    ]
    
    publicidad = models.OneToOneField(Publicidad, on_delete=models.CASCADE, related_name='web_config')
    ubicacion = models.CharField(max_length=50, choices=UBICACION_CHOICES)
    formato = models.CharField(max_length=50, blank=True, null=True)
    url_destino = models.URLField(max_length=500, blank=True, null=True)
    impresiones = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    clics = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    costo_por_dia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'publicidad_web'
        verbose_name = 'Publicidad Web'
        verbose_name_plural = 'Publicidades Web'
    
    def __str__(self):
        return f"{self.publicidad.nombre_cliente} - {self.get_ubicacion_display()}"

class PublicidadRadial(models.Model):
    """Publicidad radial específica"""
    publicidad = models.OneToOneField(Publicidad, on_delete=models.CASCADE, related_name='radial_config')
    horario = models.ForeignKey('radio.HorarioPrograma', on_delete=models.CASCADE, related_name='publicidades')
    duracion_segundos = models.IntegerField(validators=[MinValueValidator(1)])
    valor_por_segundo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'publicidad_radial'
        verbose_name = 'Publicidad Radial'
        verbose_name_plural = 'Publicidades Radiales'
        indexes = [
            models.Index(fields=['horario']),
        ]
    
    def __str__(self):
        return f"{self.publicidad.nombre_cliente} - {self.horario}"

# ==========================
# Modelos de Autoservicio
# ==========================

class EspacioPublicitario(models.Model):
    """Catálogo de ubicaciones publicitarias disponibles en el sitio web."""
    UBICACION_CHOICES = [
        ('header', 'Encabezado'),
        ('top_page', 'Parte Superior'),
        ('sidebar_left', 'Barra Lateral Izquierda'),
        ('sidebar_right', 'Barra Lateral Derecha'),
        ('content', 'Contenido'),
        ('footer', 'Pie de Página'),
    ]
    
    nombre = models.CharField('Nombre del Espacio', max_length=150)
    codigo = models.SlugField('Código', max_length=80, unique=True)
    ubicacion = models.CharField('Ubicación', max_length=30, choices=UBICACION_CHOICES)
    ancho_px = models.PositiveIntegerField('Ancho (px)')
    alto_px = models.PositiveIntegerField('Alto (px)')
    formatos_permitidos = models.JSONField(
        'Formatos Permitidos', 
        default=list, 
        help_text='Ej: ["jpg","png","webp","gif"]'
    )
    peso_max_mb = models.DecimalField(
        'Peso Máximo (MB)', 
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('2.00')
    )
    precio_por_dia = models.DecimalField(
        'Precio por Día', 
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    activo = models.BooleanField('¿Activo?', default=True)
    descripcion = models.TextField('Descripción', blank=True, null=True)

    class Meta:
        db_table = 'espacio_publicitario'
        verbose_name = 'Espacio Publicitario'
        verbose_name_plural = 'Espacios Publicitarios'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['ubicacion']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.ancho_px}x{self.alto_px})"


class SolicitudPublicidad(models.Model):
    """Solicitud de publicidad enviada por un cliente."""
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('en_revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    ]
    
    CANAL_CHOICES = [
        ('formulario_web', 'Formulario Web'),
        ('administrador', 'Creado por Administrador'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Usuario'
    )
    nombre_cliente = models.CharField('Nombre del Cliente', max_length=150)
    email = models.EmailField('Correo Electrónico')
    telefono = models.CharField('Teléfono', max_length=50, blank=True, null=True)
    whatsapp = models.CharField('WhatsApp', max_length=50, blank=True, null=True)
    mensaje_cliente = models.TextField('Mensaje Adicional', blank=True, null=True)
    estado = models.CharField(
        'Estado', 
        max_length=15, 
        choices=ESTADO_CHOICES, 
        default='borrador'
    )
    canal = models.CharField(
        'Canal de Creación', 
        max_length=20, 
        choices=CANAL_CHOICES, 
        default='formulario_web'
    )
    monto_estimado = models.DecimalField(
        'Monto Estimado', 
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última Actualización', auto_now=True)

    class Meta:
        db_table = 'solicitud_publicidad'
        verbose_name = 'Solicitud de Publicidad'
        verbose_name_plural = 'Solicitudes de Publicidad'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"Solicitud #{self.id} - {self.nombre_cliente} ({self.get_estado_display()})"


class ItemSolicitud(models.Model):
    """Cada línea de la solicitud de publicidad."""
    solicitud = models.ForeignKey(
        SolicitudPublicidad, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='Solicitud'
    )
    espacio = models.ForeignKey(
        EspacioPublicitario, 
        on_delete=models.PROTECT, 
        related_name='items_solicitud',
        verbose_name='Espacio Publicitario'
    )
    fecha_inicio = models.DateField('Fecha de Inicio')
    fecha_fin = models.DateField('Fecha de Finalización')
    precio_dia = models.DecimalField('Precio por Día', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(
        'Subtotal', 
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    url_destino = models.URLField('URL de Destino', max_length=500, blank=True, null=True)
    notas = models.TextField('Notas Adicionales', blank=True, null=True)

    class Meta:
        db_table = 'item_solicitud'
        verbose_name = 'Ítem de Solicitud'
        verbose_name_plural = 'Ítems de Solicitud'
        indexes = [
            models.Index(fields=['solicitud']),
            models.Index(fields=['espacio']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
                name='fechas_validas_item_solicitud'
            )
        ]
    
    def __str__(self):
        return f"Ítem #{self.id} - {self.espacio.codigo}"
    
    @property
    def dias(self) -> int:
        """Calcula la cantidad de días entre fecha_inicio y fecha_fin"""
        return (self.fecha_fin - self.fecha_inicio).days + 1


class CreatividadPublicitaria(models.Model):
    """Archivos de creatividad subidos por el cliente para cada ítem."""
    item = models.ForeignKey(
        ItemSolicitud, 
        on_delete=models.CASCADE, 
        related_name='creatividades',
        verbose_name='Ítem de Solicitud'
    )
    archivo = models.ImageField(
        'Archivo', 
        upload_to='publicidad/creatividades/'
    )
    ancho_px_detectado = models.PositiveIntegerField(
        'Ancho Detectado (px)', 
        blank=True, 
        null=True
    )
    alto_px_detectado = models.PositiveIntegerField(
        'Alto Detectado (px)', 
        blank=True, 
        null=True
    )
    formato_detectado = models.CharField(
        'Formato Detectado', 
        max_length=20, 
        blank=True, 
        null=True
    )
    valido = models.BooleanField('¿Válido?', default=True)
    razon_invalidez = models.TextField('Razón de Invalidez', blank=True, null=True)
    fecha_subida = models.DateTimeField('Fecha de Subida', auto_now_add=True)

    class Meta:
        db_table = 'creatividad_publicitaria'
        verbose_name = 'Creatividad Publicitaria'
        verbose_name_plural = 'Creatividades Publicitarias'
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['fecha_subida']),
        ]
    
    def __str__(self):
        return f"Creatividad #{self.id} para ítem #{self.item_id}"
    
    def clean(self):
        """Valida dimensiones, formato y peso máximo según el espacio publicitario."""
        super().clean()
        if not self.archivo:
            return
            
        espacio = self.item.espacio if self.item_id else None
        if not espacio:
            return
            
        # Validar peso
        if self.archivo.size is not None:
            mb = Decimal(self.archivo.size) / Decimal(1024 * 1024)
            if mb > espacio.peso_max_mb:
                self.valido = False
                self.razon_invalidez = f"Peso {mb:.2f}MB excede el máximo permitido de {espacio.peso_max_mb}MB"
                raise ValidationError(self.razon_invalidez)
        
        # Validar dimensiones y formato
        try:
            self.archivo.seek(0)
            with Image.open(self.archivo) as img:
                w, h = img.size
                self.ancho_px_detectado = w
                self.alto_px_detectado = h
                self.formato_detectado = (img.format or '').lower()
                
                # Validar dimensiones
                if w != espacio.ancho_px or h != espacio.alto_px:
                    self.valido = False
                    self.razon_invalidez = (
                        f"Dimensiones {w}x{h}px no coinciden con las requeridas: "
                        f"{espacio.ancho_px}x{espacio.alto_px}px"
                    )
                    raise ValidationError(self.razon_invalidez)
                
                # Validar formato
                if self.archivo.name:
                    ext = self.archivo.name.split('.')[-1].lower()
                    if ext not in espacio.formatos_permitidos:
                        self.valido = False
                        self.razon_invalidez = (
                            f"Formato no permitido: {ext}. "
                            f"Formatos permitidos: {', '.join(espacio.formatos_permitidos)}"
                        )
                        raise ValidationError(self.razon_invalidez)
                        
        except ValidationError:
            raise
        except Exception as e:
            self.valido = False
            self.razon_invalidez = f"Error al validar la imagen: {str(e)}"
            raise ValidationError(self.razon_invalidez)
        finally:
            self.archivo.seek(0)
