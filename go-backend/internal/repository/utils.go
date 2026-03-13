package repository

import "github.com/jackc/pgx/v5/pgtype"

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
