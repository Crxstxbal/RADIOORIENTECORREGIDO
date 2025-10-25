from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Pais, Ciudad, Comuna
from .serializers import PaisSerializer, CiudadSerializer, ComunaSerializer, ComunaDetailSerializer
import requests
from django.db import transaction
import urllib3

# Deshabilitar advertencias de SSL (solo para desarrollo)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Helpers para consultar API externa DIVPA con fallback
DIVPA_BASE = "https://apis.digital.gob.cl/dpa"

def _fetch_divpa_regiones():
    """Obtiene regiones desde API DIVPA. Lanza excepción si falla."""
    url = f"{DIVPA_BASE}/regiones"
    resp = requests.get(url, timeout=15, verify=False)
    resp.raise_for_status()
    return resp.json()

def _fetch_divpa_comunas_por_region(codigo_region):
    """Obtiene comunas por código de región desde API DIVPA. Lanza excepción si falla."""
    url = f"{DIVPA_BASE}/regiones/{codigo_region}/comunas"
    resp = requests.get(url, timeout=15, verify=False)
    resp.raise_for_status()
    return resp.json()

class PaisViewSet(viewsets.ModelViewSet):
    """ViewSet para países"""
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def reiniciar_datos_chile(self, request):
        """Limpia y recarga todos los datos de Chile desde la API externa DIVPA."""
        try:
            with transaction.atomic():
                # Eliminar datos de ubicación existentes para Chile
                Pais.objects.filter(nombre='Chile').delete() # Esto eliminará en cascada Ciudades y Comunas
                
                # Crear Chile
                chile = Pais.objects.create(nombre='Chile')
                
                regiones_creadas = 0
                comunas_creadas = 0
                
                # Cargar regiones desde la API
                regiones_data = _fetch_divpa_regiones()
                
                for region_data in regiones_data:
                    nombre_region = region_data.get('nombre')
                    codigo_region = region_data.get('codigo')
                    
                    if not nombre_region or not codigo_region:
                        continue

                    # Crear región como Ciudad
                    ciudad, created = Ciudad.objects.get_or_create(
                        nombre=nombre_region,
                        pais=chile
                    )
                    if created:
                        regiones_creadas += 1
                    
                    # Cargar comunas para esta región desde la API
                    comunas_data = _fetch_divpa_comunas_por_region(codigo_region)
                    for comuna_data in comunas_data:
                        nombre_comuna = comuna_data.get('nombre')
                        if not nombre_comuna:
                            continue
                        
                        _, created = Comuna.objects.get_or_create(
                            nombre=nombre_comuna,
                            ciudad=ciudad
                        )
                        if created:
                            comunas_creadas += 1
            
            return Response({
                'message': 'Datos de Chile cargados correctamente desde la API externa',
                'regiones_creadas': regiones_creadas,
                'comunas_creadas': comunas_creadas
            }, status=status.HTTP_201_CREATED)

        except requests.RequestException as e:
            return Response({
                'error': f'Error al conectar con la API externa: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'Error al procesar los datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CiudadViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ciudades (solo lectura)"""
    queryset = Ciudad.objects.select_related('pais').all()
    serializer_class = CiudadSerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        """Lista regiones (mapeadas como ciudades) intentando sincronizar primero desde API externa.
        Siempre devuelve datos desde BD para consistencia, con fallback automático si la API falla.
        """
        # Asegurar país Chile
        chile, _ = Pais.objects.get_or_create(nombre='Chile')
        try:
            regiones_data = _fetch_divpa_regiones()
            # Sincronizar regiones a BD
            created_count = 0
            with transaction.atomic():
                for region in regiones_data:
                    nombre_region = region.get('nombre') or ''
                    if not nombre_region:
                        continue
                    _, created = Ciudad.objects.get_or_create(
                        nombre=nombre_region,
                        pais=chile
                    )
                    if created:
                        created_count += 1
        except Exception:
            # Fallback silencioso: continuar con datos en BD
            pass
        # Responder siempre desde BD
        queryset = self.filter_queryset(self.get_queryset().filter(pais=chile))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_pais(self, request):
        """Obtener ciudades por país"""
        pais_id = request.query_params.get('pais_id')
        if pais_id:
            # Intentar sincronizar regiones si el país es Chile
            try:
                pais = Pais.objects.get(id=pais_id)
                if pais.nombre == 'Chile':
                    regiones_data = _fetch_divpa_regiones()
                    with transaction.atomic():
                        for region in regiones_data:
                            nombre_region = region.get('nombre') or ''
                            if not nombre_region:
                                continue
                            Ciudad.objects.get_or_create(
                                nombre=nombre_region,
                                pais=pais
                            )
            except Exception:
                # Fallback silencioso si falla la API o no existe el país
                pass
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
            # Intentar sincronizar desde API externa usando el nombre de la región
            try:
                ciudad = Ciudad.objects.select_related('pais').get(id=ciudad_id)
                if ciudad.pais.nombre == 'Chile':
                    # Buscar código de región por nombre
                    regiones_data = _fetch_divpa_regiones()
                    codigo_region = None
                    for reg in regiones_data:
                        if (reg.get('nombre') or '').strip().lower() == ciudad.nombre.strip().lower():
                            codigo_region = reg.get('codigo')
                            break
                    if codigo_region:
                        comunas_data = _fetch_divpa_comunas_por_region(codigo_region)
                        with transaction.atomic():
                            for c in comunas_data:
                                nombre_comuna = c.get('nombre') or ''
                                if not nombre_comuna:
                                    continue
                                Comuna.objects.get_or_create(
                                    nombre=nombre_comuna,
                                    ciudad=ciudad
                                )
            except Exception:
                # Fallback silencioso si falla la API o no existe la ciudad
                pass
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