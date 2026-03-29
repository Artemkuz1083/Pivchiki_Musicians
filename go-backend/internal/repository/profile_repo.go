package repository

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/katrinani/pivchiki-bot/backend/internal/db"
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
)

type ProfileRepository interface {
	GetProfile(profile domain.ProfileID) (*domain.FullProfile, error)
	UpdateProfile(profile *domain.FullProfileToUpdate) error
	CreateProfile(profile *domain.FullProfile) error
	GetFeedProfiles(profile domain.ProfileID, limit int) ([]*domain.FullProfile, error)
}

var _ ProfileRepository = (*ProfileRepositoryImpl)(nil)

type ProfileRepositoryImpl struct {
	queries *db.Queries
	db      *pgxpool.Pool
}

func NewProfileRepository(queries *db.Queries, pool *pgxpool.Pool) *ProfileRepositoryImpl {
	return &ProfileRepositoryImpl{
		queries: queries,
		db:      pool,
	}
}

func (r *ProfileRepositoryImpl) GetProfile(id domain.ProfileID) (*domain.FullProfile, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	log.Printf("[REPO:GetProfile] Попытка получить профиль для ID: %d", id)
	user, err := r.queries.GetUser(ctx, int64(id))
	if err != nil {
		log.Printf("[REPO:GetProfile:ERROR] Ошибка GetUser для ID %d: %v", id, err)
		return nil, domain.ErrNoteNotFound
	}

	genres, err := r.queries.GetUserGenres(ctx, int64(id))
	if err != nil {
		log.Printf("[REPO:GetProfile:INFO] Жанры не найдены для ID %d: %v", id, err)
		genres = []string{}
	}

	dbInstruments, err := r.queries.GetUserInstruments(ctx, int64(id))
	if err != nil {
		log.Printf("[REPO:GetProfile:INFO] Инструменты не найдены для ID %d: %v", id, err)
		dbInstruments = []db.GetUserInstrumentsRow{}
	}

	instruments := make([]*domain.Instrument, 0)
	for _, inst := range dbInstruments {
		instruments = append(instruments, &domain.Instrument{
			Instrument:                 inst.Name,
			InstrumentProficiencyLevel: uint(inst.ProficiencyLevel),
		})
	}

	profile := &domain.FullProfile{
		ID:                   id,
		UserName:             user.Name.String,
		City:                 user.City.String,
		Contact:              user.Contacts.String,
		PerformancExperience: ToPerformanceEx(user.HasPerformanceExperience),
		Link:                 textToPtr(user.ExternalLink),
		AboutUser:            textToPtr(user.AboutMe),
		Age:                  int4ToUintPtr(user.Age),
		TheoryLevel:          int4ToUintPtr(user.TheoreticalKnowledgeLevel),
		Genres:               genres,
		Instruments:          instruments,
		IsVisible:            user.IsVisible,
	}

	log.Printf("[REPO:GetProfile:SUCCESS] Профиль найден и собран для ID: %d", id)
	return profile, nil
}

func (r *ProfileRepositoryImpl) UpdateProfile(profile *domain.FullProfileToUpdate) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	log.Printf("[REPO:UpdateProfile] Начало транзакции обновления для ID: %d", profile.ID)
	tx, err := r.db.BeginTx(ctx, pgx.TxOptions{
		IsoLevel: pgx.ReadCommitted,
	})
	if err != nil {
		log.Printf("[REPO:UpdateProfile:ERROR] Не удалось начать транзакцию: %v", err)
		return err
	}
	defer tx.Rollback(ctx)

	qtx := r.queries.WithTx(tx)

	err = qtx.UpdateUserProfile(ctx, db.UpdateUserProfileParams{
		ID:                        int64(profile.ID),
		Name:                      ToText(profile.UserName),
		City:                      ToText(profile.City),
		Contacts:                  ToText(profile.Contact),
		HasPerformanceExperience:  ToText((*string)(profile.PerformancExperience)),
		AboutMe:                   ToText(profile.AboutUser),
		ExternalLink:              ToText(profile.Link),
		Age:                       ToInt4(profile.Age),
		TheoreticalKnowledgeLevel: ToInt4(profile.TheoryLevel),
		IsVisible:                 ToBool(profile.IsVisible),
	})
	if err != nil {
		log.Printf("[REPO:UpdateProfile:ERROR] Ошибка UpdateUserProfile: %v", err)
		return err
	}

	if profile.Genres != nil {
		log.Printf("[REPO:UpdateProfile] Обновление жанров для ID: %d", profile.ID)
		err = qtx.DeleteUserGenres(ctx, int64(profile.ID))
		if err != nil {
			return err
		}

		for _, genreName := range *profile.Genres {
			err = qtx.AddUserGenre(ctx, db.AddUserGenreParams{
				UserID: int64(profile.ID),
				Name:   genreName,
			})
			if err != nil {
				log.Printf("[REPO:UpdateProfile:ERROR] Ошибка добавления жанра %s: %v", genreName, err)
				return err
			}
		}
	}

	if profile.Instruments != nil {
		log.Printf("[REPO:UpdateProfile] Обновление инструментов для ID: %d", profile.ID)
		err = qtx.DeleteUserInstruments(ctx, int64(profile.ID))
		if err != nil {
			return err
		}

		for _, inst := range *profile.Instruments {
			if inst == nil {
				continue
			}

			err = qtx.AddUserInstrument(ctx, db.AddUserInstrumentParams{
				UserID:           int64(profile.ID),
				Name:             stringFromPtr(inst.Instrument),
				ProficiencyLevel: int32(uintFromPtr(inst.InstrumentProficiencyLevel)),
			})
			if err != nil {
				log.Printf("[REPO:UpdateProfile:ERROR] Ошибка добавления инструмента: %v", err)
				return err
			}
		}
	}

	if err := tx.Commit(ctx); err != nil {
		log.Printf("[REPO:UpdateProfile:ERROR] Ошибка коммита: %v", err)
		return err
	}

	log.Printf("[REPO:UpdateProfile:SUCCESS] Профиль ID %d обновлен", profile.ID)
	return nil
}

func (r *ProfileRepositoryImpl) CreateProfile(profile *domain.FullProfile) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	log.Printf("[REPO:CreateProfile] ПОПЫТКА СОЗДАНИЯ ПРОФИЛЯ. ID: %d, Name: %s", profile.ID, profile.UserName)

	tx, err := r.db.BeginTx(ctx, pgx.TxOptions{IsoLevel: pgx.ReadCommitted})
	if err != nil {
		log.Printf("[REPO:CreateProfile:ERROR] Не удалось начать транзакцию: %v", err)
		return err
	}
	defer tx.Rollback(ctx)

	qtx := r.queries.WithTx(tx)

	err = qtx.CreateUserProfile(ctx, db.CreateUserProfileParams{
		ID:                        int64(profile.ID),
		Name:                      ToText(&profile.UserName),
		City:                      ToText(&profile.City),
		Contacts:                  ToText(&profile.Contact),
		IsVisible:                 profile.IsVisible,
		Age:                       ToInt4(profile.Age),
		TheoreticalKnowledgeLevel: ToInt4(profile.TheoryLevel),
		AboutMe:                   ToText(profile.AboutUser),
		ExternalLink:              ToText(profile.Link),
		HasPerformanceExperience:  ToText((*string)(profile.PerformancExperience)),
	})
	if err != nil {
		log.Printf("[REPO:CreateProfile:ERROR] Ошибка в qtx.CreateUserProfile для ID %d: %v", profile.ID, err)
		return err
	}

	log.Printf("[REPO:CreateProfile] Базовая инфа вставлена, вставляем %d жанров", len(profile.Genres))
	for _, genre := range profile.Genres {
		if err := qtx.AddUserGenre(ctx, db.AddUserGenreParams{
			UserID: int64(profile.ID),
			Name:   genre,
		}); err != nil {
			log.Printf("[REPO:CreateProfile:ERROR] Ошибка вставки жанра %s: %v", genre, err)
			return err
		}
	}

	log.Printf("[REPO:CreateProfile] Вставляем %d инструментов", len(profile.Instruments))
	for _, inst := range profile.Instruments {
		if inst == nil {
			continue
		}
		if err := qtx.AddUserInstrument(ctx, db.AddUserInstrumentParams{
			UserID:           int64(profile.ID),
			Name:             inst.Instrument,
			ProficiencyLevel: int32(inst.InstrumentProficiencyLevel),
		}); err != nil {
			log.Printf("[REPO:CreateProfile:ERROR] Ошибка вставки инструмента %s: %v", inst.Instrument, err)
			return err
		}
	}

	if err := tx.Commit(ctx); err != nil {
		log.Printf("[REPO:CreateProfile:ERROR] Ошибка коммита транзакции: %v", err)
		return err
	}

	log.Printf("[REPO:CreateProfile:SUCCESS] ПРОФИЛЬ УСПЕШНО ЗАККОМИТИЛСЯ В БД для ID: %d", profile.ID)
	return nil
}

func (r *ProfileRepositoryImpl) GetFeedProfiles(id domain.ProfileID, limit int) ([]*domain.FullProfile, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	log.Printf("[REPO:GetFeed] Получение ленты для ID: %d, limit: %d", id, limit)
	dbRows, err := r.queries.GetFeedProfiles(ctx, db.GetFeedProfilesParams{
		ID:    int64(id),
		Limit: int32(limit),
	})
	if err != nil {
		log.Printf("[REPO:GetFeed:ERROR] Ошибка запроса ленты: %v", err)
		return nil, err
	}

	profiles := make([]*domain.FullProfile, 0, len(dbRows))

	for _, row := range dbRows {
		var genres []string
		if genresBytes, ok := row.Genres.([]byte); ok {
			if err := json.Unmarshal(genresBytes, &genres); err != nil {
				log.Printf("ошибка парсинга жанров для id %d: %v", row.ID, err)
				genres = []string{}
			}
		} else {
			genres = []string{}
		}

		type instDTO struct {
			Name             string `json:"name"`
			ProficiencyLevel uint   `json:"proficiency_level"`
		}
		var rawInsts []instDTO
		if instsBytes, ok := row.Instruments.([]byte); ok {
			if err := json.Unmarshal(instsBytes, &rawInsts); err != nil {
				log.Printf("ошибка парсинга инструментов для id %d: %v", row.ID, err)
				rawInsts = []instDTO{}
			}
		} else {
			rawInsts = []instDTO{}
		}

		domainInsts := make([]*domain.Instrument, 0, len(rawInsts))
		for _, ri := range rawInsts {
			domainInsts = append(domainInsts, &domain.Instrument{
				Instrument:                 ri.Name,
				InstrumentProficiencyLevel: ri.ProficiencyLevel,
			})
		}

		profiles = append(profiles, &domain.FullProfile{
			ID:                   domain.ProfileID(row.ID),
			UserName:             row.Name.String,
			City:                 row.City.String,
			Contact:              row.Contacts.String,
			PerformancExperience: ToPerformanceEx(row.HasPerformanceExperience),
			Link:                 textToPtr(row.ExternalLink),
			AboutUser:            textToPtr(row.AboutMe),
			Age:                  int4ToUintPtr(row.Age),
			TheoryLevel:          int4ToUintPtr(row.TheoreticalKnowledgeLevel),
			Genres:               genres,
			Instruments:          domainInsts,
			IsVisible:            row.IsVisible,
		})
	}

	log.Printf("[REPO:GetFeed:SUCCESS] Возвращено %d профилей", len(profiles))
	return profiles, nil
}