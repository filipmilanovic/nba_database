-- get available information of playoff games with missing series information
with seeds as (
	select game_id,
		   g.season,
		   th.conference as home_conference,
           ta.conference as away_conference,
		   sh.playoff_seed as home_seed,
		   sa.playoff_seed as away_seed
	from nba.games g
	inner join nba.standings sh on g.home_team_id = sh.team_id and g.season = sh.season
	inner join nba.standings sa on g.away_team_id = sa.team_id and g.season = sa.season
	inner join nba.teams th on sh.team_season_id = th.team_season_id
    inner join nba.teams ta on sa.team_season_id = ta.team_season_id
	where series_id is null
      and is_playoffs = 1
	order by game_id
),
-- define the playoff round for each game
rounds as (
	select *,
		   case
			   when home_conference != away_conference
				   then 4
			   when home_seed + away_seed = 9
				   then 1
			   when (home_seed in (1, 8)
					 and away_seed in (4, 5))
				 or (home_seed in (4, 5)
					 and away_seed in (1, 8))
				 or (home_seed in (2, 7)
					 and away_seed in (3, 6))
				 or (home_seed in (3, 6)
					 and away_seed in (2, 7))
				   then 2
			   else 3
		   end as playoff_round
	from seeds
    order by playoff_round, home_conference
),
-- define the elements of the series id (final format 004YY00RG), with G ordered by East/West, then best Seed
series_ids as (
	select *,
		   concat('004', right(season-1, 2), '00', playoff_round) as base_series_id,
           case
			   when playoff_round = 1
				   then least(home_seed, away_seed) - 1 + (home_conference = 'West')*4
		       when playoff_round = 2
				and (home_seed in (1, 8)
					 or away_seed in (1, 8))
			       then 0 + (home_conference = 'West')*2
		       when playoff_round = 2
				and (home_seed in (2, 7)
					 or away_seed in (2, 7))
			       then 1 + (home_conference = 'West')*2
		       when playoff_round = 3
			       then 0 + (home_conference = 'West')
		       else 0
		   end as matchup_id
	from rounds
),
-- concatenate the elements of the id
new_series_id as (
	select game_id,
		   concat(base_series_id, matchup_id) as series_id
	from series_ids
),
-- get the series game number
new_series_info as (
	select game_id,
		   series_id,
           row_number() over (partition by series_id order by game_id) as series_game
	from new_series_id
)
-- perform the update
update nba.games g
inner join new_series_info s on g.game_id = s.game_id
set g.series_id = s.series_id,
	g.series_game = s.series_game;
