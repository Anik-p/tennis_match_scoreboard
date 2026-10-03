from exceptions.app_error import AppErorr
from match.session_fabric import SessionFabric
from response import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from validator.validator import InputValidator
    from jinja2 import Environment

class MatchController:
    def __init__( self,
                  validator: InputValidator,
                  template_env: Environment,
                  session_fabric: SessionFabric):

        self._validator = validator
        self._template_env = template_env
        self._session_fabric = session_fabric

    def _render(self, template: str, **kwargs) -> str:
        return self._template_env.get_template(template).render(**kwargs)

    def index(self, params: dict[str, str]) -> Response:
        return Response().html(self._render("index.html"))

    def new_match_form(self, params: dict) -> Response:
        return Response().html(self._render("new-match.html", error=None))
        
    def create_new_match(self, params: dict[str, str]) -> Response:
        name_p1 = params.get("player1_name", "").strip()
        name_p2 = params.get("player2_name", "").strip()
        try:
            self._validator.validate_name_plyers(name_p1, name_p2)
        except AppErorr as err:
            return Response().html(self._render("new-match.html", error=str(err)), status=err.status_code)
        with self._session_fabric._create_match_service() as match_service:
            view = match_service.new_match(name_p1, name_p2)
            return Response().redirect(f"/match-score?uuid={view.uuid}")

    def get_match_score(self, params: dict[str, str]) -> Response:
        with self._session_fabric._create_match_service() as match_service:
            view = match_service.get_match(params.get("uuid"))
            return Response().html(self._render("match-score.html", match=view))

    def award_point(self, params: dict[str, str]) -> Response:
        with self._session_fabric._create_match_service() as match_service:
            view = match_service.award_point(params.get("uuid"), params.get("winner_id"))
            return Response().redirect(f"/match-score?uuid={view.uuid}")

    def get_matches(self, params: dict[str, str]) -> Response:
        page = self._to_page(params.get("page"))
        player_name = params.get("filter_by_player_name", "").strip() or None
        with self._session_fabric._create_match_service() as match_service:
            dto = match_service.get_finished_matches(page, player_name)
            return Response().html(self._render("matches.html",
                                 matches=dto.matchs,
                                 page=page,
                                 pages=dto.page,
                                 total=dto.total,
                                 filter=player_name or ""))

    @staticmethod
    def _to_page(raw: str | None) -> int:
        try:
            return max(1, int(raw)) if raw else 1
        except ValueError:
            return 1