from django.db import connection

class AuditMiddleware:
    """
    Inyecta el ID de usuario autenticado y la IP del cliente en 
    la sesion de PostgreSQL antes de cada request
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
          self._inyectar_contexto(request)
          response = self.get_response(request)
          return response

    def _inyectar_contexto(self, request) -> None:
          user_id = (
            str(request.user.pk)
            if request.user.is_authenticated
            else ""
          )
          ip = self._obtener_ip(request)

          with connection.cursor() as cursor:
              cursor.execute(
                  """
                  SELECT set_config('app.current_user_id', %s, FALSE),
                         set_config('app.ip_address',      %s, FALSE)
                  """,
                  [user_id, ip],
              )

    def _obtener_ip(self, request) -> str:
          # X-Forwarded-For aparece cuando hay un proxy o balanceador.
          # Tomamos la primera IP — es la del cliente real.
          x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
          if x_forwarded:
              return x_forwarded.split(",")[0].strip()
          return request.META.get("REMOTE_ADDR", "")
        
        
        