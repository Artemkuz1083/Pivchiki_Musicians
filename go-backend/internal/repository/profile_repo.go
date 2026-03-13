package repository

import (
	"context"
	"log"
	"time"

	"github.com/katrinani/pivchiki-bot/backend/internal/db"
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
)

type ProfileRepository interface {
	GetUserProfile(profile domain.ProfileID) (*domain.FullProfile, error)
}

var _ ProfileRepository = (*ProfileRepositoryImpl)(nil)

type ProfileRepositoryImpl struct {
	queries *db.Queries
}

func NewInMemoryNoteRepository(queries *db.Queries) *ProfileRepositoryImpl {
	return &ProfileRepositoryImpl{
		queries: queries,
	}
}

func (r *ProfileRepositoryImpl) GetUserProfile(id domain.ProfileID) (*domain.FullProfile, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	log.Printf("отдаем говно айди пользовтелю из бд %d", id)
	user, err := r.queries.GetUser(ctx, int64(id))
	if err != nil {
		log.Printf("бля ошибка в бд вот такая хуйня %v", err)
		return nil, domain.ErrNoteNotFound
	}

	genres, err := r.queries.GetUserGenres(ctx, int64(id))
	if err != nil {
		genres = []string{}
	}

	dbInstruments, err := r.queries.GetUserInstruments(ctx, int64(id))
	if err != nil {
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
		PerformancExperience: textToPtr(user.HasPerformanceExperience),
		Link:                 textToPtr(user.ExternalLink),
		AboutUser:            textToPtr(user.AboutMe),
		Age:                  int4ToUintPtr(user.Age),
		ProficiencyLevel:     int4ToUintPtr(user.TheoreticalKnowledgeLevel),
		TheoryLevel:          int4ToUintPtr(user.TheoreticalKnowledgeLevel),
		Genres:               genres,
		Instruments:          instruments,
		IsVisible:            user.IsVisible,
	}

	return profile, nil
}
