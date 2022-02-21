-- CHECK NUMBER OF GAMES IN GAMES
select
	g.season,
	game_type,
	count(distinct g.game_id)
from
	nba.games g
group by 1, 2
order by 1, 2
;
