import time
import logging
import requests
import settings
from db.redis.connection import get_connection as get_redis_connection

logger = logging.getLogger(__name__)

class OrgIdCache:
    """
    Gerencia o cache de IDs de organizações, com atualização sob demanda.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Implementação Singleton para o cache"""
        if cls._instance is None:
            cls._instance = cls(
                endpoint_url=settings.ORG_API_ENDPOINT,
                cache_key=settings.ORG_CACHE_KEY,
                ttl_seconds=settings.ORG_CACHE_TTL
            )
        return cls._instance
    
    def __init__(self, endpoint_url, cache_key="allowed_orgs_cache", ttl_seconds=86400):
        self.endpoint_url = endpoint_url
        self.cache_key = cache_key
        self.ttl_seconds = ttl_seconds
        self.redis = get_redis_connection()
        self.last_check_time = 0
        self.check_interval = 300  # Verifica a cada 5 minutos
        
    def _fetch_orgs_from_api(self):
        """Busca a lista de IDs de organizações do endpoint"""
        try:
            logger.info(f"Buscando organizações do endpoint: {self.endpoint_url}")
            response = requests.get(self.endpoint_url, timeout=30)
            if response.status_code == 200:
                org_ids = response.json()
                logger.info(f"Recebidas {len(org_ids)} organizações do endpoint")
                return org_ids
            else:
                logger.error(f"Erro ao buscar organizações: status {response.status_code}")
                return []
        except Exception as e:
            logger.exception(f"Exceção ao buscar organizações: {str(e)}")
            return []

    def _should_refresh_cache(self):
        """Verifica se o cache precisa ser atualizado"""
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return False
            
        self.last_check_time = current_time
        
        ttl = self.redis.ttl(self.cache_key)
        return ttl < 0 or ttl < (self.ttl_seconds * 0.25)

    def get_org_ids(self):
        """
        Obtém a lista de IDs de organizações do cache.
        Atualiza o cache automaticamente quando necessário.
        """
        # Verifica se o endpoint está configurado
        if not self.endpoint_url:
            return []
            
        # Verifica se precisa atualizar o cache
        if self._should_refresh_cache():
            org_ids = self._fetch_orgs_from_api()
            if org_ids:
                org_ids_str = ",".join(str(org_id) for org_id in org_ids)
                self.redis.setex(self.cache_key, self.ttl_seconds, org_ids_str)
                return org_ids
        
        # Tenta obter do cache
        cached_value = self.redis.get(self.cache_key)
        if cached_value:
            return [int(org_id) for org_id in cached_value.split(",") if org_id.strip()]
        
        # Retorna lista vazia se nada estiver disponível
        return []