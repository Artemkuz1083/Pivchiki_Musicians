package service

import (
	"errors"
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/repository"
)

type GroupProfileService interface {
	CreateGroupProfile(profile *domain.FullGroupProfile, creatorID domain.ProfileID) (*domain.FullGroupProfile, error)
	GetGroupProfile(id domain.GroupID) (*domain.FullGroupProfile, error)
	UpdateGroupProfile(profile *domain.FullGroupProfileToUpdate, operatorID domain.ProfileID) (*domain.FullGroupProfile, error)
	GetFeedGroup(userID domain.ProfileID, limit int, filters *domain.GroupProfileFilters) ([]*domain.FullGroupProfile, error)
	GetPublicFeedGroup(limit int) ([]*domain.FullGroupProfile, error)
	Swipe(userID domain.ProfileID, groupID domain.GroupID, action string) (*domain.GroupSwipeResult, error)
	GetMatches(userID domain.ProfileID) ([]*domain.FullGroupProfile, error)
	DeleteGroupProfile(groupID domain.GroupID, operatorID domain.ProfileID) error
	
	InviteUser(groupID domain.GroupID, targetUserID domain.ProfileID, role string) (int64, error)
	RespondToInvite(inviteID int64, userID domain.ProfileID, accept bool) error
}

type GroupProfileServiceImpl struct {
	repo repository.GroupProfileRepository
}

var _ GroupProfileService = (*GroupProfileServiceImpl)(nil)

func NewGroupProfileService(repo repository.GroupProfileRepository) GroupProfileService {
	return &GroupProfileServiceImpl{repo: repo}
}

func (s *GroupProfileServiceImpl) CreateGroupProfile(profile *domain.FullGroupProfile, creatorID domain.ProfileID) (*domain.FullGroupProfile, error) {
	err := s.repo.CreateGroupProfile(profile, creatorID)
	if err != nil {
		return nil, err
	}
	return s.repo.GetGroupProfile(profile.ID)
}

func (s *GroupProfileServiceImpl) GetGroupProfile(id domain.GroupID) (*domain.FullGroupProfile, error) {
	return s.repo.GetGroupProfile(id)
}

func (s *GroupProfileServiceImpl) UpdateGroupProfile(profile *domain.FullGroupProfileToUpdate, operatorID domain.ProfileID) (*domain.FullGroupProfile, error) {
	existing, err := s.repo.GetGroupProfile(profile.ID)
	if err != nil {
		return nil, err
	}

	isMember := false
	for _, m := range existing.Members {
		if m.UserID == operatorID {
			isMember = true
			break
		}
	}

	if !isMember {
		return nil, errors.New("permission denied: only group members can update profile")
	}

	if err := s.repo.UpdateGroupProfile(profile); err != nil {
		return nil, err
	}
	return s.repo.GetGroupProfile(profile.ID)
}

func (s *GroupProfileServiceImpl) GetFeedGroup(userID domain.ProfileID, limit int, filters *domain.GroupProfileFilters) ([]*domain.FullGroupProfile, error) {
	return s.repo.GetFeedGroupProfiles(userID, limit, filters)
}

func (s *GroupProfileServiceImpl) GetPublicFeedGroup(limit int) ([]*domain.FullGroupProfile, error) {
	return s.repo.GetPublicFeedGroup(limit)
}

func (s *GroupProfileServiceImpl) Swipe(userID domain.ProfileID, groupID domain.GroupID, action string) (*domain.GroupSwipeResult, error) {
	isMatch, err := s.repo.UserSwipeGroup(userID, groupID, action)
	if err != nil {
		return nil, err
	}
	return &domain.GroupSwipeResult{IsMatch: isMatch}, nil
}

func (s *GroupProfileServiceImpl) GetMatches(userID domain.ProfileID) ([]*domain.FullGroupProfile, error) {
	return s.repo.GetMatches(userID)
}

func (s *GroupProfileServiceImpl) InviteUser(groupID domain.GroupID, targetUserID domain.ProfileID, role string) (int64, error) {
	return s.repo.CreateInvitation(groupID, targetUserID, role)
}

func (s *GroupProfileServiceImpl) RespondToInvite(inviteID int64, userID domain.ProfileID, accept bool) error {
	status := "REJECTED"
	if accept {
		status = "ACCEPTED"
	}
	_, _, err := s.repo.RespondToInvitation(inviteID, userID, status)
	return err
}

func (s *GroupProfileServiceImpl) DeleteGroupProfile(groupID domain.GroupID, operatorID domain.ProfileID) error {
    existing, err := s.repo.GetGroupProfile(groupID)
    if err != nil {
        return err
    }

    isOwner := false
    for _, m := range existing.Members {
        if m.UserID == operatorID && m.Role == "OWNER" {
            isOwner = true
            break
        }
    }

    if !isOwner {
        return errors.New("permission denied: only the group owner can delete the profile")
    }

    return s.repo.DeleteGroupProfile(groupID)
}