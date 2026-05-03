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
// @Param        body  body      domain.FullGroupProfileToUpdate  true  "Данные для обновления (обязательно укажите ID группы)"
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
// @Summary      Лента групп (для пользователей)
// @Description  Возвращает список подходящих групп, которые текущий пользователь еще не лайкал/дизлайкал.
// @Tags         groups
// @Produce      json
// @Param        limit  query     int       false  "Лимит записей (по умолчанию 10)"
// @Param        city   query     []string  false  "Фильтр по городам" collectionFormat(multi)
// @Success      200    {array}   domain.FullGroupProfile
// @Failure      401    {object}  ErrorMsg  "Не авторизован"
// @Security     ApiKeyAuth
// @Router       /api/v1/groups/feed [get]
func (h *GroupHandler) GetFeed(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(uint64)
	if !ok {
		JSONError(w, ErrorMsg{"Unauthorized"}, http.StatusUnauthorized)
		return
	}

	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit <= 0 {
		limit = 10
	}

	filters := &domain.GroupProfileFilters{
		Cities: r.URL.Query()["city"],
	}

	profiles, err := h.Service.GetFeedGroup(domain.ProfileID(userID), limit, filters)
	if err != nil {
		JSONError(w, ErrorMsg{err.Error()}, http.StatusBadRequest)
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
