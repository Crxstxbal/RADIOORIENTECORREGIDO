from django import forms
from django.forms import ModelForm
from apps.emergente.models import BandaEmergente, BandaLink, Integrante, BandaIntegrante
from .models import Region, Comuna

class BandaEmergenteForm(ModelForm):
    """Formulario para crear y editar bandas emergentes"""
    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('orden'),
        label='Región',
        required=False,
        empty_label='Seleccione una región'
    )
    
    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.none(),
        label='Comuna',
        required=False,
        empty_label='Primero seleccione una región'
    )
    
    class Meta:
        model = BandaEmergente
        fields = [
            'nombre_banda', 'email_contacto', 'telefono_contacto', 
            'mensaje', 'documento_presentacion', 'genero', 'comuna'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si la instancia ya tiene una comuna, establecer la región correspondiente
        if 'comuna' in self.data:
            try:
                comuna_id = int(self.data.get('comuna'))
                comuna = Comuna.objects.get(id=comuna_id)
                self.fields['comuna'].queryset = Comuna.objects.filter(region=comuna.region).order_by('nombre')
                self.fields['region'].initial = comuna.region
            except (ValueError, Comuna.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.comuna:
            self.fields['comuna'].queryset = Comuna.objects.filter(
                region=self.instance.comuna.region
            ).order_by('nombre')
            self.fields['region'].initial = self.instance.comuna.region
        
        # Establecer clases CSS para los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Hacer que el campo de mensaje sea un textarea
        self.fields['mensaje'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        
        # Hacer que el campo de género sea requerido
        self.fields['genero'].required = True
        self.fields['genero'].empty_label = 'Seleccione un género'
        
        # Hacer que el campo de comuna sea requerido si se selecciona una región
        if 'region' in self.data and self.data['region']:
            self.fields['comuna'].required = True
