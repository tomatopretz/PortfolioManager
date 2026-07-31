"""Shared OpenAPI spec instance.
Lives in its own module (not app.py) so route files can import it and decorate
their views with @api.validate(...) directly"""

import json

from flask_pydantic_spec import FlaskPydanticSpec


def _format_validation_error(_req, resp, req_validation_error, _instance) -> None:
    """Rewrite pydantic's raw error list into {"error": str}, matching ErrorResultDTO."""
    if req_validation_error is None:
        return
    messages = []
    for err in req_validation_error.errors():
        field = '.'.join(str(part) for part in err['loc'])
        message = err['msg'].removeprefix('Value error, ')
        messages.append(f'{field}: {message}' if field else message)
    resp.set_data(json.dumps({'error': '\n'.join(messages)}))


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
    before=_format_validation_error,
)
