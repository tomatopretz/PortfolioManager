"""Shared OpenAPI spec instance.
Lives in its own module (not app.py) so route files can import it and decorate
their views with @api.validate(...) directly"""

from flask_pydantic_spec import FlaskPydanticSpec

class _ApiSpec(FlaskPydanticSpec):
    _hidden_schemas: set[str] = set()

    def hide_from_schemas(self, *models: type) -> None:
        self._hidden_schemas.update(m.__name__ for m in models)

    def _get_model_definitions(self) -> dict:
        return {k: v for k, v in super()._get_model_definitions().items() if k not in self._hidden_schemas}


api = _ApiSpec(
    'flask',
    title='Portfolio Manager API',
    version='0.1.0',
    path='apidocs',  # UI at /apidocs/swagger, spec at /apidocs/openapi.json
)
