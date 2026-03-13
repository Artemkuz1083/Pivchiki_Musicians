package delivery

import (
	"log"
	"net/http"

	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/service"
)

type ProfileHandler struct {
	Service service.ProfileService
}

func NewProfileHandler(s service.ProfileService) *ProfileHandler {
	return &ProfileHandler{Service: s}
}

// GetProfile godoc
// @Summary      Получить профиль текущего пользователя
// @Description  Возвращает полную информацию о профиле на основе ID из JWT токена
// @Tags         profile
// @Accept       json
// @Produce      json
// @Success      200  {object}  domain.FullProfile  "Успешное получение профиля"
// @Failure      401  {object}  ErrorMsg            "Вы не авторизованы"
// @Failure      400  {object}  ErrorMsg            "Профиль не найден"
// @Security     ApiKeyAuth
// @Router       /api/v1/profile [get]
func (h *ProfileHandler) GetProfile(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userID, ok := ctx.Value("user_id").(uint64)
	if !ok {
		msg := ErrorMsg{Message: "Вы не авторизованы в системе"}
		JSONError(w, msg, http.StatusUnauthorized)
		return
	}

	log.Printf("айди долбаеба который зашел в свой профиль %d", userID)

	profile, err := h.Service.GetUserProfile(domain.ProfileID(userID))
	if err != nil {
		msg := ErrorMsg{Message: err.Error()}
		JSONError(w, msg, http.StatusBadRequest)
		return
	}

	renderJSON(w, http.StatusOK, profile)
}
