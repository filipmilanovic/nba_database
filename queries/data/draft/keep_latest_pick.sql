with player_latest as (
	select player_id,
		   max(season) as season
	from nba.draft
	group by 1
	order by 1
)
delete from nba.draft d
where concat(d.player_id, d.season) not in
	(select concat(player_id, season)
     from player_latest)
