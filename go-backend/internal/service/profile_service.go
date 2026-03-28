package service

import (
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/repository"
)

type ProfileService interface {
	CreateUserProfile(profile *domain.FullProfile) (*domain.FullProfile, error)
	GetUserProfile(id domain.ProfileID) (*domain.FullProfile, error)
	UpdateUserProfile(profile *domain.FullProfileToUpdate) (*domain.FullProfile, error)
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
	profile, err := s.repo.GetProfile(id)
	if err != nil {
		return nil, err
	}

	return profile, nil
}

func (s *ProfileServiceImpl) UpdateUserProfile(profile *domain.FullProfileToUpdate) (*domain.FullProfile, error) {
	err := s.repo.UpdateProfile(profile)
	if err != nil {
		return nil, err
	}

	newProfile, err := s.repo.GetProfile(profile.ID)
	if err != nil {
		return nil, err
	}

	return newProfile, nil
}

func (s *ProfileServiceImpl) CreateUserProfile(profile *domain.FullProfile) (*domain.FullProfile, error) {
    err := s.repo.CreateProfile(profile)
    if err != nil {
        return nil, err
    }

    return s.repo.GetProfile(profile.ID)
}