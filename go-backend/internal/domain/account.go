package domain

type Account struct {
	ID           ProfileID
	Login        string
	PasswordHash string
	CreatedAt    int
}