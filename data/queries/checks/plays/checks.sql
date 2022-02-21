-- CHECK NUMBER OF GAMES BETWEEN GAMES AND PLAYS
select
	season,
    game_type,
	count(distinct g.game_id) as games_games,
	count(distinct p.game_id) as plays_games
from
	nba.games g
left join
	nba.plays p on g.game_id = p.game_id
group by 1, 2
order by 1, 2
;


-- CHECK SCORES BETWEEN PLAYS AND GAMES
select
	p.game_id,
    p.team_id,
    case
		when p.team_id = g.home_team_id
			then home_score
		when p.team_id = g.away_team_id
			then away_score
	end as games_score,
    sum(event_value) as plays_score
from
	nba.plays p
inner join
	nba.games g on p.game_id = g.game_id
			   and p.event_name like '%Make%'
group by 1, 2, 3
having games_score != plays_score
;


-- CHECK BOX SCORE
select
	team_id,
	player_id,
	count(distinct case when event_name = 'FG Make' then play_id end) as FGM,
	count(distinct case when event_name like 'FG%' then play_id end) AS FGA,
	count(distinct case when event_name = 'FG Make' and event_value = 3 then play_id end) as TPM,
	count(distinct case when event_name like 'FG%' and event_value = 3 then play_id end) AS TPA,
	count(distinct case when event_name = 'FT Make' then play_id end) as FTM,
	count(distinct case when event_name like 'FT%' then play_id end) AS FTA,
	count(distinct case when event_name = 'Offensive Rebound' then play_id end) AS OREB,
	count(distinct case when event_name = 'Defensive Rebound' then play_id end) AS DREB,
	count(distinct case when event_name like '%Rebound' then play_id end) AS REB,
	count(distinct case when event_name = 'Assist' then play_id end) AS AST,
	count(distinct case when event_name = 'Steal' then play_id end) AS STL,
	count(distinct case when event_name = 'Block' then play_id end) AS BLK,
	count(distinct case when event_name = 'Turnover' then play_id end) AS TOV,
	count(distinct case when event_name like '%Foul' then play_id end) AS PF,
	sum(case when event_name like '%Make' then event_value end) as PTS
from
	nba.plays
where
	game_id = 0020000001
and
	player_id is not null
group by 1, 2
;


-- CHECK EMPTY EVENTS
select
	p.*
from
	nba.plays p
inner join
	nba.games g on p.game_id = g.game_id
where
	season = 2005
and
	event_name = ''
and
	team_id is not null
and
	player_id is not null
;
