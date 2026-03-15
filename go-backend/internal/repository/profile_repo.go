package repository

import (
	"context"
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
}

var _ ProfileRepository = (*ProfileRepositoryImpl)(nil)

type ProfileRepositoryImpl struct {
	queries *db.Queries
	db    *pgxpool.Pool
}

func NewInMemoryNoteRepository(queries *db.Queries, pool *pgxpool.Pool) *ProfileRepositoryImpl {
	return &ProfileRepositoryImpl{
		queries: queries,
		db:    pool,
	}
}

func (r *ProfileRepositoryImpl) GetProfile(id domain.ProfileID) (*domain.FullProfile, error) {
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
		PerformancExperience: ToPerformanceEx(user.HasPerformanceExperience),
		Link:                 textToPtr(user.ExternalLink),
		AboutUser:            textToPtr(user.AboutMe),
		Age:                  int4ToUintPtr(user.Age),
		TheoryLevel:          int4ToUintPtr(user.TheoreticalKnowledgeLevel),
		Genres:               genres,
		Instruments:          instruments,
		IsVisible:            user.IsVisible,
	}

	return profile, nil
}

func (r *ProfileRepositoryImpl) UpdateProfile(profile *domain.FullProfileToUpdate) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	tx, err := r.db.BeginTx(ctx, pgx.TxOptions{
		IsoLevel: pgx.ReadCommitted,
	})
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	qtx := r.queries.WithTx(tx)

	err = qtx.UpdateUserProfile(ctx, db.UpdateUserProfileParams{
		ID: int64(profile.ID),
		Name: ToText(profile.UserName),
		City: ToText(profile.City),
		Contacts: ToText(profile.Contact),
		HasPerformanceExperience: ToText((*string)(profile.PerformancExperience)),
		AboutMe: ToText(profile.AboutUser),
		ExternalLink: ToText(profile.Link),
		Age: ToInt4(profile.Age), 
		TheoreticalKnowledgeLevel: ToInt4(profile.TheoryLevel),
		IsVisible: ToBool(profile.IsVisible), 
	})
	if err != nil {
		return err
	}

	if profile.Genres != nil {
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
                return err
            }
        }
	}

	if profile.Instruments != nil {
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
                return err
            }
        }
    }

	if err := tx.Commit(ctx); err != nil {
        return err
    }

	return nil
}
