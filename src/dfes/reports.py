from dfes.bans import TotalFireBans


def display_bans(latest_bans: tuple[TotalFireBans, ...]) -> None:
    for bans in latest_bans:
        print(f"Total Fire Bans")
        print(f"Issued: {bans.issued}")
        print(f"Declared for: {bans.declared_for}")
        print("")
        for location in bans.locations:
            print(f"{location[0]} / {location[1]}")
