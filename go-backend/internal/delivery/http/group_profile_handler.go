package delivery

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/service"
)

type GroupHandler struct {
	Service service.GroupProfileService
}

func NewGroupHandler(s service.GroupProfileService) *GroupHandler {
	return &GroupHandler{Service: s}
}

// CreateProfile godoc
// @Summary      Создать профиль группы
// @Description  Создает новую музыкальную группу. Текущий пользователь автоматически становится владельцем (OWNER) с правами администратора.
// @Tags         groups
// @Accept       json
// @Produce      json
// @Param        body  body      CreateGroupRequest  true  "Данные новой группы"
// @Success      201   {object}  domain.FullGroupProfile   "Группа успешно создана"
// @Failure      400   {object}  ErrorMsg                  "Некорректный JSON или валидация"
// @Failure      401   {object}  ErrorMsg                  "Пользователь не авторизован"
// @Failure      500   {object}  ErrorMsg                  "Внутренняя ошибка сервера"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups [post]
func (h *GroupHandler) CreateProfile(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	var input CreateGroupRequest
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		JSONError(w, ErrorMsg{"Invalid JSON"}, http.StatusBadRequest)
		return
	}

	newGroup := &domain.FullGroupProfile{
		GroupName:       input.Name,
		City:            input.City,
		AboutGroup:      &input.Description,
		YearOfCreation:  input.Year,
		Genres:          input.Genres,
		LevelOfSerious:  domain.LevelOfSeriousness(input.Seriousness),
		FinancialStatus: domain.FinancialStatus(input.Financial),
		IsVisible:       true,
	}

	profile, err := h.Service.CreateGroupProfile(newGroup, domain.ProfileID(userID))
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusInternalServerError)
		return
	}

	renderJSON(w, http.StatusCreated, profile)
}

// UpdateProfile godoc
// @Summary      Обновить профиль группы
// @Description  Обновляет данные существующей группы. Операцию может выполнить только участник группы с правами администратора.
// @Tags         groups
// @Accept       json
// @Produce      json
// @Param        body body domain.FullGroupProfileToUpdate true "Данные для обновления"
// @Success      200   {object}  domain.FullGroupProfile          "Профиль успешно обновлен"
// @Failure      400   {object}  ErrorMsg                         "Ошибка в данных или отсутствует ID"
// @Failure      403   {object}  ErrorMsg                         "Недостаточно прав для редактирования этой группы"
// @Failure      404   {object}  ErrorMsg                         "Группа не найдена"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups [patch]
func (h *GroupHandler) UpdateProfile(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	var input domain.FullGroupProfileToUpdate
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		JSONError(w, ErrorMsg{"Invalid JSON"}, http.StatusBadRequest)
		return
	}

	if input.ID == 0 {
		JSONError(w, ErrorMsg{"group_id is required"}, http.StatusBadRequest)
		return
	}

	profile, err := h.Service.UpdateGroupProfile(&input, domain.ProfileID(userID))
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusForbidden)
		return
	}

	renderJSON(w, http.StatusOK, profile)
}

// GetProfile godoc
// @Summary      Получить информацию о группе
// @Description  Возвращает подробный профиль группы по её ID, включая список участников и жанры.
// @Tags         groups
// @Produce      json
// @Param        id   query     int    true  "ID группы"
// @Success      200  {object}  domain.FullGroupProfile  "Данные группы"
// @Failure      404  {object}  ErrorMsg                 "Группа не найдена"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups [get]
func (h *GroupHandler) GetProfile(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Query().Get("id")
	groupID, _ := strconv.ParseInt(idStr, 10, 64)

	profile, err := h.Service.GetGroupProfile(domain.GroupID(groupID))
	if err != nil {
		JSONError(w, ErrorMsg{"Group not found"}, http.StatusNotFound)
		return
	}

	renderJSON(w, http.StatusOK, profile)
}

// GetFeed godoc
// @Summary      Лента групп с фильтрацией (для пользователей)
// @Description  Возвращает список подходящих музыкальных групп, которые текущий пользователь еще не лайкал/дизлайкал. Фильтрует по городам, жанрам и уровню серьезности.
// @Tags         groups
// @Produce      json
// @Param        limit        query     int       false  "Лимит записей (1-25, по умолчанию 10)"
// @Param        city         query     []string  false  "Фильтр по городам" collectionFormat(multi)
// @Param        genre        query     []string  false  "Фильтр по жанрам" collectionFormat(multi)
// @Param        seriousness  query     string    false  "Уровень серьезности"
// @Success      200          {array}   domain.FullGroupProfile "Список подходящих групп"
// @Failure      400          {object}  ErrorMsg  "Некорректный лимит или параметры фильтрации"
// @Failure      401          {object}  ErrorMsg  "Пользователь не авторизован"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups/feed [get]
func (h *GroupHandler) GetFeed(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{Message: "Вы не авторизованы в системе"}, http.StatusUnauthorized)
		return
	}

	strLimit := r.URL.Query().Get("limit")
	limit, err := strconv.Atoi(strLimit)
	if err != nil || limit <= 0 || limit > 25 {
		if strLimit == "" {
			limit = 10
		} else {
			JSONError(w, ErrorMsg{Message: "Некорректный лимит (допустимо от 1 до 25)"}, http.StatusBadRequest)
			return
		}
	}

	q := r.URL.Query()

	filters := &domain.GroupProfileFilters{
		Cities: q["city"],
		Genres: q["genre"],
	}

	if seriousnessStr := q.Get("seriousness"); seriousnessStr != "" {
		seriousness := domain.LevelOfSeriousness(seriousnessStr)
		filters.LevelOfSerious = &seriousness
	}

	profiles, err := h.Service.GetFeedGroup(domain.ProfileID(userID), limit, filters)
	if err != nil {
		JSONError(w, ErrorMsg{Message: err.Error()}, http.StatusBadRequest)
		return
	}

	renderJSON(w, http.StatusOK, profiles)
}

// GetPublicFeed godoc
// @Summary      Публичная лента групп
// @Description  Возвращает случайные видимые группы для неавторизованных пользователей.
// @Tags         public
// @Produce      json
// @Param        limit  query     int  false  "Лимит записей"
// @Success      200    {array}   domain.FullGroupProfile
// @Router       /api/v1/public/groups/feed [get]
func (h *GroupHandler) GetPublicFeed(w http.ResponseWriter, r *http.Request) {
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit <= 0 {
		limit = 10
	}

	profiles, err := h.Service.GetPublicFeedGroup(limit)
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusBadRequest)
		return
	}

	renderJSON(w, http.StatusOK, profiles)
}

// DeleteProfile godoc
// @Summary      Удалить профиль группы
// @Description  Полностью удаляет профиль группы и всех её участников. Операцию может выполнить только владелец (OWNER).
// @Tags         groups
// @Produce      json
// @Param        id   query     int    true  "ID группы для удаления"
// @Success      204   "Группа успешно удалена"
// @Failure      400   {object}  ErrorMsg  "Некорректный ID"
// @Failure      403   {object}  ErrorMsg  "Только владелец может удалить группу"
// @Failure      404   {object}  ErrorMsg  "Группа не найдена"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups [delete]
func (h *GroupHandler) DeleteProfile(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	idStr := r.URL.Query().Get("id")
	groupID, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		JSONError(w, ErrorMsg{"Invalid group ID"}, http.StatusBadRequest)
		return
	}

	err = h.Service.DeleteGroupProfile(domain.GroupID(groupID), domain.ProfileID(userID))
	if err != nil {
		// Если сервис вернул ошибку прав
		if err.Error() == "permission denied: only the group owner can delete the profile" {
			JSONError(w, ErrorMsg{err.Error()}, http.StatusForbidden)
			return
		}
		JSONError(w, ErrorMsg{err.Error()}, http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// UploadGroupMedia godoc
// @Summary      Загрузить медиа для группы
// @Description  Загружает файл (фото) и привязывает его к профилю группы. Доступно только владельцу группы (OWNER).
// @Tags         groups
// @Accept       multipart/form-data
// @Produce      json
// @Param        group_id  formData  int     true  "ID группы"
// @Param        file      formData  file    true  "Файл изображения (jpg/png)"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups/media [post]
func (h *GroupHandler) UploadGroupMedia(w http.ResponseWriter, r *http.Request) {
	// 1. Получаем ID юзера, который делает запрос
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	// 2. Парсим форму (лимит 10 МБ)
	if err := r.ParseMultipartForm(10 << 20); err != nil {
		JSONError(w, ErrorMsg{"Form parse error"}, http.StatusBadRequest)
		return
	}

	// 3. Достаем ID группы из параметров формы
	groupIDStr := r.FormValue("group_id")
	groupID, err := strconv.ParseInt(groupIDStr, 10, 64)
	if err != nil {
		JSONError(w, ErrorMsg{"Invalid group_id"}, http.StatusBadRequest)
		return
	}

	// 4. Получаем файл
	file, header, err := r.FormFile("file")
	if err != nil {
		JSONError(w, ErrorMsg{"File not found"}, http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 5. Подготовка папки и имени файла
	ext := filepath.Ext(header.Filename)
	folder := "./uploads/groups"
	if err := os.MkdirAll(folder, os.ModePerm); err != nil {
		JSONError(w, ErrorMsg{"Failed to create directory"}, http.StatusInternalServerError)
		return
	}

	// Формируем имя: group_{id}_{timestamp}.ext
	fileName := fmt.Sprintf("group_%d_%d%s", groupID, time.Now().Unix(), ext)
	filePath := filepath.Join(folder, fileName)

	// 6. Сохранение на диск
	dst, err := os.Create(filePath)
	if err != nil {
		JSONError(w, ErrorMsg{"Save error"}, http.StatusInternalServerError)
		return
	}
	defer dst.Close()

	if _, err := io.Copy(dst, file); err != nil {
		JSONError(w, ErrorMsg{"Write error"}, http.StatusInternalServerError)
		return
	}

	// 7. Обновление профиля группы в БД
	// Мы передаем ID пользователя как ProfileID(userID), чтобы сервис проверил права OWNER
	update := &domain.FullGroupProfileToUpdate{
		ID:        domain.GroupID(groupID),
		PhotoURL: &filePath,
	}

	_, err = h.Service.UpdateGroupProfile(update, domain.ProfileID(userID))
	if err != nil {
		// Если прав нет или группа не найдена — удаляем мусор с диска
		os.Remove(filePath)

		// Если сервис вернул ошибку прав, отдаем 403
		JSONError(w, ErrorMsg{err.Error()}, http.StatusForbidden)
		return
	}

	// Возвращаем путь к файлу
	renderJSON(w, http.StatusOK, map[string]string{"url": "/" + filePath})
}

// UserSwipeGroup godoc
// @Summary      Свайпнуть группу пользователем (лайк/дизлайк)
// @Description  Текущий авторизованный пользователь совершает действие (like/dislike) над выбранной группой. Возвращает информацию, случился ли мэтч.
// @Tags         groups
// @Accept       json
// @Produce      json
// @Param        id    path      int           true  "ID группы, которую свайпают"
// @Param        body  body      SwipeRequest  true  "Действие: like или dislike"
// @Success      200   {object}  domain.GroupSwipeResult "Результат свайпа (IsMatch: true/false)"
// @Failure      400   {object}  ErrorMsg              "Некорректный JSON или ID"
// @Failure      401   {object}  ErrorMsg              "Пользователь не авторизован"
// @Failure      500   {object}  ErrorMsg              "Внутренняя ошибка сервера"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups/feed/{id}/swipe [post]
func (h *GroupHandler) UserSwipeGroup(w http.ResponseWriter, r *http.Request) {
	targetGroupIDStr := r.PathValue("id")
	targetGroupID, _ := strconv.ParseUint(targetGroupIDStr, 10, 64)

	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	var input SwipeRequest
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		JSONError(w, ErrorMsg{"Некорректный JSON"}, http.StatusBadRequest)
		return
	}

	if input.Action != "like" && input.Action != "dislike" {
		JSONError(w, ErrorMsg{"Action должен быть like или dislike"}, http.StatusBadRequest)
		return
	}

	// Вызываем сервис. Метод Swipe возвращает *domain.GroupSwipeResult
	result, err := h.Service.Swipe(domain.ProfileID(userID), domain.GroupID(targetGroupID), input.Action)
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusInternalServerError)
		return
	}

	renderJSON(w, http.StatusOK, result)
}

// GroupSwipeUser godoc
// @Summary      Свайпнуть пользователя от имени группы
// @Description  Администратор группы совершает действие (like/dislike) над музыкантом от лица конкретной группы.
// @Tags         groups
// @Accept       json
// @Produce      json
// @Param        body  body      GroupSwipeUserRequest  true  "Данные свайпа группы"
// @Success      200   {object}  map[string]bool        "Результат: был ли это лайк и выполнен ли запрос успешнно"
// @Failure      400   {object}  ErrorMsg               "Некорректный ввод"
// @Failure      401   {object}  ErrorMsg               "Пользователь не авторизован"
// @Failure      403   {object}  ErrorMsg               "Вы не являетесь владельцем/админом этой группы"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups/swipe-user [post]
func (h *GroupHandler) GroupSwipeUser(w http.ResponseWriter, r *http.Request) {
	_, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	var input GroupSwipeUserRequest
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		JSONError(w, ErrorMsg{"Некорректный JSON"}, http.StatusBadRequest)
		return
	}

	if input.Action != "like" && input.Action != "dislike" {
		JSONError(w, ErrorMsg{"Action должен быть like или dislike"}, http.StatusBadRequest)
		return
	}
	
	// Предполагаем, что репозиторий/сервис отдаст (isLike bool, err error)
	result, err := h.Service.Swipe(domain.ProfileID(input.TargetUserID), domain.GroupID(input.GroupID), input.Action)
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusInternalServerError)
		return
	}

	renderJSON(w, http.StatusOK, result)
}

// GetGroupMatches godoc
// @Summary      Список взаимных лайков пользователя с группами
// @Tags         groups
// @Produce      json
// @Success      200  {array}   domain.FullGroupProfile  "Список групп, с которыми есть мэтч"
// @Failure      401  {object}  ErrorMsg                 "Пользователь не авторизован"
// @Failure      500  {object}  ErrorMsg                 "Внутренняя ошибка сервера"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups/matches [get]
func (h *GroupHandler) GetGroupMatches(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	matches, err := h.Service.GetMatches(domain.ProfileID(userID))
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusInternalServerError)
		return
	}

	renderJSON(w, http.StatusOK, matches)
}

// GroupSwipeUserRequest структура для свайпа музыканта группой
type GroupSwipeUserRequest struct {
	GroupID      uint64 `json:"group_id" example:"6"`
	TargetUserID uint64 `json:"target_user_id" example:"1"`
	Action       string `json:"action" example:"like"`
}