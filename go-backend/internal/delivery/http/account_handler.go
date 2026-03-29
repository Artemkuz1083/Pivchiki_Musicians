package delivery

import (
	"encoding/json"
	"net/http"

	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/service"
)

type AuthHandler struct {
	Service service.AccountService
}

func NewAuthHandler(s service.AccountService) *AuthHandler {
	return &AuthHandler{Service: s}
}

// Registry godoc
// @Summary      Регистрация нового аккаунта
// @Description  Создает аккаунт и возвращает JWT токен. Поле is_profile_created всегда false.
// @Tags         auth
// @Accept       json
// @Produce      json
// @Param        body  body      delivery.AuthRequest  true  "Данные для регистрации"
// @Success      201   {object}  delivery.AuthResponse
// @Failure      400   {object}  delivery.ErrorMsg
// @Failure      409   {object}  delivery.ErrorMsg
// @Router       /api/v1/auth/registry [post]
func (h *AuthHandler) Registry(w http.ResponseWriter, r *http.Request) {
	//TODO мб поменять потом пароль более безопаснее сделать
	var req AuthRequest
	//TODO поменять ошибки на  фиксированные а реальные записывать в логи
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		msg := ErrorMsg{Message: err.Error()}
		JSONError(w, msg, http.StatusBadRequest)
		return
	}

	//TODO валидация имени и пароля
	token, err := h.Service.Registry(&domain.Account{
		Login:        req.Login,
		PasswordHash: req.Password,
	})
	if err != nil {
		msg := ErrorMsg{Message: err.Error()}
		JSONError(w, msg, http.StatusConflict)
		return
	}

	renderJSON(w, http.StatusCreated, AuthResponse{
		Token:            token,
		IsProfileCreated: false,
	})
}

// Login godoc
// @Summary      Вход в систему
// @Description  Проверяет учетные данные и возвращает токен + флаг наличия профиля.
// @Tags         auth
// @Accept       json
// @Produce      json
// @Param        body  body      delivery.AuthRequest  true  "Данные для входа"
// @Success      200   {object}  delivery.AuthResponse
// @Failure      401   {object}  delivery.ErrorMsg
// @Router       /api/v1/auth/login [post]
func (h *AuthHandler) Login(w http.ResponseWriter, r *http.Request) {
	var req AuthRequest
	json.NewDecoder(r.Body).Decode(&req)

	token, hasProfile, err := h.Service.Login(&domain.Account{
		Login:        req.Login,
		PasswordHash: req.Password,
	})
	if err != nil {
		msg := ErrorMsg{Message: err.Error()}
		JSONError(w, msg, http.StatusUnauthorized)
		return
	}

	renderJSON(w, http.StatusOK, AuthResponse{
        Token:            token,
        IsProfileCreated: hasProfile,
    })
}
