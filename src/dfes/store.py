from dfes.bans import TotalFireBans


def file_name(bans: TotalFireBans) -> str:
    date_formatted = bans.issued.strftime("%Y_%m_%d_%H%M")
    return f"total_fire_bans_issued_{date_formatted}.rss"
