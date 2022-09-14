"""File for configuring SuperSet, i.e. the superset_config.py file

This config adds an /api/v1/execute_sql_json/ endpoint under OAuth authentication, to
allow running queries through the API. Standard Superset only has /superset/sql_json/
which is only accessible via a browser.
"""
import logging
from typing import Optional, cast

from cachelib.file import FileSystemCache
from flask import request
from flask_appbuilder.api import protect
from flask_appbuilder.views import expose
from superset.initialization import SupersetAppInitializer

log = logging.getLogger(__name__)


class CustomInitializer(SupersetAppInitializer):
    def init_views(self) -> None:
        from superset.exceptions import SupersetErrorsException
        from superset.extensions import appbuilder
        from superset.sqllab.command import CommandResult
        from superset.sqllab.command_status import SqlJsonExecutionStatus
        from superset.sqllab.exceptions import SqlLabException
        from superset.sqllab.sqllab_execution_context import SqlJsonExecutionContext, SqlResults
        from superset.views.base import BaseSupersetView, json_error_response, json_success
        from superset.views.core import Superset

        class CustomContext(SqlJsonExecutionContext):
            def __init__(self, *args, **kwargs):
                self.query_limit = kwargs.pop("query_limit")
                super().__init__(*args, **kwargs)
                # Override the SQL_MAX_ROW default set implicitly in the previous line. Just needs to be higher
                # than 'displayLimit' so 'displayLimitReached' can be calculated correctly.
                self.limit = self.query_limit + 1

            def get_execution_result(self) -> Optional[SqlResults]:
                self._sql_result["displayLimit"] = self.query_limit  # Add max rows info to query result
                return self._sql_result

        class SqlExecuteRestApi(BaseSupersetView):
            """Make the superset.views.core.Superset.sql_json() endpoint available under /api/v1 and OAuth
            protected
            """

            route_base = "/api/v1"
            allow_browser_login = True
            query_limit = 10  # NOTE: 1_000_000 or some other high value would be a better value for production

            @expose("/execute_sql_json/", methods=["POST"])
            @protect()
            def execute_sql_json(self):
                """Almost verbatim copy of superset.views.core.Superset.sql_json. Added non-default query
                limits.
                """
                try:
                    log_params = {"user_agent": cast(Optional[str], request.headers.get("USER_AGENT"))}
                    execution_context = CustomContext(request.json, query_limit=self.query_limit)
                    command = Superset._create_sql_json_command(execution_context, log_params)
                    # Override the DISPLAY_MAX_ROW default set implicitly in the previous line
                    command._execution_context_convertor.set_max_row_in_display(self.query_limit)
                    try:
                        command_result: CommandResult = command.run()
                    except SupersetErrorsException as e:
                        payload = {"errors": [ex.to_dict() for ex in e.errors]}
                        return json_error_response(status=400, payload=payload)
                    status_code = 200
                    if command_result["status"] == SqlJsonExecutionStatus.QUERY_IS_RUNNING:
                        status_code = 202
                    return json_success(command_result["payload"], status_code)
                except SqlLabException as ex:
                    log.error(ex.message)
                    Superset._set_http_status_into_Sql_lab_exception(ex)
                    payload = {"errors": [ex.to_dict()]}
                    return json_error_response(status=ex.status, payload=payload)

        super().init_views()
        appbuilder.add_view_no_menu(SqlExecuteRestApi)


APP_INITIALIZER = CustomInitializer
RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")
