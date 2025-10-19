from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Pais, Ciudad, Comuna
from .serializers import PaisSerializer, CiudadSerializer, ComunaSerializer, ComunaDetailSerializer
import requests
from django.db import transaction
import urllib3
from .datos_chile import REGIONES_COMUNAS

# Deshabilitar advertencias de SSL (solo para desarrollo)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PaisViewSet(viewsets.ModelViewSet):
    """ViewSet para países"""
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def reiniciar_datos_chile(self, request):
        """Limpia y recarga todos los datos de Chile desde datos locales"""
        try:
            with transaction.atomic():
                # Eliminar todos los datos de ubicación existentes
                Comuna.objects.all().delete()
                Ciudad.objects.all().delete()
                Pais.objects.all().delete()
                
                # Crear Chile
                chile, _ = Pais.objects.get_or_create(nombre='Chile')
                
                ciudades_creadas = 0
                comunas_creadas = 0
                
                # Cargar regiones y comunas desde datos locales
                for nombre_region, comunas_list in REGIONES_COMUNAS.items():
                    # Crear región como ciudad
                    ciudad, created = Ciudad.objects.get_or_create(
                        nombre=nombre_region,
                        pais=chile
                    )
                    if created:
                        ciudades_creadas += 1
                    
                    # Crear comunas de esta región
                    for nombre_comuna in comunas_list:
                        _, created = Comuna.objects.get_or_create(
                            nombre=nombre_comuna,
                            ciudad=ciudad
                        )
                        if created:
                            comunas_creadas += 1
                
                return Response({
                    'message': 'Datos de Chile cargados correctamente',
                    'regiones_creadas': ciudades_creadas,
                    'comunas_creadas': comunas_creadas
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': f'Error al procesar datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CiudadViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ciudades (solo lectura)"""
    queryset = Ciudad.objects.select_related('pais').all()
    serializer_class = CiudadSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def por_pais(self, request):
        """Obtener ciudades por país"""
        pais_id = request.query_params.get('pais_id')
        if pais_id:
            ciudades = self.queryset.filter(pais_id=pais_id)
            serializer = self.get_serializer(ciudades, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['post'])
    def cargar_desde_api(self, request):
        """Cargar regiones de Chile desde API externa y guardar en BD"""
        try:
            # API pública de regiones de Chile
            api_url = "https://apis.digital.gob.cl/dpa/regiones"
            response = requests.get(api_url, timeout=10, verify=False)
            response.raise_for_status()
            
            regiones_data = response.json()
            
            # Obtener o crear Chile
            chile, _ = Pais.objects.get_or_create(nombre='Chile')
            
            ciudades_creadas = 0
            with transaction.atomic():
                for region in regiones_data:
                    nombre_region = region.get('nombre', '')
                    if nombre_region:
                        _, created = Ciudad.objects.get_or_create(
                            nombre=nombre_region,
                            pais=chile
                        )
                        if created:
                            ciudades_creadas += 1
            
            return Response({
                'message': f'Se cargaron {ciudades_creadas} regiones desde la API',
                'total_regiones': len(regiones_data)
            }, status=status.HTTP_201_CREATED)
            
        except requests.RequestException as e:
            return Response({
                'error': f'Error al conectar con la API: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'Error al procesar datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ComunaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para comunas (solo lectura)"""
    queryset = Comuna.objects.select_related('ciudad__pais').all()
    serializer_class = ComunaSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def por_ciudad(self, request):
        """Obtener comunas por ciudad"""
        ciudad_id = request.query_params.get('ciudad_id')
        if ciudad_id:
            comunas = self.queryset.filter(ciudad_id=ciudad_id)
            serializer = ComunaDetailSerializer(comunas, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['post'])
    def cargar_desde_api(self, request):
        """Cargar comunas de Chile desde API externa y guardar en BD"""
        try:
            # API pública de regiones de Chile
            api_url = "https://apis.digital.gob.cl/dpa/regiones"
            response = requests.get(api_url, timeout=10, verify=False)
            response.raise_for_status()
            
            regiones_data = response.json()
            
            # Obtener Chile
            chile = Pais.objects.get(nombre='Chile')
            
            comunas_creadas = 0
            comunas_totales = 0
            
            with transaction.atomic():
                for region in regiones_data:
                    codigo_region = region.get('codigo', '')
                    nombre_region = region.get('nombre', '')
                    
                    if not codigo_region or not nombre_region:
                        continue
                    
                    # Obtener o crear la región como ciudad
                    ciudad, _ = Ciudad.objects.get_or_create(
                        nombre=nombre_region,
                        pais=chile
                    )
                    
                    # Obtener comunas de esta región
                    comunas_url = f"https://apis.digital.gob.cl/dpa/regiones/{codigo_region}/comunas"
                    comunas_response = requests.get(comunas_url, timeout=10, verify=False)
                    comunas_response.raise_for_status()
                    
                    comunas_data = comunas_response.json()
                    comunas_totales += len(comunas_data)
                    
                    for comuna in comunas_data:
                        nombre_comuna = comuna.get('nombre', '')
                        if nombre_comuna:
                            _, created = Comuna.objects.get_or_create(
                                nombre=nombre_comuna,
                                ciudad=ciudad
                            )
                            if created:
                                comunas_creadas += 1
            
            return Response({
                'message': f'Se cargaron {comunas_creadas} comunas desde la API',
                'total_comunas': comunas_totales,
                'nuevas_comunas': comunas_creadas
            }, status=status.HTTP_201_CREATED)
            
        except Pais.DoesNotExist:
            return Response({
                'error': 'Primero debes cargar las regiones. País Chile no encontrado.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({
                'error': f'Error al conectar con la API: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'Error al procesar datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
