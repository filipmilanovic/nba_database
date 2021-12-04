with series_info as (
	select series_id,
		   home_team_id as higher_seed_team_id,
		   sh.playoff_seed as higher_seed,
		   away_team_id as lower_seed_team_id,
		   sa.playoff_seed as lower_seed
	from nba.games g
	inner join nba.standings sh on g.home_team_id = sh.team_id and g.season = sh.season
	inner join nba.standings sa on g.away_team_id = sa.team_id and g.season = sa.season
	where game_type = 2
	  and series_game = 1
)

update nba.playoffs p
inner join series_info s on p.series_id = s.series_id
set p.higher_seed_team_id = s.higher_seed_team_id,
	p.higher_seed = s.higher_seed,
    p.lower_seed_team_id = s.lower_seed_team_id,
    p.lower_seed = s.lower_seed
where p.higher_seed_team_id = 0;
