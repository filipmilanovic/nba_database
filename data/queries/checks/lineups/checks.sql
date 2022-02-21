-- CHECK NUMBER OF GAMES WITH LINEUPS
select
	g.season,
	game_type,
	count(distinct g.game_id)
from
	nba.games g
inner join
	nba.lineups l on g.game_id = l.game_id
group by 1, 2
order by 1, 2
;
