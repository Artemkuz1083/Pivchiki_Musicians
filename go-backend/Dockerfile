FROM golang:1.25-alpine

WORKDIR /app

RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

RUN go install github.com/swaggo/swag/cmd/swag@latest

COPY . .

RUN swag init -g cmd/pivchiki_musicians/main.go --parseDependency --parseInternal

RUN go build -o main ./cmd/pivchiki_musicians/main.go

EXPOSE 8080
CMD ["/app/main"]