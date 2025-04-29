import time
import logging
import requests
import settings
from db.redis.connection import get_connection as get_redis_connection

logger = logging.getLogger(__name__)

class ProjectUUIDCache:
    """
    Gerencia o cache de uuid de projetos, com atualização sob demanda.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Implementação Singleton para o cache"""
        if cls._instance is None:
            cls._instance = cls(
                endpoint_url=settings.PROJECT_API_ENDPOINT,
                cache_key=settings.PROJECT_CACHE_KEY,
                ttl_seconds=settings.PROJECT_CACHE_TTL
            )
        return cls._instance
    
    def __init__(self, endpoint_url, cache_key="allowed_projects_cache", ttl_seconds=86400):
        self.endpoint_url = endpoint_url
        self.cache_key = cache_key
        self.ttl_seconds = ttl_seconds
        self.redis = get_redis_connection()
        self.last_check_time = 0
        self.check_interval = 300  # Verifica a cada 5 minutos
        
    def _fetch_projects_from_api(self):
        """Busca a lista de uuids de projetos do endpoint"""
        try:
            headers = {"Authorization": f"Token {settings.STATIC_API_TOKEN}"}
            logger.info(f"Buscando projetos do endpoint: {self.endpoint_url}")
            response = requests.get(self.endpoint_url, headers=headers, timeout=30)
            if response.status_code == 200:
                project_uuids    = response.json()
                logger.info(f"Recebidas {len(project_uuids)} projetos do endpoint")
                return project_uuids
            else:
                logger.error(f"Erro ao buscar projetos: status {response.status_code}")
                return []
        except Exception as e:
            logger.exception(f"Exceção ao buscar projetos: {str(e)}")
            return []

    def _should_refresh_cache(self):
        """Verifica se o cache precisa ser atualizado"""
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return False
            
        self.last_check_time = current_time
        
        ttl = self.redis.ttl(self.cache_key)
        return ttl < 0 or ttl < (self.ttl_seconds * 0.25)

    def get_projects_uuids(self):
        """
        Obtém a lista de uuids de projetos do cache.
        Atualiza o cache automaticamente quando necessário.
        """
        # Verifica se o endpoint está configurado
        if not self.endpoint_url:
            return []
            
        # Verifica se precisa atualizar o cache
        if self._should_refresh_cache():
            projects_uuids   = self._fetch_projects_from_api()
            if projects_uuids:
                projects_uuids_str = ",".join(str(project_uuid) for project_uuid in projects_uuids)
                self.redis.setex(self.cache_key, self.ttl_seconds, projects_uuids_str)
                return projects_uuids
        
        # Tenta obter do cache
        cached_value = self.redis.get(self.cache_key)
        if cached_value:
            return [str(project_uuid) for project_uuid in cached_value.split(",") if project_uuid.strip()]
        
        # Retorna lista vazia se nada estiver disponível
        return []