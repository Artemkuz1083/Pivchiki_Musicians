package service

import (
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/repository"
)

type ProfileService interface {
	GetUserProfile(id domain.ProfileID) (*domain.FullProfile, error)
}

var _ ProfileService = (*ProfileServiceImpl)(nil)

type ProfileServiceImpl struct {
	repo repository.ProfileRepository
}

func NewProfileService(
	repo repository.ProfileRepository,
) *ProfileServiceImpl {
	return &ProfileServiceImpl{
		repo: repo,
	}
}

func (s *ProfileServiceImpl) GetUserProfile(id domain.ProfileID) (*domain.FullProfile, error) {
	profile, err := s.repo.GetUserProfile(id)
	if err != nil {
		return nil, err
	}

	return profile, nil
}
