update nba.standings s
inner join nba.teams t on s.team_season_id = t.team_season_id
set playoff_seed = 5
where s.season = 2001
  and team_name = 'Dallas Mavericks'
  and playoff_seed = 4;
