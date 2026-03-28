package repository

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/katrinani/pivchiki-bot/backend/internal/db"
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
)

type AccountRepository interface {
	CreateAccount(account *domain.Account) (int64 ,error)
	GetAccountByLogin(login string) (*domain.Account, error)
	CheckAccountIsExist(login string) (bool, error)
}

var _ AccountRepository = (*AccountRepositoryImpl)(nil)

type AccountRepositoryImpl struct {
	queries *db.Queries
	db      *pgxpool.Pool
}

func NewAccountRepository(queries *db.Queries, pool *pgxpool.Pool) *AccountRepositoryImpl {
	return &AccountRepositoryImpl{
		queries: queries,
		db:      pool,
	}
}

func (r *AccountRepositoryImpl) CreateAccount(acc *domain.Account) (int64 ,error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	id, err := r.queries.CreateAccount(ctx, db.CreateAccountParams{
		Login:        acc.Login,
		PasswordHash: acc.PasswordHash,
	})
	if err != nil {
		return 0, err
	}

	return id, nil
}

func (r *AccountRepositoryImpl) GetAccountByLogin(login string) (*domain.Account, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	user, err := r.queries.GetAccountByLogin(ctx, login)
    if err != nil {
        return nil, err
    }

	return &domain.Account{
        ID:           domain.ProfileID(user.ID),
        Login:        user.Login,
        PasswordHash: user.PasswordHash,
    }, nil
}

//TODO сделать чтобы проверял профиль а не акканут
// проверить что айди ака и профился одинаковые
func (r *AccountRepositoryImpl) CheckAccountIsExist(login string) (bool, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	isExist, err := r.queries.CheckAccountExists(ctx, login)
    if err != nil {
        return false, err
    }

	return isExist, nil
}