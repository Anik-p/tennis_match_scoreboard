from exceptions.app_error import AppError
from response import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from match.service import MatchService
    from validator.validator import InputValidator
    from jinja2 import Environment

class MatchController:
    def __init__( self,
                  validator: InputValidator,
                  template_env: Environment):
        self._validator = validator
        self._template_env = template_env

    def _render(self, template: str, **kwargs) -> str:
        return self._template_env.get_template(template).render(**kwargs)

    def index(self, params: dict[str, str], match_service: MatchService) -> Response:
        return Response().html(self._render("index.html"))

    def new_match_form(self, params: dict, match_service: MatchService) -> Response:
        return Response().html(self._render("new-match.html", error=None))
        
    def create_new_match(self, params: dict[str, str], match_service: MatchService) -> Response:
        name_p1 = params.get("player1_name", "").strip()
        name_p2 = params.get("player2_name", "").strip()
        try:
            self._validator.validate_name_plyers(name_p1, name_p2)
        except AppError as err:
            return Response().html(self._render("new-match.html", error=str(err)), status=err.status_code)
        view = match_service.new_match(name_p1, name_p2)
        return Response().redirect(f"/match-score?uuid={view.uuid}")

    def get_match_score(self, params: dict[str, str], match_service: MatchService) -> Response:
        view = match_service.get_match(params.get("uuid"))
        return Response().html(self._render("match-score.html", match=view))

    def award_point(self, params: dict[str, str], match_service: MatchService) -> Response:
        view = match_service.award_point(params.get("uuid"), params.get("winner_id"))
        return Response().redirect(f"/match-score?uuid={view.uuid}")

    def get_matches(self, params: dict[str, str], match_service: MatchService) -> Response:
        page = self._to_page(params.get("page"))
        player_name = params.get("filter_by_player_name", "").strip() or None
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