package repository

import (
	"context"
	"encoding/json"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/katrinani/pivchiki-bot/backend/internal/db"
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
)

// GroupProfileRepository — тот самый интерфейс, который ты просил
type GroupProfileRepository interface {
	// Profile Ops
	CreateGroupProfile(profile *domain.FullGroupProfile, creatorID domain.ProfileID) error
	GetGroupProfile(id domain.GroupID) (*domain.FullGroupProfile, error)
	UpdateGroupProfile(profile *domain.FullGroupProfileToUpdate) error
	DeleteGroupProfile(id domain.GroupID) error

	// Feed
	GetFeedGroupProfiles(userID domain.ProfileID, limit int, filters *domain.GroupProfileFilters) ([]*domain.FullGroupProfile, error)
	GetPublicFeedGroup(limit int) ([]*domain.FullGroupProfile, error)

	// Interactions & Matches
	UserSwipeGroup(userID domain.ProfileID, groupID domain.GroupID, action string) (bool, error)
	GroupSwipeUser(groupID domain.GroupID, targetUserID domain.ProfileID, action string) (bool, error)
	GetMatches(userID domain.ProfileID) ([]*domain.FullGroupProfile, error)

	// Members & Invitations
	CreateInvitation(groupID domain.GroupID, userID domain.ProfileID, role string) (int64, error)
	RespondToInvitation(inviteID int64, userID domain.ProfileID, status string) (domain.GroupID, string, error)
	RemoveMemberFromGroup(groupID domain.GroupID, userID domain.ProfileID) error
	GetUserGroups(userID domain.ProfileID) ([]domain.FullGroupProfile, error)
}

type GroupProfileRepositoryImpl struct {
	queries *db.Queries
	db      *pgxpool.Pool
}

// Убеждаемся, что реализация соответствует интерфейсу
var _ GroupProfileRepository = (*GroupProfileRepositoryImpl)(nil)

func NewGroupProfileRepository(queries *db.Queries, pool *pgxpool.Pool) GroupProfileRepository {
	return &GroupProfileRepositoryImpl{
		queries: queries,
		db:      pool,
	}
}

// --- PROFILE OPS ---

func (r *GroupProfileRepositoryImpl) CreateGroupProfile(profile *domain.FullGroupProfile, creatorID domain.ProfileID) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	tx, err := r.db.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)
	qtx := r.queries.WithTx(tx)

	concertsJSON, _ := json.Marshal(profile.Concerts)

	groupID, err := qtx.CreateGroupProfile(ctx, db.CreateGroupProfileParams{
		Name:             profile.GroupName,
		City:             pgtype.Text{String: profile.City, Valid: true},
		FormationDate:    pgtype.Int4{Int32: int32(profile.YearOfCreation), Valid: true},
		Platforms:        profile.Platforms,
		Description:      ToText(profile.AboutGroup),
		IsVisible:        profile.IsVisible,
		SeriousnessLevel: pgtype.Text{String: string(profile.LevelOfSerious), Valid: true},
		FinancialStatus:  pgtype.Text{String: string(profile.FinancialStatus), Valid: true},
		Concerts:         concertsJSON,
	})
	if err != nil {
		return err
	}

	err = qtx.AddGroupMember(ctx, db.AddGroupMemberParams{
		GroupID: groupID,
		UserID:  int64(creatorID),
		Role:    "OWNER",
		IsAdmin: true,
	})
	if err != nil {
		return err
	}

	for _, genre := range profile.Genres {
		_ = qtx.AddGroupGenre(ctx, db.AddGroupGenreParams{GroupID: groupID, Name: genre})
	}

	profile.ID = domain.GroupID(groupID)
	return tx.Commit(ctx)
}

func (r *GroupProfileRepositoryImpl) GetGroupProfile(id domain.GroupID) (*domain.FullGroupProfile, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	row, err := r.queries.GetGroup(ctx, int64(id))
	if err != nil {
		return nil, err
	}

	genres, _ := r.queries.GetGroupGenres(ctx, int64(id))
	dbMembers, _ := r.queries.GetGroupMembers(ctx, int64(id))

	members := make([]domain.GroupMember, 0, len(dbMembers))
	for _, m := range dbMembers {
		members = append(members, domain.GroupMember{
			UserID: domain.ProfileID(m.UserID),
			Name:   m.Name.String,
			Role:   m.Role,
		})
	}

	var concerts map[int]string
	if row.Concerts != nil {
		_ = json.Unmarshal(row.Concerts, &concerts)
	}

	return &domain.FullGroupProfile{
		ID:              domain.GroupID(row.ID),
		GroupName:       row.Name,
		City:            row.City.String,
		AboutGroup:      textToPtr(row.Description),
		YearOfCreation:  uint(row.FormationDate.Int32),
		Platforms:       row.Platforms,
		IsVisible:       row.IsVisible,
		LevelOfSerious:  domain.LevelOfSeriousness(row.SeriousnessLevel.String),
		FinancialStatus: domain.FinancialStatus(row.FinancialStatus.String),
		Genres:          genres,
		Members:         members,
		Concerts:        concerts,
	}, nil
}

func (r *GroupProfileRepositoryImpl) UpdateGroupProfile(profile *domain.FullGroupProfileToUpdate) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	tx, err := r.db.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)
	qtx := r.queries.WithTx(tx)

	var concertsJSON []byte
	if profile.Concerts != nil {
		concertsJSON, _ = json.Marshal(profile.Concerts)
	}

	err = qtx.UpdateGroupProfile(ctx, db.UpdateGroupProfileParams{
		ID:               int64(profile.ID),
		Name:             stringFromPtr(profile.GroupName),
		City:             ToText(profile.City),
		FormationDate:    ToInt4(profile.YearOfCreation),
		Platforms:        *profile.Platforms,
		Description:      ToText(profile.AboutGroup),
		IsVisible:        ToBool(profile.IsVisible),
		SeriousnessLevel: pgtype.Text{String: string(*profile.LevelOfSerious), Valid: profile.LevelOfSerious != nil},
		FinancialStatus:  pgtype.Text{String: string(*profile.FinancialStatus), Valid: profile.FinancialStatus != nil},
		Concerts:         concertsJSON,
	})
	if err != nil {
		return err
	}

	if profile.Genres != nil {
		_ = qtx.DeleteGroupGenres(ctx, int64(profile.ID))
		for _, g := range *profile.Genres {
			_ = qtx.AddGroupGenre(ctx, db.AddGroupGenreParams{GroupID: int64(profile.ID), Name: g})
		}
	}

	return tx.Commit(ctx)
}

func (r *GroupProfileRepositoryImpl) DeleteGroupProfile(id domain.GroupID) error {
	return r.queries.DeleteGroupProfile(context.Background(), int64(id))
}

// --- FEED OPS ---

func (r *GroupProfileRepositoryImpl) GetFeedGroupProfiles(userID domain.ProfileID, limit int, filters *domain.GroupProfileFilters) ([]*domain.FullGroupProfile, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	params := db.GetGroupFeedParams{
		SwiperUserID: int64(userID),
		Limit:        int32(limit),
		Cities:       filters.Cities,
	}

	rows, err := r.queries.GetGroupFeed(ctx, params)
	if err != nil {
		return nil, err
	}

	result := make([]*domain.FullGroupProfile, 0, len(rows))
	for _, row := range rows {
		result = append(result, r.mapFeedRowToGroup(row))
	}
	return result, nil
}

func (r *GroupProfileRepositoryImpl) GetPublicFeedGroup(limit int) ([]*domain.FullGroupProfile, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    rows, err := r.queries.GetPublicGroupFeed(ctx, int32(limit))
    if err != nil {
        return nil, err
    }

    result := make([]*domain.FullGroupProfile, 0, len(rows))
    for _, row := range rows {
        feedRow := db.GetGroupFeedRow{
            ID:               row.ID,
            Name:             row.Name,
            City:             row.City,
            FormationDate:    row.FormationDate,
            Platforms:        row.Platforms,
            Description:      row.Description,
            IsVisible:        row.IsVisible,
            SeriousnessLevel: row.SeriousnessLevel,
            FinancialStatus:  row.FinancialStatus,
            Concerts:         row.Concerts,
            CreatedAt:        row.CreatedAt,
            Genres:           row.Genres,
            Members:          row.Members,
        }
        
        result = append(result, r.mapFeedRowToGroup(feedRow))
    }
    return result, nil
}

// --- INTERACTIONS & MATCHES ---

func (r *GroupProfileRepositoryImpl) UserSwipeGroup(userID domain.ProfileID, groupID domain.GroupID, action string) (bool, error) {
	ctx := context.Background()
	err := r.queries.AddGroupInteraction(ctx, db.AddGroupInteractionParams{
		SwiperUserID:  int64(userID),
		TargetGroupID: int64(groupID),
		Action:        action,
	})
	if err != nil {
		return false, err
	}

	if action != "like" {
		return false, nil
	}

	matches, _ := r.queries.GetGroupMatches(ctx, int64(userID))
	for _, m := range matches {
		if m.ID == int64(groupID) {
			return true, nil
		}
	}
	return false, nil
}

func (r *GroupProfileRepositoryImpl) GroupSwipeUser(groupID domain.GroupID, targetUserID domain.ProfileID, action string) (bool, error) {
	err := r.queries.AddGroupLikeUser(context.Background(), db.AddGroupLikeUserParams{
		SwiperGroupID: int64(groupID),
		TargetUserID:  int64(targetUserID),
		Action:        action,
	})
	return action == "like", err
}

func (r *GroupProfileRepositoryImpl) GetMatches(userID domain.ProfileID) ([]*domain.FullGroupProfile, error) {
	ctx := context.Background()
	rows, err := r.queries.GetGroupMatches(ctx, int64(userID))
	if err != nil {
		return nil, err
	}

	result := make([]*domain.FullGroupProfile, 0, len(rows))
	for _, row := range rows {
		var concerts map[int]string
		_ = json.Unmarshal(row.Concerts, &concerts)

		genres, ok := row.Genres.([]string)
		if !ok {
			genres = []string{}
		}

		result = append(result, &domain.FullGroupProfile{
			ID:              domain.GroupID(row.ID),
			GroupName:       row.Name,
			City:            row.City.String,
			AboutGroup:      textToPtr(row.Description),
			YearOfCreation:  uint(row.FormationDate.Int32),
			Platforms:       row.Platforms,
			IsVisible:       row.IsVisible,
			LevelOfSerious:  domain.LevelOfSeriousness(row.SeriousnessLevel.String),
			FinancialStatus: domain.FinancialStatus(row.FinancialStatus.String),
			Genres:          genres,
			Concerts:        concerts,
		})
	}
	return result, nil
}

// --- MEMBERS & INVITATIONS ---

func (r *GroupProfileRepositoryImpl) CreateInvitation(groupID domain.GroupID, userID domain.ProfileID, role string) (int64, error) {
	id, err := r.queries.CreateInvitation(context.Background(), db.CreateInvitationParams{
        GroupID: int64(groupID),
        UserID:  int64(userID),
        Role:    role,
    })
    
    return int64(id), err
}

func (r *GroupProfileRepositoryImpl) RespondToInvitation(inviteID int64, userID domain.ProfileID, status string) (domain.GroupID, string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	tx, err := r.db.Begin(ctx)
	if err != nil {
		return 0, "", err
	}
	defer tx.Rollback(ctx)
	qtx := r.queries.WithTx(tx)

	res, err := qtx.RespondToInvitation(ctx, db.RespondToInvitationParams{
		ID:     int32(inviteID),
		Status: status,
		UserID: int64(userID),
	})
	if err != nil {
		return 0, "", err
	}

	if status == "ACCEPTED" {
		err = qtx.AddGroupMember(ctx, db.AddGroupMemberParams{
			GroupID: res.GroupID,
			UserID:  int64(userID),
			Role:    res.Role,
			IsAdmin: false,
		})
		if err != nil {
			return 0, "", err
		}
	}

	return domain.GroupID(res.GroupID), res.Role, tx.Commit(ctx)
}

func (r *GroupProfileRepositoryImpl) RemoveMemberFromGroup(groupID domain.GroupID, userID domain.ProfileID) error {
	return r.queries.RemoveMemberFromGroup(context.Background(), db.RemoveMemberFromGroupParams{
		GroupID: int64(groupID),
		UserID:  int64(userID),
	})
}

func (r *GroupProfileRepositoryImpl) GetUserGroups(userID domain.ProfileID) ([]domain.FullGroupProfile, error) {
	rows, err := r.queries.GetUserGroups(context.Background(), int64(userID))
	if err != nil {
		return nil, err
	}

	result := make([]domain.FullGroupProfile, 0, len(rows))
	for _, row := range rows {
		result = append(result, domain.FullGroupProfile{
			ID:        domain.GroupID(row.ID),
			GroupName: row.Name,
		})
	}
	return result, nil
}

// --- HELPER MAPPING ---

func (r *GroupProfileRepositoryImpl) mapFeedRowToGroup(row db.GetGroupFeedRow) *domain.FullGroupProfile {
	var members []domain.GroupMember

	if row.Members != nil {
		switch v := row.Members.(type) {
		case []byte:
			_ = json.Unmarshal(v, &members)
		case string:
			_ = json.Unmarshal([]byte(v), &members)
		default:
			if b, err := json.Marshal(v); err == nil {
				_ = json.Unmarshal(b, &members)
			}
		}
	}

	var concerts map[int]string
	if len(row.Concerts) > 0 {
		_ = json.Unmarshal(row.Concerts, &concerts)
	}

	var genres []string
	if row.Genres != nil {
		switch v := row.Genres.(type) {
		case []string:
			genres = v
		case []interface{}:
			for _, item := range v {
				if s, ok := item.(string); ok {
					genres = append(genres, s)
				}
			}
		default:
			genres = []string{}
		}
	}

	if genres == nil {
		genres = []string{}
	}

	return &domain.FullGroupProfile{
		ID:              domain.GroupID(row.ID),
		GroupName:       row.Name,
		City:            row.City.String,
		AboutGroup:      textToPtr(row.Description),
		YearOfCreation:  uint(row.FormationDate.Int32),
		Platforms:       row.Platforms,
		IsVisible:       row.IsVisible,
		LevelOfSerious:  domain.LevelOfSeriousness(row.SeriousnessLevel.String),
		FinancialStatus: domain.FinancialStatus(row.FinancialStatus.String),
		Genres:          genres,
		Members:         members,
		Concerts:        concerts,
	}
}
