package repository

import (
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
)

func textToPtr(t pgtype.Text) *string {
	if !t.Valid {
		return nil
	}
	return &t.String
}

func int4ToUintPtr(i pgtype.Int4) *uint {
	if !i.Valid {
		return nil
	}
	res := uint(i.Int32)
	return &res
}

func ToPerformanceEx(t pgtype.Text) *domain.PerformanceExperience {
	if !t.Valid {
		return nil
	}

	val := domain.PerformanceExperience(t.String)
	return &val
}

func ToText(s *string) pgtype.Text {
	return pgtype.Text{String: stringFromPtr(s), Valid: s != nil}
}

func ToInt4(u *uint) pgtype.Int4 {
	return pgtype.Int4{Int32: int32(uintFromPtr(u)), Valid: u != nil}
}

func ToBool(b *bool) pgtype.Bool {
	return pgtype.Bool{Bool: boolFromPtr(b), Valid: b != nil}
}

func stringFromPtr(s *string) string {
	if s != nil {
		return *s
	}
	return ""
}
func uintFromPtr(u *uint) uint {
	if u != nil {
		return *u
	}
	return 0
}
func boolFromPtr(b *bool) bool {
	if b != nil {
		return *b
	}
	return false
}
