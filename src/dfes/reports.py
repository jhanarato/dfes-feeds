from dfes.bans import TotalFireBans


def display_bans(latest_bans: tuple[TotalFireBans, ...]) -> None:
    for bans in latest_bans:
        print(f"Total Fire Bans")
        print(f"Issued: {bans.issued}")
        if bans.revoked:
            print(f"Revoked for: {bans.declared_for}")
        else:
            print(f"Declared for: {bans.declared_for}")
        for location in bans.locations:
            print(f"{location[0]} / {location[1]}")
        print("")