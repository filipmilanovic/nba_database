drop table if exists nba.teams
;

create table nba.teams (
    team_season_id BIGINT PRIMARY KEY,
    team_id INT,
    team_name VARCHAR(33),
    abbreviation VARCHAR(3),
    conference VARCHAR(4),
    division VARCHAR(10),
    season INT,
    utc_written_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
    INDEX(team_id)
)
;
