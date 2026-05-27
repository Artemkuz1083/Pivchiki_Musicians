package delivery

import (
	"encoding/json"
	"net/http"

	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/metrics"
	"github.com/katrinani/pivchiki-bot/backend/internal/service"
	"github.com/prometheus/client_golang/prometheus"
)

type AuthHandler struct {
	Service service.AccountService
}

func NewAuthHandler(s service.AccountService) *AuthHandler {
	return &AuthHandler{Service: s}
}

// Registry godoc
// @Summary      Регистрация нового аккаунта
// @Description  Создает аккаунт, устанавливает HttpOnly сессионную куку refresh_token и возвращает Access JWT токен. Поле is_profile_created всегда false.
// @Tags         auth
// @Accept       json
// @Produce      json
// @Param        body  body      delivery.AuthRequest  true  "Данные для регистрации"
// @Success      201   {object}  delivery.AuthResponse
// @Header       201   {string}  Set-Cookie            "refresh_token=...; Path=/api/v1/auth; HttpOnly; Max-Age=2592000"
// @Failure      400   {object}  delivery.ErrorMsg     "Некорректный JSON"
// @Failure      409   {object}  delivery.ErrorMsg     "Логин уже занят или ошибка базы"
// @Router       /api/v1/auth/registry [post]
func (h *AuthHandler) Registry(w http.ResponseWriter, r *http.Request) {
	source := "web"
	metrics.RegistrationStarted.WithLabelValues(source).Inc()

	timer := prometheus.NewTimer(metrics.RegistrationDuration.WithLabelValues(source))
	defer timer.ObserveDuration()

	var req AuthRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		metrics.RegistrationErrors.WithLabelValues(source, "json_parse").Inc()
		JSONError(w, ErrorMsg{Message: err.Error()}, http.StatusBadRequest)
		return
	}

	accessToken, refreshToken, err := h.Service.Registry(&domain.Account{
		Login:        req.Login,
		PasswordHash: req.Password,
	})
	if err != nil {
		metrics.RegistrationErrors.WithLabelValues(source, "db_error").Inc()
		JSONError(w, ErrorMsg{Message: err.Error()}, http.StatusConflict)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refresh_token",
		Value:    refreshToken,
		Path:     "/",
		HttpOnly: true,
		Secure:   false,
		SameSite: http.SameSiteLaxMode,
		MaxAge:   30 * 24 * 60 * 60,
	})

	renderJSON(w, http.StatusCreated, AuthResponse{
		Token:            accessToken,
		IsProfileCreated: false,
	})
}

// Login godoc
// @Summary      Вход в систему
// @Description  Проверяет учетные данные, устанавливает HttpOnly сессионную куку refresh_token и возвращает Access JWT токен + флаг наличия профиля.
// @Tags         auth
// @Accept       json
// @Produce      json
// @Param        body  body      delivery.AuthRequest  true  "Данные для входа"
// @Success      200   {object}  delivery.AuthResponse
// @Header       200   {string}  Set-Cookie            "refresh_token=...; Path=/api/v1/auth; HttpOnly; Max-Age=2592000"
// @Failure      400   {object}  delivery.ErrorMsg     "Некорректный JSON"
// @Failure      401   {object}  delivery.ErrorMsg     "Неверный логин или пароль"
// @Router       /api/v1/auth/login [post]
func (h *AuthHandler) Login(w http.ResponseWriter, r *http.Request) {
	var req AuthRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		JSONError(w, ErrorMsg{Message: err.Error()}, http.StatusBadRequest)
		return
	}

	accessToken, refreshToken, hasProfile, err := h.Service.Login(&domain.Account{
		Login:        req.Login,
		PasswordHash: req.Password,
	})
	if err != nil {
		JSONError(w, ErrorMsg{Message: err.Error()}, http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refresh_token",
		Value:    refreshToken,
		Path:     "/",
		HttpOnly: true,
		Secure:   false,
		SameSite: http.SameSiteLaxMode,
		MaxAge:   30 * 24 * 60 * 60,
	})

	renderJSON(w, http.StatusOK, AuthResponse{
		Token:            accessToken,
		IsProfileCreated: hasProfile,
	})
}

// Refresh godoc
// @Summary      Обновить Access-токен
// @Description  Принимает Refresh-токен из HttpOnly-куки, проверяет его и выдает новую пару токенов (Access и Refresh).
// @Tags         auth
// @Produce      json
// @Success      200  {object}  map[string]string "Возвращает новый access_token"
// @Failure      401  {object}  ErrorMsg          "Токен невалиден или протух"
// @Router       /api/v1/auth/refresh [post]
func (h *AuthHandler) Refresh(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("refresh_token")
	if err != nil {
		JSONError(w, ErrorMsg{"Refresh token not found"}, http.StatusUnauthorized)
		return
	}

	refreshToken := cookie.Value

	newAccessToken, newRefreshToken, err := h.Service.RefreshTokens(refreshToken)
	if err != nil {
		JSONError(w, ErrorMsg{"Invalid or expired refresh token"}, http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refresh_token",
		Value:    newRefreshToken,
		Path:     "/",   // Доступно только для auth-ручек ради безопасности
		HttpOnly: true,  // Защита от кражи через JS (XSS)
		Secure:   false, // Поставь true на продакшене (требует HTTPS)
		SameSite: http.SameSiteLaxMode,
		MaxAge:   30 * 24 * 60 * 60, // 30 дней в секундах
	})

	renderJSON(w, http.StatusOK, map[string]string{
		"access_token": newAccessToken,
	})
}
