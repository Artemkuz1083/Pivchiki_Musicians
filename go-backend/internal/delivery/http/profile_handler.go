package delivery

import (
	"encoding/json"
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

// GetUserProfile godoc
// @Summary      Получить профиль текущего пользователя
// @Description  Возвращает полную информацию о профиле на основе ID из JWT токена
// @Tags         userProfile
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

// UpdateUserProfile godoc
// @Summary      Обновить один из параметров пользователя
// @Description  Возвращает полную информацию о профиле на основе ID из JWT токена
// @Tags         userProfile
// @Accept       json
// @Produce      json
// @Param        body body      delivery.UpdateProfile  true  "Данные для обновления"
// @Success      200  {object}  domain.FullProfile  "Успешное получение профиля"
// @Failure      401  {object}  ErrorMsg            "Вы не авторизованы"
// @Failure      400  {object}  ErrorMsg            "Профиль не найден"
// @Security     ApiKeyAuth
// @Router       /api/v1/profile [patch]
func (h *ProfileHandler) UpdateProfile(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userID, ok := ctx.Value("user_id").(uint64)
	if !ok {
		msg := ErrorMsg{Message: "Вы не авторизованы в системе"}
		JSONError(w, msg, http.StatusUnauthorized)
		return
	}

	log.Printf("айди долбаеба который хочет обновить свой профиль %d", userID)

	var updateProfile UpdateProfile
	if err := json.NewDecoder(r.Body).Decode(&updateProfile); err != nil {
		msg := ErrorMsg{Message: err.Error()}
		JSONError(w, msg, http.StatusBadRequest)
		return
	}

	if updateProfile.PerformancExperience != nil && !updateProfile.PerformancExperience.IsValid() {
		msg := ErrorMsg{Message: "невалидное значение опыта исполнения"}
		JSONError(w, msg, http.StatusBadRequest)
		return
	}

	var domainInstruments []*domain.UpdateInstrument
	if updateProfile.Instruments != nil {
		domainInstruments = make([]*domain.UpdateInstrument, 0, len(*updateProfile.Instruments))
		for _, inst := range *updateProfile.Instruments {
			if inst != nil {
				domainInstruments = append(domainInstruments, &domain.UpdateInstrument{
					Instrument:                 inst.Instrument,
					InstrumentProficiencyLevel: inst.InstrumentProficiencyLevel,
				})
			}
		}
	}

	newProfile := &domain.FullProfileToUpdate{
		ID:                   domain.ProfileID(userID),
		UserName:             updateProfile.UserName,
		City:                 updateProfile.City,
		Contact:              updateProfile.Contact,
		PerformancExperience: updateProfile.PerformancExperience,
		Link:                 updateProfile.Link,
		AboutUser:            updateProfile.AboutUser,
		Age:                  updateProfile.Age,
		TheoryLevel:          updateProfile.TheoryLevel,
		Genres:               updateProfile.Genres,
		Instruments:          &domainInstruments,
		IsVisible:            updateProfile.IsVisible,
	}

	profile, err := h.Service.UpdateUserProfile(newProfile)
	if err != nil {
		msg := ErrorMsg{Message: err.Error()}
		JSONError(w, msg, http.StatusBadRequest)
		return
	}

	renderJSON(w, http.StatusOK, profile)
}

// CreateProfile godoc
// @Summary      Создать профиль
// @Description  Создает запись в таблице users для текущего аккаунта
// @Tags         userProfile
// @Accept       json
// @Produce      json
// @Param        body body CreateProfile true "Данные для создания профиля"
// @Success      201  {object}  domain.FullProfile
// @Failure      401  {object}  ErrorMsg            "Вы не авторизованы"
// @Failure      400  {object}  ErrorMsg            "Профиль не найден"
// @Security     ApiKeyAuth
// @Router       /api/v1/profile [post]
func (h *ProfileHandler) CreateProfile(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userID, ok := ctx.Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	var input CreateProfile
    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        JSONError(w, ErrorMsg{Message: "Ошибка декодирования: " + err.Error()}, http.StatusBadRequest)
        return
    }

	domainInstruments := make([]*domain.Instrument, 0, len(input.Instruments))
    for _, inst := range input.Instruments {
        domainInstruments = append(domainInstruments, &domain.Instrument{
            Instrument:                 inst.Instrument,
            InstrumentProficiencyLevel: inst.InstrumentProficiencyLevel,
        })
    }

	newProfile := &domain.FullProfile{
        ID:                   domain.ProfileID(userID),
        UserName:             input.UserName,
        City:                 input.City,
        Contact:              input.Contact,
        IsVisible:            input.IsVisible,
        Genres:               input.Genres,
        Instruments:          domainInstruments,
        PerformancExperience: nil,
        Link:                 nil,
        AboutUser:            nil,
        Age:                  nil,
        TheoryLevel:          nil,
    }

	if newProfile.Genres == nil {
        newProfile.Genres = []string{}
    }

	profile, err := h.Service.CreateUserProfile(newProfile)
    if err != nil {
        JSONError(w, ErrorMsg{Message: err.Error()}, http.StatusBadRequest)
        return
    }

	renderJSON(w, http.StatusCreated, profile)
}
