from dfes.bans import TotalFireBans


def display_bans(bans: TotalFireBans) -> None:
    print(f"Total Fire Bans")
    print(f"Issued: {bans.issued}")
    print(f"Declared for: {bans.declared_for}")
    print("")
    for location in bans.locations:
        print(f"{location[0]} / {location[1]}")
