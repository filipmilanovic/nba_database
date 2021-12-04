-- CHECK NUMBER OF PLAYOFF GAMES IN GAMES
select
	g.season,
	game_type,
	count(distinct g.game_id)
from
	nba.games g
inner join
 	nba.playoffs p on g.series_id = p.series_id
;
